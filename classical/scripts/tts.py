import argparse, csv
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import re

from matplotlib.ticker import MaxNLocator
from seaborn import color_palette
from math import sqrt

lt_table = {
    'bh_1': '1',
    'bh_2': '2',
    'bh_4': '4',
    'bh_8': '8',
    'bh_16': '16',
    'bh_32': '32',
    'bh_64': '64',
    'bh_128': '128',
    'bh_256': '256',
    'bh_512': '512',
    'da_1': '1',
    'da_2': '2',
    'da_4': '4',
    'da_8': '8',
    'da_16': '16',
    'da_32': '32',
    'da_64': '64',
    'da_128': '128',
    'da_256': '256',
    'da_512': '512',
    'da_1024': '1024',
    'da_2048': '2048',
    'da_4096': '4096',
    'da_8192': '8192',
    'ipopt_0': 'Ipopt',
    'sqp_0': 'SQP',
    'sgd_16': '16',
    'sgd_8': '8',
    'sgd_4': '4',
    'sgd_2': '2',
    'sgd_1': '1',
    'sgd_0.5': '1/2',
    'sgd_0.25': '1/4',
    'sgd_0.125': '1/8',
    'sgd_0.0625': '1/16',
    'sgd_0.03125': '1/32',
    'sgd_0.015625': '1/64',
    'sgd_0.0078125': '1/128',
    'sgd_0.00390625': '1/256',
    'sgd_0.001953125': '1/512',
    'sgd2_2': '2',
    'sgd2_4': '4',
    'sgd2_8': '8',
    'sgd2_16': '16',
    'sgd2_32': '32',
    'sgd2_64': '64',
    'sgd2_128': '128',
    'sgd2_256': '256',
    'sgd2_512': '512',
    'sgd2_1024': '1024',
    'gb_0': 'Gurobi',
}

LOCAL_MIN = 0.0883667
INF = 1e10

def R(p0, p):
    if p > p0:
        return 1
    else:
        return math.ceil(math.log(1 - p0) / math.log(1 - p))

def label_transform(s):
    if args.ltoff:
        return s
    if args.rainbow:
        x = re.search(r'([a-z0-9]*)_([0-9\.]*)', s)
        return x.group(2)
    if s in lt_table.keys():
        return lt_table[s]
    else:
        return s

def plot_tts(specified_iter=None):
    data = {}
    with open(args.input, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = (row['prefix'], int(row['dim']), float(row['maxiter']), row['maxiter'])
            if row['result'] == 'Unknown':
                continue
            res = float(row['result'])
            if res < LOCAL_MIN / 2:
                hit = 1
            else:
                hit = 0
            if args.useiter:
                time_used = float(row['maxiter'])
            else:
                time_used = float(row['usertime'])
            if key in data:
                cnt, tot_hit, tot_utime, utime_list = data[key]
                utime_list.append((time_used, hit))
                data[key] = (cnt + 1, tot_hit + hit, tot_utime + time_used, utime_list)
            else:
                data[key] = (1, hit, time_used, [(time_used, hit)])
    curves={}
    if args.rainbow:
        cutoff_list=[]
    for key in sorted(data.keys()):
        if not args.dynamic:
            cnt, tot_hit, tot_utime, _ = data[key]
            prefix, dim, _, maxiter = key
            suc_prob = float(tot_hit) / cnt
            ci_95_radius = 1.96 * sqrt(suc_prob * (1 - suc_prob) / cnt)
            #print(ci_95_radius)
            if tot_hit >= args.robustness:
                hypo_tts = tot_utime / cnt * R(0.99, suc_prob)
                hypo_tts_ub = tot_utime / cnt * R(0.99, suc_prob - ci_95_radius)
                hypo_tts_lb = tot_utime / cnt * R(0.99, suc_prob + ci_95_radius)
                #print("[%.5lf,%.5lf]" % (hypo_tts_lb, hypo_tts_ub))
                if (prefix, maxiter) in curves:
                    curves[(prefix, maxiter)].append({'x':dim, 'y':hypo_tts, 'y_ub':hypo_tts_ub, 'y_lb':hypo_tts_lb})
                else:
                    curves[(prefix, maxiter)] = [{'x':dim, 'y':hypo_tts, 'y_ub':hypo_tts_ub, 'y_lb':hypo_tts_lb}]
            if args.verbose:
                print("[VERBOSE] %s_n%d_u%s: prob. = %d/%d" % (prefix, dim, maxiter, tot_hit, cnt))
        else:
            cnt, _, _, utime_list = data[key]
            prefix, dim, _, maxiter = key
            utime_list.sort()
            m = len(utime_list)
            tot_hit = tot_utime = 0
            min_tts = INF
            for i in range(m):
                utime, hit = utime_list[i]
                tot_hit += hit
                tot_utime += utime
                cur_suc_prob = float(tot_hit) / cnt
                ci_95_radius = 1.96 * sqrt(cur_suc_prob * (1 - cur_suc_prob) / cnt)
                if tot_hit >= args.robustness:
                    cur_tts = (tot_utime + utime * (cnt - i - 1)) / cnt * R(0.99, cur_suc_prob)
                else:
                    cur_tts = INF
                if cur_tts < min_tts:
                    min_tts = cur_tts
                    min_tts_ub = (tot_utime + utime * (cnt - i - 1)) / cnt * R(0.99, cur_suc_prob - ci_95_radius)
                    min_tts_lb = (tot_utime + utime * (cnt - i - 1)) / cnt * R(0.99, cur_suc_prob + ci_95_radius)
                    min_tts_cutoff = utime
            #if not args.rainbow:
            if (prefix, maxiter) in curves:
                curves[(prefix, maxiter)].append({'x':dim, 'y':min_tts, 'y_ub':min_tts_ub, 'y_lb':min_tts_lb})
            else:
                curves[(prefix, maxiter)] = [{'x':dim, 'y':min_tts, 'y_ub':min_tts_ub, 'y_lb':min_tts_lb}]
            if args.rainbow:
                cutoff_list.append(min_tts_cutoff)
            if args.verbose:
                print("[VERBOSE] %s_n%d_u%s: prob. = %d/%d; cutoff = %.4f" % (prefix, dim, maxiter, tot_hit, cnt, min_tts_cutoff))

    if args.rainbow:
        cutoff_list.sort()
        for cutoff in cutoff_list:
            maxiter = ("%.4f" % cutoff)
            for key in sorted(data.keys()):
                cnt, _, _, utime_list = data[key]
                prefix, dim, _, _ = key
                utime_list.sort()
                m = len(utime_list)
                tot_hit = tot_utime = 0
                for i in range(m):
                    utime, hit = utime_list[i]
                    if utime <= cutoff:
                        tot_hit += hit
                    tot_utime += min(utime, cutoff)
                suc_prob = float(tot_hit) / cnt
                ci_95_radius = 1.96 * sqrt(suc_prob * (1 - suc_prob) / cnt)
                if tot_hit >= args.robustness:
                    hypo_tts = tot_utime / cnt * R(0.99, suc_prob)
                    hypo_tts_ub = tot_utime / cnt * R(0.99, suc_prob - ci_95_radius)
                    hypo_tts_lb = tot_utime / cnt * R(0.99, suc_prob + ci_95_radius)
                    #print("[%.5lf,%.5lf]" % (hypo_tts_lb, hypo_tts_ub))
                    if (prefix, maxiter) in curves:
                        curves[(prefix, maxiter)].append({'x':dim, 'y':hypo_tts, 'y_ub':hypo_tts_ub, 'y_lb':hypo_tts_lb})
                    else:
                        curves[(prefix, maxiter)] = [{'x':dim, 'y':hypo_tts, 'y_ub':hypo_tts_ub, 'y_lb':hypo_tts_lb}]

    if args.rainbow:
        palette = color_palette("husl", len(curves) - 1)
    else:
        palette = color_palette("husl", len(curves))

    for i, key in enumerate(curves):
        if args.rainbow:
            i -= 1
        prefix, maxiter = key
        curves[key].sort(key=lambda e: e['x'])
        #print(curves[key])
        x = [p['x'] for p in curves[key]]
        y = [p['y'] for p in curves[key]]
        y_err = [[p['y'] - p['y_lb'] for p in curves[key]], [p['y_ub'] - p['y'] for p in curves[key]]]
        if specified_iter is None or maxiter == specified_iter:
            if args.rainbow and maxiter == '0':
                plt.plot(x, y, linewidth=5, color=(0,0,0,0.3), label='Minimal TTS')
            else:
                plt.errorbar(x, y, yerr=y_err, color=palette[i], label=label_transform(prefix+"_"+maxiter), capsize=3)
            #plt.scatter(x, y, s=100, color=palette[i])
                plt.plot(x, y, linewidth=1, color=palette[i])

'''
def plot_tts_plus(specified_iter=None):
    data = {}
    with open(args.input, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = (row['prefix'], int(row['dim']), float(row['maxiter']))
            if key in data:
                cnt, tot_res, tot_utime = data[key]
                data[key] = (cnt + 1, tot_res + float(row['result']), tot_utime + float(row['usertime']))
            else:
                data[key] = (1, float(row['result']), float(row['usertime']))
    curves={}
    for key in data:
        cnt, tot_res, tot_utime = data[key]
        prefix, dim, maxiter = key
        suc_prob_per_well = 1.0 - tot_res / cnt / LOCAL_MIN / dim
        hypo_suc_prob = suc_prob_per_well ** dim
        hypo_tts = tot_utime / cnt / hypo_suc_prob
        if (prefix, maxiter) in curves:
            curves[(prefix, maxiter)].append({'x':dim, 'y':hypo_tts})
        else:
            curves[(prefix, maxiter)] = [{'x':dim, 'y':hypo_tts}]
        #print("%s: %s: %g" % (key, data[key], hypo_tts))
    for key in curves:
        prefix, maxiter = key
        curves[key].sort(key=lambda e: e['x'])
        #print(curves[key])
        x = [p['x'] for p in curves[key]]
        y = [p['y'] for p in curves[key]]
        if specified_iter is None or maxiter == specified_iter:
            plt.plot(x, y, label=prefix+"_"+str(maxiter)+"+")
'''

def main(args):
    plot_tts()
    #plot_tts_plus()

    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.legend(loc="lower right", fontsize="8", title=args.ltitle, title_fontsize="8", ncol=3)
    plt.yscale('log')
    plt.xlabel("Dimensionaity")
    plt.ylabel("Time-to-Solution (%s)" % args.yunit)
    plt.savefig(args.output)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='set output .PNG file name', required=True)
    parser.add_argument('-i', '--input', help='set input .CSV file name', required=True)
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument('--useiter', default=False, help='compute TTS using the "maxiter" field', action='store_true')
    parser.add_argument('--dynamic', default=False, help='enable the dynamic TTS estimation', action='store_true')
    parser.add_argument('--rainbow', default=False, help='draw all curves for dynamic TTS estimation', action='store_true')
    parser.add_argument('--yunit', default='sec', help='set the unit for y axis (default="sec")')
    parser.add_argument('--robustness', type=int, default=5, help='kill data points with less than this number of success instances observed')
    parser.add_argument('--ltoff', default=False, help='disable automatic label transformation', action='store_true')
    parser.add_argument('--ltitle', default='Legend', help='set the legend title (default="Legend")')
    args = parser.parse_args()
    main(args)
import argparse, csv
import matplotlib.pyplot as plt
import matplotlib as mpl

from matplotlib.ticker import MaxNLocator

LOCAL_MIN = 0.0883667
INF = 1e10

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
    for key in sorted(data.keys()):
        if not args.dynamic:
            cnt, tot_hit, tot_utime, _ = data[key]
            prefix, dim, _, maxiter = key
            suc_prob = float(tot_hit) / cnt
            if suc_prob > 0:
                hypo_tts = tot_utime / cnt / suc_prob
                if (prefix, maxiter) in curves:
                    curves[(prefix, maxiter)].append({'x':dim, 'y':hypo_tts})
                else:
                    curves[(prefix, maxiter)] = [{'x':dim, 'y':hypo_tts}]
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
                if tot_hit > 0:
                    cur_tts = (tot_utime + utime * (cnt - i - 1)) / cnt / cur_suc_prob
                else:
                    cur_tts = INF
                if cur_tts < min_tts:
                    min_tts = cur_tts
                    min_tts_cutoff = utime
            if (prefix, maxiter) in curves:
                curves[(prefix, maxiter)].append({'x':dim, 'y':min_tts})
            else:
                curves[(prefix, maxiter)] = [{'x':dim, 'y':min_tts}]
            if args.verbose:
                print("[VERBOSE] %s_n%d_u%s: prob. = %d/%d; cutoff = %.4f" % (prefix, dim, maxiter, tot_hit, cnt, min_tts_cutoff))

    for key in curves:
        prefix, maxiter = key
        curves[key].sort(key=lambda e: e['x'])
        #print(curves[key])
        x = [p['x'] for p in curves[key]]
        y = [p['y'] for p in curves[key]]
        if specified_iter is None or maxiter == specified_iter:
            plt.scatter(x, y, label=prefix+"_"+maxiter)
            plt.plot(x, y)

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

def main(args):
    plot_tts()
    #plot_tts_plus()

    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.legend(loc="upper left", fontsize="7")
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
    parser.add_argument('--yunit', default='sec', help='set the unit for y axis (default="sec")')
    args = parser.parse_args()
    main(args)
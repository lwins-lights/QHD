import argparse, csv
import matplotlib.pyplot as plt
import matplotlib as mpl

LOCAL_MIN = 0.0883667

def plot_tts(specified_iter=None):
    data = {}
    with open(args.input, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = (row['prefix'], int(row['dim']), int(row['maxiter']))
            res = float(row['result'])
            if res < LOCAL_MIN / 2:
                hit = 1
            else:
                hit = 0
            if key in data:
                cnt, tot_hit, tot_utime = data[key]
                data[key] = (cnt + 1, tot_hit + hit, tot_utime + float(row['usertime']))
            else:
                data[key] = (1, hit, float(row['usertime']))
    curves={}
    for key in data:
        cnt, tot_hit, tot_utime = data[key]
        prefix, dim, maxiter = key
        #suc_prob_per_well = 1.0 - tot_res / cnt / LOCAL_MIN / dim
        #hypo_suc_prob = suc_prob_per_well ** dim
        #hypo_tts = tot_utime / cnt / hypo_suc_prob
        suc_prob = float(tot_hit) / cnt
        if suc_prob > 0:
            hypo_tts = tot_utime / cnt / suc_prob
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
            plt.plot(x, y, label=prefix+"_"+str(maxiter))

def plot_tts_plus(specified_iter=None):
    data = {}
    with open(args.input, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = (row['prefix'], int(row['dim']), int(row['maxiter']))
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

    plt.legend(loc="upper left")
    plt.yscale('log')
    plt.savefig(args.output)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='set output .PNG file name', required=True)
    parser.add_argument('-i', '--input', help='set input .CSV file name', required=True)
    args = parser.parse_args()
    main(args)
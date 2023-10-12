import argparse, os, time
import subprocess as sp
import multiprocessing as mp
import pickle
from tqdm import tqdm

def async_shell(command, key, queue):
    result = sp.run(
        command,
        capture_output = True, 
        text = True
    )
    queue.put((key, result.stdout + result.stderr))

def drain_queue_to(tot_procs, thr, queue, output_fn):
    while tot_procs > thr:
        while not queue.empty():
            tot_procs -= 1
            exp_key, exp_return = queue.get()
            with open(output_fn, mode='ab') as handle:
                pickle.dump((exp_key, exp_return), handle, protocol=pickle.HIGHEST_PROTOCOL)
        time.sleep(10)
    return tot_procs

def sqp(dir_this):
    q = mp.Queue()
    tot_procs = 0
    for s in tqdm(range(args.minseed, args.maxseed)):
        for n in range(1, args.maxdim + 1):
            async_shell(
                [
                    "timeout",
                    str(args.hardtimeout),
                    "/usr/bin/time",
                    "-f",
                    r"User Time: %U\nSystem Time: %S",
                    "python",
                    os.path.join(dir_this, "../solvers/dual_annealing.py"),
                    "-n",
                    str(n),
                    "-s",
                    str(s),
                    "--scipy",
                    "SLSQP"
                ],
                'sqp_n%s_s%s.txt' % (str(n), str(s)),
                q
            )
            tot_procs += 1
            tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def bh(dir_this):
    q = mp.Queue()
    tot_procs = 0
    for s in tqdm(range(args.minseed, args.maxseed)):
        for u in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            for n in range(1, args.maxdim + 1):
                async_shell(
                    [
                        "timeout",
                        str(args.hardtimeout),
                        "/usr/bin/time",
                        "-f",
                        r"User Time: %U\nSystem Time: %S",
                        "python",
                        os.path.join(dir_this, "../solvers/dual_annealing.py"),
                        "-n",
                        str(n),
                        "-s",
                        str(s),
                        "--maxiter",
                        str(u),
                        "--basinhopping"
                    ],
                    'bh_n%s_s%s_u%s.txt' % (str(n), str(s), str(u)),
                    q
                )
                tot_procs += 1
                tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def main():
    dir_this = os.path.dirname(os.path.realpath(__file__))
    if args.sqp:
        sqp(dir_this)
    elif args.bh:
        bh(dir_this)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqp', default=False, action='store_true')
    parser.add_argument('--bh', default=False, action='store_true')
    parser.add_argument('--minseed', type=int, required=True)
    parser.add_argument('--maxseed', type=int, required=True)
    parser.add_argument('--maxdim', type=int, required=True)
    parser.add_argument('--par', type=int, required=True)
    parser.add_argument('--hardtimeout', type=int, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()
    main()
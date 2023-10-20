import argparse, os, time
import subprocess as sp
import multiprocessing as mp
import pickle
import datetime
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
        #if args.verbose:
        #    print(datetime.datetime.now(), end='  ', flush=True)
        #    print('Sleep(10)', flush=True)
    return tot_procs

def sqp(dir_this):
    q = mp.Queue()
    tot_procs = 0
    for s in tqdm(range(args.minseed, args.maxseed)):
        for n in range(1, args.maxdim + 1):
            p = mp.Process(target=async_shell, args=
                ([
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
                q))
            p.start()
            tot_procs += 1
            tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def bh(dir_this):
    q = mp.Queue()
    tot_procs = 0
    for s in tqdm(range(args.minseed, args.maxseed)):
        for u in [8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
            for n in range(1, args.maxdim + 1):
                p = mp.Process(target=async_shell, args=
                    ([
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
                    q))
                p.start()
                tot_procs += 1
                tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def sgd2(dir_this):
    q = mp.Queue()
    tot_procs = 0
    for s in tqdm(range(args.minseed, args.maxseed)):
        for u in [2, 4, 8, 16, 32, 64, 128, 256, 512]:
            for n in range(1, args.maxdim + 1):
                p = mp.Process(target=async_shell, args=
                    ([
                        "timeout",
                        str(args.hardtimeout),
                        "/usr/bin/time",
                        "-f",
                        r"User Time: %U\nSystem Time: %S",
                        "python",
                        os.path.join(dir_this, "../solvers/sgd.py"),
                        "-n",
                        str(n),
                        "-s",
                        str(s),
                        "--lr",
                        str(u),
                        "--lrqhd"
                    ],
                    'sgd2_n%s_s%s_u%s.txt' % (str(n), str(s), str(u)),
                    q))
                p.start()
                tot_procs += 1
                tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def sgd(dir_this):
    q = mp.Queue()
    tot_procs = 0
    for s in tqdm(range(args.minseed, args.maxseed)):
        for u in ["8", "4", "2", "1", "0.5", "0.25", "0.125", "0.0625", "0.03125"]:
            for n in range(1, args.maxdim + 1):
                p = mp.Process(target=async_shell, args=
                    ([
                        "timeout",
                        str(args.hardtimeout),
                        "/usr/bin/time",
                        "-f",
                        r"User Time: %U\nSystem Time: %S",
                        "python",
                        os.path.join(dir_this, "../solvers/sgd.py"),
                        "-n",
                        str(n),
                        "-s",
                        str(s),
                        "--lr",
                        str(u)
                    ],
                    'sgd_n%s_s%s_u%s.txt' % (str(n), str(s), str(u)),
                    q))
                p.start()
                tot_procs += 1
                tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def gb(dir_this):
    q = mp.Queue()
    tot_procs = 0
    if not args.verbose:
        s_list = tqdm(range(args.minseed, args.maxseed))
    else:
        s_list = range(args.minseed, args.maxseed)
    for s in s_list:
        for n in range(1, args.maxdim + 1):
            if args.verbose:
                print(datetime.datetime.now(), end='  ', flush=True)
                print(r'Initiating (s=%d, n=%d)' % (s, n), flush=True)
            p = mp.Process(target=async_shell, args=
                ([
                    "timeout",
                    str(args.hardtimeout),
                    "/usr/bin/time",
                    "-f",
                    r"User Time: %U\nSystem Time: %S",
                    "python",
                    os.path.join(dir_this, "../solvers/gurobi.py"),
                    "-n",
                    str(n),
                    "-s",
                    str(s),
                    "--timeout",
                    str(args.timeout)
                ],
                'gb_n%s_s%s.txt' % (str(n), str(s)),
                q))
            p.start()
            tot_procs += 1
            tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def da(dir_this):
    q = mp.Queue()
    tot_procs = 0
    for s in tqdm(range(args.minseed, args.maxseed)):
        for u in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]:
            for n in range(1, args.maxdim + 1):
                p = mp.Process(target=async_shell, args=
                    ([
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
                        str(u)
                    ],
                    'da_n%s_s%s_u%s.txt' % (str(n), str(s), str(u)),
                    q))
                p.start()
                tot_procs += 1
                tot_procs = drain_queue_to(tot_procs, args.par - 1, q, args.output)
    tot_procs = drain_queue_to(tot_procs, 0, q, args.output)

def main():
    dir_this = os.path.dirname(os.path.realpath(__file__))
    if args.sqp:
        sqp(dir_this)
    elif args.bh:
        bh(dir_this)
    elif args.sgd2:
        sgd2(dir_this)
    elif args.sgd:
        sgd(dir_this)
    elif args.gb:
        gb(dir_this)
    elif args.da:
        da(dir_this)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqp', default=False, action='store_true')
    parser.add_argument('--bh', default=False, action='store_true')
    parser.add_argument('--sgd2', default=False, action='store_true')
    parser.add_argument('--sgd', default=False, action='store_true')
    parser.add_argument('--gb', default=False, action='store_true')
    parser.add_argument('--da', default=False, action='store_true')
    parser.add_argument('--minseed', type=int, required=True)
    parser.add_argument('--maxseed', type=int, required=True)
    parser.add_argument('--maxdim', type=int, required=True)
    parser.add_argument('--par', type=int, required=True)
    parser.add_argument('--hardtimeout', type=int, required=True)
    parser.add_argument('--timeout', type=int, default=3600)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    args = parser.parse_args()
    main()

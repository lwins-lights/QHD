import numpy as np
import argparse
import math
import func

EPS = 1e-8
INF = 1e10

def grad(f, x, n):
    ret = np.array([0] * n, dtype=np.double)
    for i in range(n):
        xi = x[i]
        x[i] = xi + EPS
        fp = f(x)
        x[i] = xi - EPS
        fm = f(x)
        x[i] = xi
        ret[i] = (fp - fm) / (2 * EPS)
    return ret

def sgd(f, x, lr0, niter_success, lrmax, lrqhd):
    ###########################
    # If lrqhd:
    #    t \in [1/2lr0, lr0/2]
    #    lr \in [lr0, 1/lr0]
    #    lr = 1/2t
    ###########################
    n = len(x)
    lr = lr0
    cur_min = INF
    x_opt = x[:] # shallow copy
    nfev = 0
    if lrqhd:
        t = 1 / (2 * lr0)
    else:
        iter_to_stop = niter_success
    while ((not lrqhd) and iter_to_stop > 0) or \
          (lrqhd and t < lr0 / 2):
        f_grad = grad(f, x, n)

        if lr < lrmax:
            x = x - (f_grad + np.random.normal(size=n) / math.sqrt(n)) * lr
            lr_used = lr
        else:
            x = x - (f_grad + np.random.normal(size=n) * math.sqrt(lr / lrmax / n)) * lrmax
            lr_used = lrmax

        if lrqhd:
            t += lr_used
            lr = 1 / (2 * t)
        else:
            niter_success -= 1

        f_new = f(x)
        #print(f_new)
        if f_new < cur_min:
            cur_min = f_new
            x_opt = x[:]
            if not lrqhd:
                iter_to_stop = niter_success

        nfev += 2 * n + 1
    result = {}
    result['message'] = 'N/A'
    result['nfev'] = nfev
    result['x'] = x_opt
    return result

def main(args):
    # init
    np.random.seed(seed=args.seed)
    n = args.dim
    # get the objective function and the ground truth optimal
    f, opt = func.gen_func_and_opt(n, no_rotation=args.no_rotation)
    # optimize
    x0 = np.random.normal(size=n)
    result = sgd(f, x0, lr0=args.lr, niter_success=args.niters, lrmax=args.lrmax, lrqhd=args.lrqhd)
    # summarize the result
    print('Status: %s' % result['message'])
    print('Total Evaluations: %d' % result['nfev'])
    # evaluate solution
    solution = result['x']
    evaluation = f(solution)
    print('Solution: f(%s) = %.8f' % (solution, evaluation))
    print('Ground Truth: f(%s) = %.8f' % (np.array(opt), f(opt)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--seed', type=int, help='set random seed', default=10007)
    parser.add_argument('-n', '--dim', type=int, help='set dimension', required=True)
    parser.add_argument('--no-rotation', dest='no_rotation', 
     help='disable the random rotation', default=False, action='store_true')
    parser.add_argument('--lr', type=float, help='set the initial effective learning rate', required=True)
    parser.add_argument('--niters', type=int, 
     help='return if the global minimum candidate remains the same for this number of iterations', default=1000)
    parser.add_argument('--lrqhd',
     help='use QHD learning rate schedule', default=False, action='store_true')
    parser.add_argument('--lrmax', type=float, help='set the maximal learning rate', default=0.01)
    args = parser.parse_args()
    main(args)

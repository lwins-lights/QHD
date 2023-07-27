import numpy as np
import argparse
from scipy.optimize import dual_annealing, basinhopping, minimize
from cyipopt import minimize_ipopt
import math
import func


from scipy.optimize import rosen, rosen_der

def main(args):
    # init
    np.random.seed(seed=args.seed)
    n = args.dim
    # get the objective function and the ground truth optimal
    f, opt = func.gen_func_and_opt(n, no_rotation=args.no_rotation)
    # optimize
    x0 = np.random.normal(size=n)
    if args.basinhopping:
        if args.maxiter > 0:
            result = basinhopping(f, x0, niter=args.maxiter)
        else:
            result = basinhopping(f, x0)
    elif args.ipopt:
        if args.maxiter > 0:
            result = minimize_ipopt(f, x0, options={'maxiter':args.maxiter})
        else:
            result = minimize_ipopt(f, x0)
    elif args.method != 'none':
        if args.maxiter > 0:
            result = minimize(f, x0, method=args.method, options={'maxiter':args.maxiter})
        else:
            result = minimize(f, x0, method=args.method)
    else:
        bound = [[func.LB * math.sqrt(n), func.UB * math.sqrt(n)]] * n
        if args.maxiter > 0:
            result = dual_annealing(f, bound, maxiter=args.maxiter)
        else:
            result = dual_annealing(f, bound)
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
    parser.add_argument('--basinhopping', help='use basin hopping instead of dual annealing',
     default=False, action='store_true')
    parser.add_argument('--ipopt', help='use Ipopt instead of dual annealing',
     default=False, action='store_true')
    parser.add_argument('--scipy', dest='method', 
     help='use scipy.optimize.minimize with the specified method instead of dual annealing',
     default='none')
    parser.add_argument('--maxiter', type=int, help='set maximum number of iterations', default = -1)
    args = parser.parse_args()
    main(args)

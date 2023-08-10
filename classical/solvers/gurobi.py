from colorama import *
from sys import *
from sympy import *
from gurobipy import *

from scipy.stats import ortho_group
from copy import deepcopy

import numpy as np
import re
import argparse

F_MIN = -0.295648678894007
Y_OPT = -0.722242350222327
DEBUG = False

def debug_msg(msg):
    if DEBUG:
        print(Fore.GREEN + "[DEBUG] ", end='')
        print(msg)
        print(Style.RESET_ALL, end='')

def addUnboundedVar(m, nam):
    return m.addVar(name=nam, lb=-GRB.INFINITY, ub=GRB.INFINITY)

def gen_1d_double_well(x):
    return x ** 4 - (x - 1/32) ** 2 - F_MIN # make global minimum ~0

def get_random_unitary(n, no_rotation=False):
    if n == 1:
        return [[1]]
    elif no_rotation:
        return np.identity(n)
    else:
        return ortho_group.rvs(dim = n) # generate a random unitary

def gen_func(n, no_rotation=False):
    # initialize x0, x1, ...
    x = []
    for i in range(n):
        xi = symbols('x' + str(i))
        x.append(xi)
    # let {yi} be {xi} randomly rotated
    # let {opti} be ground truth optimal
    u = get_random_unitary(n, no_rotation=no_rotation)
    y = []
    opt = []
    for i in range(n):
        yi = 0
        opti = 0
        for j in range(n):
            yi = yi + x[j] * u[i][j]
            opti = opti + Y_OPT * u[j][i]
        y.append(yi)
        opt.append(opti)
    # get the function
    f = 0
    for i in range(n):
        f = f + gen_1d_double_well(y[i])
    # get the numerical one
    def f_eval(x):
        y = []
        for i in range(n):
            yi = 0
            for j in range(n):
                yi = yi + x[j] * u[i][j]
            y.append(yi)
        ret = 0
        for i in range(n):
            ret = ret + gen_1d_double_well(y[i])
        return ret
    # return the polynomial
    return poly(f), x, opt, f_eval 

def enu_multiset(n, k):
    ret = []
    if k == 0:
        ret = [[]]
    elif k == 1:
        for i in range(n):
            ret.append([i])
    else:
        ret = []
        l = enu_multiset(n, k - 1)
        for i in l:
            for j in range(i[-1], n):
                temp = deepcopy(i)
                temp.append(j)
                ret.append(temp)
    return ret

# generate a sympy monomial according to exponent list l
def mono(l, x):
    ret = 1
    for i in l:
        ret = ret * x[i]
    return ret 

# convert a exponent multiset to gurobi varname
def exp_to_gname(l):
    ret = ""
    for i in l:
        ret = ret + "x" + str(i)
    return ret

def main(args):
    #init
    np.random.seed(seed=args.seed)
    n = args.dim

    # get func
    f, x, opt, f_eval = gen_func(n, no_rotation=args.no_rotation)
    debug_msg(f)

    # model initialization
    m = Model()
    m.setParam("NonConvex", 2)
    m.setParam("TimeLimit", args.timeout)
    if args.logfile is not None:
        m.setParam("LogFile", args.logfile)
    m.setParam("Threads", args.threads)

    # variable declaration
    z = {} # gurobi var
    for l in enu_multiset(n, 2) + enu_multiset(n, 1):
        z[str(l)] = addUnboundedVar(m, exp_to_gname(l))

    '''
    m.update()
    debug_msg(z)
    debug_msg(m.getVars())
    '''

    # set objective
    expr = f.coeff_monomial(1)
    for l in enu_multiset(n, 2) + enu_multiset(n, 1):
        expr = expr + f.coeff_monomial(mono(l, x)) * z[str(l)]
    for l in enu_multiset(n, 4):
        expr = expr + f.coeff_monomial(mono(l, x)) * z[str(l[0:2])] * z[str(l[2:4])]
    m.setObjective(expr, GRB.MINIMIZE)

    m.update()
    debug_msg(m.getObjective())

    # set constraint
    for l in enu_multiset(n, 2):
        m.addConstr(z[str(l)] == z[str([l[0]])] * z[str([l[1]])])
    #for l in enu_multiset(n, 4):
    #    m.addConstr(z[str(l)] == z[str(l[0:2])] * z[str(l[2:4])])

    m.update()
    debug_msg(m.getConstrs())

    if DEBUG:
        m.write('model.lp')

    m.optimize()

    x_res = [0] * n
    p = re.compile(r'^x[0-9]+$')
    for v in m.getVars():
        if p.match(v.VarName):
            i = int(v.Varname[1:])
            x_res[i] = v.X
        #print('%s %g' %(v.VarName, v.X))

    print('Obj: %g' %m.ObjVal)
    print('Solution: f(%s) = %.8f' % (np.array(x_res), f_eval(x_res)))
    print('Ground Truth: f(%s) = %.8f' % (np.array(opt), f_eval(opt)))

def test():
    m = Model()
    m.setParam("NonConvex", 2)

    x = addUnboundedVar(m, "x")
    y = addUnboundedVar(m, "y")

    m.setObjective(y * y - (x - 1/32) * (x - 1/32) - F_MIN, GRB.MINIMIZE)

    m.addConstr(y == x * x)

    m.optimize()

    for v in m . getVars ():
        print('%s %g' %(v.VarName, v.X))
    print('Obj: %g' %m.ObjVal)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--seed', type=int, help='set random seed', default=10007)
    parser.add_argument('-n', '--dim', type=int, help='set dimension', required=True)
    parser.add_argument('--no-rotation', dest='no_rotation', 
     help='disable the random rotation', default=False, action='store_true')
    parser.add_argument('-t', '--timeout', type=int, help='set timeout in seconds (default = 60)',
     default=60)
    parser.add_argument('-l', '--logfile', help='specify a log file to print gurobi log',
     default=None)
    parser.add_argument('--threads', type=int, help='set parallelism number',
     default=1)
    args = parser.parse_args()
    main(args)
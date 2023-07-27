import numpy as np
from scipy.stats import ortho_group

F_MIN = -0.295648678894007
Y_OPT = -0.722242350222327
UB = 1
LB = -1

def get_random_unitary(n, no_rotation=False):
    if n == 1:
        return [[1]]
    elif no_rotation:
        return np.identity(n)
    else:
        return ortho_group.rvs(dim = n) # generate a random unitary

def func(x):
    return x ** 4 - (x - 1/32) ** 2 - F_MIN # make global minimum ~ 0

def gen_func_and_opt(n, no_rotation=False):
    u = get_random_unitary(n, no_rotation=no_rotation)
    #print(u)
    def f(x):
        y = []
        for i in range(n):
            yi = 0
            for j in range(n):
                yi = yi + x[j] * u[i][j]
            y.append(yi)
        ret = 0
        for i in range(n):
            ret = ret + func(y[i])
        return ret
    opt = []
    for i in range(n):
        opti = 0
        for j in range(n):
            opti = opti + Y_OPT * u[j][i]
        opt.append(opti)
    return f, opt

'''
def test():
    f, opt = gen_func_and_opt(1)
    print(f([0]))
    print(opt)

if __name__ == "__main__":
    np.random.seed(seed=10007)
    test()
'''
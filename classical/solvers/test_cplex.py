import cplex
from docplex.mp.model import Model

def test():
    print(cplex.__version__)
    m = Model()

    x = m.continuous_var(name = 'x', lb=-m.infinity, ub=m.infinity)
    y = m.continuous_var(name = 'y', lb=-m.infinity, ub=m.infinity)
    #x = m.continuous_var(name = 'x')
    #y = m.continuous_var(name = 'y')

    m.add_constraint(y == x * x)

    f = y * y - (x - 1/32) * (x - 1/32)
    m.set_objective('min', f)
    m.parameters.optimalitytarget.set(2)


    m.print_information()
    m.solve()

if __name__ == "__main__":
    test()
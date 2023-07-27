import sys, os
import subprocess
import re
import numpy as np
import csv
import matplotlib.pyplot as plt

RAND_MAX = 1000000007
LOCAL_MIN = 0.0883667
DIR = script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
RESULT_DIR = DIR + "/results"

def extract_objective(s):
    s_inline = s.replace('\n', ' ')
    return float(re.search('Solution: f\(\[.*?\]\) = ([0-9\.]*)', s_inline).group(1))

def write_to_csv(dict_data, fn):
    with open(RESULT_DIR + "/" + fn, 'w') as csvfile:
        csv_columns = dict_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)

def plot_to_file(dict_data, fn):
    x = []
    y = []
    for data in dict_data:
        x.append(data["dim"])
        y.append(data["result"] / LOCAL_MIN / data["dim"])
    plt.plot(x, y, 'o', color='red')
    plt.savefig(RESULT_DIR + "/" + fn)

    plt.show()

def batch(batch_name, solver_dir, n_list, seed=10007, extra_args=[]):
    data = []
    np.random.seed(seed=seed)
    for n in n_list:
        rnd = np.random.randint(RAND_MAX)
        print("Running %s for (dim, seed) = (%d, %d)" % (batch_name, n, rnd))
        res = subprocess.run(["python3", DIR + solver_dir, "--dim", str(n), "--seed", str(rnd)] + extra_args, stdout=subprocess.PIPE)
        raw_obj = extract_objective(res.stdout.decode("utf-8"))
        data.append({"dim":n, "seed":rnd, "result":raw_obj})
    write_to_csv(data, batch_name + ".csv")
    plot_to_file(data, batch_name + ".png")

def main():
    #batch('dual_annealing', '/../solvers/dual_annealing.py', range(1, 51, 1))
    #batch('ipopt', '/../solvers/dual_annealing.py', range(1, 51, 1), extra_args=['--ipopt'])
    #batch('sqp', '/../solvers/dual_annealing.py', range(1, 51, 1), extra_args=['--scipy', 'SLSQP'])
    batch('basinhopping', '/../solvers/dual_annealing.py', range(1, 51, 1), extra_args=['--basinhopping'])
    #batch('gurobi', '/../solvers/gurobi.py', range(1, 31, 1), extra_args=['--timeout', '60'])
'''
def test():
    np.random.seed(seed=101)
    print(np.random.randint(10, size=5))
    np.random.seed(seed=101)
    print(np.random.randint(10, size=5))
    result = subprocess.run(["python3", DIR + "/../solvers/dual_annealing.py", "-n", "10"], stdout=subprocess.PIPE)
    obj = extract_objective(result.stdout.decode("utf-8"))
    print(obj)
'''

if __name__ == "__main__":
    main()
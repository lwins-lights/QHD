
# A Quantum-Classical Performance Separation in Nonconvex Optimization

## Introduction

This repository contains all necessary code for our experiments on classical optimization algorithms against optimization instances of multidimensional double-wells. In [our paper](https://arxiv.org/abs/2311.00811), we prove that [quantum Hamiltonian descent](https://jiaqileng.github.io/quantum-hamiltonian-descent/) can solve these optimization instances with query complexity $\widetilde{\mathcal{O}}(d^3)$ and gate complexity $\widetilde{\mathcal{O}}(d^4)$, where $d$ denotes the dimensionality of an instance. Our experiment suggests that representative state-of-the-art classical optimization algorithms/solvers (including Gurobi) would require a super-polynomial time to solve such optimization instances.

### Roadmap
* `solvers/` contains source code of various algorithms/solvers. All scripts except `func.py` are executable with built-in `--help` command.
	* `func.py` is used to generate (the oracle to) a multidimensional double-well instance.
	* `dual_annealing.py` is the core script to test various algorithms against instances provided by `func.py`.
	* `ipopt.py` is the core script to test [Ipopt](https://coin-or.github.io/Ipopt/index.html).
	* `gurobi.py` is the core script to test [Gurobi](https://www.gurobi.com/). It does not rely on `func.py` since Gurobi requires an *explicit* description to the optimization objective rather than a black-box oracle access to it.
	* `sgd.py` is the core script to test stochastic (or perturbed) gradient descent.
* `scripts/` contains various scripts to automate the whole experiment. One does not necessarily rely on these scripts and can write own testing scripts with ease.

## Usage
### Prerequisites
It is recommended to run our code on Debian-based Linux distributions.
For Gurobi and Ipopt experiments, corresponding solvers should be installed: [Gurobi](https://www.gurobi.com/), [Ipopt](https://coin-or.github.io/Ipopt/index.html).
Then, install Python 3 by `apt` and necessary dependencies by `pip`:
```
$ sudo apt install python-is-python3
$ pip install colorama cyipopt gurobipy matplotlib numpy scipy seaborn sympy tqdm
```
### Using solvers
This section will explain how to use various solvers in the `solvers/` directory.
#### Dual annealing, basin-hopping and SQP
We start with `dual_annealing.py`. The following command will run the dual annealing algorithm on a $F_U(\cdot)$ with dimensionality `2` and $U$ randomized with the random seed `123456`. 
```
$ python dual_annealing.py -n 2 -s 123456
```
The random seed also governs internal randomness of the dual annealing algorithm itself, which means *multiple runs of the above command should give identical results*.
To add the maximum iteration number constraint, say `100`, simply add an `--maxiter` argument:
```
$ python dual_annealing.py -n 2 -s 123456 --maxiter 100
```
The same code is also used to run the basin-hopping and the SQP algorithms:
```
# use basin-hopping instead
$ python dual_annealing.py -n 2 -s 123456 --maxiter 100 --basinhopping 
# use SQP instead
$ python dual_annealing.py -n 2 -s 123456 --maxiter 100 --scipy SLSQP
``` 
One can also check the built-in help message by `python dual_annealing.py --help`.
#### Ipopt and Gurobi
The usage of `ipopt.py` is almost the same as `dual_annealing.py`:
```
$ python ipopt.py -n 2 -s 123456 --ipopt 
```
The same applies to `gurobi.py`, but note that the random seed only has effect on $U$ as Gurobi is deterministic:
```
$ python gurobi.py -n 2 -s 123456 
```
The built-in `--help` command also works for `ipopt.py` and `gurobi.py`.

### Replicating the experiment
We start with the experiment for dual annealing using the script `script/tts_experiment.py`. It is recommended to scale down the experiment first to test if it works. Note that all .py scripts have built-in `--help` command.
#### Walkthrough for dual annealing
##### Step 1. Run the solver
```
# Usage: python scripts/tts_experiment.py --da --minseed MINSEED --maxseed MAXSEED --maxdim MAXDIM --par PAR --hardtimeout HARDTIMEOUT --output OUTPUTFN
$ mkdir da
$ python scripts/tts_experiment.py --da --minseed 0 --maxseed 10000 --maxdim 15 --par 128 --hardtimeout 1800 --output da/da.pickle
```
The script `scripts/tts_experiment.py` basically calls the dual annealing solver (`solvers/dual_annealing.py`) with all possible combination of the following parameters:
* DIM (dimensionality): [1, MAXDIM]
* SEED: [MINSEED, MAXSEED)
* MAXITER: 2^6, 2^7, ..., 2^14

To be specific, below is the way DIM, SEED and MAXITER participate:
```
python dual_annealing.py -n DIM -s SEED --maxiter MAXITER
```
For other parameters, 
* PAR controls how many `dual_annealing.py` will be running simultaneously 
* HARDTIMEOUT specifies how long (in seconds) the script will wait for the result before killing each individual `dual_annealing.py`.
* OUTPUTFN is the output pickle file path.

The script will save all results in the `da/da.pickle` pickle file.
##### Step 2. Aggregate data
Now that the experiment is done and all data is saved in `da/`. Use the following to aggregate data in a single CSV file:
```
$ python scripts/archiver.py -i da -o da.csv
```
Note that the script will collect *all* pickle files in the input folder `da`. This means one can run the previous step in parallel on different machines by assigning different seed range, and then use the script to aggregate multiple .pickle files. For instance, we can replace the previous step with the following:
```
# On machine 1
$ python scripts/tts_experiment.py --da --minseed 0 --maxseed 5000 --maxdim 15 --par 128 --hardtimeout 1800 --output da_1.pickle
# On machine 2
$ python scripts/tts_experiment.py --da --minseed 5000 --maxseed 10000 --maxdim 15 --par 128 --hardtimeout 1800 --output da_2.pickle
# And then collect .pickle files in a single folder
```

##### Step 3. Draw the TTS figure
Use the following script to draw the final TTS figure. 
```
$ python scripts/tts.py -i da.csv -o da.png --ltitle "Maximum Iteration Number"
```
#### Other solvers
The usage is similar for experiments of other solvers.
```
### basin-hopping
$ python scripts/tts_experiment.py --da --minseed 0 --maxseed 10000 --maxdim 15 --par 128 --hardtimeout 1800 --output results_bh/bh.pickle
$ python scripts/archiver.py -i results_bh -o bh.csv
$ python scripts/tts.py -i bh.csv -o bh.png --ltitle "Maximum Iteration Number"

### SQP
$ python scripts/tts_experiment.py --da --minseed 0 --maxseed 100000 --maxdim 15 --par 128 --hardtimeout 1800 --output results_sqp/sqp.pickle
$ python scripts/archiver.py -i results_sqp -o sqp.csv
$ python scripts/tts.py -i sqp.csv -o sqp.png --ltitle ""

### SGD with fixed learning rates
$ python scripts/tts_experiment.py --sgd --minseed 0 --maxseed 10000 --maxdim 15 --par 128 --hardtimeout 1800 --output results_sgd/sgd.pickle
$ python scripts/archiver.py -i results_sgd -o sgd.csv
$ python scripts/tts.py -i sgd.csv -o sgd.png --ltitle "Effective Learning Rate"

### SGD with QHD learning rate schedules
$ python scripts/tts_experiment.py --sgd2 --minseed 0 --maxseed 10000 --maxdim 15 --par 128 --hardtimeout 1800 --output results_sgd/sgd.pickle
$ python scripts/archiver.py -i results_sgd2 -o sgd2.csv
$ python scripts/tts.py -i sgd2.csv -o sgd2.png --ltitle "Value of λ_f"

### Gurobi
$ python scripts/tts_experiment.py --gb --minseed 0 --maxseed 3000 --maxdim 15 --par 128 --hardtimeout 3600 --timeout 1800 --output results_gb/gb.pickle
$ python scripts/archiver.py -i results_gb -o gb.csv --gurobi
$ python scripts/tts.py -i gb.csv -o gb.png --ltitle "Work Limit" --yunit "work unit" --dynamic --rainbow
```

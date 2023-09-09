
# Classical Solvers against Multidimensional Double-Wells

This repository contains all necessary code for our experiments on classical solvers against multidimensional double-wells.
## Usage
### Prerequisites
It is recommended to run our code on Debian-based Linux distributions.
For Gurobi and Ipopt experiments, corresponding solvers should be installed: [Gurobi](https://www.gurobi.com/), [Ipopt](https://coin-or.github.io/Ipopt/index.html).
Then, install Python 3 by `apt` and necessary dependencies by `pip`:
```
sudo apt install python-is-python3
pip install colorama cyipopt gurobipy matplotlib numpy scipy seaborn sympy tqdm
```
### Using solvers
This section will explain how to use various solvers in the `solvers/` directory.
#### Dual annealing, basin-hopping and SQP
We start with `dual_annealing.py`. The following command will run the dual annealing algorithm on a $F_U(\cdot)$ with dimensionality `2` and $U$ randomized with the random seed `123456`. 
```
python dual_annealing.py -n 2 -s 123456
```
The random seed also governs internal randomness of the dual annealing algorithm itself, which means *multiple runs of the above command should give identical results*.
To add the maximum iteration number constraint, say `100`, simply add an `--maxiter` argument:
```
python dual_annealing.py -n 2 -s 123456 --maxiter 100
```
The same code is also used to run the basin-hopping and the SQP algorithms:
```
# use basin-hopping instead
python dual_annealing.py -n 2 -s 123456 --maxiter 100 --basinhopping 
# use SQP instead
python dual_annealing.py -n 2 -s 123456 --maxiter 100 --scipy SLSQP
``` 
One can also check the built-in help message by `python dual_annealing.py --help`.
#### Ipopt and Gurobi
The usage of `ipopt.py` is almost the same as `dual_annealing.py`:
```
python ipopt.py -n 2 -s 123456 --ipopt 
```
The same applies to `gurobi.py`, but note that the random seed only has effect on $U$ as Gurobi is deterministic:
```
python gurobi.py -n 2 -s 123456 
```
The built-in `--help` command also works for `ipopt.py` and `gurobi.py`.

### Replicating the experiment
We start with the experiment for dual annealing using the script `scripts/tts_da.sh`. It is recommended to scale down the experiment first to test if it works. Note that all .py scripts have built-in `--help` command.
#### Walkthrough for dual annealing
##### Step 1. Run the solver
```
# Usage: bash scripts/tts_da.sh MAXN MINSEED MAXSEED
bash scripts/tts_da.sh 20 0 2000
```
The script `scripts/tts_da.sh` basically calls the dual annealing solver (`solvers/dual_annealing.py`) with all possible combination of the following parameters:
* DIM (dimensionality): [1, MAXN]
* SEED: [MINSEED, MAXSEED)
* MAXITER: 1, 2, 4, ..., 8192

To be specific, below is the way DIM, SEED and MAXITER participate:
```
python dual_annealing.py -n DIM -s SEED --maxiter MAXITER
```
The script will time (`/usr/bin/time`) the solver and save the result in the `results_da/` folder with filename `da_nDIM_sSEED_uMAXITER.txt`.
##### Step 2. Aggregate data
Now that the experiment is done and all data is saved in `results_da/`. Use the following to aggregate data in a single CSV file:
```
python scripts/archiver.py -d results_da -o da.csv
```
##### Step 3. Draw the TTS figure
Use the following script to draw the final TTS figure. 
```
python scripts/tts.py -i da.csv -o da.png --ltitle "Maximum Iteration Number"
```
#### Other solvers
The usage is similar for experiments of other solvers.
```
### basin-hopping
# Usage: bash scripts/tts_bh.sh MAXN MINSEED MAXSEED
bash scripts/tts_bh.sh 20 0 2000 
python scripts/archiver.py -d results_bh -o bh.csv
python scripts/tts.py -i bh.csv -o bh.png --ltitle "Maximum Iteration Number"

### Ipopt
# Usage: bash scripts/tts_ipopt.sh MAXN MINSEED REP PAR HARDTIMEOUT
#   PAR specifies the degree of parallelism
#   the range of SEED is [MINSEED, MINSEED+REP*PAR)
bash scripts/tts_ipopt.sh 10 0 1000 12 600 
python scripts/archiver.py -d results_ipopt -o ipopt.csv
python scripts/tts.py -i ipopt.csv -o ipopt.png --ltitle ""

### SQP
# Usage: bash scripts/tts_sqp.sh MAXN MINSEED REP PAR HARDTIMEOUT
bash scripts/tts_sqp.sh 10 0 1000 12 600 
python scripts/archiver.py -d results_sqp -o sqp.csv
python scripts/tts.py -i sqp.csv -o sqp.png --ltitle ""

### SGD with fixed learning rates
# Usage: bash scripts/tts_sgd.sh MAXN MINSEED REP PAR
bash scripts/tts_sgd.sh 10 0 64 16
python scripts/archiver.py -d results_sgd -o sgd.csv
python scripts/tts.py -i sgd.csv -o sgd.png --ltitle "Effective Learning Rate"

### SGD with QHD learning rate schedules
# Usage: bash scripts/tts_sgd2.sh MAXN MINSEED REP PAR
bash scripts/tts_sgd2.sh 10 0 64 16
python scripts/archiver.py -d results_sgd2 -o sgd2.csv
python scripts/tts.py -i sgd2.csv -o sgd2.png --ltitle "Value of Lambda_f"

### Gurobi
# Usage: bash scripts/tts_gb.sh MAXN MINSEED REP PAR TIMELIMIT HARDTIMEOUT
bash scripts/tts_gb.sh 10 0 8 16 900 1800
python scripts/archiver.py -d results_gb -o gb.csv --gurobi
python scripts/tts.py -i gb.csv -o gb.png --ltitle "Work Limit" --yunit "work unit" --dynamic --rainbow
```

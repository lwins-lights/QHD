#!/bin/bash

MAXN=$1
MINSEED=$2
MAXSEED=$3
MAXITERLIST=(1 2 4 8 16 32 64 128 256 512)

# dir of this script
DIRNAME=$(dirname "$0")

# make the folder if not found
mkdir -p results_bh

# pid list
pidList=()

for ((s=MINSEED; s<MAXSEED; s++))
do
    echo "[$(date)] Seed $s"
    for ((n=1; n<=MAXN; n++))  
    do
        for u in ${MAXITERLIST[@]} 
	do
    	    /usr/bin/time -f "User Time: %U\nSystem Time: %S" python "${DIRNAME}/../solvers/dual_annealing.py" -n $n --seed $s --maxiter $u --basinhopping &> "results_bh/bh_n${n}_s${s}_u${u}.txt" &
	    pidList[${#pidList[@]}]=$!
        done
    done
    # echo "pidList: ${pidList[*]}"
    # wait for all subprocesses
    for pid in ${pidList[@]}
    do
        wait $pid
    done
    pidList=()
done	

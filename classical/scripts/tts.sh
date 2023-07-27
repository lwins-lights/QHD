#!/bin/bash

MAXN=2
MAXSEED=2
MAXITERLIST=(1 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192)

# dir of this script
DIRNAME=$(dirname "$0")

# make the folder if not found
mkdir -p results

# pid list
pidList=()

for ((n=1; n<=MAXN; n++)) 
do
    for ((s=0; s<MAXSEED; s++)) 
    do
        for u in ${MAXITERLIST[@]} 
	do
    	    /usr/bin/time -f "User Time: %U\nSystem Time: %S" python "${DIRNAME}/../solvers/dual_annealing.py" -n $n --seed $s --maxiter $u &> "results/da_n${n}_s${s}_u${u}.txt" &
	    pidList[${#pidList[@]}]=$!
        done
    done
done	

# wait for all subprocesses
for pid in ${pidList[@]}
do
    wait $pid
done


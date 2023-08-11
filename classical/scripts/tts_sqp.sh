#!/bin/bash

MAXN=$1
MINSEED=$2
REP=$3
PAR=$4
TIMEOUT=$5
#MAXITERLIST=(8 16 32 64 128 256 512 1024)
#MAXITERLIST=(32 64 128 256 512 1024)

# dir of this script
DIRNAME=$(dirname "$0")

# make the folder if not found
mkdir -p results_sqp

# pid list
pidList=()

# DEBUG switch
DEBUG=0

for ((n=1; n<=MAXN; n++)); do
    maxi=$((REP))
    echo "[$(date)] Dim $n; Rep $maxi; Par $PAR"
    for ((i=0; i<maxi; i++)); do
        echo "[$(date)] Group $i"
        for ((j=0; j<PAR; j++)); do
            s=$((MINSEED + i * PAR + j))
            timeout $((TIMEOUT)) /usr/bin/time -f "User Time: %U\nSystem Time: %S" python "${DIRNAME}/../solvers/dual_annealing.py" -n $n --seed $s --scipy SLSQP &> "results_sqp/sqp_n${n}_s${s}.txt" &
            pidList[${#pidList[@]}]=$!
        done
        # wait for all subprocesses
        for pid in ${pidList[@]}; do
            if ((DEBUG == 1)); then
                echo "[DEBUG] Collecting $pid"
            fi
            wait $pid
        done
        pidList=()
    done
done
#!/bin/bash

MAXN=$1
MINSEED=$2
REP=$3
PAR=$4
#TIMEOUT=$5
#HARDTIMEOUT=$6
LRLIST=(2 4 8 16 32 64 128 256 512 1024)
#LRLIST=(1024)
#MAXITERLIST=(32 64 128 256 512 1024)

# dir of this script
DIRNAME=$(dirname "$0")

# make the folder if not found
mkdir -p results_sgd2

# pid list
pidList=()

# DEBUG switch
DEBUG=0
for u in ${LRLIST[@]}; do
    for ((n=10; n<=MAXN; n++)); do
        echo "[$(date)] LR $u; Dim $n; Rep $REP; Par $PAR"
        for ((i=0; i<REP; i++)); do
	    echo "[$(date)] Group $i" 
            for ((j=0; j<PAR; j++)); do
                s=$((MINSEED + i * PAR + j))
		/usr/bin/time -f "User Time: %U\nSystem Time: %S" python "${DIRNAME}/../solvers/sgd.py" -n $n --seed $s --lr $u --lrqhd &> "results_sgd2/sgd2_n${n}_s${s}_u${u}.txt" &
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
done

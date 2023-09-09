#!/bin/bash

MAXN=$1
MINSEED=$2
REP=$3
PAR=$4
TIMEOUT=$5
HARDTIMEOUT=$6
#MAXITERLIST=(8 16 32 64 128 256 512 1024)
#MAXITERLIST=(32 64 128 256 512 1024)

# dir of this script
DIRNAME=$(dirname "$0")

# make the folder if not found
mkdir -p results_gb

# pid list
pidList=()

# DEBUG switch
DEBUG=0

    for ((n=1; n<=MAXN; n++)); do
        echo "[$(date)] Dim $n; Rep $REP; Par $PAR"
        for ((i=0; i<REP; i++)); do
	    echo "[$(date)] Group $i" 
            for ((j=0; j<PAR; j++)); do
                s=$((MINSEED + i * PAR + j))
		timeout $((HARDTIMEOUT)) /usr/bin/time -f "User Time: %U\nSystem Time: %S" python "${DIRNAME}/../solvers/gurobi.py" -n $n --seed $s --timeout $TIMEOUT &> "results_gb/gb_n${n}_s${s}.txt" &
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

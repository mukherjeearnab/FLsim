#!/bin/sh
CUDA_DEV=$1
CONDA_ENV=$2
BOOTNODE=$3
START_ID=$4
SESSIONS=$5

if [ $# -lt 5 ]; then
    echo "Not enough Args Supplied. Aborting..."
    exit
fi

for n in $(eval echo {0..$(($SESSIONS - 1))}); do
    SESSION_ID=$(($START_ID + $n * 10))
    echo "Starting 10 nodes with start_id = $(($START_ID + $n * 10))"
    ST_COMM="bash auto/tmux_10c.sh $CUDA_DEV $CONDA_ENV $BOOTNODE $SESSION_ID 10 n"
    echo $ST_COMM
    eval $ST_COMM
done

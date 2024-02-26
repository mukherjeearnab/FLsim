#!/bin/sh
CUDA_DEV=$1
CONDA_ENV=$2
BOOTNODE=$3
START_ID=$4
MAX_NODES=$5
ATTACH=$6

if [ $# -lt 5 ]; then
    echo "Not enough Args Supplied. Aborting..."
    exit
fi

if [[ -z "$ATTACH" ]]; then
    ATTACH="n"
fi

tmux new-session -d

tmux split-window -h

# right
tmux select-pane -t 1
tmux split-window -v
tmux split-window -v
tmux split-window -v

tmux select-pane -t 1
tmux split-window -v

# # left
tmux select-pane -t 0
tmux split-window -v
tmux split-window -v
tmux split-window -v

tmux select-pane -t 0
tmux split-window -v

for n in $(eval echo {0..$(($MAX_NODES - 1))}); do
    tmux select-pane -t $n
    tmux send-keys "HISTFILE=\"$PWD/.auto_history\"" C-m
    tmux send-keys "export CUDA_VISIBLE_DEVICES=$CUDA_DEV" C-m
    tmux send-keys "conda activate $CONDA_ENV" C-m
    tmux send-keys 'cd ./node' C-m
    tmux send-keys "sleep 10 && python main.py -n node_$((START_ID + n)) -b $BOOTNODE -c -w -m" C-m
done

tmux select-pane -t 0

if [[ "$ATTACH" == "y" ]]; then
    tmux -2 attach-session
fi

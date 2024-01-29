#!/bin/sh
CUDA_DEV=$1
CONDA_ENV=$2
BOOTNODE=$3
START_ID=$4

if [ $# -lt 4 ]; then
    echo "Not enough Args Supplied. Aborting..."
    exit
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

for n in {0..9}; do
    tmux select-pane -t $n
    tmux send-keys "export CUDA_VISIBLE_DEVICES=$CUDA_DEV" C-m
    tmux send-keys "conda activate $CONDA_ENV" C-m
    tmux send-keys 'cd ./node' C-m
    # tmux send-keys 'sleep 10' C-m
    tmux send-keys "sleep 10 && python main.py -n node_$((START_ID + n)) -b $BOOTNODE -c -w -m" C-m
done

tmux select-pane -t 0

tmux -2 attach-session

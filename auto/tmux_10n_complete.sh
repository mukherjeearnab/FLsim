#!/bin/sh
CUDA_DEV=$1
CONDA_ENV=$2
SERVER=$3
REDIS=$4

if [ $# -lt 2 ]; then
    echo "Not enough Args Supplied. Aborting..."
    exit
fi

tmux new-session -d

tmux split-window -h

tmux select-pane -t 0
tmux split-window -v

tmux select-pane -t 2
tmux split-window -v
tmux split-window -v
tmux split-window -v

tmux select-pane -t 2
tmux split-window -v
tmux split-window -v

tmux select-pane -t 2
tmux split-window -v

tmux select-pane -t 6
tmux split-window -v

tmux select-pane -t 1
tmux split-window -v
tmux split-window -v

tmux select-pane -t 1
tmux split-window -v

tmux select-pane -t 0
tmux split-window -v
tmux split-window -v

for n in {0..14}; do
    tmux select-pane -t $n
    tmux send-keys "export CUDA_VISIBLE_DEVICES=$CUDA_DEV" C-m
    tmux send-keys "conda activate $CONDA_ENV" C-m
done

tmux select-pane -t 0
tmux send-keys 'cd ./controller' C-m
tmux send-keys "python main.py" C-m

tmux select-pane -t 1
tmux send-keys 'cd ./logicon' C-m
tmux send-keys "python main.py" C-m

tmux select-pane -t 2
tmux send-keys 'cd ./distributor' C-m
tmux send-keys "python main.py" C-m

tmux select-pane -t 3
tmux send-keys 'cd ./perflogger' C-m
tmux send-keys "python main.py" C-m

tmux select-pane -t 4
tmux send-keys 'cd ./kvstore' C-m
tmux send-keys "python main.py" C-m

for n in {5..14}; do
    tmux select-pane -t $n
    tmux send-keys 'cd ./node' C-m
    tmux send-keys 'sleep 5' C-m
    tmux send-keys "python main.py -n node_$((n - 5)) -c -w -m" C-m
done

tmux select-pane -t 0

tmux -2 attach-session

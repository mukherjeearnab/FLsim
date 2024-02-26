#!/bin/sh
CUDA_DEV=$1
CONDA_ENV=$2
START_ID=$3
MAX_NODES=$4
ATTACH=$5

if [ $# -lt 4 ]; then
    echo "Not enough Args Supplied. Aborting..."
    exit
fi

if [[ -z "$ATTACH" ]]; then
    ATTACH="n"
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
    tmux send-keys "HISTFILE=\"$PWD/.auto_history\"" C-m
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

if [ "$MAX_NODES" -gt 0 ]; then
    # start the bootnode
    tmux select-pane -t 5
    tmux send-keys 'cd ./node' C-m
    tmux send-keys "sleep 5 && python main.py -n node_$((START_ID + 0)) -c -w -m" C-m
fi

if [ "$MAX_NODES" -gt 1 ]; then
    # start the rest of the nodes
    for n in $(eval echo {6..$(($MAX_NODES + 4))}); do
        tmux select-pane -t $n
        tmux send-keys 'cd ./node' C-m
        tmux send-keys "sleep 10 && python main.py -n node_$((START_ID + n - 5)) -b 5011 -c -w -m" C-m
    done
fi

tmux select-pane -t 0

if [[ "$ATTACH" == "y" ]]; then
    tmux -2 attach-session
fi

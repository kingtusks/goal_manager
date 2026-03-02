#!/bin/bash

evals=("planner", "executor", "constructor", "reflector", "replanner")

for eval in evals; do
    docker exec -it goal_manager_backend python agents/evals/$eval_eval.py
    echo "eval $eval is done"
done

docker exec -it goal_manager_backend python agents/evals/e2e.py

echo "all evals are done"
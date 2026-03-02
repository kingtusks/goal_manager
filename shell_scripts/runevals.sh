#!/bin/bash

evals = ("planner", "executor")

for eval in evals; do
    docker exec -it goal_manager_backend python agents/evals/$eval_eval.py
    echo "eval $eval is done"
done
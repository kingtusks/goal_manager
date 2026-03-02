#!/bin/bash

evals=("planner" "executor" "constructor" "reflector" "replanner")

for e in "${evals[@]}"; do
    docker exec -it goal_manager_backend python agents/evals/${e}_eval.py
    echo "eval ${e} is done"
done

docker exec -it goal_manager_backend python agents/evals/e2e.py

echo "all evals are done"
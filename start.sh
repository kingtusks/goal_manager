#!/bin/bash

clean() {
    echo "shutting down"
    kill $(jobs -p) 2>/dev/null
    exit
}

trap clean SIGINT SIGTERM

source .venv/Scripts/activate
fastapi dev backend/main.py &
cd frontend
npm run dev & 

wait
#!/bin/bash
#DEPRECIATED

PORTS=(8000 8001 8002 8003 5173 11434 6379 5433)    

for PORT in "${PORTS[@]}"; do
    PIDS=$(sudo fuser $PORT/tcp 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "Killing port $PORT (PID: $PIDS)"
        sudo fuser -k $PORT/tcp 2>/dev/null
    else
        echo "Port $PORT is free"
    fi
done

echo "Done"
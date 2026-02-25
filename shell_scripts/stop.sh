#!/bin/bash

pkill -f "_mcp.py"
pkill -f "uvicorn main:app"
pkill -f "vite"
sudo pkill -f "ollama serve"

echo "stopped everything i think"
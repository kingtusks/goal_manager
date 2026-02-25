#!/bin/bash

#just for me 2>/dev/null just makes it so errors wont be visible
redis-server --daemonize yes 2>/dev/null 

ollama serve & 

sleep 2

source env/bin/activate

python backend/agents/mcp_servers/database_mcp.py &
python backend/agents/mcp_servers/redis_mcp.py &
python backend/agents/mcp_servers/websearch_mcp.py &

sleep 3

cd backend
uvicorn main:app --reload &
cd ..

sleep 2

cd frontend
npm run dev
cd ..
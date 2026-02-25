# Goal Manager

Goal Manager is an AI-powered system designed to help users achieve their goals through a structured, multi-agent workflow. It breaks down complex goals into actionable tasks, executes them, reflects on the results, and adapts the plan dynamically.

## Features

-   **Multi-Agent Workflow**: Utilizes specialized agents for planning, execution, reflection, and construction of learning materials.
-   **Model Context Protocol (MCP)**: Integrates with MCP servers for specialized tools:
    -   **Web Search**: Real-time information gathering.
    -   **Database**: Persistent storage of goals, plans, and progress.
    -   **Redis**: High-speed caching and state management.
-   **Local LLM Integration**: Powered by **Ollama**, allowing for private and customizable AI operations.
-   **Dynamic Adaptation**: A "Replanner" agent adjusts future tasks based on previous outcomes and reflections.
-   **Modern Web UI**: A clean React-based frontend for managing goals and tracking progress.

## Architecture

The system consists of several specialized agents:

1.  **Planner**: Takes a goal and creates a list of actionable tasks.
2.  **Executor**: Performs individual tasks using available tools (e.g., web search).
3.  **Reflector**: Analyzes the output of a task to ensure it meets quality standards and objectives.
4.  **Constructor**: Transforms task outputs into structured learning materials or quizzes (integrated into the frontend).
5.  **Replanner**: Updates the remaining plan based on feedback from the Reflector.

## Tech Stack

-   **Backend**: FastAPI (Python)
-   **Frontend**: React (Vite)
-   **Database**: PostgreSQL
-   **Caching**: Redis
-   **AI Engine**: Ollama (Local LLMs)
-   **Orchestration**: Docker & Docker Compose

## Prerequisites

-   [Docker](https://www.docker.com/) and Docker Compose
-   [Ollama](https://ollama.ai/) installed and running on your host machine (or within Docker)

## Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd goal_manager
    ```

2.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in the required values (Database credentials, Ollama model name, etc.).
    ```bash
    cp .env.example .env
    ```

3.  **Start the services**:
    ```bash
    docker-compose up --build
    ```
    This will spin up the database, Redis, MCP servers, backend, and frontend.

4.  **Ollama Configuration**:
    Ensure the model specified in your `.env` (e.g., `llama3`) is pulled in Ollama:
    ```bash
    ollama pull llama3
    ```

## Usage

1.  Access the frontend at `http://localhost:5173`.
2.  Sign up/Login to your account.
3.  Create a new Goal.
4.  The system will automatically trigger the **Planner** to generate a roadmap.
5.  Execute tasks one by one and watch the agents work through the plan!

from fastmcp import FastMCP
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from decouple import config
from typing import Optional
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root) #had to do this stupid shit cus python wouldnt know where backend is

from backend.models import GoalsTable, TasksTable, AgentOutputsTable

#port 8002

mcp = FastMCP("Database Search")

engine = None
AsyncSessionLocal = None

async def get_session():
    global engine, AsyncSessionLocal
    if not engine:
        db_url = config("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

        engine = create_async_engine(
            db_url,
            echo=False,
            pool_size=10,
            max_overflow=20
        )
        
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        return AsyncSessionLocal()

@mcp.tool()
async def search_goals(query: str, limit: int = 10):
    async with await get_session() as session:
        stmt = select(GoalsTable).where(
            GoalsTable.goal.ilike(f"%{query}%")
        ).order_by(GoalsTable.created_at.desc()).limit(limit)

        result = await session.execute(stmt)
        goals = result.scalars().all()

        print(f"found {len(goals)} goals")

        return [
            {
                "id": g.id,
                "goal": g.goal,
                "created_at": g.created_at.isoformat() if g.created_at else None
            }
            for g in goals
        ]

@mcp.tool()
async def get_all_goals(limit: int = 20):
    async with await get_session() as session:
        stmt = select(GoalsTable).order_by(
            GoalsTable.created_at.desc()
        ).limit(limit)
        
        result = await session.execute(stmt)
        goals = result.scalars().all()
        
        return [
            {
                "id": g.id,
                "goal": g.goal,
                "created_at": g.created_at.isoformat() if g.created_at else None
            }
            for g in goals
        ]

@mcp.tool()
async def get_goal_details(goal_id: int):
    async with await get_session() as session:
        stmt = select(GoalsTable).where(GoalTable.id == goal_id)
        result = await session.execute(stmt)
        goal = result.scalar_one_or_none()

        if not goal:
            return None

        return {
            "id": goal.id,
            "goal": goal.goal,
            "created_at": goal.created_at.isoformat() if goal.created_at else None
        }

@mcp.tool()
async def get_tasks_for_goal(goal_id: int, status: Optional[str] = None):
    async with await get_session() as session:
        stmt =  select(TasksTable).where(TasksTable.goal_id == goal_id)
        if status:
            stmt = stmt.where(TasksTable.status == status)

        stmt = stmt.order_by(TasksTable.created_at.desc())
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        print(f"got {len(tasks)} tasks")

        return [
            {
                "id": t.id,
                "description": t.description,
                "status": t.status,
                "scheduled_day": t.scheduled_day,
                "estimated_minutes": t.estimated_minutes,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            }
            for t in tasks
        ]

@mcp.tool()
async def search_tasks(query: str, status: Optional[str] = None, limit: int = 10):
    async with await get_session() as session:
        stmt = select(TasksTable).where(
            TasksTable.description.ilike(f"%{query}%")
        )

        if status:
            stmt = stmt.where(TasksTable.status == status)

        result = await session.execute(stmt)
        tasks = result.scalars().all()

        return [
            {
                "id": t.id,
                "goal_id": t.goal_id,
                "description": t.description,
                "status": t.status,
                "scheduled_day": t.scheduled_day,
                "estimated_minutes": t.estimated_minutes
            }
            for t in tasks
        ]

@mcp.tool()
async def get_all_tasks(status: Optional[str] = None, limit: int = 20):
    async with await get_session() as session:
        stmt = select(TasksTable)
        if status:
            stmt.where(TasksTable.status == status)
        
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        return [
            {
                "id": t.id,
                "goal_id": t.goal_id,
                "description": t.description,
                "status": t.status,
                "scheduled_day": t.scheduled_day,
                "estimated_minutes": t.estimated_minutes
            }
            for t in tasks
        ]

@mcp.tool()
async def get_goal_with_tasks(goal_id: int):
    async with await get_session() as session:
        goal_stmt = select(GoalsTable).where(GoalsTable.id == goal_id)
        goal_result = await session.execute(goal_stmt)
        goal = goal_result.scalar_one_or_none()
        
        if not goal:
            return {"error": "no goal found"}
        
        tasks_stmt = select(TasksTable).where(TasksTable.goal_id == goal_id)
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()

        return {
            "goal": {
                "id": goal.id,
                "goal": goal.goal,
                "created_at": goal.created_at.isoformat() if goal.created_at else None
            },
            "tasks": [
                {
                    "id": t.id,
                    "description": t.description,
                    "status": t.status,
                    "scheduled_day": t.scheduled_day,
                    "estimated_minutes": t.estimated_minutes
                }
                for t in tasks
            ],
            "summary": {
                "total_tasks": len(tasks),
                "completed": len([t for t in tasks if t.status == "completed"]),
                "pending": len([t for t in tasks if t.status == "pending"]),
                "in_progress": len([t for t in tasks if t.status == "in_progress"]),
                "total_estimated_minutes": sum(t.estimated_minutes or 0 for t in tasks)
            }
        }
    
@mcp.tool()
async def get_task_stats():
    async with await get_session() as session:
        stats_stmt = select(
            func.count(TasksTable.id).label("total_tasks"),
            func.count(TasksTable.id).filter(TasksTable.status == "completed").label("completed"),
            func.count(TasksTable.id).filter(TasksTable.status == "pending").label("pending"),
            func.count(TasksTable.id).filter(TasksTable.status == "in_progress").label("in_progress"),
            func.sum(TasksTable.estimated_minutes).filter(TasksTable.status == "pending").label("pending_minutes")
        )

        result = await session.execute(stats_stmt)
        stats = result.one()

        return {
            "total_tasks": stats.total_tasks or 0,
            "completed": stats.completed or 0,
            "pending": stats.pending or 0,
            "in_progress": stats.in_progress or 0,
            "pending_minutes": stats.pending_minutes or 0
        }

@mcp.tool()
async def get_agent_outputs(task_id: int, agent_type: Optional[str] = None):
    async with await get_session() as session:
        stmt = select(AgentOutputsTable).where(
            AgentOutputsTable.task_id == task_id
        )

        if agent_type:
            stmt = stmt.where(AgentOutputsTable.agent_type == agent_type)
        
        stmt = stmt.order_by(AgentOutputsTable.created_at.desc())
        result = await session.execute(stmt)
        outputs = result.scalars().all()

        return [
            {
                "id": o.id,
                "agent_type": o.agent_type,
                "output_text": o.output_text,
                "created_at": o.created_at.isoformat() if o.created_at else None
            }
            for o in outputs
        ]

@mcp.tool()
async def get_recent_agent_outputs(agent_type: Optional[str] = None, limit: int = 10):
    async with await get_session() as session:
        stmt = select(AgentOutputsTable)
        
        if agent_type:
            stmt = stmt.where(AgentOutputsTable.agent_type == agent_type)
        
        stmt = stmt.order_by(AgentOutputsTable.created_at.desc()).limit(limit)        
        result = await session.execute(stmt)
        outputs = result.scalars().all()
        
        return [
            {
                "id": o.id,
                "task_id": o.task_id,
                "agent_type": o.agent_type,
                "output_text": o.output_text,
                "created_at": o.created_at.isoformat() if o.created_at else None
            }
            for o in outputs
        ]

if __name__ == "__main__":
    mcp.run(transport="sse", host=config("MCP_HOST"), port=8002)

from fastmcp import FastMCP
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from decouple import config
from typing import Optional
from ...models import GoalsTable, TasksTable, AgentOutputsTable

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

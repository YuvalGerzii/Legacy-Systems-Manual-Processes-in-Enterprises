"""API routes for Agentic Operations."""

from typing import List
from uuid import UUID
from fastapi import APIRouter
from src.agents.models import Agent, AgentTask, AgentType

router = APIRouter()


@router.post("/tasks", response_model=AgentTask)
async def create_agent_task(task: AgentTask) -> AgentTask:
    """Create a new agent task."""
    return task


@router.get("/tasks/{task_id}", response_model=AgentTask)
async def get_task_status(task_id: UUID) -> AgentTask:
    """Get task status."""
    return AgentTask(
        id=task_id,
        agent_type=AgentType.PROCUREMENT,
        description="Sample task",
        status="completed",
    )


@router.get("/agents", response_model=List[Agent])
async def list_agents() -> List[Agent]:
    """List available agents."""
    return [
        Agent(
            type=AgentType.PROCUREMENT,
            name="Procurement Agent",
            capabilities=["Vendor selection", "Purchase order creation"],
        )
    ]


@router.get("/health")
async def health_check() -> dict:
    """Health check."""
    return {"status": "healthy", "module": "agents"}

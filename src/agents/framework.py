"""
Intelligent Agent Framework
Base classes and interfaces for specialized AI agents
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from loguru import logger

from src.core.llm import get_local_llm


class AgentRole(str, Enum):
    """Agent role types."""
    DISCOVERY = "discovery"
    ASSESSMENT = "assessment"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    ADVISORY = "advisory"


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTask(BaseModel):
    """Task for an agent to execute."""
    id: UUID = Field(default_factory=uuid4)
    type: str
    description: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 5
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    """Result from agent execution."""
    task_id: UUID
    agent_id: str
    status: AgentStatus
    output: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    reasoning: str = ""
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Base class for all intelligent agents.

    Each agent has:
    - A specific role and expertise
    - Ability to analyze and reason using local LLM
    - Structured output format
    - Collaboration capabilities
    """

    def __init__(self, agent_id: str, role: AgentRole):
        """Initialize agent."""
        self.agent_id = agent_id
        self.role = role
        self.status = AgentStatus.IDLE
        self.llm = get_local_llm()
        self.memory: List[Dict[str, Any]] = []

        logger.info(f"Initialized {self.__class__.__name__} (ID: {agent_id}, Role: {role})")

    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute a task.

        Args:
            task: Task to execute

        Returns:
            AgentResult: Execution result
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        pass

    async def analyze_with_llm(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 2000,
    ) -> str:
        """
        Use local LLM to analyze and reason.

        Args:
            prompt: Analysis prompt
            context: Optional context information
            max_tokens: Maximum tokens to generate

        Returns:
            str: LLM response
        """
        messages = []

        if context:
            messages.append({
                "role": "system",
                "content": f"You are a {self.role} agent. {context}"
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        self.status = AgentStatus.THINKING

        try:
            response = await self.llm.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=max_tokens,
            )

            self.status = AgentStatus.IDLE
            return response

        except Exception as e:
            logger.error(f"LLM analysis failed for {self.agent_id}: {e}")
            self.status = AgentStatus.FAILED
            raise

    def remember(self, key: str, value: Any) -> None:
        """Store information in agent memory."""
        self.memory.append({
            "timestamp": datetime.utcnow(),
            "key": key,
            "value": value,
        })

    def recall(self, key: str) -> Optional[Any]:
        """Recall information from memory."""
        for item in reversed(self.memory):
            if item["key"] == key:
                return item["value"]
        return None

    def get_context_summary(self) -> str:
        """Get summary of agent's memory/context."""
        if not self.memory:
            return "No prior context."

        recent = self.memory[-5:]  # Last 5 items
        summary = "\n".join([
            f"- {item['key']}: {str(item['value'])[:100]}"
            for item in recent
        ])
        return f"Recent context:\n{summary}"


class AgentOrchestrator:
    """
    Orchestrates multiple agents to work together on complex tasks.

    Coordinates agents, manages task distribution, and aggregates results.
    """

    def __init__(self):
        """Initialize orchestrator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.results: Dict[UUID, AgentResult] = {}

        logger.info("Agent orchestrator initialized")

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id} ({agent.role})")

    async def execute_workflow(
        self,
        workflow_name: str,
        tasks: List[AgentTask],
    ) -> List[AgentResult]:
        """
        Execute a workflow with multiple tasks.

        Args:
            workflow_name: Name of the workflow
            tasks: List of tasks to execute

        Returns:
            List[AgentResult]: Results from all tasks
        """
        logger.info(f"Starting workflow: {workflow_name} ({len(tasks)} tasks)")

        results = []

        for task in tasks:
            # Find appropriate agent for task
            agent = self._find_agent_for_task(task)

            if not agent:
                logger.warning(f"No agent found for task: {task.type}")
                continue

            # Execute task
            logger.info(f"Assigning task {task.id} to agent {agent.agent_id}")
            result = await agent.execute(task)

            results.append(result)
            self.results[result.task_id] = result

        logger.info(f"Workflow {workflow_name} completed with {len(results)} results")
        return results

    def _find_agent_for_task(self, task: AgentTask) -> Optional[BaseAgent]:
        """Find best agent for a task."""
        # Simple matching based on task type
        for agent in self.agents.values():
            capabilities = agent.get_capabilities()
            if any(cap in task.type for cap in capabilities):
                return agent

        return None

    async def collaborate(
        self,
        lead_agent: str,
        supporting_agents: List[str],
        task: AgentTask,
    ) -> AgentResult:
        """
        Multiple agents collaborate on a task.

        Args:
            lead_agent: ID of lead agent
            supporting_agents: IDs of supporting agents
            task: Task to execute

        Returns:
            AgentResult: Aggregated result
        """
        logger.info(f"Collaboration: {lead_agent} leading with {len(supporting_agents)} supporting agents")

        # Supporting agents provide input
        supporting_results = []
        for agent_id in supporting_agents:
            agent = self.agents.get(agent_id)
            if agent:
                result = await agent.execute(task)
                supporting_results.append(result)

        # Lead agent synthesizes
        lead = self.agents.get(lead_agent)
        if lead:
            # Add supporting results to task input
            task.input_data["supporting_analysis"] = [
                r.output for r in supporting_results
            ]

            final_result = await lead.execute(task)
            return final_result

        raise ValueError(f"Lead agent {lead_agent} not found")

    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all registered agents."""
        return {
            agent_id: agent.get_capabilities()
            for agent_id, agent in self.agents.items()
        }

"""Low-Code Workflow Designer Engine for SMEs.

This module provides a drag-and-drop workflow builder with AI-powered features
for small and medium enterprises to automate their processes without coding.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import json

from loguru import logger

from .models import (
    LowCodeWorkflow,
    LowCodeNode,
    LowCodeConnection,
    NodeType,
    NodeCategory,
    WorkflowValidationResult,
    WorkflowExecution,
    WorkflowStatus,
)


class LowCodeWorkflowDesigner:
    """Visual workflow designer with drag-and-drop capabilities."""

    def __init__(self):
        """Initialize the low-code workflow designer."""
        self.workflows: Dict[UUID, LowCodeWorkflow] = {}
        self.executions: Dict[UUID, WorkflowExecution] = {}

    async def create_workflow(
        self,
        name: str,
        description: Optional[str] = None,
        nodes: Optional[List[LowCodeNode]] = None,
        connections: Optional[List[LowCodeConnection]] = None,
    ) -> LowCodeWorkflow:
        """Create a new low-code workflow.

        Args:
            name: Name of the workflow
            description: Optional description
            nodes: List of workflow nodes
            connections: List of connections between nodes

        Returns:
            Created workflow

        Example:
            >>> designer = LowCodeWorkflowDesigner()
            >>> workflow = await designer.create_workflow(
            ...     name="Invoice Approval",
            ...     description="Automated invoice approval process"
            ... )
        """
        workflow = LowCodeWorkflow(
            name=name,
            description=description,
            nodes=nodes or [],
            connections=connections or [],
        )
        self.workflows[workflow.id] = workflow
        logger.info(f"Created workflow: {workflow.name} ({workflow.id})")
        return workflow

    async def add_node(
        self,
        workflow_id: UUID,
        node_type: NodeType,
        label: str,
        config: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, int]] = None,
    ) -> LowCodeNode:
        """Add a node to the workflow.

        Args:
            workflow_id: ID of the workflow
            node_type: Type of the node
            label: Display label for the node
            config: Node configuration
            position: Position on the canvas (x, y)

        Returns:
            Created node

        Example:
            >>> node = await designer.add_node(
            ...     workflow_id=workflow.id,
            ...     node_type=NodeType.AI_APPROVAL,
            ...     label="AI Invoice Review",
            ...     config={"threshold": 0.8}
            ... )
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        category = self._get_node_category(node_type)
        node = LowCodeNode(
            type=node_type,
            category=category,
            label=label,
            config=config or {},
            position=position or {"x": 0, "y": 0},
        )

        workflow = self.workflows[workflow_id]
        workflow.nodes.append(node)
        workflow.updated_at = datetime.utcnow()

        logger.info(f"Added node {node.label} to workflow {workflow.name}")
        return node

    async def connect_nodes(
        self,
        workflow_id: UUID,
        source_node_id: str,
        target_node_id: str,
        condition: Optional[str] = None,
    ) -> LowCodeConnection:
        """Connect two nodes in the workflow.

        Args:
            workflow_id: ID of the workflow
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            condition: Optional condition for the connection

        Returns:
            Created connection

        Example:
            >>> connection = await designer.connect_nodes(
            ...     workflow_id=workflow.id,
            ...     source_node_id=trigger_node.id,
            ...     target_node_id=approval_node.id
            ... )
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]

        # Validate nodes exist
        node_ids = {node.id for node in workflow.nodes}
        if source_node_id not in node_ids:
            raise ValueError(f"Source node {source_node_id} not found")
        if target_node_id not in node_ids:
            raise ValueError(f"Target node {target_node_id} not found")

        connection = LowCodeConnection(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            condition=condition,
        )

        workflow.connections.append(connection)
        workflow.updated_at = datetime.utcnow()

        logger.info(f"Connected nodes in workflow {workflow.name}")
        return connection

    async def validate_workflow(
        self, workflow_id: UUID
    ) -> WorkflowValidationResult:
        """Validate a workflow for errors and issues.

        Args:
            workflow_id: ID of the workflow to validate

        Returns:
            Validation result with errors, warnings, and suggestions

        Example:
            >>> result = await designer.validate_workflow(workflow.id)
            >>> if result.is_valid:
            ...     print("Workflow is ready to execute!")
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        errors = []
        warnings = []
        suggestions = []

        # Check for at least one trigger node
        trigger_nodes = [
            n for n in workflow.nodes if n.category == NodeCategory.TRIGGERS
        ]
        if not trigger_nodes:
            errors.append("Workflow must have at least one trigger node")

        # Check for isolated nodes (no connections)
        connected_nodes = set()
        for conn in workflow.connections:
            connected_nodes.add(conn.source_node_id)
            connected_nodes.add(conn.target_node_id)

        isolated_nodes = [
            n.label for n in workflow.nodes if n.id not in connected_nodes
        ]
        if isolated_nodes and len(workflow.nodes) > 1:
            warnings.append(
                f"Isolated nodes detected: {', '.join(isolated_nodes)}"
            )

        # Check for circular dependencies
        if self._has_circular_dependency(workflow):
            errors.append("Circular dependency detected in workflow")

        # Check for proper end nodes
        end_nodes = [
            n
            for n in workflow.nodes
            if n.type in [NodeType.SUCCESS, NodeType.FAILURE]
        ]
        if not end_nodes and len(workflow.nodes) > 1:
            suggestions.append("Consider adding SUCCESS or FAILURE end nodes")

        # Check node configurations
        for node in workflow.nodes:
            if node.type == NodeType.AI_APPROVAL and not node.config.get(
                "threshold"
            ):
                warnings.append(
                    f"Node '{node.label}' missing AI threshold configuration"
                )

        is_valid = len(errors) == 0

        return WorkflowValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
        )

    async def execute_workflow(
        self, workflow_id: UUID, input_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """Execute a low-code workflow.

        Args:
            workflow_id: ID of the workflow to execute
            input_data: Optional input data for the workflow

        Returns:
            Workflow execution record

        Example:
            >>> execution = await designer.execute_workflow(
            ...     workflow_id=workflow.id,
            ...     input_data={"invoice_id": "INV-001", "amount": 5000}
            ... )
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]

        # Validate before execution
        validation = await self.validate_workflow(workflow_id)
        if not validation.is_valid:
            raise ValueError(
                f"Workflow validation failed: {', '.join(validation.errors)}"
            )

        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.executions[execution.id] = execution

        logger.info(f"Starting execution of workflow {workflow.name}")

        try:
            # Execute workflow nodes in topological order
            result = await self._execute_nodes(workflow, input_data or {})

            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.result = result
            execution.logs.append(
                f"Workflow completed successfully at {datetime.utcnow()}"
            )

            # Update workflow statistics
            workflow.execution_count += 1
            workflow.last_executed_at = datetime.utcnow()

            logger.info(f"Workflow {workflow.name} completed successfully")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            execution.logs.append(f"Workflow failed: {str(e)}")

            logger.error(f"Workflow {workflow.name} failed: {str(e)}")

        return execution

    async def _execute_nodes(
        self, workflow: LowCodeWorkflow, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute workflow nodes in the correct order.

        Args:
            workflow: The workflow to execute
            input_data: Input data for the workflow

        Returns:
            Execution result
        """
        # Find trigger nodes to start execution
        trigger_nodes = [
            n for n in workflow.nodes if n.category == NodeCategory.TRIGGERS
        ]

        if not trigger_nodes:
            raise ValueError("No trigger nodes found")

        # Build execution graph
        graph = self._build_execution_graph(workflow)

        # Execute nodes in topological order
        context = {"input": input_data, "variables": workflow.variables}
        visited = set()

        for trigger in trigger_nodes:
            await self._execute_node_recursive(
                trigger, workflow, graph, context, visited
            )

        return context

    async def _execute_node_recursive(
        self,
        node: LowCodeNode,
        workflow: LowCodeWorkflow,
        graph: Dict[str, List[str]],
        context: Dict[str, Any],
        visited: set,
    ) -> Any:
        """Recursively execute a node and its dependencies.

        Args:
            node: Current node to execute
            workflow: The workflow
            graph: Execution graph
            context: Execution context
            visited: Set of visited node IDs

        Returns:
            Node execution result
        """
        if node.id in visited:
            return context.get(node.id)

        visited.add(node.id)

        # Execute node based on type
        result = await self._execute_single_node(node, context)
        context[node.id] = result

        # Execute connected nodes
        if node.id in graph:
            for next_node_id in graph[node.id]:
                next_node = next(
                    (n for n in workflow.nodes if n.id == next_node_id), None
                )
                if next_node:
                    await self._execute_node_recursive(
                        next_node, workflow, graph, context, visited
                    )

        return result

    async def _execute_single_node(
        self, node: LowCodeNode, context: Dict[str, Any]
    ) -> Any:
        """Execute a single node.

        Args:
            node: Node to execute
            context: Execution context

        Returns:
            Node execution result
        """
        logger.info(f"Executing node: {node.label} ({node.type})")

        # Placeholder for actual node execution
        # In production, this would call specific handlers for each node type
        if node.type == NodeType.MANUAL_TRIGGER:
            return {"triggered": True, "timestamp": datetime.utcnow()}

        elif node.type == NodeType.AI_APPROVAL:
            # This would integrate with the AI agent system
            return {
                "approved": True,
                "confidence": 0.95,
                "reasoning": "AI approved based on configured criteria",
            }

        elif node.type == NodeType.HUMAN_APPROVAL:
            # This would integrate with the HITL Hub
            return {"status": "pending_approval", "assigned_to": "manager"}

        elif node.type == NodeType.HTTP_REQUEST:
            # Make HTTP request based on config
            return {"status": 200, "data": {}}

        elif node.type == NodeType.EMAIL_SEND:
            # Send email based on config
            return {"sent": True, "message_id": str(uuid4())}

        else:
            return {"executed": True, "node_type": node.type}

    def _build_execution_graph(
        self, workflow: LowCodeWorkflow
    ) -> Dict[str, List[str]]:
        """Build an execution graph from workflow connections.

        Args:
            workflow: The workflow

        Returns:
            Dictionary mapping node IDs to their successor node IDs
        """
        graph: Dict[str, List[str]] = {}

        for conn in workflow.connections:
            if conn.source_node_id not in graph:
                graph[conn.source_node_id] = []
            graph[conn.source_node_id].append(conn.target_node_id)

        return graph

    def _has_circular_dependency(self, workflow: LowCodeWorkflow) -> bool:
        """Check if workflow has circular dependencies.

        Args:
            workflow: The workflow to check

        Returns:
            True if circular dependency exists
        """
        graph = self._build_execution_graph(workflow)
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            if node_id in graph:
                for neighbor in graph[node_id]:
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True

            rec_stack.remove(node_id)
            return False

        for node in workflow.nodes:
            if node.id not in visited:
                if has_cycle(node.id):
                    return True

        return False

    def _get_node_category(self, node_type: NodeType) -> NodeCategory:
        """Get the category for a node type.

        Args:
            node_type: The node type

        Returns:
            Node category
        """
        trigger_types = {
            NodeType.MANUAL_TRIGGER,
            NodeType.SCHEDULE_TRIGGER,
            NodeType.WEBHOOK_TRIGGER,
            NodeType.EMAIL_TRIGGER,
            NodeType.FILE_TRIGGER,
        }

        action_types = {
            NodeType.HTTP_REQUEST,
            NodeType.EMAIL_SEND,
            NodeType.DATABASE_QUERY,
            NodeType.FILE_OPERATION,
            NodeType.NOTIFICATION,
            NodeType.DATA_TRANSFORM,
        }

        logic_types = {
            NodeType.CONDITION,
            NodeType.LOOP,
            NodeType.SWITCH,
            NodeType.DELAY,
        }

        integration_types = {
            NodeType.SALESFORCE,
            NodeType.SAP,
            NodeType.ORACLE,
            NodeType.SHAREPOINT,
            NodeType.SLACK,
            NodeType.TEAMS,
        }

        ai_types = {
            NodeType.AI_APPROVAL,
            NodeType.AI_CLASSIFICATION,
            NodeType.AI_EXTRACTION,
            NodeType.AI_GENERATION,
        }

        human_types = {
            NodeType.HUMAN_APPROVAL,
            NodeType.HUMAN_INPUT,
            NodeType.HUMAN_REVIEW,
        }

        output_types = {NodeType.SUCCESS, NodeType.FAILURE}

        if node_type in trigger_types:
            return NodeCategory.TRIGGERS
        elif node_type in action_types:
            return NodeCategory.ACTIONS
        elif node_type in logic_types:
            return NodeCategory.LOGIC
        elif node_type in integration_types:
            return NodeCategory.INTEGRATIONS
        elif node_type in ai_types:
            return NodeCategory.AI
        elif node_type in human_types:
            return NodeCategory.HUMAN
        elif node_type in output_types:
            return NodeCategory.OUTPUTS
        else:
            return NodeCategory.ACTIONS

    async def export_workflow(
        self, workflow_id: UUID, format: str = "json"
    ) -> str:
        """Export workflow to various formats.

        Args:
            workflow_id: ID of the workflow to export
            format: Export format (json, yaml, python)

        Returns:
            Exported workflow as string

        Example:
            >>> json_str = await designer.export_workflow(workflow.id, "json")
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]

        if format == "json":
            return workflow.model_dump_json(indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def import_workflow(
        self, workflow_data: str, format: str = "json"
    ) -> LowCodeWorkflow:
        """Import workflow from various formats.

        Args:
            workflow_data: Workflow data as string
            format: Import format (json, yaml)

        Returns:
            Imported workflow

        Example:
            >>> workflow = await designer.import_workflow(json_str, "json")
        """
        if format == "json":
            data = json.loads(workflow_data)
            workflow = LowCodeWorkflow(**data)
            self.workflows[workflow.id] = workflow
            return workflow
        else:
            raise ValueError(f"Unsupported import format: {format}")


# Singleton instance
_designer_instance: Optional[LowCodeWorkflowDesigner] = None


def get_lowcode_designer() -> LowCodeWorkflowDesigner:
    """Get the global low-code workflow designer instance.

    Returns:
        Global LowCodeWorkflowDesigner instance
    """
    global _designer_instance
    if _designer_instance is None:
        _designer_instance = LowCodeWorkflowDesigner()
    return _designer_instance

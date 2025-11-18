"""API routes for Enterprise Automation Fabric and Low-Code Workflow Platform."""

from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from src.automation_fabric.models import (
    WorkflowDefinition,
    WorkflowExecution,
    APIEmulationConfig,
    LowCodeWorkflow,
    LowCodeNode,
    LowCodeConnection,
    WorkflowTemplate,
    WorkflowValidationResult,
    PluginDefinition,
    PluginConnection,
    NodeType,
    NodeCategory,
)
from src.automation_fabric.engine import AutomationEngine, APIEmulator
from src.automation_fabric.lowcode_designer import get_lowcode_designer
from src.automation_fabric.workflow_templates import WorkflowTemplateLibrary
from src.automation_fabric.node_library import NodeLibrary
from src.automation_fabric.ai_approval_assistant import (
    get_approval_assistant,
    ApprovalRequest,
)
from src.automation_fabric.plugin_system import get_plugin_manager
from src.core.logger import logger

router = APIRouter()
automation_engine = AutomationEngine()
api_emulator = APIEmulator()
lowcode_designer = get_lowcode_designer()
approval_assistant = get_approval_assistant()
plugin_manager = get_plugin_manager()


@router.post("/workflows", response_model=WorkflowDefinition)
async def create_workflow(workflow: WorkflowDefinition) -> WorkflowDefinition:
    """Create a new automation workflow."""
    logger.info(f"Creating workflow: {workflow.name}")
    return workflow


@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_workflow(
    workflow_id: UUID, workflow: WorkflowDefinition
) -> WorkflowExecution:
    """Execute a workflow."""
    try:
        execution = await automation_engine.execute_workflow(workflow)
        return execution
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}/executions", response_model=List[WorkflowExecution])
async def get_workflow_executions(workflow_id: UUID) -> List[WorkflowExecution]:
    """Get execution history for a workflow."""
    executions = [
        exec for exec in automation_engine.executions.values()
        if exec.workflow_id == workflow_id
    ]
    return executions


@router.post("/api-emulation", response_model=dict)
async def create_api_emulation(config: APIEmulationConfig) -> dict:
    """Create an API emulation for a legacy system."""
    logger.info(f"Creating API emulation for system: {config.system_id}")
    return {"status": "created", "system_id": config.system_id}


@router.get("/health")
async def health_check() -> dict:
    """Health check for automation fabric."""
    return {"status": "healthy", "module": "automation_fabric"}


# ============================================================================
# LOW-CODE WORKFLOW PLATFORM API ROUTES
# ============================================================================


# -------------------- Workflow Management --------------------


@router.post("/lowcode/workflows", response_model=LowCodeWorkflow)
async def create_lowcode_workflow(
    name: str,
    description: Optional[str] = None,
) -> LowCodeWorkflow:
    """Create a new low-code workflow.

    Example:
        POST /api/v1/automation/lowcode/workflows
        {
            "name": "Invoice Approval",
            "description": "Automated invoice approval process"
        }
    """
    try:
        workflow = await lowcode_designer.create_workflow(name, description)
        logger.info(f"Created low-code workflow: {workflow.name}")
        return workflow
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lowcode/workflows/{workflow_id}", response_model=LowCodeWorkflow)
async def get_lowcode_workflow(workflow_id: UUID) -> LowCodeWorkflow:
    """Get a low-code workflow by ID."""
    workflow = lowcode_designer.workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.get("/lowcode/workflows", response_model=List[LowCodeWorkflow])
async def list_lowcode_workflows() -> List[LowCodeWorkflow]:
    """List all low-code workflows."""
    return list(lowcode_designer.workflows.values())


@router.post("/lowcode/workflows/{workflow_id}/nodes", response_model=LowCodeNode)
async def add_node_to_workflow(
    workflow_id: UUID,
    node_type: NodeType,
    label: str,
    config: Optional[Dict[str, Any]] = None,
    position: Optional[Dict[str, int]] = None,
) -> LowCodeNode:
    """Add a node to a workflow.

    Example:
        POST /api/v1/automation/lowcode/workflows/{id}/nodes
        {
            "node_type": "ai_approval",
            "label": "AI Invoice Review",
            "config": {"threshold": 0.85},
            "position": {"x": 300, "y": 100}
        }
    """
    try:
        node = await lowcode_designer.add_node(
            workflow_id, node_type, label, config, position
        )
        return node
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lowcode/workflows/{workflow_id}/connections", response_model=LowCodeConnection)
async def connect_nodes(
    workflow_id: UUID,
    source_node_id: str,
    target_node_id: str,
    condition: Optional[str] = None,
) -> LowCodeConnection:
    """Connect two nodes in a workflow.

    Example:
        POST /api/v1/automation/lowcode/workflows/{id}/connections
        {
            "source_node_id": "node-1",
            "target_node_id": "node-2",
            "condition": "amount > 1000"
        }
    """
    try:
        connection = await lowcode_designer.connect_nodes(
            workflow_id, source_node_id, target_node_id, condition
        )
        return connection
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lowcode/workflows/{workflow_id}/validate", response_model=WorkflowValidationResult)
async def validate_workflow(workflow_id: UUID) -> WorkflowValidationResult:
    """Validate a workflow for errors and issues.

    Returns validation result with errors, warnings, and suggestions.
    """
    try:
        result = await lowcode_designer.validate_workflow(workflow_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lowcode/workflows/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_lowcode_workflow(
    workflow_id: UUID,
    input_data: Optional[Dict[str, Any]] = None,
) -> WorkflowExecution:
    """Execute a low-code workflow.

    Example:
        POST /api/v1/automation/lowcode/workflows/{id}/execute
        {
            "input_data": {
                "invoice_id": "INV-001",
                "amount": 5000
            }
        }
    """
    try:
        execution = await lowcode_designer.execute_workflow(workflow_id, input_data)
        return execution
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lowcode/workflows/{workflow_id}/export")
async def export_workflow(
    workflow_id: UUID,
    format: str = Query("json", description="Export format (json, yaml, python)"),
) -> Dict[str, Any]:
    """Export a workflow to various formats."""
    try:
        exported = await lowcode_designer.export_workflow(workflow_id, format)
        return {"format": format, "data": exported}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- Workflow Templates --------------------


@router.get("/lowcode/templates", response_model=List[WorkflowTemplate])
async def list_workflow_templates(
    category: Optional[str] = None,
    industry: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> List[WorkflowTemplate]:
    """Get available workflow templates.

    Query parameters:
    - category: Filter by category (Finance, HR, Sales, etc.)
    - industry: Filter by industry
    - difficulty: Filter by difficulty (beginner, intermediate, advanced)

    Example:
        GET /api/v1/automation/lowcode/templates?category=Finance&difficulty=beginner
    """
    templates = WorkflowTemplateLibrary.get_all_templates()

    # Apply filters
    if category:
        templates = [t for t in templates if t.category == category]
    if industry:
        templates = [t for t in templates if t.industry == industry or t.industry == "All"]
    if difficulty:
        templates = [t for t in templates if t.difficulty == difficulty]

    return templates


@router.get("/lowcode/templates/{template_id}", response_model=WorkflowTemplate)
async def get_workflow_template(template_id: UUID) -> WorkflowTemplate:
    """Get a specific workflow template by ID."""
    templates = WorkflowTemplateLibrary.get_all_templates()
    template = next((t for t in templates if t.id == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/lowcode/templates/{template_id}/instantiate", response_model=LowCodeWorkflow)
async def instantiate_template(
    template_id: UUID,
    workflow_name: Optional[str] = None,
) -> LowCodeWorkflow:
    """Create a new workflow from a template.

    Example:
        POST /api/v1/automation/lowcode/templates/{id}/instantiate
        {
            "workflow_name": "My Invoice Approval"
        }
    """
    templates = WorkflowTemplateLibrary.get_all_templates()
    template = next((t for t in templates if t.id == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Create workflow from template
    workflow = LowCodeWorkflow(
        name=workflow_name or template.name,
        description=template.description,
        nodes=template.nodes,
        connections=template.connections,
        is_template=False,
        template_id=template.id,
        category=template.category,
        tags=template.tags,
    )

    lowcode_designer.workflows[workflow.id] = workflow
    logger.info(f"Instantiated workflow from template: {template.name}")

    return workflow


# -------------------- Node Library --------------------


@router.get("/lowcode/nodes")
async def get_available_nodes(
    category: Optional[NodeCategory] = None,
) -> List[Dict[str, Any]]:
    """Get available workflow nodes for drag-and-drop designer.

    Query parameters:
    - category: Filter by category (triggers, actions, logic, ai, etc.)

    Example:
        GET /api/v1/automation/lowcode/nodes?category=ai
    """
    nodes = NodeLibrary.get_all_nodes()

    if category:
        nodes = [n for n in nodes if n["category"] == category]

    return nodes


@router.get("/lowcode/nodes/{node_type}")
async def get_node_definition(node_type: NodeType) -> Dict[str, Any]:
    """Get detailed definition for a specific node type."""
    try:
        definition = NodeLibrary.get_node_definition(node_type)
        return definition
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------- AI Approval Assistant --------------------


@router.post("/lowcode/ai-approval/process")
async def process_ai_approval(request: ApprovalRequest) -> Dict[str, Any]:
    """Process an approval request using AI.

    Example:
        POST /api/v1/automation/lowcode/ai-approval/process
        {
            "id": "uuid",
            "workflow_id": "uuid",
            "request_type": "invoice",
            "data": {
                "amount": 4500,
                "vendor_name": "Acme Corp"
            },
            "criteria": "Approve if amount < $5000",
            "threshold": 0.8
        }
    """
    try:
        decision = await approval_assistant.process_approval(request)
        return {
            "request_id": str(decision.request_id),
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "risk_factors": decision.risk_factors,
            "recommendations": decision.recommendations,
            "timestamp": decision.timestamp.isoformat(),
        }
    except Exception as e:
        logger.error(f"AI approval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lowcode/ai-approval/stats")
async def get_approval_stats() -> Dict[str, Any]:
    """Get AI approval statistics.

    Returns metrics like auto-approval rate, average confidence, etc.
    """
    stats = approval_assistant.get_approval_stats()
    return stats


@router.get("/lowcode/ai-approval/decision/{decision_id}")
async def explain_decision(decision_id: UUID) -> Dict[str, Any]:
    """Get detailed explanation for a past AI approval decision."""
    explanation = await approval_assistant.explain_decision(decision_id)

    if not explanation:
        raise HTTPException(status_code=404, detail="Decision not found")

    return explanation


# -------------------- Plugin System --------------------


@router.get("/lowcode/plugins", response_model=List[PluginDefinition])
async def list_available_plugins() -> List[PluginDefinition]:
    """Get list of available plugin definitions."""
    return plugin_manager.get_available_plugins()


@router.post("/lowcode/plugins/connections", response_model=Dict[str, Any])
async def create_plugin_connection(connection: PluginConnection) -> Dict[str, Any]:
    """Create and test a plugin connection.

    Example:
        POST /api/v1/automation/lowcode/plugins/connections
        {
            "plugin_id": "uuid",
            "name": "Production Salesforce",
            "configuration": {"instance_url": "https://company.salesforce.com"},
            "credentials": {"client_id": "...", "client_secret": "..."}
        }
    """
    try:
        success = await plugin_manager.create_connection(connection)

        return {
            "connection_id": str(connection.id),
            "status": "success" if success else "failed",
            "test_status": connection.test_status,
            "message": "Connection created and tested successfully" if success else "Connection test failed",
        }
    except Exception as e:
        logger.error(f"Plugin connection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lowcode/plugins/connections", response_model=List[PluginConnection])
async def list_plugin_connections() -> List[PluginConnection]:
    """Get list of active plugin connections."""
    return plugin_manager.get_active_connections()


@router.post("/lowcode/plugins/execute")
async def execute_plugin_operation(
    connection_id: UUID,
    operation: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute an operation on a plugin.

    Example:
        POST /api/v1/automation/lowcode/plugins/execute
        {
            "connection_id": "uuid",
            "operation": "send_message",
            "params": {
                "channel": "#general",
                "message": "Hello from workflow!"
            }
        }
    """
    try:
        result = await plugin_manager.execute_plugin_operation(
            connection_id, operation, params
        )

        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms,
            "timestamp": result.timestamp.isoformat(),
        }
    except Exception as e:
        logger.error(f"Plugin execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

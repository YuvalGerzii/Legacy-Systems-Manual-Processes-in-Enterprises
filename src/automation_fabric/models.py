"""Data models for Enterprise Automation Fabric."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ActionType(str, Enum):
    """Types of automation actions."""

    CLICK = "click"
    TYPE = "type"
    READ = "read"
    NAVIGATE = "navigate"
    WAIT = "wait"
    EXTRACT = "extract"
    VALIDATE = "validate"
    API_CALL = "api_call"


class AutomationAction(BaseModel):
    """Single automation action."""

    action_type: ActionType
    target: str
    value: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    """Workflow definition."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    actions: List[AutomationAction]
    frequency: Optional[str] = None  # cron expression
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowExecution(BaseModel):
    """Workflow execution record."""

    id: UUID = Field(default_factory=uuid4)
    workflow_id: UUID
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    logs: List[str] = Field(default_factory=list)


class PatternRecognitionResult(BaseModel):
    """Result of pattern recognition analysis."""

    pattern_id: UUID = Field(default_factory=uuid4)
    pattern_name: str
    frequency: int
    confidence: float
    suggested_workflow: WorkflowDefinition
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class APIEmulationConfig(BaseModel):
    """Configuration for API emulation."""

    system_id: str
    base_url: str
    authentication: Dict[str, Any]
    endpoints: List[Dict[str, Any]]
    rate_limit: Optional[int] = None
    timeout: int = 30


# ============================================================================
# LOW-CODE WORKFLOW PLATFORM MODELS
# ============================================================================


class NodeType(str, Enum):
    """Types of workflow nodes for drag-and-drop designer."""

    # Trigger Nodes
    MANUAL_TRIGGER = "manual_trigger"
    SCHEDULE_TRIGGER = "schedule_trigger"
    WEBHOOK_TRIGGER = "webhook_trigger"
    EMAIL_TRIGGER = "email_trigger"
    FILE_TRIGGER = "file_trigger"

    # Action Nodes
    HTTP_REQUEST = "http_request"
    EMAIL_SEND = "email_send"
    DATABASE_QUERY = "database_query"
    FILE_OPERATION = "file_operation"
    NOTIFICATION = "notification"
    DATA_TRANSFORM = "data_transform"

    # Logic Nodes
    CONDITION = "condition"
    LOOP = "loop"
    SWITCH = "switch"
    DELAY = "delay"

    # Integration Nodes
    SALESFORCE = "salesforce"
    SAP = "sap"
    ORACLE = "oracle"
    SHAREPOINT = "sharepoint"
    SLACK = "slack"
    TEAMS = "teams"

    # AI Nodes
    AI_APPROVAL = "ai_approval"
    AI_CLASSIFICATION = "ai_classification"
    AI_EXTRACTION = "ai_extraction"
    AI_GENERATION = "ai_generation"

    # Human-in-the-Loop Nodes
    HUMAN_APPROVAL = "human_approval"
    HUMAN_INPUT = "human_input"
    HUMAN_REVIEW = "human_review"

    # End Nodes
    SUCCESS = "success"
    FAILURE = "failure"


class NodeCategory(str, Enum):
    """Categories for organizing nodes."""

    TRIGGERS = "triggers"
    ACTIONS = "actions"
    LOGIC = "logic"
    INTEGRATIONS = "integrations"
    AI = "ai"
    HUMAN = "human"
    OUTPUTS = "outputs"


class LowCodeNode(BaseModel):
    """Visual workflow node for drag-and-drop designer."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: NodeType
    category: NodeCategory
    label: str
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    icon: Optional[str] = None
    color: Optional[str] = None
    is_enabled: bool = True


class LowCodeConnection(BaseModel):
    """Connection between workflow nodes."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    source_node_id: str
    target_node_id: str
    source_output: str = "default"
    target_input: str = "default"
    condition: Optional[str] = None
    label: Optional[str] = None


class WorkflowTemplate(BaseModel):
    """Pre-built workflow template for common use cases."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    category: str
    industry: Optional[str] = None
    use_case: str
    tags: List[str] = Field(default_factory=list)
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    estimated_time_minutes: int = 30
    nodes: List[LowCodeNode]
    connections: List[LowCodeConnection]
    configuration_steps: List[str] = Field(default_factory=list)
    required_integrations: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    author: str = "Enterprise AI Suite"
    downloads: int = 0
    rating: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LowCodeWorkflow(BaseModel):
    """Complete low-code workflow definition."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    nodes: List[LowCodeNode]
    connections: List[LowCodeConnection]
    variables: Dict[str, Any] = Field(default_factory=dict)
    is_template: bool = False
    template_id: Optional[UUID] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    enabled: bool = True
    owner: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_executed_at: Optional[datetime] = None
    execution_count: int = 0


class WorkflowValidationResult(BaseModel):
    """Result of workflow validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class PluginDefinition(BaseModel):
    """Plugin for integrating with existing systems."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    system_type: str
    version: str
    authentication_type: str  # oauth2, api_key, basic, custom
    endpoints: List[Dict[str, Any]]
    configuration_schema: Dict[str, Any]
    icon_url: Optional[str] = None
    documentation_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PluginConnection(BaseModel):
    """Configured connection to an external system."""

    id: UUID = Field(default_factory=uuid4)
    plugin_id: UUID
    name: str
    configuration: Dict[str, Any]
    credentials: Dict[str, str]  # Should be encrypted in production
    test_status: str = "pending"  # pending, success, failed
    last_tested_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

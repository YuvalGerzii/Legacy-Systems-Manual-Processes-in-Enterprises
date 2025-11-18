"""Node Library for Low-Code Workflow Platform.

This module provides pre-configured node definitions for the drag-and-drop
workflow designer, making it easy for SMEs to build workflows visually.
"""

from typing import Dict, List, Any
from .models import NodeType, NodeCategory


class NodeLibrary:
    """Library of pre-configured workflow nodes for drag-and-drop designer."""

    @staticmethod
    def get_all_nodes() -> List[Dict[str, Any]]:
        """Get all available node definitions.

        Returns:
            List of node definitions with metadata

        Example:
            >>> library = NodeLibrary()
            >>> nodes = library.get_all_nodes()
            >>> for node in nodes:
            ...     print(f"{node['label']}: {node['description']}")
        """
        return [
            # ============================================================
            # TRIGGER NODES
            # ============================================================
            {
                "type": NodeType.MANUAL_TRIGGER,
                "category": NodeCategory.TRIGGERS,
                "label": "Manual Trigger",
                "description": "Start workflow manually via button click",
                "icon": "play_circle",
                "color": "#4CAF50",
                "inputs": [],
                "outputs": ["default"],
                "config_schema": {
                    "button_label": {
                        "type": "string",
                        "default": "Start Workflow",
                        "description": "Label for the trigger button",
                    }
                },
            },
            {
                "type": NodeType.SCHEDULE_TRIGGER,
                "category": NodeCategory.TRIGGERS,
                "label": "Schedule Trigger",
                "description": "Start workflow on a schedule (cron)",
                "icon": "schedule",
                "color": "#4CAF50",
                "inputs": [],
                "outputs": ["default"],
                "config_schema": {
                    "cron_expression": {
                        "type": "string",
                        "required": True,
                        "description": "Cron expression (e.g., '0 9 * * 1-5' for weekdays at 9am)",
                    },
                    "timezone": {
                        "type": "string",
                        "default": "UTC",
                        "description": "Timezone for schedule",
                    },
                },
            },
            {
                "type": NodeType.WEBHOOK_TRIGGER,
                "category": NodeCategory.TRIGGERS,
                "label": "Webhook Trigger",
                "description": "Start workflow when webhook receives data",
                "icon": "webhook",
                "color": "#4CAF50",
                "inputs": [],
                "outputs": ["default"],
                "config_schema": {
                    "webhook_url": {
                        "type": "string",
                        "readonly": True,
                        "description": "Auto-generated webhook URL",
                    },
                    "authentication": {
                        "type": "select",
                        "options": ["none", "api_key", "oauth2"],
                        "default": "api_key",
                    },
                },
            },
            {
                "type": NodeType.EMAIL_TRIGGER,
                "category": NodeCategory.TRIGGERS,
                "label": "Email Trigger",
                "description": "Start workflow when email is received",
                "icon": "email",
                "color": "#4CAF50",
                "inputs": [],
                "outputs": ["default"],
                "config_schema": {
                    "email_address": {
                        "type": "string",
                        "required": True,
                        "description": "Email address to monitor",
                    },
                    "filter_from": {
                        "type": "string",
                        "description": "Filter by sender email",
                    },
                    "filter_subject": {
                        "type": "string",
                        "description": "Filter by subject keywords",
                    },
                },
            },
            {
                "type": NodeType.FILE_TRIGGER,
                "category": NodeCategory.TRIGGERS,
                "label": "File Trigger",
                "description": "Start workflow when file is added/modified",
                "icon": "folder",
                "color": "#4CAF50",
                "inputs": [],
                "outputs": ["default"],
                "config_schema": {
                    "watch_path": {
                        "type": "string",
                        "required": True,
                        "description": "Path to watch for files",
                    },
                    "file_pattern": {
                        "type": "string",
                        "default": "*.*",
                        "description": "File pattern to match (e.g., '*.pdf')",
                    },
                    "event": {
                        "type": "select",
                        "options": ["created", "modified", "deleted"],
                        "default": "created",
                    },
                },
            },
            # ============================================================
            # ACTION NODES
            # ============================================================
            {
                "type": NodeType.HTTP_REQUEST,
                "category": NodeCategory.ACTIONS,
                "label": "HTTP Request",
                "description": "Make HTTP/REST API call",
                "icon": "http",
                "color": "#2196F3",
                "inputs": ["default"],
                "outputs": ["success", "error"],
                "config_schema": {
                    "method": {
                        "type": "select",
                        "options": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                        "required": True,
                    },
                    "url": {
                        "type": "string",
                        "required": True,
                        "description": "API endpoint URL",
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers",
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body (for POST/PUT)",
                    },
                },
            },
            {
                "type": NodeType.EMAIL_SEND,
                "category": NodeCategory.ACTIONS,
                "label": "Send Email",
                "description": "Send email notification",
                "icon": "send",
                "color": "#2196F3",
                "inputs": ["default"],
                "outputs": ["sent", "failed"],
                "config_schema": {
                    "to": {
                        "type": "string",
                        "required": True,
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "required": True,
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "text",
                        "required": True,
                        "description": "Email body (supports templates)",
                    },
                    "attachments": {
                        "type": "array",
                        "description": "File attachments",
                    },
                },
            },
            {
                "type": NodeType.DATABASE_QUERY,
                "category": NodeCategory.ACTIONS,
                "label": "Database Query",
                "description": "Query or update database",
                "icon": "storage",
                "color": "#2196F3",
                "inputs": ["default"],
                "outputs": ["success", "error"],
                "config_schema": {
                    "connection": {
                        "type": "select",
                        "required": True,
                        "description": "Database connection",
                    },
                    "query_type": {
                        "type": "select",
                        "options": ["SELECT", "INSERT", "UPDATE", "DELETE"],
                        "required": True,
                    },
                    "query": {
                        "type": "text",
                        "required": True,
                        "description": "SQL query",
                    },
                },
            },
            {
                "type": NodeType.FILE_OPERATION,
                "category": NodeCategory.ACTIONS,
                "label": "File Operation",
                "description": "Read, write, or move files",
                "icon": "file_copy",
                "color": "#2196F3",
                "inputs": ["default"],
                "outputs": ["success", "error"],
                "config_schema": {
                    "operation": {
                        "type": "select",
                        "options": ["read", "write", "move", "copy", "delete"],
                        "required": True,
                    },
                    "path": {
                        "type": "string",
                        "required": True,
                        "description": "File path",
                    },
                    "content": {
                        "type": "text",
                        "description": "Content for write operation",
                    },
                },
            },
            {
                "type": NodeType.NOTIFICATION,
                "category": NodeCategory.ACTIONS,
                "label": "Send Notification",
                "description": "Send notification to users",
                "icon": "notifications",
                "color": "#2196F3",
                "inputs": ["default"],
                "outputs": ["default"],
                "config_schema": {
                    "channel": {
                        "type": "select",
                        "options": ["email", "slack", "teams", "sms", "push"],
                        "required": True,
                    },
                    "recipient": {
                        "type": "string",
                        "required": True,
                        "description": "Recipient identifier",
                    },
                    "message": {
                        "type": "text",
                        "required": True,
                        "description": "Notification message",
                    },
                },
            },
            {
                "type": NodeType.DATA_TRANSFORM,
                "category": NodeCategory.ACTIONS,
                "label": "Transform Data",
                "description": "Transform or map data",
                "icon": "transform",
                "color": "#2196F3",
                "inputs": ["default"],
                "outputs": ["default"],
                "config_schema": {
                    "transformation": {
                        "type": "text",
                        "required": True,
                        "description": "Transformation logic (JavaScript/Python)",
                    },
                    "input_schema": {
                        "type": "object",
                        "description": "Expected input schema",
                    },
                },
            },
            # ============================================================
            # LOGIC NODES
            # ============================================================
            {
                "type": NodeType.CONDITION,
                "category": NodeCategory.LOGIC,
                "label": "Condition (If/Else)",
                "description": "Branch based on condition",
                "icon": "alt_route",
                "color": "#FF9800",
                "inputs": ["default"],
                "outputs": ["true", "false"],
                "config_schema": {
                    "condition": {
                        "type": "text",
                        "required": True,
                        "description": "Condition expression (e.g., amount > 1000)",
                    },
                    "operator": {
                        "type": "select",
                        "options": [
                            "equals",
                            "not_equals",
                            "greater_than",
                            "less_than",
                            "contains",
                            "regex",
                        ],
                    },
                },
            },
            {
                "type": NodeType.LOOP,
                "category": NodeCategory.LOGIC,
                "label": "Loop",
                "description": "Repeat actions for each item",
                "icon": "loop",
                "color": "#FF9800",
                "inputs": ["default"],
                "outputs": ["item", "complete"],
                "config_schema": {
                    "items": {
                        "type": "array",
                        "required": True,
                        "description": "Items to loop over",
                    },
                    "max_iterations": {
                        "type": "number",
                        "default": 100,
                        "description": "Maximum iterations",
                    },
                },
            },
            {
                "type": NodeType.SWITCH,
                "category": NodeCategory.LOGIC,
                "label": "Switch",
                "description": "Multi-way branch (case statement)",
                "icon": "call_split",
                "color": "#FF9800",
                "inputs": ["default"],
                "outputs": ["case1", "case2", "case3", "default"],
                "config_schema": {
                    "variable": {
                        "type": "string",
                        "required": True,
                        "description": "Variable to switch on",
                    },
                    "cases": {
                        "type": "array",
                        "description": "Case values",
                    },
                },
            },
            {
                "type": NodeType.DELAY,
                "category": NodeCategory.LOGIC,
                "label": "Delay",
                "description": "Wait for specified time",
                "icon": "schedule",
                "color": "#FF9800",
                "inputs": ["default"],
                "outputs": ["default"],
                "config_schema": {
                    "duration": {
                        "type": "number",
                        "required": True,
                        "description": "Duration in seconds",
                    },
                    "unit": {
                        "type": "select",
                        "options": ["seconds", "minutes", "hours", "days"],
                        "default": "seconds",
                    },
                },
            },
            # ============================================================
            # AI NODES
            # ============================================================
            {
                "type": NodeType.AI_APPROVAL,
                "category": NodeCategory.AI,
                "label": "AI Approval Assistant",
                "description": "AI reviews and approves/rejects requests",
                "icon": "smart_toy",
                "color": "#9C27B0",
                "inputs": ["default"],
                "outputs": ["approved", "rejected", "escalate"],
                "config_schema": {
                    "threshold": {
                        "type": "number",
                        "default": 0.8,
                        "min": 0,
                        "max": 1,
                        "description": "Confidence threshold for auto-approval",
                    },
                    "criteria": {
                        "type": "text",
                        "required": True,
                        "description": "Approval criteria in natural language",
                    },
                    "escalation_rules": {
                        "type": "object",
                        "description": "Rules for human escalation",
                    },
                    "model": {
                        "type": "select",
                        "options": ["llama3.2:3b", "mistral:7b", "qwen2.5:14b"],
                        "default": "llama3.2:3b",
                    },
                },
            },
            {
                "type": NodeType.AI_CLASSIFICATION,
                "category": NodeCategory.AI,
                "label": "AI Classification",
                "description": "Classify data using AI",
                "icon": "category",
                "color": "#9C27B0",
                "inputs": ["default"],
                "outputs": ["classified"],
                "config_schema": {
                    "categories": {
                        "type": "array",
                        "required": True,
                        "description": "List of categories",
                    },
                    "input_field": {
                        "type": "string",
                        "required": True,
                        "description": "Field to classify",
                    },
                },
            },
            {
                "type": NodeType.AI_EXTRACTION,
                "category": NodeCategory.AI,
                "label": "AI Data Extraction",
                "description": "Extract structured data from text",
                "icon": "text_fields",
                "color": "#9C27B0",
                "inputs": ["default"],
                "outputs": ["extracted"],
                "config_schema": {
                    "fields_to_extract": {
                        "type": "array",
                        "required": True,
                        "description": "Fields to extract (e.g., invoice_number, date, amount)",
                    },
                    "source_field": {
                        "type": "string",
                        "required": True,
                        "description": "Source text field",
                    },
                },
            },
            {
                "type": NodeType.AI_GENERATION,
                "category": NodeCategory.AI,
                "label": "AI Content Generation",
                "description": "Generate text content using AI",
                "icon": "auto_awesome",
                "color": "#9C27B0",
                "inputs": ["default"],
                "outputs": ["generated"],
                "config_schema": {
                    "prompt": {
                        "type": "text",
                        "required": True,
                        "description": "Generation prompt",
                    },
                    "max_tokens": {
                        "type": "number",
                        "default": 500,
                        "description": "Maximum output length",
                    },
                },
            },
            # ============================================================
            # HUMAN-IN-THE-LOOP NODES
            # ============================================================
            {
                "type": NodeType.HUMAN_APPROVAL,
                "category": NodeCategory.HUMAN,
                "label": "Human Approval",
                "description": "Request human approval",
                "icon": "how_to_reg",
                "color": "#795548",
                "inputs": ["default"],
                "outputs": ["approved", "rejected"],
                "config_schema": {
                    "approver": {
                        "type": "string",
                        "required": True,
                        "description": "Approver email or role",
                    },
                    "message": {
                        "type": "text",
                        "required": True,
                        "description": "Approval request message",
                    },
                    "timeout_hours": {
                        "type": "number",
                        "default": 24,
                        "description": "Hours before timeout",
                    },
                },
            },
            {
                "type": NodeType.HUMAN_INPUT,
                "category": NodeCategory.HUMAN,
                "label": "Human Input",
                "description": "Request human input/data",
                "icon": "input",
                "color": "#795548",
                "inputs": ["default"],
                "outputs": ["submitted"],
                "config_schema": {
                    "fields": {
                        "type": "array",
                        "required": True,
                        "description": "Fields to collect",
                    },
                    "assignee": {
                        "type": "string",
                        "required": True,
                        "description": "Person to provide input",
                    },
                },
            },
            {
                "type": NodeType.HUMAN_REVIEW,
                "category": NodeCategory.HUMAN,
                "label": "Human Review",
                "description": "Request human review/verification",
                "icon": "fact_check",
                "color": "#795548",
                "inputs": ["default"],
                "outputs": ["verified", "corrections_needed"],
                "config_schema": {
                    "reviewer": {
                        "type": "string",
                        "required": True,
                        "description": "Reviewer email or role",
                    },
                    "checklist": {
                        "type": "array",
                        "description": "Review checklist items",
                    },
                },
            },
            # ============================================================
            # INTEGRATION NODES
            # ============================================================
            {
                "type": NodeType.SALESFORCE,
                "category": NodeCategory.INTEGRATIONS,
                "label": "Salesforce",
                "description": "Integrate with Salesforce CRM",
                "icon": "cloud",
                "color": "#00A1E0",
                "inputs": ["default"],
                "outputs": ["success", "error"],
                "config_schema": {
                    "operation": {
                        "type": "select",
                        "options": [
                            "create_record",
                            "update_record",
                            "query",
                            "delete_record",
                        ],
                        "required": True,
                    },
                    "object_type": {
                        "type": "string",
                        "required": True,
                        "description": "Salesforce object (e.g., Account, Lead)",
                    },
                },
            },
            {
                "type": NodeType.SAP,
                "category": NodeCategory.INTEGRATIONS,
                "label": "SAP",
                "description": "Integrate with SAP ERP",
                "icon": "account_balance",
                "color": "#0FAAFF",
                "inputs": ["default"],
                "outputs": ["success", "error"],
                "config_schema": {
                    "module": {
                        "type": "select",
                        "options": ["FI", "CO", "MM", "SD", "PP"],
                        "required": True,
                    },
                    "transaction": {
                        "type": "string",
                        "required": True,
                        "description": "SAP transaction code",
                    },
                },
            },
            {
                "type": NodeType.SLACK,
                "category": NodeCategory.INTEGRATIONS,
                "label": "Slack",
                "description": "Send message to Slack channel",
                "icon": "tag",
                "color": "#4A154B",
                "inputs": ["default"],
                "outputs": ["sent"],
                "config_schema": {
                    "channel": {
                        "type": "string",
                        "required": True,
                        "description": "Slack channel name",
                    },
                    "message": {
                        "type": "text",
                        "required": True,
                        "description": "Message to send",
                    },
                },
            },
            {
                "type": NodeType.TEAMS,
                "category": NodeCategory.INTEGRATIONS,
                "label": "Microsoft Teams",
                "description": "Send message to Teams channel",
                "icon": "groups",
                "color": "#5558AF",
                "inputs": ["default"],
                "outputs": ["sent"],
                "config_schema": {
                    "team": {
                        "type": "string",
                        "required": True,
                        "description": "Team name",
                    },
                    "channel": {
                        "type": "string",
                        "required": True,
                        "description": "Channel name",
                    },
                    "message": {
                        "type": "text",
                        "required": True,
                        "description": "Message to send",
                    },
                },
            },
            # ============================================================
            # OUTPUT NODES
            # ============================================================
            {
                "type": NodeType.SUCCESS,
                "category": NodeCategory.OUTPUTS,
                "label": "Success",
                "description": "Mark workflow as successful",
                "icon": "check_circle",
                "color": "#4CAF50",
                "inputs": ["default"],
                "outputs": [],
                "config_schema": {
                    "message": {
                        "type": "text",
                        "description": "Success message",
                    }
                },
            },
            {
                "type": NodeType.FAILURE,
                "category": NodeCategory.OUTPUTS,
                "label": "Failure",
                "description": "Mark workflow as failed",
                "icon": "error",
                "color": "#F44336",
                "inputs": ["default"],
                "outputs": [],
                "config_schema": {
                    "error_message": {
                        "type": "text",
                        "description": "Error message",
                    }
                },
            },
        ]

    @staticmethod
    def get_nodes_by_category(category: NodeCategory) -> List[Dict[str, Any]]:
        """Get nodes filtered by category.

        Args:
            category: Node category to filter by

        Returns:
            List of nodes in the category

        Example:
            >>> ai_nodes = NodeLibrary.get_nodes_by_category(NodeCategory.AI)
        """
        all_nodes = NodeLibrary.get_all_nodes()
        return [n for n in all_nodes if n["category"] == category]

    @staticmethod
    def get_node_definition(node_type: NodeType) -> Dict[str, Any]:
        """Get definition for a specific node type.

        Args:
            node_type: Type of node to get definition for

        Returns:
            Node definition

        Example:
            >>> definition = NodeLibrary.get_node_definition(NodeType.AI_APPROVAL)
        """
        all_nodes = NodeLibrary.get_all_nodes()
        for node in all_nodes:
            if node["type"] == node_type:
                return node
        raise ValueError(f"Node type {node_type} not found in library")

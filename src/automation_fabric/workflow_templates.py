"""Pre-built Workflow Templates for SMEs.

This module provides ready-to-use workflow templates for common business
processes in small and medium enterprises.
"""

from typing import List
from uuid import uuid4

from .models import (
    WorkflowTemplate,
    LowCodeNode,
    LowCodeConnection,
    NodeType,
    NodeCategory,
)


class WorkflowTemplateLibrary:
    """Library of pre-built workflow templates for SMEs."""

    @staticmethod
    def get_all_templates() -> List[WorkflowTemplate]:
        """Get all available workflow templates.

        Returns:
            List of workflow templates

        Example:
            >>> templates = WorkflowTemplateLibrary.get_all_templates()
            >>> for template in templates:
            ...     print(f"{template.name}: {template.description}")
        """
        return [
            WorkflowTemplateLibrary._invoice_approval_template(),
            WorkflowTemplateLibrary._employee_onboarding_template(),
            WorkflowTemplateLibrary._expense_approval_template(),
            WorkflowTemplateLibrary._purchase_order_template(),
            WorkflowTemplateLibrary._customer_feedback_template(),
            WorkflowTemplateLibrary._leave_request_template(),
            WorkflowTemplateLibrary._document_approval_template(),
            WorkflowTemplateLibrary._lead_qualification_template(),
        ]

    @staticmethod
    def _invoice_approval_template() -> WorkflowTemplate:
        """Create invoice approval workflow template."""
        # Define nodes
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.EMAIL_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="New Invoice Email",
            description="Triggered when invoice email arrives",
            config={
                "email_address": "invoices@company.com",
                "filter_subject": "invoice",
            },
            position={"x": 100, "y": 100},
        )

        extract_data = LowCodeNode(
            id="extract_1",
            type=NodeType.AI_EXTRACTION,
            category=NodeCategory.AI,
            label="Extract Invoice Data",
            description="Extract invoice details using AI",
            config={
                "fields_to_extract": [
                    "invoice_number",
                    "vendor_name",
                    "amount",
                    "due_date",
                    "line_items",
                ],
                "source_field": "email_body",
            },
            position={"x": 300, "y": 100},
        )

        ai_approval = LowCodeNode(
            id="ai_approval_1",
            type=NodeType.AI_APPROVAL,
            category=NodeCategory.AI,
            label="AI Invoice Review",
            description="AI reviews invoice for auto-approval",
            config={
                "threshold": 0.85,
                "criteria": "Approve if amount < $5000 AND vendor is in approved list AND all required fields are present",
                "escalation_rules": {"amount_threshold": 5000},
            },
            position={"x": 500, "y": 100},
        )

        human_approval = LowCodeNode(
            id="human_approval_1",
            type=NodeType.HUMAN_APPROVAL,
            category=NodeCategory.HUMAN,
            label="Manager Approval",
            description="Manager approves high-value invoices",
            config={
                "approver": "manager@company.com",
                "message": "Please review and approve this invoice",
                "timeout_hours": 48,
            },
            position={"x": 500, "y": 250},
        )

        update_system = LowCodeNode(
            id="action_1",
            type=NodeType.DATABASE_QUERY,
            category=NodeCategory.ACTIONS,
            label="Update Accounting System",
            description="Record approved invoice in system",
            config={
                "query_type": "INSERT",
                "query": "INSERT INTO invoices (invoice_number, vendor, amount, status) VALUES (?, ?, ?, 'approved')",
            },
            position={"x": 700, "y": 100},
        )

        notify_ap = LowCodeNode(
            id="notify_1",
            type=NodeType.EMAIL_SEND,
            category=NodeCategory.ACTIONS,
            label="Notify Accounts Payable",
            description="Send notification to AP team",
            config={
                "to": "ap@company.com",
                "subject": "Invoice Approved: {{invoice_number}}",
                "body": "Invoice {{invoice_number}} for {{amount}} has been approved and is ready for payment.",
            },
            position={"x": 900, "y": 100},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="Workflow Complete",
            config={"message": "Invoice processed successfully"},
            position={"x": 1100, "y": 100},
        )

        # Define connections
        connections = [
            LowCodeConnection(
                source_node_id=trigger.id,
                target_node_id=extract_data.id,
            ),
            LowCodeConnection(
                source_node_id=extract_data.id,
                target_node_id=ai_approval.id,
            ),
            LowCodeConnection(
                source_node_id=ai_approval.id,
                target_node_id=update_system.id,
                source_output="approved",
                label="Auto-approved",
            ),
            LowCodeConnection(
                source_node_id=ai_approval.id,
                target_node_id=human_approval.id,
                source_output="escalate",
                label="Needs review",
            ),
            LowCodeConnection(
                source_node_id=human_approval.id,
                target_node_id=update_system.id,
                source_output="approved",
            ),
            LowCodeConnection(
                source_node_id=update_system.id,
                target_node_id=notify_ap.id,
            ),
            LowCodeConnection(
                source_node_id=notify_ap.id,
                target_node_id=success.id,
            ),
        ]

        return WorkflowTemplate(
            name="Invoice Approval Workflow",
            description="Automated invoice approval with AI review and escalation",
            category="Finance",
            industry="All",
            use_case="Automate invoice approval process with AI pre-screening and human escalation for high-value invoices",
            tags=["invoice", "approval", "finance", "ai", "automation"],
            difficulty="beginner",
            estimated_time_minutes=15,
            nodes=[
                trigger,
                extract_data,
                ai_approval,
                human_approval,
                update_system,
                notify_ap,
                success,
            ],
            connections=connections,
            configuration_steps=[
                "Configure email address to monitor for invoices",
                "Set AI approval threshold (default: $5,000)",
                "Specify manager email for escalations",
                "Configure database connection for accounting system",
                "Set AP team notification email",
            ],
            required_integrations=["email", "database"],
            rating=4.8,
        )

    @staticmethod
    def _employee_onboarding_template() -> WorkflowTemplate:
        """Create employee onboarding workflow template."""
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.MANUAL_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="Start Onboarding",
            config={"button_label": "Onboard New Employee"},
            position={"x": 100, "y": 100},
        )

        create_accounts = LowCodeNode(
            id="action_1",
            type=NodeType.HTTP_REQUEST,
            category=NodeCategory.ACTIONS,
            label="Create User Accounts",
            config={
                "method": "POST",
                "url": "https://api.company.com/users",
                "headers": {"Content-Type": "application/json"},
            },
            position={"x": 300, "y": 100},
        )

        send_welcome = LowCodeNode(
            id="email_1",
            type=NodeType.EMAIL_SEND,
            category=NodeCategory.ACTIONS,
            label="Send Welcome Email",
            config={
                "subject": "Welcome to the Team!",
                "body": "Welcome {{employee_name}}! Here are your login credentials and getting started guide.",
            },
            position={"x": 500, "y": 100},
        )

        assign_tasks = LowCodeNode(
            id="action_2",
            type=NodeType.DATABASE_QUERY,
            category=NodeCategory.ACTIONS,
            label="Assign Onboarding Tasks",
            config={
                "query_type": "INSERT",
                "query": "INSERT INTO onboarding_tasks (employee_id, task_list) VALUES (?, ?)",
            },
            position={"x": 700, "y": 100},
        )

        notify_team = LowCodeNode(
            id="slack_1",
            type=NodeType.SLACK,
            category=NodeCategory.INTEGRATIONS,
            label="Notify Team on Slack",
            config={
                "channel": "#general",
                "message": "Please welcome {{employee_name}} to the team!",
            },
            position={"x": 900, "y": 100},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="Onboarding Complete",
            position={"x": 1100, "y": 100},
        )

        connections = [
            LowCodeConnection(
                source_node_id=trigger.id, target_node_id=create_accounts.id
            ),
            LowCodeConnection(
                source_node_id=create_accounts.id, target_node_id=send_welcome.id
            ),
            LowCodeConnection(
                source_node_id=send_welcome.id, target_node_id=assign_tasks.id
            ),
            LowCodeConnection(
                source_node_id=assign_tasks.id, target_node_id=notify_team.id
            ),
            LowCodeConnection(
                source_node_id=notify_team.id, target_node_id=success.id
            ),
        ]

        return WorkflowTemplate(
            name="Employee Onboarding",
            description="Streamlined employee onboarding workflow",
            category="HR",
            industry="All",
            use_case="Automate employee onboarding process including account creation, welcome emails, and task assignment",
            tags=["hr", "onboarding", "employee", "automation"],
            difficulty="beginner",
            estimated_time_minutes=20,
            nodes=[
                trigger,
                create_accounts,
                send_welcome,
                assign_tasks,
                notify_team,
                success,
            ],
            connections=connections,
            configuration_steps=[
                "Configure user account creation API",
                "Customize welcome email template",
                "Define onboarding task checklist",
                "Set Slack channel for announcements",
            ],
            required_integrations=["api", "email", "slack"],
            rating=4.7,
        )

    @staticmethod
    def _expense_approval_template() -> WorkflowTemplate:
        """Create expense approval workflow template."""
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.WEBHOOK_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="Expense Submitted",
            position={"x": 100, "y": 100},
        )

        validate_expense = LowCodeNode(
            id="condition_1",
            type=NodeType.CONDITION,
            category=NodeCategory.LOGIC,
            label="Validate Amount",
            config={"condition": "amount <= 500", "operator": "less_than"},
            position={"x": 300, "y": 100},
        )

        ai_check = LowCodeNode(
            id="ai_1",
            type=NodeType.AI_APPROVAL,
            category=NodeCategory.AI,
            label="AI Expense Review",
            config={
                "threshold": 0.9,
                "criteria": "Approve if expense is within policy, has receipt, and category is valid",
            },
            position={"x": 500, "y": 50},
        )

        manager_approval = LowCodeNode(
            id="human_1",
            type=NodeType.HUMAN_APPROVAL,
            category=NodeCategory.HUMAN,
            label="Manager Approval",
            config={"approver": "manager@company.com"},
            position={"x": 500, "y": 200},
        )

        process_payment = LowCodeNode(
            id="action_1",
            type=NodeType.HTTP_REQUEST,
            category=NodeCategory.ACTIONS,
            label="Process Reimbursement",
            config={"method": "POST", "url": "https://api.payroll.com/reimburse"},
            position={"x": 700, "y": 100},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="Approved",
            position={"x": 900, "y": 100},
        )

        connections = [
            LowCodeConnection(
                source_node_id=trigger.id, target_node_id=validate_expense.id
            ),
            LowCodeConnection(
                source_node_id=validate_expense.id,
                target_node_id=ai_check.id,
                source_output="true",
                label="Low amount",
            ),
            LowCodeConnection(
                source_node_id=validate_expense.id,
                target_node_id=manager_approval.id,
                source_output="false",
                label="High amount",
            ),
            LowCodeConnection(
                source_node_id=ai_check.id,
                target_node_id=process_payment.id,
                source_output="approved",
            ),
            LowCodeConnection(
                source_node_id=manager_approval.id,
                target_node_id=process_payment.id,
                source_output="approved",
            ),
            LowCodeConnection(
                source_node_id=process_payment.id, target_node_id=success.id
            ),
        ]

        return WorkflowTemplate(
            name="Expense Approval",
            description="Smart expense approval with AI validation",
            category="Finance",
            industry="All",
            use_case="Automate expense approval with AI validation for low amounts and manager approval for high amounts",
            tags=["expense", "approval", "finance", "ai"],
            difficulty="intermediate",
            estimated_time_minutes=25,
            nodes=[
                trigger,
                validate_expense,
                ai_check,
                manager_approval,
                process_payment,
                success,
            ],
            connections=connections,
            configuration_steps=[
                "Set expense amount threshold ($500)",
                "Configure AI approval criteria",
                "Set manager for high-value approvals",
                "Connect to payroll system API",
            ],
            required_integrations=["webhook", "api"],
            rating=4.6,
        )

    @staticmethod
    def _purchase_order_template() -> WorkflowTemplate:
        """Create purchase order workflow template."""
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.MANUAL_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="New Purchase Request",
            position={"x": 100, "y": 100},
        )

        check_budget = LowCodeNode(
            id="db_1",
            type=NodeType.DATABASE_QUERY,
            category=NodeCategory.ACTIONS,
            label="Check Budget",
            config={"query_type": "SELECT"},
            position={"x": 300, "y": 100},
        )

        budget_available = LowCodeNode(
            id="condition_1",
            type=NodeType.CONDITION,
            category=NodeCategory.LOGIC,
            label="Budget Available?",
            config={"condition": "budget_remaining > requested_amount"},
            position={"x": 500, "y": 100},
        )

        create_po = LowCodeNode(
            id="action_1",
            type=NodeType.HTTP_REQUEST,
            category=NodeCategory.ACTIONS,
            label="Create Purchase Order",
            config={"method": "POST", "url": "https://api.erp.com/purchase-orders"},
            position={"x": 700, "y": 50},
        )

        notify_vendor = LowCodeNode(
            id="email_1",
            type=NodeType.EMAIL_SEND,
            category=NodeCategory.ACTIONS,
            label="Send PO to Vendor",
            position={"x": 900, "y": 50},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="PO Created",
            position={"x": 1100, "y": 50},
        )

        reject = LowCodeNode(
            id="failure_1",
            type=NodeType.FAILURE,
            category=NodeCategory.OUTPUTS,
            label="Insufficient Budget",
            position={"x": 700, "y": 200},
        )

        connections = [
            LowCodeConnection(
                source_node_id=trigger.id, target_node_id=check_budget.id
            ),
            LowCodeConnection(
                source_node_id=check_budget.id, target_node_id=budget_available.id
            ),
            LowCodeConnection(
                source_node_id=budget_available.id,
                target_node_id=create_po.id,
                source_output="true",
            ),
            LowCodeConnection(
                source_node_id=budget_available.id,
                target_node_id=reject.id,
                source_output="false",
            ),
            LowCodeConnection(
                source_node_id=create_po.id, target_node_id=notify_vendor.id
            ),
            LowCodeConnection(
                source_node_id=notify_vendor.id, target_node_id=success.id
            ),
        ]

        return WorkflowTemplate(
            name="Purchase Order Processing",
            description="Automated purchase order creation with budget validation",
            category="Procurement",
            industry="All",
            use_case="Streamline purchase order creation with automatic budget checking and vendor notification",
            tags=["purchase", "procurement", "budget", "automation"],
            difficulty="intermediate",
            estimated_time_minutes=30,
            nodes=[
                trigger,
                check_budget,
                budget_available,
                create_po,
                notify_vendor,
                success,
                reject,
            ],
            connections=connections,
            configuration_steps=[
                "Connect to budget/finance database",
                "Configure ERP system API",
                "Set vendor email templates",
            ],
            required_integrations=["database", "api", "email"],
            rating=4.5,
        )

    @staticmethod
    def _customer_feedback_template() -> WorkflowTemplate:
        """Create customer feedback processing workflow."""
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.WEBHOOK_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="Feedback Received",
            position={"x": 100, "y": 100},
        )

        classify = LowCodeNode(
            id="ai_1",
            type=NodeType.AI_CLASSIFICATION,
            category=NodeCategory.AI,
            label="Classify Sentiment",
            config={
                "categories": ["positive", "neutral", "negative", "urgent"],
                "input_field": "feedback_text",
            },
            position={"x": 300, "y": 100},
        )

        route = LowCodeNode(
            id="switch_1",
            type=NodeType.SWITCH,
            category=NodeCategory.LOGIC,
            label="Route by Sentiment",
            config={"variable": "sentiment"},
            position={"x": 500, "y": 100},
        )

        escalate = LowCodeNode(
            id="action_1",
            type=NodeType.SLACK,
            category=NodeCategory.INTEGRATIONS,
            label="Alert Support Team",
            config={"channel": "#customer-support"},
            position={"x": 700, "y": 50},
        )

        thank_you = LowCodeNode(
            id="email_1",
            type=NodeType.EMAIL_SEND,
            category=NodeCategory.ACTIONS,
            label="Send Thank You",
            position={"x": 700, "y": 200},
        )

        save = LowCodeNode(
            id="db_1",
            type=NodeType.DATABASE_QUERY,
            category=NodeCategory.ACTIONS,
            label="Save to CRM",
            position={"x": 900, "y": 100},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="Processed",
            position={"x": 1100, "y": 100},
        )

        connections = [
            LowCodeConnection(source_node_id=trigger.id, target_node_id=classify.id),
            LowCodeConnection(source_node_id=classify.id, target_node_id=route.id),
            LowCodeConnection(
                source_node_id=route.id,
                target_node_id=escalate.id,
                source_output="case1",
                label="Negative/Urgent",
            ),
            LowCodeConnection(
                source_node_id=route.id,
                target_node_id=thank_you.id,
                source_output="case2",
                label="Positive",
            ),
            LowCodeConnection(source_node_id=escalate.id, target_node_id=save.id),
            LowCodeConnection(source_node_id=thank_you.id, target_node_id=save.id),
            LowCodeConnection(source_node_id=save.id, target_node_id=success.id),
        ]

        return WorkflowTemplate(
            name="Customer Feedback Processing",
            description="AI-powered customer feedback routing and response",
            category="Customer Service",
            industry="All",
            use_case="Automatically classify and route customer feedback with AI sentiment analysis",
            tags=["customer", "feedback", "ai", "sentiment", "support"],
            difficulty="intermediate",
            estimated_time_minutes=20,
            nodes=[trigger, classify, route, escalate, thank_you, save, success],
            connections=connections,
            configuration_steps=[
                "Configure feedback webhook URL",
                "Set Slack channel for escalations",
                "Customize thank you email template",
                "Connect to CRM database",
            ],
            required_integrations=["webhook", "slack", "database", "email"],
            rating=4.7,
        )

    @staticmethod
    def _leave_request_template() -> WorkflowTemplate:
        """Create leave request approval workflow."""
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.MANUAL_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="Submit Leave Request",
            position={"x": 100, "y": 100},
        )

        check_balance = LowCodeNode(
            id="db_1",
            type=NodeType.DATABASE_QUERY,
            category=NodeCategory.ACTIONS,
            label="Check Leave Balance",
            position={"x": 300, "y": 100},
        )

        manager_approval = LowCodeNode(
            id="human_1",
            type=NodeType.HUMAN_APPROVAL,
            category=NodeCategory.HUMAN,
            label="Manager Approval",
            position={"x": 500, "y": 100},
        )

        update_calendar = LowCodeNode(
            id="action_1",
            type=NodeType.HTTP_REQUEST,
            category=NodeCategory.ACTIONS,
            label="Update Calendar",
            config={"method": "POST", "url": "https://api.calendar.com/events"},
            position={"x": 700, "y": 100},
        )

        notify_team = LowCodeNode(
            id="email_1",
            type=NodeType.EMAIL_SEND,
            category=NodeCategory.ACTIONS,
            label="Notify Team",
            position={"x": 900, "y": 100},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="Leave Approved",
            position={"x": 1100, "y": 100},
        )

        connections = [
            LowCodeConnection(
                source_node_id=trigger.id, target_node_id=check_balance.id
            ),
            LowCodeConnection(
                source_node_id=check_balance.id, target_node_id=manager_approval.id
            ),
            LowCodeConnection(
                source_node_id=manager_approval.id,
                target_node_id=update_calendar.id,
                source_output="approved",
            ),
            LowCodeConnection(
                source_node_id=update_calendar.id, target_node_id=notify_team.id
            ),
            LowCodeConnection(
                source_node_id=notify_team.id, target_node_id=success.id
            ),
        ]

        return WorkflowTemplate(
            name="Leave Request Approval",
            description="Streamlined leave request and approval process",
            category="HR",
            industry="All",
            use_case="Automate leave request approval with balance checking and team notification",
            tags=["hr", "leave", "approval", "vacation"],
            difficulty="beginner",
            estimated_time_minutes=15,
            nodes=[
                trigger,
                check_balance,
                manager_approval,
                update_calendar,
                notify_team,
                success,
            ],
            connections=connections,
            configuration_steps=[
                "Connect to HR database for leave balances",
                "Set manager approval email",
                "Configure calendar integration",
                "Set team notification distribution list",
            ],
            required_integrations=["database", "api", "email"],
            rating=4.6,
        )

    @staticmethod
    def _document_approval_template() -> WorkflowTemplate:
        """Create document approval workflow."""
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.FILE_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="Document Uploaded",
            position={"x": 100, "y": 100},
        )

        ai_review = LowCodeNode(
            id="ai_1",
            type=NodeType.AI_CLASSIFICATION,
            category=NodeCategory.AI,
            label="AI Document Review",
            config={"categories": ["contract", "invoice", "report", "other"]},
            position={"x": 300, "y": 100},
        )

        human_review = LowCodeNode(
            id="human_1",
            type=NodeType.HUMAN_REVIEW,
            category=NodeCategory.HUMAN,
            label="Legal Review",
            position={"x": 500, "y": 100},
        )

        final_approval = LowCodeNode(
            id="human_2",
            type=NodeType.HUMAN_APPROVAL,
            category=NodeCategory.HUMAN,
            label="Executive Approval",
            position={"x": 700, "y": 100},
        )

        archive = LowCodeNode(
            id="action_1",
            type=NodeType.FILE_OPERATION,
            category=NodeCategory.ACTIONS,
            label="Archive Document",
            config={"operation": "move"},
            position={"x": 900, "y": 100},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="Approved",
            position={"x": 1100, "y": 100},
        )

        connections = [
            LowCodeConnection(source_node_id=trigger.id, target_node_id=ai_review.id),
            LowCodeConnection(
                source_node_id=ai_review.id, target_node_id=human_review.id
            ),
            LowCodeConnection(
                source_node_id=human_review.id,
                target_node_id=final_approval.id,
                source_output="verified",
            ),
            LowCodeConnection(
                source_node_id=final_approval.id,
                target_node_id=archive.id,
                source_output="approved",
            ),
            LowCodeConnection(source_node_id=archive.id, target_node_id=success.id),
        ]

        return WorkflowTemplate(
            name="Document Approval",
            description="Multi-stage document review and approval",
            category="Legal",
            industry="All",
            use_case="Automate document approval with AI classification and multi-level human review",
            tags=["document", "approval", "legal", "compliance"],
            difficulty="intermediate",
            estimated_time_minutes=25,
            nodes=[
                trigger,
                ai_review,
                human_review,
                final_approval,
                archive,
                success,
            ],
            connections=connections,
            configuration_steps=[
                "Set folder to monitor for documents",
                "Configure AI document classification",
                "Set legal reviewer email",
                "Set executive approver email",
                "Configure document archive location",
            ],
            required_integrations=["file_system"],
            rating=4.5,
        )

    @staticmethod
    def _lead_qualification_template() -> WorkflowTemplate:
        """Create lead qualification workflow."""
        trigger = LowCodeNode(
            id="trigger_1",
            type=NodeType.WEBHOOK_TRIGGER,
            category=NodeCategory.TRIGGERS,
            label="New Lead Captured",
            position={"x": 100, "y": 100},
        )

        enrich_data = LowCodeNode(
            id="action_1",
            type=NodeType.HTTP_REQUEST,
            category=NodeCategory.ACTIONS,
            label="Enrich Lead Data",
            config={"method": "POST", "url": "https://api.clearbit.com/enrich"},
            position={"x": 300, "y": 100},
        )

        ai_score = LowCodeNode(
            id="ai_1",
            type=NodeType.AI_CLASSIFICATION,
            category=NodeCategory.AI,
            label="AI Lead Scoring",
            config={
                "categories": ["hot", "warm", "cold"],
                "input_field": "lead_data",
            },
            position={"x": 500, "y": 100},
        )

        route_lead = LowCodeNode(
            id="switch_1",
            type=NodeType.SWITCH,
            category=NodeCategory.LOGIC,
            label="Route Lead",
            position={"x": 700, "y": 100},
        )

        assign_sales = LowCodeNode(
            id="salesforce_1",
            type=NodeType.SALESFORCE,
            category=NodeCategory.INTEGRATIONS,
            label="Create Opportunity",
            config={"operation": "create_record", "object_type": "Opportunity"},
            position={"x": 900, "y": 50},
        )

        nurture = LowCodeNode(
            id="email_1",
            type=NodeType.EMAIL_SEND,
            category=NodeCategory.ACTIONS,
            label="Add to Nurture Campaign",
            position={"x": 900, "y": 200},
        )

        success = LowCodeNode(
            id="success_1",
            type=NodeType.SUCCESS,
            category=NodeCategory.OUTPUTS,
            label="Lead Processed",
            position={"x": 1100, "y": 100},
        )

        connections = [
            LowCodeConnection(
                source_node_id=trigger.id, target_node_id=enrich_data.id
            ),
            LowCodeConnection(
                source_node_id=enrich_data.id, target_node_id=ai_score.id
            ),
            LowCodeConnection(
                source_node_id=ai_score.id, target_node_id=route_lead.id
            ),
            LowCodeConnection(
                source_node_id=route_lead.id,
                target_node_id=assign_sales.id,
                source_output="case1",
                label="Hot Lead",
            ),
            LowCodeConnection(
                source_node_id=route_lead.id,
                target_node_id=nurture.id,
                source_output="case2",
                label="Warm/Cold",
            ),
            LowCodeConnection(
                source_node_id=assign_sales.id, target_node_id=success.id
            ),
            LowCodeConnection(source_node_id=nurture.id, target_node_id=success.id),
        ]

        return WorkflowTemplate(
            name="Lead Qualification & Routing",
            description="AI-powered lead qualification and automatic routing",
            category="Sales",
            industry="All",
            use_case="Automatically qualify and route leads with AI scoring and data enrichment",
            tags=["sales", "lead", "crm", "ai", "qualification"],
            difficulty="advanced",
            estimated_time_minutes=35,
            nodes=[
                trigger,
                enrich_data,
                ai_score,
                route_lead,
                assign_sales,
                nurture,
                success,
            ],
            connections=connections,
            configuration_steps=[
                "Configure lead capture webhook",
                "Set up data enrichment API (e.g., Clearbit)",
                "Configure AI scoring criteria",
                "Connect to Salesforce CRM",
                "Set up nurture campaign",
            ],
            required_integrations=["webhook", "api", "salesforce", "email"],
            rating=4.8,
        )

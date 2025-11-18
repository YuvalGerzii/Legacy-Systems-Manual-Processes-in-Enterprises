"""Low-Code Workflow Platform - Usage Examples.

This file demonstrates how to use the Low-Code Workflow Automation Platform
for common SME use cases.
"""

import asyncio
from uuid import uuid4

from src.automation_fabric.lowcode_designer import get_lowcode_designer
from src.automation_fabric.workflow_templates import WorkflowTemplateLibrary
from src.automation_fabric.node_library import NodeLibrary
from src.automation_fabric.ai_approval_assistant import (
    get_approval_assistant,
    ApprovalRequest,
)
from src.automation_fabric.plugin_system import (
    get_plugin_manager,
    initialize_default_plugins,
)
from src.automation_fabric.models import (
    NodeType,
    NodeCategory,
    PluginConnection,
)


async def example_1_create_simple_workflow():
    """Example 1: Create a simple workflow from scratch."""
    print("=" * 60)
    print("Example 1: Creating a Simple Invoice Approval Workflow")
    print("=" * 60)

    designer = get_lowcode_designer()

    # Create workflow
    workflow = await designer.create_workflow(
        name="Simple Invoice Approval",
        description="Basic invoice approval workflow"
    )
    print(f"✓ Created workflow: {workflow.name}")

    # Add trigger node
    trigger = await designer.add_node(
        workflow_id=workflow.id,
        node_type=NodeType.EMAIL_TRIGGER,
        label="New Invoice Email",
        config={
            "email_address": "invoices@company.com",
            "filter_subject": "invoice"
        },
        position={"x": 100, "y": 100}
    )
    print(f"✓ Added trigger node: {trigger.label}")

    # Add AI approval node
    ai_approval = await designer.add_node(
        workflow_id=workflow.id,
        node_type=NodeType.AI_APPROVAL,
        label="AI Invoice Review",
        config={
            "threshold": 0.85,
            "criteria": "Approve if amount < $5000 AND vendor is in approved list AND all required fields are present"
        },
        position={"x": 300, "y": 100}
    )
    print(f"✓ Added AI approval node: {ai_approval.label}")

    # Add email notification node
    email_node = await designer.add_node(
        workflow_id=workflow.id,
        node_type=NodeType.EMAIL_SEND,
        label="Send Approval Email",
        config={
            "to": "ap@company.com",
            "subject": "Invoice Approved: {{invoice_number}}",
            "body": "Invoice {{invoice_number}} for ${{amount}} has been approved."
        },
        position={"x": 500, "y": 100}
    )
    print(f"✓ Added email node: {email_node.label}")

    # Add success node
    success = await designer.add_node(
        workflow_id=workflow.id,
        node_type=NodeType.SUCCESS,
        label="Workflow Complete",
        config={"message": "Invoice processed successfully"},
        position={"x": 700, "y": 100}
    )
    print(f"✓ Added success node: {success.label}")

    # Connect nodes
    await designer.connect_nodes(workflow.id, trigger.id, ai_approval.id)
    await designer.connect_nodes(
        workflow.id,
        ai_approval.id,
        email_node.id,
        condition="approved"
    )
    await designer.connect_nodes(workflow.id, email_node.id, success.id)
    print("✓ Connected all nodes")

    # Validate workflow
    validation = await designer.validate_workflow(workflow.id)
    if validation.is_valid:
        print("✓ Workflow validation passed!")
    else:
        print(f"✗ Validation errors: {validation.errors}")
        print(f"⚠ Warnings: {validation.warnings}")

    print(f"\nWorkflow ID: {workflow.id}")
    print()


async def example_2_use_template():
    """Example 2: Create workflow from pre-built template."""
    print("=" * 60)
    print("Example 2: Using Pre-Built Template")
    print("=" * 60)

    designer = get_lowcode_designer()

    # Get all templates
    templates = WorkflowTemplateLibrary.get_all_templates()
    print(f"Available templates: {len(templates)}")

    # Show templates by category
    categories = {}
    for template in templates:
        if template.category not in categories:
            categories[template.category] = []
        categories[template.category].append(template)

    print("\nTemplates by category:")
    for category, tmpl_list in categories.items():
        print(f"\n{category}:")
        for tmpl in tmpl_list:
            print(f"  - {tmpl.name} ({tmpl.difficulty})")
            print(f"    {tmpl.description}")
            print(f"    Estimated time: {tmpl.estimated_time_minutes} min")

    # Use the invoice approval template
    invoice_template = next(
        t for t in templates if "Invoice Approval" in t.name
    )

    # Create workflow from template
    workflow = await designer.create_workflow(
        name="My Invoice Approval Process",
        description=invoice_template.description,
        nodes=invoice_template.nodes,
        connections=invoice_template.connections
    )

    print(f"\n✓ Created workflow from template: {workflow.name}")
    print(f"  Nodes: {len(workflow.nodes)}")
    print(f"  Connections: {len(workflow.connections)}")
    print(f"\nConfiguration steps:")
    for i, step in enumerate(invoice_template.configuration_steps, 1):
        print(f"  {i}. {step}")

    print()


async def example_3_ai_approval():
    """Example 3: Use AI approval assistant."""
    print("=" * 60)
    print("Example 3: AI-Powered Approval Assistant")
    print("=" * 60)

    assistant = get_approval_assistant()

    # Process an invoice approval
    request = ApprovalRequest(
        id=uuid4(),
        workflow_id=uuid4(),
        request_type="invoice",
        data={
            "invoice_number": "INV-12345",
            "vendor_name": "Acme Corporation",
            "amount": 4500,
            "due_date": "2025-12-31",
            "description": "Office supplies - Q4 2025",
            "category": "Office Expenses",
            "has_receipt": True
        },
        criteria="Approve if amount < $5000 AND vendor is in approved list AND receipt is attached",
        threshold=0.8
    )

    print(f"Processing approval request...")
    print(f"  Type: {request.request_type}")
    print(f"  Amount: ${request.data['amount']:,.2f}")
    print(f"  Vendor: {request.data['vendor_name']}")

    decision = await assistant.process_approval(request)

    print(f"\n{'='*40}")
    print(f"AI DECISION: {decision.decision.upper()}")
    print(f"{'='*40}")
    print(f"Confidence: {decision.confidence:.1%}")
    print(f"\nReasoning:")
    print(f"  {decision.reasoning}")

    if decision.risk_factors:
        print(f"\nRisk Factors:")
        for risk in decision.risk_factors:
            print(f"  ⚠ {risk}")

    if decision.recommendations:
        print(f"\nRecommendations:")
        for rec in decision.recommendations:
            print(f"  → {rec}")

    # Show stats
    stats = assistant.get_approval_stats()
    print(f"\n--- Approval Statistics ---")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Auto-approval rate: {stats['auto_approval_rate']:.1%}")
    print(f"Average confidence: {stats['average_confidence']:.1%}")

    print()


async def example_4_batch_approvals():
    """Example 4: Process multiple approvals in batch."""
    print("=" * 60)
    print("Example 4: Batch Approval Processing")
    print("=" * 60)

    assistant = get_approval_assistant()

    # Create multiple requests
    requests = [
        ApprovalRequest(
            id=uuid4(),
            workflow_id=uuid4(),
            request_type="expense",
            data={
                "employee_name": "John Smith",
                "amount": 150,
                "category": "Meals",
                "date": "2025-11-15",
                "description": "Client dinner",
                "has_receipt": True,
                "business_purpose": "Sales meeting with Acme Corp"
            },
            criteria="Approve if amount < $500 AND has receipt AND valid business purpose",
            threshold=0.85
        ),
        ApprovalRequest(
            id=uuid4(),
            workflow_id=uuid4(),
            request_type="expense",
            data={
                "employee_name": "Jane Doe",
                "amount": 75,
                "category": "Transport",
                "date": "2025-11-16",
                "description": "Taxi to airport",
                "has_receipt": True,
                "business_purpose": "Travel to conference"
            },
            criteria="Approve if amount < $500 AND has receipt AND valid business purpose",
            threshold=0.85
        ),
        ApprovalRequest(
            id=uuid4(),
            workflow_id=uuid4(),
            request_type="expense",
            data={
                "employee_name": "Bob Johnson",
                "amount": 800,
                "category": "Training",
                "date": "2025-11-17",
                "description": "Online course subscription",
                "has_receipt": False,
                "business_purpose": "Professional development"
            },
            criteria="Approve if amount < $500 AND has receipt AND valid business purpose",
            threshold=0.85
        ),
    ]

    print(f"Processing {len(requests)} approval requests in parallel...\n")

    decisions = await assistant.batch_process_approvals(requests)

    for i, (request, decision) in enumerate(zip(requests, decisions), 1):
        print(f"Request #{i}: {request.data['employee_name']}")
        print(f"  Amount: ${request.data['amount']:.2f}")
        print(f"  Decision: {decision.decision.upper()} (confidence: {decision.confidence:.1%})")
        if decision.decision == "escalate":
            print(f"  ⚠ Escalation reason: {decision.recommendations[0] if decision.recommendations else 'Low confidence'}")
        print()

    print()


async def example_5_explore_nodes():
    """Example 5: Explore available nodes."""
    print("=" * 60)
    print("Example 5: Exploring Available Workflow Nodes")
    print("=" * 60)

    # Get all nodes
    all_nodes = NodeLibrary.get_all_nodes()
    print(f"Total available nodes: {len(all_nodes)}\n")

    # Group by category
    by_category = {}
    for node in all_nodes:
        category = node["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(node)

    # Display by category
    for category in NodeCategory:
        nodes = by_category.get(category, [])
        if nodes:
            print(f"\n{category.value.upper()} ({len(nodes)} nodes):")
            print("-" * 60)
            for node in nodes:
                print(f"  📦 {node['label']}")
                print(f"     Type: {node['type']}")
                print(f"     Description: {node['description']}")
                print(f"     Inputs: {node['inputs']}, Outputs: {node['outputs']}")
                print()

    # Show AI nodes in detail
    print("\n" + "=" * 60)
    print("AI NODES - DETAILED VIEW")
    print("=" * 60)

    ai_nodes = NodeLibrary.get_nodes_by_category(NodeCategory.AI)
    for node in ai_nodes:
        print(f"\n🤖 {node['label']}")
        print(f"   {node['description']}")
        print(f"   Configuration:")
        for key, config in node['config_schema'].items():
            required = " (required)" if config.get('required') else ""
            default = f" [default: {config.get('default')}]" if 'default' in config else ""
            print(f"     - {key}: {config.get('description', 'N/A')}{required}{default}")

    print()


async def example_6_plugin_integration():
    """Example 6: Set up plugin integrations."""
    print("=" * 60)
    print("Example 6: Plugin System Integration")
    print("=" * 60)

    # Initialize default plugins
    await initialize_default_plugins()

    plugin_manager = get_plugin_manager()

    # List available plugins
    plugins = plugin_manager.get_available_plugins()
    print(f"Available plugins: {len(plugins)}\n")

    for plugin in plugins:
        print(f"📌 {plugin.name}")
        print(f"   Type: {plugin.system_type}")
        print(f"   Version: {plugin.version}")
        print(f"   Auth: {plugin.authentication_type}")
        print(f"   Endpoints:")
        for endpoint in plugin.endpoints:
            print(f"     - {endpoint['name']}: {endpoint['description']}")
        print()

    # Example: Create Slack connection (mock)
    print("Creating Slack connection (demo)...")
    slack_plugin = next(p for p in plugins if p.system_type == "slack")

    connection = PluginConnection(
        plugin_id=slack_plugin.id,
        name="Demo Slack Workspace",
        configuration={"workspace": "demo-workspace"},
        credentials={"bot_token": "xoxb-demo-token"}
    )

    # Note: This would actually test the connection in production
    print(f"✓ Connection configured: {connection.name}")
    print(f"  Plugin: {slack_plugin.name}")
    print(f"  Status: {connection.test_status}")

    print()


async def example_7_complete_workflow_execution():
    """Example 7: Complete workflow with execution."""
    print("=" * 60)
    print("Example 7: Complete Workflow Creation and Execution")
    print("=" * 60)

    designer = get_lowcode_designer()

    # Create expense approval workflow
    workflow = await designer.create_workflow(
        name="Expense Approval Workflow",
        description="Automated expense approval with AI validation"
    )

    # Build workflow
    trigger = await designer.add_node(
        workflow.id, NodeType.MANUAL_TRIGGER, "Submit Expense",
        position={"x": 100, "y": 100}
    )

    validate = await designer.add_node(
        workflow.id, NodeType.CONDITION, "Check Amount",
        config={"condition": "amount <= 500"},
        position={"x": 300, "y": 100}
    )

    ai_check = await designer.add_node(
        workflow.id, NodeType.AI_APPROVAL, "AI Review (Low Amount)",
        config={
            "threshold": 0.9,
            "criteria": "Approve if has receipt and valid business purpose"
        },
        position={"x": 500, "y": 50}
    )

    human_approval = await designer.add_node(
        workflow.id, NodeType.HUMAN_APPROVAL, "Manager Approval (High Amount)",
        config={"approver": "manager@company.com"},
        position={"x": 500, "y": 200}
    )

    success = await designer.add_node(
        workflow.id, NodeType.SUCCESS, "Approved",
        position={"x": 700, "y": 100}
    )

    # Connect nodes
    await designer.connect_nodes(workflow.id, trigger.id, validate.id)
    await designer.connect_nodes(
        workflow.id, validate.id, ai_check.id,
        condition="true"
    )
    await designer.connect_nodes(
        workflow.id, validate.id, human_approval.id,
        condition="false"
    )
    await designer.connect_nodes(
        workflow.id, ai_check.id, success.id,
        condition="approved"
    )
    await designer.connect_nodes(
        workflow.id, human_approval.id, success.id,
        condition="approved"
    )

    print(f"✓ Workflow created: {workflow.name}")
    print(f"  Nodes: {len(workflow.nodes)}")
    print(f"  Connections: {len(workflow.connections)}")

    # Validate
    validation = await designer.validate_workflow(workflow.id)
    print(f"\nValidation: {'✓ PASSED' if validation.is_valid else '✗ FAILED'}")
    if validation.warnings:
        print("Warnings:")
        for warning in validation.warnings:
            print(f"  ⚠ {warning}")

    # Execute workflow
    print("\nExecuting workflow...")
    execution = await designer.execute_workflow(
        workflow.id,
        input_data={
            "employee": "John Smith",
            "amount": 250,
            "category": "Meals",
            "has_receipt": True,
            "business_purpose": "Client meeting"
        }
    )

    print(f"\nExecution completed!")
    print(f"  Status: {execution.status}")
    print(f"  Duration: {(execution.completed_at - execution.started_at).total_seconds():.2f}s")
    print(f"\nLogs:")
    for log in execution.logs:
        print(f"  {log}")

    # Export workflow
    exported = await designer.export_workflow(workflow.id, "json")
    print(f"\n✓ Workflow exported to JSON ({len(exported)} characters)")

    print()


async def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 8 + "LOW-CODE WORKFLOW PLATFORM EXAMPLES" + " " * 15 + "║")
    print("║" + " " * 12 + "For Small & Medium Enterprises" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    examples = [
        example_1_create_simple_workflow,
        example_2_use_template,
        example_3_ai_approval,
        example_4_batch_approvals,
        example_5_explore_nodes,
        example_6_plugin_integration,
        example_7_complete_workflow_execution,
    ]

    for i, example in enumerate(examples, 1):
        try:
            await example()
        except Exception as e:
            print(f"❌ Example {i} failed: {str(e)}\n")

        if i < len(examples):
            print("Press Enter to continue to next example...")
            # In interactive mode, would wait for input
            # input()
            print()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nFor more information, see docs/LOWCODE_WORKFLOW_PLATFORM.md")
    print()


if __name__ == "__main__":
    asyncio.run(main())

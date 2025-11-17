"""AI-Powered Approval Assistant for Low-Code Workflows.

This module provides intelligent approval automation using local LLMs,
reducing manual review burden for SMEs while maintaining control.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from loguru import logger
from pydantic import BaseModel

from ..core.llm import get_local_llm


class ApprovalRequest(BaseModel):
    """Approval request data."""

    id: UUID
    workflow_id: UUID
    request_type: str  # invoice, expense, leave, purchase, etc.
    data: Dict[str, Any]
    criteria: str
    threshold: float = 0.8
    metadata: Dict[str, Any] = {}


class ApprovalDecision(BaseModel):
    """AI approval decision."""

    request_id: UUID
    decision: str  # approved, rejected, escalate
    confidence: float
    reasoning: str
    extracted_facts: Dict[str, Any]
    risk_factors: List[str] = []
    recommendations: List[str] = []
    timestamp: datetime


class AIApprovalAssistant:
    """AI-powered approval assistant using local LLMs.

    This assistant analyzes approval requests and makes intelligent decisions
    based on configured criteria, escalating to humans when uncertain.

    Features:
    - 100% FREE (uses local Ollama LLMs)
    - Configurable approval criteria
    - Automatic escalation for edge cases
    - Detailed reasoning and audit trail
    - Integration with existing agent framework
    """

    def __init__(self):
        """Initialize AI approval assistant."""
        self.llm_client = get_local_llm()
        self.approval_history: List[ApprovalDecision] = []

    async def process_approval(
        self, request: ApprovalRequest
    ) -> ApprovalDecision:
        """Process an approval request using AI.

        Args:
            request: Approval request to process

        Returns:
            AI approval decision with reasoning

        Example:
            >>> assistant = AIApprovalAssistant()
            >>> request = ApprovalRequest(
            ...     id=uuid4(),
            ...     workflow_id=uuid4(),
            ...     request_type="invoice",
            ...     data={"amount": 4500, "vendor": "Acme Corp"},
            ...     criteria="Approve if amount < $5000 and vendor is approved"
            ... )
            >>> decision = await assistant.process_approval(request)
            >>> print(f"Decision: {decision.decision}")
            >>> print(f"Confidence: {decision.confidence}")
        """
        logger.info(
            f"Processing approval request {request.id} ({request.request_type})"
        )

        # Build AI prompt based on request type
        prompt = self._build_approval_prompt(request)

        # Get AI analysis
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                model="llama3.2:3b",
                temperature=0.1,  # Low temperature for consistent decisions
            )

            # Parse AI response
            decision = self._parse_ai_response(response, request)

            # Apply confidence threshold
            if decision.confidence < request.threshold:
                decision.decision = "escalate"
                decision.recommendations.append(
                    f"Confidence {decision.confidence:.2f} below threshold {request.threshold}"
                )

            # Store in history
            self.approval_history.append(decision)

            logger.info(
                f"AI decision for {request.id}: {decision.decision} (confidence: {decision.confidence:.2f})"
            )

            return decision

        except Exception as e:
            logger.error(f"AI approval failed: {str(e)}")
            # On error, escalate to human
            return ApprovalDecision(
                request_id=request.id,
                decision="escalate",
                confidence=0.0,
                reasoning=f"AI processing failed: {str(e)}. Escalating to human review.",
                extracted_facts={},
                risk_factors=["AI processing error"],
                recommendations=["Manual review required"],
                timestamp=datetime.utcnow(),
            )

    def _build_approval_prompt(self, request: ApprovalRequest) -> str:
        """Build AI prompt for approval decision.

        Args:
            request: Approval request

        Returns:
            Formatted prompt for LLM
        """
        if request.request_type == "invoice":
            return self._build_invoice_prompt(request)
        elif request.request_type == "expense":
            return self._build_expense_prompt(request)
        elif request.request_type == "leave":
            return self._build_leave_prompt(request)
        elif request.request_type == "purchase":
            return self._build_purchase_prompt(request)
        else:
            return self._build_generic_prompt(request)

    def _build_invoice_prompt(self, request: ApprovalRequest) -> str:
        """Build prompt for invoice approval."""
        data = request.data
        return f"""You are an AI approval assistant for invoice processing.

APPROVAL CRITERIA:
{request.criteria}

INVOICE DETAILS:
- Invoice Number: {data.get('invoice_number', 'N/A')}
- Vendor: {data.get('vendor_name', 'N/A')}
- Amount: ${data.get('amount', 0):,.2f}
- Due Date: {data.get('due_date', 'N/A')}
- Description: {data.get('description', 'N/A')}
- Category: {data.get('category', 'N/A')}

TASK:
Analyze this invoice and decide whether to:
1. APPROVE - Invoice meets all criteria
2. REJECT - Invoice clearly violates criteria
3. ESCALATE - Uncertain or edge case requiring human review

Provide your response in this exact format:

DECISION: [APPROVE/REJECT/ESCALATE]
CONFIDENCE: [0.0-1.0]
REASONING: [Detailed explanation of your decision]
EXTRACTED_FACTS: [Key facts you used: amount, vendor status, etc.]
RISK_FACTORS: [Any concerns or red flags]
RECOMMENDATIONS: [Suggestions for handling this case]

Be thorough and conservative. When in doubt, escalate to human review.
"""

    def _build_expense_prompt(self, request: ApprovalRequest) -> str:
        """Build prompt for expense approval."""
        data = request.data
        return f"""You are an AI approval assistant for expense reimbursement.

APPROVAL CRITERIA:
{request.criteria}

EXPENSE DETAILS:
- Employee: {data.get('employee_name', 'N/A')}
- Amount: ${data.get('amount', 0):,.2f}
- Category: {data.get('category', 'N/A')}
- Date: {data.get('date', 'N/A')}
- Description: {data.get('description', 'N/A')}
- Has Receipt: {data.get('has_receipt', False)}
- Business Purpose: {data.get('business_purpose', 'N/A')}

TASK:
Analyze this expense and decide: APPROVE, REJECT, or ESCALATE.

Provide your response in the standard format with DECISION, CONFIDENCE, REASONING, etc.

Check for:
- Compliance with expense policy
- Receipt availability
- Reasonable amount for category
- Clear business purpose
"""

    def _build_leave_prompt(self, request: ApprovalRequest) -> str:
        """Build prompt for leave request approval."""
        data = request.data
        return f"""You are an AI approval assistant for leave requests.

APPROVAL CRITERIA:
{request.criteria}

LEAVE REQUEST:
- Employee: {data.get('employee_name', 'N/A')}
- Leave Type: {data.get('leave_type', 'N/A')}
- Start Date: {data.get('start_date', 'N/A')}
- End Date: {data.get('end_date', 'N/A')}
- Days Requested: {data.get('days', 0)}
- Available Balance: {data.get('available_days', 0)}
- Reason: {data.get('reason', 'N/A')}

TASK:
Analyze this leave request and decide: APPROVE, REJECT, or ESCALATE.

Consider:
- Available leave balance
- Blackout periods or busy seasons
- Advance notice
- Team coverage

Provide response in standard format.
"""

    def _build_purchase_prompt(self, request: ApprovalRequest) -> str:
        """Build prompt for purchase order approval."""
        data = request.data
        return f"""You are an AI approval assistant for purchase orders.

APPROVAL CRITERIA:
{request.criteria}

PURCHASE ORDER:
- Requested By: {data.get('requester', 'N/A')}
- Item/Service: {data.get('item', 'N/A')}
- Amount: ${data.get('amount', 0):,.2f}
- Vendor: {data.get('vendor', 'N/A')}
- Department: {data.get('department', 'N/A')}
- Budget Available: ${data.get('budget_available', 0):,.2f}
- Justification: {data.get('justification', 'N/A')}

TASK:
Analyze this purchase order and decide: APPROVE, REJECT, or ESCALATE.

Check:
- Budget availability
- Vendor approval status
- Business justification
- Spending authority limits

Provide response in standard format.
"""

    def _build_generic_prompt(self, request: ApprovalRequest) -> str:
        """Build generic approval prompt."""
        data_str = "\n".join([f"- {k}: {v}" for k, v in request.data.items()])
        return f"""You are an AI approval assistant.

APPROVAL CRITERIA:
{request.criteria}

REQUEST DATA:
{data_str}

TASK:
Analyze this request and decide: APPROVE, REJECT, or ESCALATE.

Provide your response in this format:
DECISION: [APPROVE/REJECT/ESCALATE]
CONFIDENCE: [0.0-1.0]
REASONING: [Explanation]
EXTRACTED_FACTS: [Key facts]
RISK_FACTORS: [Concerns]
RECOMMENDATIONS: [Suggestions]
"""

    def _parse_ai_response(
        self, response: str, request: ApprovalRequest
    ) -> ApprovalDecision:
        """Parse AI response into structured decision.

        Args:
            response: Raw AI response
            request: Original request

        Returns:
            Structured approval decision
        """
        lines = response.strip().split("\n")
        decision_text = "escalate"
        confidence = 0.5
        reasoning = ""
        extracted_facts = {}
        risk_factors = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("DECISION:"):
                decision_text = line.split(":", 1)[1].strip().lower()
            elif line.startswith("CONFIDENCE:"):
                try:
                    conf_str = line.split(":", 1)[1].strip()
                    confidence = float(conf_str)
                except:
                    confidence = 0.5
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
                current_section = "reasoning"
            elif line.startswith("EXTRACTED_FACTS:"):
                current_section = "facts"
            elif line.startswith("RISK_FACTORS:"):
                current_section = "risk"
            elif line.startswith("RECOMMENDATIONS:"):
                current_section = "recommendations"
            elif line and current_section:
                if current_section == "reasoning":
                    reasoning += " " + line
                elif current_section == "risk" and line.startswith("-"):
                    risk_factors.append(line[1:].strip())
                elif current_section == "recommendations" and line.startswith(
                    "-"
                ):
                    recommendations.append(line[1:].strip())

        # Validate decision
        if decision_text not in ["approve", "reject", "escalate", "approved", "rejected"]:
            decision_text = "escalate"
            recommendations.append("Uncertain AI response, escalating to human")

        # Normalize decision text
        if decision_text in ["approve", "approved"]:
            decision_text = "approved"
        elif decision_text in ["reject", "rejected"]:
            decision_text = "rejected"
        else:
            decision_text = "escalate"

        return ApprovalDecision(
            request_id=request.id,
            decision=decision_text,
            confidence=min(max(confidence, 0.0), 1.0),  # Clamp to 0-1
            reasoning=reasoning or "No reasoning provided",
            extracted_facts=extracted_facts,
            risk_factors=risk_factors,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
        )

    async def batch_process_approvals(
        self, requests: List[ApprovalRequest]
    ) -> List[ApprovalDecision]:
        """Process multiple approval requests in parallel.

        Args:
            requests: List of approval requests

        Returns:
            List of approval decisions

        Example:
            >>> decisions = await assistant.batch_process_approvals(requests)
        """
        tasks = [self.process_approval(req) for req in requests]
        return await asyncio.gather(*tasks)

    def get_approval_stats(self) -> Dict[str, Any]:
        """Get approval statistics.

        Returns:
            Dictionary with approval metrics

        Example:
            >>> stats = assistant.get_approval_stats()
            >>> print(f"Auto-approval rate: {stats['auto_approval_rate']:.1%}")
        """
        if not self.approval_history:
            return {
                "total_requests": 0,
                "approved": 0,
                "rejected": 0,
                "escalated": 0,
                "auto_approval_rate": 0.0,
                "average_confidence": 0.0,
            }

        approved = sum(
            1 for d in self.approval_history if d.decision == "approved"
        )
        rejected = sum(
            1 for d in self.approval_history if d.decision == "rejected"
        )
        escalated = sum(
            1 for d in self.approval_history if d.decision == "escalate"
        )

        total = len(self.approval_history)
        avg_confidence = sum(d.confidence for d in self.approval_history) / total

        return {
            "total_requests": total,
            "approved": approved,
            "rejected": rejected,
            "escalated": escalated,
            "auto_approval_rate": (approved + rejected) / total if total > 0 else 0.0,
            "average_confidence": avg_confidence,
        }

    async def explain_decision(
        self, decision_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get detailed explanation for a past decision.

        Args:
            decision_id: ID of the decision to explain

        Returns:
            Detailed decision explanation

        Example:
            >>> explanation = await assistant.explain_decision(decision.request_id)
        """
        decision = next(
            (d for d in self.approval_history if d.request_id == decision_id),
            None,
        )

        if not decision:
            return None

        return {
            "request_id": str(decision.request_id),
            "decision": decision.decision,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "timestamp": decision.timestamp.isoformat(),
            "risk_factors": decision.risk_factors,
            "recommendations": decision.recommendations,
            "audit_trail": {
                "decision_made_at": decision.timestamp.isoformat(),
                "ai_model": "llama3.2:3b (local)",
                "processing_method": "AI-powered analysis",
            },
        }


# Singleton instance
_assistant_instance: Optional[AIApprovalAssistant] = None


def get_approval_assistant() -> AIApprovalAssistant:
    """Get the global AI approval assistant instance.

    Returns:
        Global AIApprovalAssistant instance
    """
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = AIApprovalAssistant()
    return _assistant_instance

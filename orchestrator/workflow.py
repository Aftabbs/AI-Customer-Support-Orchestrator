"""Main Orchestrator using LangGraph"""
from typing import Dict, Any, TypedDict
import time
from datetime import datetime
from langgraph.graph import StateGraph, END
from agents import ClassifierAgent, TechnicalAgent, BillingAgent, GeneralAgent
from guardrails import ContentFilter, ResponseValidator, EscalationChecker
from evaluation import MetricsTracker, AgentEvaluator


class AgentState(TypedDict):
    """State passed between agents"""
    ticket: str
    ticket_id: str
    category: str
    response: str
    confidence: float
    escalated: bool
    guardrail_violations: list
    metadata: dict
    start_time: float
    agent_used: str


class SupportOrchestrator:
    """Orchestrates multi-agent workflow for support tickets"""

    def __init__(self):
        # Initialize agents
        self.classifier = ClassifierAgent()
        self.technical_agent = TechnicalAgent()
        self.billing_agent = BillingAgent()
        self.general_agent = GeneralAgent()

        # Initialize guardrails
        self.content_filter = ContentFilter()
        self.response_validator = ResponseValidator()
        self.escalation_checker = EscalationChecker()

        # Initialize evaluation
        self.metrics_tracker = MetricsTracker()
        self.evaluator = AgentEvaluator()

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classify", self._classify_ticket)
        workflow.add_node("route", self._route_ticket)
        workflow.add_node("validate", self._validate_response)
        workflow.add_node("check_escalation", self._check_escalation)
        workflow.add_node("finalize", self._finalize_response)

        # Define edges
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "route")
        workflow.add_edge("route", "validate")
        workflow.add_edge("validate", "check_escalation")
        workflow.add_edge("check_escalation", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _classify_ticket(self, state: AgentState) -> AgentState:
        """Classify the ticket"""
        result = self.classifier.process({"ticket": state["ticket"]})
        state["category"] = result["content"]
        state["metadata"]["classification_reason"] = result["metadata"].get("reason", "")
        state["confidence"] = result["metadata"].get("confidence", 0.5)
        return state

    def _route_ticket(self, state: AgentState) -> AgentState:
        """Route to appropriate specialist agent"""
        category = state["category"]

        # Select agent based on category
        if category == "TECHNICAL":
            agent = self.technical_agent
        elif category == "BILLING":
            agent = self.billing_agent
        else:
            agent = self.general_agent

        # Process with selected agent
        result = agent.process({"ticket": state["ticket"]})
        state["response"] = result["content"]
        state["agent_used"] = agent.name
        state["metadata"]["agent_metadata"] = result["metadata"]

        # Update confidence
        has_search = result["metadata"].get("search_used", False)
        response_length = len(result["content"])
        state["confidence"] = self.evaluator.calculate_confidence(
            agent.name,
            response_length,
            has_search
        )

        return state

    def _validate_response(self, state: AgentState) -> AgentState:
        """Validate response with guardrails"""
        response = state["response"]
        violations = []

        # Check content filter
        is_safe, content_violations = self.content_filter.check_content(response)
        if not is_safe:
            violations.extend(content_violations)
            state["response"] = self.content_filter.sanitize_response(response, content_violations)

        # Validate response quality
        is_valid, error_msg = self.response_validator.validate_response(response)
        if not is_valid:
            violations.append(f"Quality issue: {error_msg}")

        # Check completeness
        if not self.response_validator.check_completeness(response):
            violations.append("Response appears incomplete")

        state["guardrail_violations"] = violations
        return state

    def _check_escalation(self, state: AgentState) -> AgentState:
        """Check if escalation needed"""
        should_escalate, reasons = self.escalation_checker.should_escalate(
            state["ticket"],
            state["confidence"],
            state["category"]
        )

        state["escalated"] = should_escalate

        if should_escalate:
            escalation_msg = self.escalation_checker.get_escalation_message(reasons)
            state["response"] = f"{state['response']}\n\n---\n{escalation_msg}"
            state["metadata"]["escalation_reasons"] = reasons

        return state

    def _finalize_response(self, state: AgentState) -> AgentState:
        """Finalize and log metrics"""
        response_time = time.time() - state["start_time"]

        # Log metrics
        self.metrics_tracker.log_interaction(
            ticket_id=state["ticket_id"],
            category=state["category"],
            confidence=state["confidence"],
            response_time=response_time,
            escalated=state["escalated"],
            guardrail_violations=state["guardrail_violations"],
            agent_used=state["agent_used"]
        )

        state["metadata"]["response_time"] = round(response_time, 2)
        return state

    def process_ticket(self, ticket: str) -> Dict[str, Any]:
        """
        Process a support ticket through the workflow

        Args:
            ticket: Support ticket text

        Returns:
            Dictionary with response and metadata
        """
        # Initialize state
        initial_state: AgentState = {
            "ticket": ticket,
            "ticket_id": f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "category": "",
            "response": "",
            "confidence": 0.0,
            "escalated": False,
            "guardrail_violations": [],
            "metadata": {},
            "start_time": time.time(),
            "agent_used": ""
        }

        # Run workflow
        final_state = self.workflow.invoke(initial_state)

        # Return formatted result
        return {
            "ticket_id": final_state["ticket_id"],
            "category": final_state["category"],
            "response": final_state["response"],
            "confidence": final_state["confidence"],
            "escalated": final_state["escalated"],
            "agent_used": final_state["agent_used"],
            "metadata": final_state["metadata"],
            "guardrail_violations": final_state["guardrail_violations"]
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        return self.metrics_tracker.get_summary_stats()

    def export_metrics(self, filepath: str = "metrics_log.json"):
        """Export metrics to file"""
        self.metrics_tracker.export_metrics(filepath)

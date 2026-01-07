"""Escalation Rules Guardrail"""
from typing import List, Dict, Tuple
import yaml


class EscalationChecker:
    """Determines if ticket needs human escalation"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.triggers = config['guardrails']['escalation_triggers']
        self.confidence_threshold = config['guardrails']['confidence_threshold']

    def should_escalate(self, ticket: str, confidence: float, category: str = None) -> Tuple[bool, List[str]]:
        """
        Check if ticket should be escalated to human

        Args:
            ticket: Support ticket text
            confidence: Confidence score of agent response (0.0 to 1.0)
            category: Ticket category (optional)

        Returns:
            Tuple of (should_escalate, reasons)
        """
        reasons = []
        ticket_lower = ticket.lower()

        # Check confidence threshold
        if confidence < self.confidence_threshold:
            reasons.append(f"Low confidence score: {confidence:.2f}")

        # Check for escalation triggers
        for trigger in self.triggers:
            if trigger.lower() in ticket_lower:
                reasons.append(f"Trigger word detected: {trigger}")

        # Check for urgent indicators
        urgent_words = ['urgent', 'emergency', 'critical', 'asap', 'immediately']
        if any(word in ticket_lower for word in urgent_words):
            reasons.append("Urgent issue detected")

        # Check for complex scenarios
        if ticket_lower.count('?') > 3:
            reasons.append("Multiple complex questions")

        should_escalate = len(reasons) > 0
        return should_escalate, reasons

    def get_escalation_message(self, reasons: List[str]) -> str:
        """
        Generate escalation message

        Args:
            reasons: List of escalation reasons

        Returns:
            Escalation message
        """
        return (
            f"This ticket has been flagged for human review due to:\n"
            f"{chr(10).join(['- ' + reason for reason in reasons])}\n\n"
            f"A support specialist will review this case and reach out to you shortly."
        )

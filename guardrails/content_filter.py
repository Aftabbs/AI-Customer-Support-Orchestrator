"""Content Filter Guardrail"""
from typing import Dict, List, Tuple
import yaml


class ContentFilter:
    """Filters and validates content for prohibited topics"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.prohibited_topics = config['guardrails']['prohibited_topics']

    def check_content(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check if content contains prohibited topics

        Args:
            text: Text to check

        Returns:
            Tuple of (is_safe, list of violations)
        """
        violations = []
        text_lower = text.lower()

        for topic in self.prohibited_topics:
            if topic.lower() in text_lower:
                violations.append(topic)

        is_safe = len(violations) == 0
        return is_safe, violations

    def sanitize_response(self, response: str, violations: List[str]) -> str:
        """
        Sanitize response if violations found

        Args:
            response: Original response
            violations: List of violations

        Returns:
            Sanitized or warning message
        """
        if not violations:
            return response

        return (
            f"I apologize, but I cannot provide {', '.join(violations)} as it's outside "
            f"my support scope. Please consult with a qualified professional or I can "
            f"escalate this to a human agent who can better assist you."
        )

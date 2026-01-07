"""Response Validator Guardrail"""
from typing import Dict, Tuple
import yaml


class ResponseValidator:
    """Validates response quality and safety"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.max_length = config['guardrails']['max_response_length']
        self.min_length = config['guardrails']['min_response_length']

    def validate_response(self, response: str) -> Tuple[bool, str]:
        """
        Validate response meets quality standards

        Args:
            response: Response to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not response or not response.strip():
            return False, "Response is empty"

        response_length = len(response.strip())

        if response_length < self.min_length:
            return False, f"Response too short ({response_length} chars, minimum {self.min_length})"

        if response_length > self.max_length:
            return False, f"Response too long ({response_length} chars, maximum {self.max_length})"

        # Check for common quality issues
        if response.count('?') > 5:
            return False, "Response contains too many questions instead of answers"

        # Check for placeholder text
        placeholders = ['TODO', 'FIXME', '[INSERT', 'XXX']
        for placeholder in placeholders:
            if placeholder in response.upper():
                return False, f"Response contains placeholder: {placeholder}"

        return True, ""

    def check_completeness(self, response: str) -> bool:
        """
        Check if response appears complete

        Args:
            response: Response to check

        Returns:
            True if response appears complete
        """
        # Check if response ends properly
        ending_punctuation = ['.', '!', '?']
        if response.strip() and response.strip()[-1] in ending_punctuation:
            return True

        return False

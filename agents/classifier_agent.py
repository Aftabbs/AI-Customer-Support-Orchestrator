"""Classifier Agent - Categorizes support tickets"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent


class ClassifierAgent(BaseAgent):
    """Classifies support tickets into categories"""

    def __init__(self):
        super().__init__(
            name="Ticket Classifier",
            description="Categorizes support tickets",
            temperature=0.2
        )

        self.classification_prompt = PromptTemplate(
            input_variables=["ticket"],
            template="""You are a support ticket classifier. Analyze the following ticket and categorize it.

Categories:
- TECHNICAL: Issues with product functionality, bugs, errors, technical problems
- BILLING: Payment issues, subscription questions, invoices, refunds
- GENERAL: General inquiries, feature requests, information requests, other questions

Ticket: {ticket}

Analyze the ticket and respond with ONLY the category name (TECHNICAL, BILLING, or GENERAL) and a brief reason.

Format:
CATEGORY: [category]
REASON: [brief reason in one sentence]"""
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the ticket

        Args:
            input_data: Dictionary with 'ticket' key

        Returns:
            Dictionary with category and reason
        """
        ticket = input_data.get("ticket", "")

        if not ticket:
            return self.format_response(
                content="GENERAL",
                metadata={"reason": "Empty ticket", "confidence": 0.5}
            )

        try:
            prompt = self.classification_prompt.format(ticket=ticket)
            result = self.llm.invoke(prompt)
            response = result.content

            # Parse response
            category = "GENERAL"  # default
            reason = "Unable to classify"

            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith("CATEGORY:"):
                    category = line.split("CATEGORY:")[1].strip().upper()
                elif line.startswith("REASON:"):
                    reason = line.split("REASON:")[1].strip()

            # Validate category
            valid_categories = ["TECHNICAL", "BILLING", "GENERAL"]
            if category not in valid_categories:
                category = "GENERAL"

            return self.format_response(
                content=category,
                metadata={
                    "reason": reason,
                    "confidence": 0.85
                }
            )

        except Exception as e:
            return self.format_response(
                content="GENERAL",
                metadata={
                    "reason": f"Classification error: {str(e)}",
                    "confidence": 0.3
                }
            )

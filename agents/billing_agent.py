"""Billing Support Agent"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent


class BillingAgent(BaseAgent):
    """Handles billing and payment issues"""

    def __init__(self):
        super().__init__(
            name="Billing Support Agent",
            description="Handles billing, payments, and subscription queries",
            temperature=0.3
        )

        self.billing_prompt = PromptTemplate(
            input_variables=["ticket"],
            template="""You are a billing support specialist. Help resolve this billing issue.

Customer Issue: {ticket}

Provide a helpful, professional response that:
1. Acknowledges their billing concern
2. Explains the situation clearly
3. Provides next steps or resolution
4. Reassures the customer

Important guidelines:
- Be empathetic about billing concerns
- Clearly explain any charges or policies
- Offer to investigate further if needed
- For refunds over $100, mention that a specialist will review

Keep your response concise (max 300 words) and professional.

Response:"""
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle billing support ticket

        Args:
            input_data: Dictionary with 'ticket' key

        Returns:
            Dictionary with response and metadata
        """
        ticket = input_data.get("ticket", "")

        if not ticket:
            return self.format_response(
                content="I'm here to help with your billing question. What can I assist you with?",
                metadata={}
            )

        try:
            prompt = self.billing_prompt.format(ticket=ticket)
            result = self.llm.invoke(prompt)
            response = result.content.strip()

            # Check for high-value refund requests
            high_value_refund = False
            ticket_lower = ticket.lower()
            if 'refund' in ticket_lower:
                # Simple heuristic for high value detection
                if any(word in ticket_lower for word in ['$1000', '$500', 'thousand', 'hundred']):
                    high_value_refund = True

            return self.format_response(
                content=response,
                metadata={
                    "high_value_refund": high_value_refund
                }
            )

        except Exception as e:
            return self.format_response(
                content=(
                    f"I understand you have a billing question. "
                    f"I'd be happy to help clarify any charges or assist with your account. "
                    f"Could you provide more specific details about your concern?"
                ),
                metadata={
                    "error": str(e)
                }
            )

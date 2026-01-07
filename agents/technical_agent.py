"""Technical Support Agent"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent
from utils.serper_search import search_web


class TechnicalAgent(BaseAgent):
    """Handles technical support issues"""

    def __init__(self):
        super().__init__(
            name="Technical Support Agent",
            description="Handles technical issues and troubleshooting",
            temperature=0.3
        )

        self.support_prompt = PromptTemplate(
            input_variables=["ticket", "search_results"],
            template="""You are a technical support specialist. Help resolve this technical issue.

Customer Issue: {ticket}

Additional Information (from web search):
{search_results}

Provide a helpful, professional response that:
1. Acknowledges the issue
2. Provides clear troubleshooting steps or solution
3. Offers additional help if needed

Keep your response concise (max 400 words) and actionable.

Response:"""
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle technical support ticket

        Args:
            input_data: Dictionary with 'ticket' key

        Returns:
            Dictionary with response and metadata
        """
        ticket = input_data.get("ticket", "")

        if not ticket:
            return self.format_response(
                content="I'd be happy to help with your technical issue. Could you please provide more details?",
                metadata={"search_used": False}
            )

        try:
            # Perform web search for additional context
            search_query = f"technical support {ticket[:100]}"
            search_results = search_web(search_query, num_results=2)

            # Format search results
            search_context = "\n".join([
                f"- {r['title']}: {r['snippet']}" for r in search_results
            ])

            # Generate response
            prompt = self.support_prompt.format(
                ticket=ticket,
                search_results=search_context if search_context else "No additional information available"
            )

            result = self.llm.invoke(prompt)
            response = result.content.strip()

            return self.format_response(
                content=response,
                metadata={
                    "search_used": True,
                    "search_results": search_results[:2]
                }
            )

        except Exception as e:
            return self.format_response(
                content=(
                    f"I understand you're experiencing a technical issue. "
                    f"Let me help you troubleshoot this. Could you provide more details about "
                    f"what you're seeing and what steps you've already tried?"
                ),
                metadata={
                    "search_used": False,
                    "error": str(e)
                }
            )

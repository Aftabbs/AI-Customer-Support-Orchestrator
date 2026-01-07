"""General Support Agent"""
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent
from utils.serper_search import search_web


class GeneralAgent(BaseAgent):
    """Handles general inquiries and information requests"""

    def __init__(self):
        super().__init__(
            name="General Support Agent",
            description="Handles general inquiries and information requests",
            temperature=0.4
        )

        self.general_prompt = PromptTemplate(
            input_variables=["ticket", "search_results"],
            template="""You are a customer support agent. Help answer this general inquiry.

Customer Question: {ticket}

Additional Information (from web search):
{search_results}

Provide a helpful, friendly response that:
1. Directly answers their question
2. Provides relevant information
3. Offers additional assistance if needed

Keep your response conversational but professional (max 300 words).

Response:"""
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle general support ticket

        Args:
            input_data: Dictionary with 'ticket' key

        Returns:
            Dictionary with response and metadata
        """
        ticket = input_data.get("ticket", "")

        if not ticket:
            return self.format_response(
                content="Hello! How can I assist you today?",
                metadata={"search_used": False}
            )

        try:
            # Perform web search for general questions
            search_query = ticket[:100]
            search_results = search_web(search_query, num_results=2)

            # Format search results
            search_context = "\n".join([
                f"- {r['title']}: {r['snippet']}" for r in search_results
            ])

            # Generate response
            prompt = self.general_prompt.format(
                ticket=ticket,
                search_results=search_context if search_context else "No additional information needed"
            )

            result = self.llm.invoke(prompt)
            response = result.content.strip()

            return self.format_response(
                content=response,
                metadata={
                    "search_used": bool(search_context),
                    "search_results": search_results[:2] if search_context else []
                }
            )

        except Exception as e:
            return self.format_response(
                content=(
                    f"Thank you for reaching out! I'd be happy to help. "
                    f"Could you provide a bit more detail so I can give you the best answer?"
                ),
                metadata={
                    "search_used": False,
                    "error": str(e)
                }
            )

"""Agent Evaluator Module"""
from typing import Dict, Tuple
from langchain_core.prompts import PromptTemplate
from utils.llm_config import get_llm


class AgentEvaluator:
    """Evaluates agent responses for quality and accuracy"""

    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        self.eval_prompt = PromptTemplate(
            input_variables=["ticket", "response", "category"],
            template="""You are an expert evaluator for customer support AI agents.

Ticket: {ticket}
Category: {category}
Agent Response: {response}

Evaluate the response on these criteria:
1. Relevance: Does it address the ticket?
2. Accuracy: Is the information correct?
3. Completeness: Does it fully answer the question?
4. Professionalism: Is the tone appropriate?
5. Clarity: Is it easy to understand?

Provide:
1. Overall quality score (0.0 to 1.0)
2. Brief evaluation (max 100 words)

Format your response as:
SCORE: [0.0-1.0]
EVALUATION: [your evaluation]"""
        )

    def evaluate_response(
        self,
        ticket: str,
        response: str,
        category: str
    ) -> Tuple[float, str]:
        """
        Evaluate an agent response

        Args:
            ticket: Original ticket text
            response: Agent's response
            category: Ticket category

        Returns:
            Tuple of (quality_score, evaluation_text)
        """
        try:
            prompt = self.eval_prompt.format(
                ticket=ticket,
                response=response,
                category=category
            )

            result = self.llm.invoke(prompt)
            evaluation = result.content

            # Parse score
            score = 0.5  # default
            eval_text = evaluation

            if "SCORE:" in evaluation:
                lines = evaluation.split('\n')
                for line in lines:
                    if line.startswith("SCORE:"):
                        try:
                            score = float(line.split("SCORE:")[1].strip())
                            score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
                        except:
                            pass
                    elif line.startswith("EVALUATION:"):
                        eval_text = line.split("EVALUATION:")[1].strip()

            return score, eval_text

        except Exception as e:
            return 0.5, f"Evaluation failed: {str(e)}"

    def calculate_confidence(
        self,
        agent_name: str,
        response_length: int,
        has_search_results: bool = False
    ) -> float:
        """
        Calculate confidence score based on heuristics

        Args:
            agent_name: Name of the agent
            response_length: Length of response in characters
            has_search_results: Whether search was used

        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.7  # Base confidence

        # Adjust based on response length
        if response_length < 50:
            confidence -= 0.2
        elif response_length > 200:
            confidence += 0.1

        # Boost if search was used
        if has_search_results:
            confidence += 0.15

        # Agent-specific adjustments
        if agent_name == "classifier":
            confidence += 0.1  # Classifier is usually confident

        return max(0.0, min(1.0, confidence))

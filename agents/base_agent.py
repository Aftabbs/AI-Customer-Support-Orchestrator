"""Base Agent Class"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.llm_config import get_llm


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, name: str, description: str, temperature: float = 0.3):
        """
        Initialize base agent

        Args:
            name: Agent name
            description: Agent description
            temperature: LLM temperature
        """
        self.name = name
        self.description = description
        self.temperature = temperature
        self.llm = get_llm(temperature=temperature)

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return output

        Args:
            input_data: Input data dictionary

        Returns:
            Output data dictionary
        """
        pass

    def format_response(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format agent response

        Args:
            content: Response content
            metadata: Optional metadata

        Returns:
            Formatted response dictionary
        """
        response = {
            "agent": self.name,
            "content": content,
            "metadata": metadata or {}
        }
        return response

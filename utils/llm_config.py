"""LLM Configuration Module"""
import os
from typing import Optional
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.3, max_tokens: int = 2048, model: Optional[str] = None) -> ChatGroq:
    """
    Get configured LLM instance with Groq

    Args:
        temperature: Model temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
        model: Model name (defaults to env variable)

    Returns:
        ChatGroq instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    model_name = model or os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    return ChatGroq(
        api_key=api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

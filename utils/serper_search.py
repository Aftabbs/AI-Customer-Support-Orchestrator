"""Web Search Module using Serper API"""
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def search_web(query: str, num_results: int = 3) -> List[Dict[str, str]]:
    """
    Search the web using Serper API

    Args:
        query: Search query string
        num_results: Number of results to return

    Returns:
        List of search results with title, link, and snippet
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [{"title": "Search unavailable", "link": "", "snippet": "SERPER_API_KEY not configured"}]

    url = "https://google.serper.dev/search"

    payload = {
        "q": query,
        "num": num_results
    }

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })

        return results if results else [{"title": "No results", "link": "", "snippet": "No search results found"}]

    except Exception as e:
        return [{"title": "Search error", "link": "", "snippet": f"Error: {str(e)}"}]

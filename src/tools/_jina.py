# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import *

import requests

from src.config.search_config import search_config
from src.tools._search import SearchClient, SearchResult

class JinaSearchClient(SearchClient):
    """Client for searching web using Jina HTTP API"""

    def __init__(self):
        # Initialize configuration from search config
        self._url = "https://s.jina.ai/"
        self._headers = {
            "Authorization": f"Bearer {search_config.jina_api_key}",
            "Accept": "application/json",
            "X-Retain-Images": "none",
            "X-Timeout": str(search_config.timeout),
        }

    def search(self, query: str, top_n: int) -> List[SearchResult]:
        """
        Perform a web search and retrieve results

        Args:
            query: Search query string
            top_n: Number of results to retrieve

        Returns:
            List of SearchResult objects containing search information
        """
        search_results: List[SearchResult] = []
        try:
            params = {
                "q": query,
                "num": top_n,
            }
            response = requests.get(self._url, headers=self._headers, params=params)
            response.raise_for_status()
            result = response.json()
            for data in result.get("data", []):
                search_results.append(
                    SearchResult(
                        url=data.get("url", ""),
                        title=data.get("title", ""),
                        summary=data.get("description", ""),
                        content=data.get("content", ""),
                        date=data.get("publishedTime", ""),
                    )
                )
        except Exception as e:
            print(f"Error in Jina search: {e}")
            return []
        return search_results

if __name__ == "__main__":
    # Example usage
    client = JinaSearchClient()
    query = "What is the best pc game in 2024?"
    top_n = 5
    results = client.search(query, top_n)
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Title: {result.title}")
        print(f"Summary: {result.summary}")
        print(f"Content: {result.content[:200]}...")

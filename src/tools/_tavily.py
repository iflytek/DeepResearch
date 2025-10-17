# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import *

import tavily

from src.config.search_config import search_config
from src.tools._search import SearchClient, SearchResult

class TavilySearchClient(SearchClient):
    """Client for searching web using Tavily SDK"""
    def __init__(self):
        self._client = tavily.TavilyClient(api_key=search_config.tavily_api_key)

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
            search_response = self._client.search(
                query=query,
                max_results=top_n,
                include_raw_content=True
            )
            for search_result in search_response.get('results', []):
                search_results.append(SearchResult(
                    url=search_result.get('url', ''),
                    title=search_result.get('title', ''),
                    summary=search_result.get('content', ''),
                    content=search_result.get('raw_content', ''),
                    date=''
                ))

        except Exception as e:
            print(f"Error in Tavily search: {e}")
        
        return search_results

# test
if __name__ == "__main__":
    client = TavilySearchClient()
    results = client.search("What is the best pc game in 2024?", 5)
    for result in results:
        print(result.title)
        print(result.summary)
        print(result.content)
        print("---")
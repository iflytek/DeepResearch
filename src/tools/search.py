# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import *
import asyncio

from src.config.search_config import search_config
from src.tools import _search
from src.tools._jina import JinaSearchClient
from src.tools._tavily import TavilySearchClient

SearchResult = _search.SearchResult


class SearchClient:
    """Search client factory"""
    _client: _search.SearchClient
    def __init__(self) -> None:
        if search_config.engine == "jina":
            self._client = JinaSearchClient()
        elif search_config.engine == "tavily":
            self._client = TavilySearchClient()
        else:
            raise ValueError(f"Unknown search engine: {search_config.engine}")

    def search(self, query: str, top_n: int) -> List[SearchResult]:
        """
        Perform a web search and retrieve results

        Args:
            query: Search query string
            top_n: Number of results to retrieve

        Returns:
            List of SearchResult objects containing search information
        """
        return self._client.search(query, top_n)

if __name__ == "__main__":
    # Example usage
    search_client = SearchClient()
    results = search_client.search("Python asyncio", 2)
    for result in results:
        print(f'{result.title}: {result.url} ({result.summary})')
        print('--------------------------------------------------')
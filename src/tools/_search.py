# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import *
from dataclasses import dataclass

@dataclass(kw_only=True)
class SearchResult:
    """Data structure to hold search result information"""
    url: str
    title: str
    summary: str
    content: str
    date: str = ""
    id: int = 0

class SearchClient:
    """Base class for search clients"""
    def search(self, query: str, top_n: int) -> List[SearchResult]:
        """
        Perform a web search and retrieve results

        Args:
            query: Search query string
            top_n: Number of results to retrieve

        Returns:
            List of SearchResult objects containing search information
        """
        raise NotImplementedError("Subclasses must implement search method")

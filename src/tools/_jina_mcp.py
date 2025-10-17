# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import *
import re
import asyncio

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from src.config.search_config import search_config
from src.tools._search import SearchClient, SearchResult


class JinaMcpSearchClient:
    """Client for searching web using Jina API with MCP-SSE"""

    def __init__(self):
        # Initialize configuration from search config
        self._server_url = "https://mcp.jina.ai/sse"
        self._auth_token = search_config.jina_api_key
        self._timeout = search_config.timeout

        # Compile regex patterns once for efficiency
        self._title_re = re.compile(r'title: (.*?)(?=\n)', re.DOTALL)
        self._url_re = re.compile(r'url: (.*?)(?=\n)', re.DOTALL)
        self._snippet_re = re.compile(r'snippet: (.*)', re.DOTALL)
        self._content_re = re.compile(r'content: (.*)', re.DOTALL)

    async def search(self, query: str, top_n: int) -> List[SearchResult]:
        """
        Perform a web search and retrieve results

        Args:
            query: Search query string
            top_n: Number of results to retrieve

        Returns:
            List of SearchResult objects containing search information
        """
        async with sse_client(
                url=self._server_url,
                headers={"Authorization": f"Bearer {self._auth_token}"}
        ) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return await self._search(session, query, top_n)

    async def _search(self, session: ClientSession, query: str, top_n: int) -> List[SearchResult]:
        """
        Internal search implementation that handles the actual search logic

        Args:
            session: Active client session
            query: Search query string
            top_n: Number of results to retrieve

        Returns:
            List of SearchResult objects
        """
        search_results = []

        try:
            # Perform web search
            search_tool_result = await session.call_tool(
                name="search_web",
                arguments={"query": query, "num": top_n}
            )

            # Process each search result if content exists
            if hasattr(search_tool_result, "content"):
                # Create tasks for concurrent URL processing
                url_tasks = []
                for content in search_tool_result.content:
                    if content.type == "text":
                        # Extract metadata using regex
                        title_match = self._title_re.search(content.text)
                        url_match = self._url_re.search(content.text)
                        snippet_match = self._snippet_re.search(content.text)

                        # Validate required fields
                        if not (title_match and url_match and snippet_match):
                            continue

                        title = title_match.group(1).strip()
                        url = url_match.group(1).strip()
                        snippet = snippet_match.group(1).strip().split('\ndate')[0]

                        # Create task for concurrent processing
                        url_tasks.append(self._fetch_url_content(
                            session, title, snippet, url
                        ))

                # Process all URLs concurrently
                if url_tasks:
                    results = await asyncio.gather(*url_tasks)
                    search_results = [r for r in results if r is not None]

        except Exception as e:
            print(f"Error during search for '{query}': {str(e)}")

        return search_results

    async def _fetch_url_content(
            self,
            session: ClientSession,
            title: str,
            snippet: str,
            url: str
    ) -> Optional[SearchResult]:
        """
        Fetch content from a URL asynchronously

        Args:
            session: Active client session
            title: Result title
            snippet: Result summary snippet
            url: URL to fetch content from

        Returns:
            SearchResult if successful, None otherwise
        """
        try:
            # Fetch content from URL
            read_result = await session.call_tool(
                name="read_url",
                arguments={"url": url}
            )

            # Extract and process content
            if hasattr(read_result, "content"):
                full_text = ''.join([
                    content.text for content in read_result.content
                    if content.type == "text"
                ])

                content_match = self._content_re.search(full_text)
                if content_match:
                    web_content = content_match.group(1).strip()
                    return SearchResult(url, title, snippet, web_content)

        except Exception as e:
            print(f"Error fetching content from {url}: {str(e)}")

        return None


if __name__ == "__main__":
    # Example usage
    async def main():
        client = JinaSearchClient()
        query = "What is the best pc game in 2024?"
        top_n = 5
        results = await client.search(query, top_n)

        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"Title: {result.title}")
            print(f"Summary: {result.summary}")
            print(f"Content: {result.content[:200]}...")


    asyncio.run(main())


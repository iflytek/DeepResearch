# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

#!/usr/bin/env python3
"""
MCP Server
four Tools
  1. arxiv_search / arxiv_read
  2. pubmed_search / pubmed_read
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from lxml import etree
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, ServerCapabilities
from mcp.server import InitializationOptions
from typing import cast

# Import local modules
from .arxiv import Client as ArxivClient, Query, SortBy, SortOrder
from .pubmed import PubMedService, PubMedSearchResult, PubMedFetchResult

STORAGE = Path(os.getenv("PAPER_STORAGE", "./paper_cache"))
STORAGE.mkdir(exist_ok=True)

arxiv_client = ArxivClient()
pubmed_service = PubMedService()


async def arxiv_search_async(
        query: str, max_results: int = 5, date_from: str = "", date_to: str = ""
) -> TextContent:
    try:
        q = Query(
            terms=_build_terms(query),
            max_page_number=1,
            max_results_per_page=50,
            sort_by=SortBy.SUBMITTED_DATE,
            sort_order=SortOrder.DESCENDING,
        )
        papers: List[Dict[str, Any]] = []
        for page in arxiv_client.search(q):
            if hasattr(page, 'error') and page.error:
                return TextContent(type="text", text=f"search error: {page.error}")
            if not page.feed or not page.feed.entry:
                break
            for ent in page.feed.entry:
                pub_day = _parse_day(ent.published or ent.updated or "")
                authors = [a.name for a in ent.author if a.name]
                pdf_url = next(
                    (lnk.href for lnk in ent.link if lnk.type == "application/pdf"), ""
                )
                arxiv_id = ent.id.split("/")[-1] if ent.id else ""
                p = {
                    "id": arxiv_id,
                    "title": ent.title or "",
                    "authors": authors,
                    "abstract": (ent.summary.body if ent.summary else "") or "",
                    "published": pub_day,
                    "url": pdf_url,
                }
                if date_from and p["published"] < date_from:
                    continue
                if date_to and p["published"] > date_to:
                    continue
                papers.append(p)

        papers = papers[:max_results] if max_results else papers
        for p in papers:
            (STORAGE / f"{p['id']}.json").write_text(
                json.dumps(p, ensure_ascii=False), encoding="utf8"
            )
        return TextContent(
            type="text",
            text=json.dumps({"papers": papers}, ensure_ascii=False, indent=2),
        )
    except Exception as e:
        return TextContent(type="text", text=f"arxiv search error: {e}")

def arxiv_search(query: str, max_results: int = 5, date_from: str = "", date_to: str = "") -> str:
    """
    Synchronous wrapper for arxiv_search_async
    Returns: JSON string with search results
    """
    result = asyncio.run(arxiv_search_async(query, max_results, date_from, date_to))
    return result.text


async def arxiv_read_async(paper_id: str) -> TextContent:
    try:
        meta_path = STORAGE / f"{paper_id}.json"
        pdf_path = STORAGE / f"{paper_id}.pdf"
        md_path = STORAGE / f"{paper_id}.md"

        if not meta_path.exists():
            q = Query(article_ids=[paper_id], max_results_per_page=1)
            pages = list(arxiv_client.search(q))
            if not pages or hasattr(pages[0], 'error') and pages[0].error or not pages[0].feed.entry:
                return TextContent(type="text", text="can not find paper")
            ent = pages[0].feed.entry[0]
            pub_day = _parse_day(ent.published or ent.updated or "")
            authors = [a.name for a in ent.author if a.name]
            pdf_url = next(
                (lnk.href for lnk in ent.link if lnk.type == "application/pdf"), ""
            )
            p = {
                "id": paper_id,
                "title": ent.title or "",
                "authors": authors,
                "abstract": (ent.summary.body if ent.summary else "") or "",
                "published": pub_day,
                "url": pdf_url,
            }
            meta_path.write_text(json.dumps(p, ensure_ascii=False), encoding="utf8")
        else:
            p = json.loads(meta_path.read_text(encoding="utf8"))

        if not pdf_path.exists():
            err = arxiv_client.download_paper(paper_id, str(STORAGE))
            if err:
                return TextContent(type="text", text=f"download PDF error: {err}")

        if not md_path.exists():
            try:
                import pymupdf4llm
            except ImportError:
                return TextContent(
                    type="text", text="please install pymupdf4llm first: pip install pymupdf4llm"
                )
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _pdf2md, pdf_path, md_path)

        md_text = md_path.read_text(encoding="utf8")
        meta = {k: p[k] for k in ("title", "id", "authors", "published", "url", "abstract")}
        return TextContent(
            type="text",
            text=json.dumps({"meta": meta, "markdown": md_text}, ensure_ascii=False),
        )
    except Exception as e:
        return TextContent(type="text", text=f"arxiv read error: {e}")

def arxiv_read(paper_id: str) -> str:
    """
    Synchronous wrapper for arxiv_read_async
    Returns: JSON string with paper content
    """
    result = asyncio.run(arxiv_read_async(paper_id))
    return result.text


async def pubmed_search_async(
        query: str, max_results: int = 5, date_from: str = "", date_to: str = ""
) -> TextContent:
    try:

        url = pubmed_service.generate_pubmed_search_url(
            query=query,
            start_date=date_from or "1900/01/01",
            end_date=date_to or "2100/12/31",
            num_results=max_results,
        )
        resp = await asyncio.get_event_loop().run_in_executor(
            None, lambda: requests.get(url, timeout=30)
        )
        resp.raise_for_status()

        root = etree.fromstring(resp.content)
        id_list = root.xpath("//IdList/Id/text()")

        if not id_list:
            return TextContent(type="text", text="can not find PubMed paper")

        fetch_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
            f"db=pubmed&id={','.join(id_list)}&retmode=xml"
        )
        fetch_resp = await asyncio.get_event_loop().run_in_executor(
            None, lambda: requests.get(fetch_url, timeout=30)
        )
        fetch_resp.raise_for_status()
        fetch_root = etree.fromstring(fetch_resp.content)

        papers = []
        for article in fetch_root.xpath("//PubmedArticle"):
            pmid = "".join(article.xpath(".//PMID/text()"))
            title = "".join(article.xpath(".//ArticleTitle/text()"))
            abstract = "".join(article.xpath(".//Abstract/AbstractText/text()"))
            authors = article.xpath(".//Author/LastName/text()")
            pub_year = "".join(article.xpath(".//PubDate/Year/text()"))
            pub_month = "".join(article.xpath(".//PubDate/Month/text()"))
            doi = "".join(article.xpath(".//ArticleId[@IdType='doi']/text()"))

            papers.append(
                {
                    "id": pmid,
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "published": f"{pub_year}-{pub_month}",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "doi": doi,
                }
            )

        for p in papers:
            (STORAGE / f"pubmed_{p['id']}.json").write_text(
                json.dumps(p, ensure_ascii=False), encoding="utf8"
            )

        return TextContent(
            type="text",
            text=json.dumps({"papers": papers}, ensure_ascii=False, indent=2),
        )
    except Exception as e:
        return TextContent(type="text", text=f"pubmed search error: {e}")

def pubmed_search(query: str, max_results: int = 5, date_from: str = "", date_to: str = "") -> str:
    """
    Synchronous wrapper for pubmed_search_async
    Returns: JSON string with search results
    """
    result = asyncio.run(pubmed_search_async(query, max_results, date_from, date_to))
    return result.text


async def pubmed_read_async(paper_id: str) -> TextContent:
    try:
        meta_path = STORAGE / f"pubmed_{paper_id}.json"
        pdf_path = STORAGE / f"pubmed_{paper_id}.pdf"
        md_path = STORAGE / f"pubmed_{paper_id}.md"

        if not meta_path.exists():

            url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
                f"db=pubmed&id={paper_id}&retmode=xml"
            )
            resp = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(url, timeout=30)
            )
            resp.raise_for_status()
            root = etree.fromstring(resp.content)
            article = root.xpath("//PubmedArticle")[0]
            pmid = "".join(article.xpath(".//PMID/text()"))
            title = "".join(article.xpath(".//ArticleTitle/text()"))
            abstract = "".join(article.xpath(".//Abstract/AbstractText/text()"))
            authors = article.xpath(".//Author/LastName/text()")
            pub_year = "".join(article.xpath(".//PubDate/Year/text()"))
            pub_month = "".join(article.xpath(".//PubDate/Month/text()"))
            doi = "".join(article.xpath(".//ArticleId[@IdType='doi']/text()"))

            p = {
                "id": pmid,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published": f"{pub_year}-{pub_month}",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "doi": doi,
            }
            meta_path.write_text(json.dumps(p, ensure_ascii=False), encoding="utf8")
        else:
            p = json.loads(meta_path.read_text(encoding="utf8"))

        doi = p.get("doi")
        if not doi:
            return TextContent(type="text", text="DOI is empty")
        if not pdf_path.exists():
            try:
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(
                    None, pubmed_service.download_pubmed_paper, doi, f"pubmed_{paper_id}", str(STORAGE)
                )
                if not success:
                    return TextContent(type="text", text="download PDF error: download failed")
            except Exception as e:
                return TextContent(type="text", text=f"download PDF exception: {str(e)}")

        # PDF to Markdown
        if not md_path.exists():
            try:
                import pymupdf4llm
            except ImportError:
                return TextContent(
                    type="text", text="please install pymupdf4llm first: pip install pymupdf4llm"
                )
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _pdf2md, pdf_path, md_path)

        md_text = md_path.read_text(encoding="utf8")
        meta = {k: p[k] for k in ("title", "id", "authors", "published", "url", "abstract")}
        return TextContent(
            type="text",
            text=json.dumps({"meta": meta, "markdown": md_text}, ensure_ascii=False),
        )
    except Exception as e:
        return TextContent(type="text", text=f"pubmed read error: {e}")

def pubmed_read(paper_id: str) -> str:
    """
    Synchronous wrapper for pubmed_read_async
    Returns: JSON string with paper content
    """
    result = asyncio.run(pubmed_read_async(paper_id))
    return result.text


def _build_terms(raw: str) -> str:
    parts = raw.strip().split()
    return " AND ".join(f"all:{p}" for p in parts if p)


def _parse_day(dt_str: str) -> str:
    if not dt_str:
        return ""
    try:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    except Exception:
        return ""


def _pdf2md(pdf_path: Path, md_path: Path) -> None:
    import pymupdf4llm
    md = pymupdf4llm.to_markdown(str(pdf_path), show_progress=False)
    md_path.write_text(md, encoding="utf8")


server = Server("paper-server")


@server.list_tools()
async def list_tools():
    return [
        {
            "name": "arxiv_search",
            "description": "Search for papers on arXiv with advanced filtering. ArXiv has over 1.5 million open "
                           "access papers in mathematics, physics, computer science, econometrics, econometrics, "
                           "statistics, electronic engineering, systems science, economics, and other fields.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 5},
                    "date_from": {"type": "string", "default": ""},
                    "date_to": {"type": "string", "default": ""},
                },
                "required": ["query"],
            },
        },
        {
            "name": "arxiv_read",
            "description": "Read the full content of a paper in markdown format by paper_id from arxiv.",
            "inputSchema": {
                "type": "object",
                "properties": {"paper_id": {"type": "string"}},
                "required": ["paper_id"],
            },
        },
        {
            "name": "pubmed_search",
            "description": "Search for papers on PubMed with advanced filtering.PubMed is a database with over 35 "
                           "million citations for biomedical literature from MEDLINE, life science journals, "
                           "and online books.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 5},
                    "date_from": {"type": "string", "default": ""},
                    "date_to": {"type": "string", "default": ""},
                },
                "required": ["query"],
            },
        },
        {
            "name": "pubmed_read",
            "description": "Read the full content of a paper in markdown format by paper_id from pubmed.",
            "inputSchema": {
                "type": "object",
                "properties": {"paper_id": {"type": "string"}},
                "required": ["paper_id"],
            },
        },
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "arxiv_search":
        return await arxiv_search_async(**arguments)
    if name == "arxiv_read":
        return await arxiv_read_async(**arguments)
    if name == "pubmed_search":
        return await pubmed_search_async(**arguments)
    if name == "pubmed_read":
        return await pubmed_read_async(**arguments)
    raise ValueError(f"Unknown tool {name}")

# Export the synchronous functions for external use
__all__ = ['arxiv_search', 'arxiv_read', 'pubmed_search', 'pubmed_read']


EMPTY_SERVER_CAPABILITIES = ServerCapabilities(
    experimental={},
    logging=None,
    prompts=None,
    resources=None,
    tools=None,
)


async def main():
    async with stdio_server() as (reader, writer):
        await server.run(
            reader,
            writer,
            initialization_options=cast(
                InitializationOptions,
                {
                    "server_name": "paper-server",
                    "server_version": "0.2.0",
                    "capabilities": EMPTY_SERVER_CAPABILITIES,
                },
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())

# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

# Export the four main functions from paper_mcp_server
from .paper_mcp_server import arxiv_search, arxiv_read, pubmed_search, pubmed_read

__all__ = ['arxiv_search', 'arxiv_read', 'pubmed_search', 'pubmed_read']

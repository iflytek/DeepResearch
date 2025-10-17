# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

#!/usr/bin/env python3
"""
test paper_mcp_server
"""
import json
from src.mcp import arxiv_search, arxiv_read, pubmed_search, pubmed_read


def test_arxiv_search():
    print("\n=== test ArXiv search===")
    try:
        results = arxiv_search("machine learning", max_results=1)
        print(f"arxiv search result: {results}")
        data = json.loads(results)
        if data.get('papers'):
            print(f"get {len(data['papers'])} paper")
            print(f"first paper title: {data['papers'][0]['title']}")
            return data['papers'][0]['id']
        else:
            print("arxiv find no paper")
            return None
    except Exception as e:
        print(f"arxiv search test error: {e}")
        return None

def test_arxiv_read(paper_id):
    """test arXiv read"""
    if not paper_id:
        print("\n=== get no paper id ===")
        return

    try:
        content = arxiv_read(paper_id)
        print(f"get paper content")

        data = json.loads(content)
        if 'meta' in data:
            print(f"paper title: {data['meta']['title']}")
            print(f"author: {', '.join(data['meta']['authors'])}")
            print(f"abstract length: {len(data['meta']['abstract'])} words")
        if 'markdown' in data:
            print(f"Markdown length: {len(data['markdown'])} word")
    except Exception as e:
        print(f"arxiv read test failed: {e}")

def test_pubmed_search():
    """test PubMed search"""
    print("\n=== test PubMed search ===")
    try:
        results = pubmed_search("covid-19", max_results=1)
        print(f"search result: {results}")

        data = json.loads(results)
        if data.get('papers'):
            print(f"get {len(data['papers'])} paper")
            print(f"first paper title: {data['papers'][0]['title']}")
            return data['papers'][0]['id']
        else:
            print("pubmed find no paper")
            return None
    except Exception as e:
        print(f"pubmed search error: {e}")
        return None

def test_pubmed_read(paper_id):
    """test PubMed read"""
    if not paper_id:
        print("\n no paper id")
        return

    try:

        content = pubmed_read(paper_id)
        print(f"get paper content")
        print(f"paper length: {len(content)}")
        print(f"100 words: {repr(content[:100]) if len(content) > 0 else 'no content'}")
        data = json.loads(content)
        if 'meta' in data:
            print(f"paper title: {data['meta']['title']}")
            print(f"author: {', '.join(data['meta']['authors'])}")
            print(f"abstract length: {len(data['meta']['abstract'])} words")
        if 'markdown' in data:
            print(f"Markdown length: {len(data['markdown'])} words")
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
    except Exception as e:
        print(f"pubmed read error: {e}")

def main():
    """test all tools"""

    arxiv_paper_id = test_arxiv_search()
    test_arxiv_read(arxiv_paper_id)
    

    pubmed_paper_id = test_pubmed_search()
    test_pubmed_read(pubmed_paper_id)
    
    print("\n=== test finished ===")

if __name__ == "__main__":
    main()
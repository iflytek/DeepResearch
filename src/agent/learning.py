# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
from typing import List

from langchain_core.runnables import RunnableConfig

from .message import ReportState
from .deepsearch import DeepSearch, DeepSearchResult
from src.config.workflow_config import workflow_configs
from src.tools.search import SearchResult


def learning_node(state: ReportState, config: RunnableConfig):
    outline = state.get("outline")
    knowledge = state.get("knowledge", [])
    search_id = state.get("search_id", 1)
    for chapter in outline.sub_chapter:
        ds = DeepSearch(outline.title,
                        chapter.title,
                        [title for title in chapter.sub_chapter],
                        chapter.summary,
                        config.get("configurable", {}).get("depth", 3),
                        workflow_configs.get("search", {}).get("topN", 5))
        results = ds.deep_search()
        search_results = get_all_search_results(results)
        for key, value in search_results.items():
            knowledge += [
                {"id": search_id + i, "content": result.content, "url": result.url}
                for i, result in enumerate(value)
            ]
            search_id += len(value)

        chapter.learning_knowledge = [
            {"insight": re_knowledge.insight,
             "real_reference": get_real_reference_ids(knowledge, re_knowledge.references)}
            for re_knowledge in results.re_knowledge
        ]
    return {
        "outline": outline,
        "search_id": search_id,
        "knowledge": knowledge,
    }


def get_all_search_results(result: DeepSearchResult) -> List[SearchResult]:
    search_result = {}
    while result:
        search_result = search_result | result.search_result
        result = result.children
    return search_result


def get_real_reference_ids(search_results: List, references: List[SearchResult]) -> List[int]:
    url_to_id = {search["url"]: search["id"] for search in search_results}

    reference_ids = []
    seen = set()

    for reference in references:
        if reference.url in url_to_id:
            ref_id = url_to_id[reference.url]
            if ref_id not in seen:
                reference_ids.append(ref_id)
                seen.add(ref_id)

    reference_ids.sort()
    return reference_ids

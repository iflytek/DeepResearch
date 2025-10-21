# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
import json
from typing import List

from .message import ReportState, Chapter
from src.llms.llm import llm
from src.prompts.template import apply_prompt_template
from src.utils.print_util import colored_print
from langgraph.types import Command
from src.tools.search import SearchClient
from src.config.workflow_config import workflow_configs
import logging
from datetime import datetime
import re
from src.utils.parse_model_res import extract_xml_content

logger = logging.getLogger(__name__)


def outline_search_node(state: ReportState):
    """Search some knowledge for outline."""
    sq = llm(llm_type="query_generation", messages=apply_prompt_template(
        prompt_name="outline/outline_sq",
        state={
            "now": datetime.now().strftime("%a %b %d %Y"),
            "query": state.get("topic"),
            "reasoning": state.get("logic")
        }
    ), stream=False)
    search_queries = extract_xml_content(sq, "search")
    search_client = SearchClient()
    search_id = state.get("search_id", 1)
    outline_knowledge = state.get("knowledge", [])
    for search_query in search_queries:
        try:
            colored_print(f'Searching: {search_query}', color="purple")
            results = search_client.search(search_query,
                                                 workflow_configs.
                                                 get("search", {}).
                                                 get("topN", 5))
            outline_knowledge += [
                {"id": search_id + i, "content": result.content, "url": result.url}
                for i, result in enumerate(results)
            ]
            search_id += len(results)
            for result in results:
                colored_print(f'{result.title} -- ', color="cyan", end="")
                colored_print(result.url, color="blue", underline=True)
        except Exception as e:
            logger.error(f"search {search_query} error: {e}")
    return {
        "search_id": search_id,
        "knowledge": outline_knowledge,
    }

def outline_node(state: ReportState):
    """Generate outline for this report"""
    outline = ""
    for think, content in llm(llm_type="planner", messages=apply_prompt_template(
            prompt_name="outline/outline",
            state={
                "domain": state.get("domain"),
                "now": datetime.now().strftime("%a %b %d %Y"),
                "query": state.get("topic"),
                "reasoning": state.get("logic"),
                "thinking": state.get("details"),
                "reference": outline_knowledge_2_str(state.get("outline_knowledge", ""))
            }
    ), stream=True):
        if think:
            colored_print(think, color="orange", end="")
        if content:
            outline += content
    try:
        chapter = parse_outline(outline)
    except ValueError as e:
        logger.error(f"outline is invalid: {outline}")
        return Command(goto="__end__",
                      update={
                          "output": {
                              "message": outline
                          }})
    colored_print("\n\n" + chapter.get_outline(), color="green", end="")
    return Command(goto="learning", update={
        "outline": chapter
    })


def outline_knowledge_2_str(outline_knowledge, max_length=100000):
    max_col = 0
    for knowledge in outline_knowledge:
        max_col = max(max_col, len(knowledge))
    result = []
    total_length = 0

    for i in range(max_col):
        for knowledge in outline_knowledge:
            if i < len(knowledge):
                content = knowledge[i].get("content", "")
                if total_length + len(content) > max_length:
                    break
                result.append({"content": content, "id": knowledge[i].get("id", 0)})
                total_length += len(content)

    return json.dumps(result)


markdown_regexp = re.compile(r'(?s)```\s*markdown\n(.*)```')
title_regexp = re.compile(r'^(#+)\s+(.*)')


def parse_outline(outline_str: str) -> Chapter:
    # 使用markdown_regexp提取markdown代码块内容
    markdown_match = markdown_regexp.search(outline_str)
    if markdown_match:
        outline_str = markdown_match.group(1)

    root = Chapter(id=0, level=0)
    current_chapter = root
    id_counter = 0
    title_list: List[str] = []

    lines = outline_str.split('\n')

    # 解析标题并构建章节结构
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 使用title_regexp匹配标题格式
        title_match = title_regexp.match(line)
        if title_match:
            id_counter += 1
            level = len(title_match.group(1))
            title = title_match.group(2)

            # 找到合适的父节点
            # 增加安全检查，防止current_chapter为None
            while current_chapter and current_chapter.level >= level:
                current_chapter = current_chapter.parent_chapter

            # 再次检查current_chapter是否为None
            if not current_chapter:
                current_chapter = root

            # 创建新章节
            new_chapter = Chapter(id=id_counter, level=level, title=title, parent_chapter=current_chapter)

            current_chapter.sub_chapter.append(new_chapter)
            current_chapter = new_chapter
            title_list.append(title_match.group(0))
        else:
            summary_match = extract_xml_content(line, "summary")
            if summary_match:
                current_chapter.summary = summary_match[0]

            # 使用thinking_regexp提取思路
            thinking_match = extract_xml_content(line, "thinking")
            if thinking_match:
                current_chapter.thinking = thinking_match[0]

    if not root.sub_chapter:
        raise ValueError("no valid chapter found")

    # 清理根节点的父引用
    root_chapter = root.sub_chapter[0]
    root_chapter.parent_chapter = None
    parent_to_nil(root_chapter.sub_chapter)

    # 转换为字典
    return root_chapter


def parent_to_nil(chapters: List[Chapter]) -> None:
    for chapter in chapters:
        chapter.parent_chapter = None
        parent_to_nil(chapter.sub_chapter)

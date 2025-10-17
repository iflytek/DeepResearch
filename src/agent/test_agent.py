# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import pytest
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from .prep import rewrite_node, classify_node, generic_node, clarify_node
from .outline import outline_search_node, outline_node, outline_knowledge_2_str
from langgraph.types import Command
from src.tools.search import SearchResult
from typing import Generator
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development."
                                          "prospects.")],
    }

@pytest.fixture
def mock_classify_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development."
                                          "prospects.")],
        "topic": "Please introduce iFlytek to me and help me analyze its development prospects."
    }

@pytest.fixture
def mock_clarify_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development.")],
        "domain": "Company Research"
    }


@pytest.fixture
def mock_rewrite_state():
    return {
        "messages": [
            HumanMessage(content='The main customers of the computing power leasing industry.'),
            AIMessage(content='''To help accurately analyze the customer structure of the computing power leasing industry, could you please provide the following information:
1. * * Regional Scope * *: Are you interested in the Chinese market, major global regions such as North America and Asia Pacific, or specific countries/regions?
2. * * Customer type * *: Is it necessary to distinguish between enterprise customers (such as Internet companies and scientific research institutions) and individual developers, or further refine them to industry fields (such as AI training, film and television rendering)?
3. * * Analysis Dimension * *: Is it more focused on customer size distribution, demand driving factors, or key criteria for customers to choose service providers?'''),
            HumanMessage(content='''1. Chinese market;
             2. Distinguish between corporate and individual clients;
             3. Analyze customer selection of service provider labels'''),
        ],
    }

@pytest.fixture
def mock_outline_search_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development.")],
        "domain": "Company Research",
        "topic": "Please introduce iFlytek to me and help me analyze its development.",
        "logic": "Research the company background → Analyze industry landscape and emerging trends → Consolidate financial performance and key indicators → Identify core business segments and growth drivers → Integrate market dynamics to highlight potential risks",
        "details": "mock reasoning",
        "knowledge": [],
        }

@pytest.fixture
def mock_outline_state():
    return {
        "messages": [HumanMessage(content="Please introduce iFlytek to me and help me analyze its development.")],
        "domain": "Company Research",
        "topic": "Please introduce iFlytek to me and help me analyze its development.",
        "details": "Research the company background → Analyze industry landscape and emerging trends → Consolidate financial performance and key indicators → Identify core business segments and growth drivers → Integrate market dynamics to highlight potential risks",
        "logic": "mock reasoning",
        "knowledge": [[{"id": 1, "content": "", "url": "http://test.com", "title": "empty", "summary": "mock"}]],
        }


def test_generic_node_response(
    mock_state
):
    result = generic_node(mock_state)
    assert isinstance(result, dict)
    assert isinstance(result["output"], dict)
    assert isinstance(result["output"]["stream_message"], Generator)


def test_classify_node_response(
    mock_classify_state
):
    result = classify_node(mock_classify_state)
    assert isinstance(result, Command)
    assert result.goto == "clarify"
    assert isinstance(result.update, dict)
    assert result.update["domain"] == "Company Research"
    assert isinstance(result.update["logic"], str)
    assert isinstance(result.update["details"], str)


def test_clarify_node_response(
    mock_clarify_state
):
    result = clarify_node(mock_clarify_state)
    assert isinstance(result, Command)
    assert result.goto == "__end__"
    assert isinstance(result.update, dict)
    assert isinstance(result.update["output"], dict)
    assert isinstance(result.update["output"]["stream_message"], Generator)


def test_rewrite_node_response(
    mock_rewrite_state
):
    result = rewrite_node(mock_rewrite_state)
    assert isinstance(result, Command)
    assert isinstance(result.update, dict)
    assert isinstance(result.update["topic"], str)

def test_outline_search_node_response(
    mock_outline_search_state
):
    results = []
    required_keys = {"id", "content", "url", "title"}
    for updated_state in outline_search_node(mock_outline_search_state):
        results.append(updated_state)
        assert isinstance(updated_state, dict)
        assert isinstance(updated_state["knowledge"], list)
        assert len(updated_state["knowledge"]) == len(results)
        for knowledge in updated_state["knowledge"]:
            assert isinstance(knowledge, list)
            for single in knowledge:
                assert isinstance(single, dict)
                actual_keys = set(single.keys())
                assert required_keys.issubset(actual_keys)
        assert isinstance(updated_state["output"], dict)
        assert isinstance(updated_state["output"]["search_query"], str)
        assert isinstance(updated_state["output"]["search"], list)
        for search in updated_state["output"]["search"]:
            assert isinstance(search, SearchResult)


def test_outline_node_response(mock_outline_state):
    # 1. 定义模拟数据：LLM 输出的两帧数据
    mock_llm_output = [
        ("mock thinking", ""),  # 第一帧：只有 thinking，无 content
        ("", """```markdown
# Report Title
## I. Industry Landscape Overview
<summary>Comprehensively analyzes the current state and emerging trends of the XX industry, defining scope (technology, market, policy), key entities (leading players and new entrants), and main focus areas (competition and regulatory drivers) as the foundation for subsequent research.</summary>  
### 1.1 Technological Evolution: From Innovation to Maturity  
<thinking>Analyze the development path along the technology maturity curve, explaining the potential impact of each stage on the industry.</thinking>  
### 1.2 Market Landscape: Divergent Strategies Among Leading Firms  
<thinking>Focus on market share dynamics and conduct comparative analysis to reveal competitive differentiation.</thinking>  
...
## III. Outlook and Strategic Recommendations
<summary>Synthesizes key findings from the preceding chapters to form actionable strategic insights.</summary>  
<thinking>Adopt a conclusion-first approach, presenting core insights, then expanding arguments and recommendations step by step.</thinking>
```""")  # 第二帧：无 thinking，有 content
    ]

    # 2. 模拟 parse_outline 返回的 Chapter 对象
    mock_chapter = MagicMock()
    mock_chapter.get_outline.return_value = "解析后的大纲文本"  # 模拟章节的大纲文本

    with patch("src.llms.llm.llm") as mock_llm, \
            patch("src.prompts.template.apply_prompt_template") as mock_prompt:
        def llm_generator():
            for item in mock_llm_output:
                yield item

        mock_llm.return_value = llm_generator()
        mock_prompt.return_value = [SystemMessage(content="mock system message")]

        outputs = list(outline_node(mock_outline_state))

        mock_llm.assert_called_once_with(
            llm_type="planner",
            messages=mock_prompt.return_value,
            stream=True
        )

        expected_prompt_state = {
                "domain": mock_outline_state.get("domain"),
                "now": datetime.now().strftime("%a %b %d %Y"),
                "query": mock_outline_state.get("topic"),
                "reasoning": mock_outline_state.get("logic"),
                "thinking": mock_outline_state.get("details"),
                "reference": outline_knowledge_2_str(mock_outline_state.get("knowledge", ""))
            }
        mock_prompt.assert_called_once_with(
            prompt_name="outline/outline",
            state=expected_prompt_state
        )

        assert len(outputs) == 3

        first_output = outputs[0]
        assert "output" in first_output
        assert first_output["output"]["message"] == "mock thinking"
        assert "outline" not in first_output

        second_output = outputs[1]
        assert "output" in second_output
        assert second_output["output"]["message"] == ""
        assert "outline" not in second_output

        final_output = outputs[2]
        assert "outline" in final_output
        assert final_output["outline"] == mock_chapter

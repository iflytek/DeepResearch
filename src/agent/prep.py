# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
from langchain_core.runnables import RunnableConfig

from .message import ReportState
from src.llms.llm import llm
from src.prompts.template import apply_prompt_template
from src.utils import parse_model_res
from src.utils.print_util import colored_print
from langgraph.types import Command
from langchain_core.messages import AIMessage, HumanMessage
from src.data.category import get_analysis_data
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def preprocess_node(state: ReportState):
    """preprocess data"""
    messages = state.get("messages")
    converted_messages = []
    if isinstance(messages, list):
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content", "")  # 默认为空内容

                if role == "user":
                    converted = HumanMessage(content=content)
                    converted_messages.append(converted)
                elif role == "assistant":
                    converted = AIMessage(content=content)
                    converted_messages.append(converted)
            elif isinstance(msg, HumanMessage):
                converted_messages.append(msg)
            elif isinstance(msg, AIMessage):
                converted_messages.append(msg)
            else:
                try:
                    content = str(msg)
                    converted = HumanMessage(content=content)
                    converted_messages.append(converted)
                except Exception as e:
                    # 无法转换的情况（如特殊对象），直接丢弃
                    continue
    elif isinstance(messages, dict):
        role = messages.get("role")
        content = messages.get("content", "")  # 默认为空内容
        if role == "user":
            converted = HumanMessage(content=content)
            converted_messages.append(converted)
    elif isinstance(messages, HumanMessage):
        converted_messages.append(messages)
    else:
        try:
            content = str(messages)
            converted = HumanMessage(content=content)
            converted_messages.append(converted)
        except Exception as e:
            # For situations where conversion is not possible (such as special objects), discard them directly
            pass
    if not converted_messages:
        return Command(goto="__end__")
    elif len(converted_messages) == 1:
        return Command(update={"messages": converted_messages, "topic": converted_messages[0].content}, goto="classify")
    elif len(converted_messages) == 3:
        return Command(update={"messages": converted_messages}, goto="rewrite")
    # Starting from the third round, only the model will be called to reply
    else:
        return Command(update={"messages": converted_messages}, goto="generic")


def rewrite_node(state: ReportState):
    """Rewrite user requirements based on interaction history to obtain report topics"""
    rewrite = llm(llm_type="basic", messages=apply_prompt_template(
        prompt_name="prep/rewrite",
        state={
            "now": datetime.now().strftime("%a %b %d %Y"),
            "messages": state.get("messages")
        }
    ), stream=False)
    rewrite = parse_model_res.extract_xml_content(rewrite, "rewrite")
    if rewrite:
        return Command(
            update={
                "topic": rewrite[0]
            }
        )
    else:
        topic = ""
        for message in state.get("messages"):
            topic += message.type + ":" + message.content + "\n"
        return Command(
            update={
                "topic": topic
            }
        )


def classify_node(state: ReportState):
    """Classify user questions to write reports on different topics"""
    classify = llm(llm_type="basic", messages=apply_prompt_template(
        prompt_name="prep/classify",
        state={
            "query": state.get("topic")
        }
    ), stream=False)
    domain = parse_model_res.extract_xml_content(classify, "domain")
    if domain:
        domain = domain[0]
    else:
        logger.error(f"Classify result has no tag <domain>.")
        return Command(
            goto="generic",
        )
    # Only provide one round of clarification, and generate a report directly for the second round.
    try:
        logic, details = get_analysis_data(domain)
    except ValueError as e:
        # If the report details for the corresponding category cannot be found, reply with the generic model
        logger.warning(f"Currently, report generation in the {domain} domain is not supported.")
        return Command(
            goto="generic",
        )
    if len(state.get("messages")) == 1:
        return Command(
            update={
                "domain": domain,
                "logic": logic,
                "details": details,
            },
            goto="clarify",
        )
    else:
        return Command(
            update={
                "domain": domain,
                "logic": logic,
                "details": details,
            },
            goto="outline_search",
        )


def clarify_node(state: ReportState):
    """Clarify user issues, only clarify once"""
    clarify = llm(llm_type="clarify", messages=apply_prompt_template(
        prompt_name="prep/clarify",
        state={
            "query": state.get("topic"),
            "now": datetime.now().strftime("%a %b %d %Y"),
        }
    ), stream=False)
    if parse_model_res.extract_xml_content(clarify, "query"):
        return Command(
            goto="outline_sq",
        )
    confirm = parse_model_res.extract_xml_content(clarify, "confirm")
    if confirm:
        colored_print(confirm[0], color="green", end="")
        return Command(
            update={
              "output": {
                  "message": confirm[0]
              },
            },
            goto="__end__",
        )
    return Command(
        goto="generic",
    )


def generic_node(state: ReportState):
    try:
        response = ""
        for think, content in llm(llm_type="basic", messages=state.get("messages"), stream=True):
            if think:
                colored_print(think, color="orange", end="")
            if content:
                colored_print(content, color="green", end="")
                response += content
        return {"output": {"message": response}}
    except Exception as e:
        logger.error(f"An exception occurred during the call to the LLM: {e}")
# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License


# from llms.llm import llm
#
# print("=== Non-streaming Response ===")
# non_stream_response = llm("planner", "Hello! What's your name?", stream=False)
# print(non_stream_response)
#
# print("\n=== Streaming Response ===")
# for chunk in llm("planner", "Could you tell me a short joke?", stream=True):
#     print(chunk, end="", flush=True)
# print()
import asyncio
from typing import List, Union
from langgraph.types import Command

from src.agent.agent import build_agent
from langchain.schema import HumanMessage, AIMessage

graph = build_agent()


class PrintColor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


async def call_agent(
        messages: List[Union[HumanMessage, AIMessage]],
        max_depth: 3,
        save_as_html: True
) -> List[Union[HumanMessage, AIMessage]]:
    if not messages:
        raise ValueError("Input could not be empty")
    state = {
        "messages": messages
    }
    config = {
        "configurable": {
            "depth": max_depth,
            "save_as_html": save_as_html,
            "save_path": "./example/report"
        }
    }
    output = ""
    for message in graph.stream(
        input=state, config=config, stream_mode="values"
    ):
        if isinstance(message, Command):
            message = message.update
        if isinstance(message, dict) and "messages" in message:
            if "output" in message and isinstance(message["output"], dict):
                if "message" in message["output"]:
                    output = message["output"]["message"]
    messages.append(AIMessage(content=output))
    return messages


async def interactive_agent(max_depth: int = 3, save_as_html: bool = True):
    """
    Interactive function for conversing with the agent
    :param max_depth: Maximum depth for deepresearch.
    :param need_html: Save report as html in local.

    """
    messages: List[Union[HumanMessage, AIMessage]] = []

    welcome = "Welcome to iFlytek's DeepResearch!\n"
    input_prompt = "\nEnter your message and press Enter to send. \nType 'quit' to exit. \nType 'clear' to start a new session.\nPlease enter: "

    print(welcome)
    while True:
        try:
            user_input = input(input_prompt)
        except KeyboardInterrupt:
            print("\nProgram interrupted")
            break

        if user_input.lower() == 'quit':
            print("Exiting conversation, goodbye!")
            break
        if user_input.lower() == 'clear':
            messages = []
            print(welcome)
            continue

        messages.append(HumanMessage(content=user_input))

        print("Agent is processing...")
        messages = await call_agent(messages=messages, max_depth=max_depth, save_as_html=save_as_html)


if __name__ == '__main__':
    asyncio.run(interactive_agent(max_depth=1))


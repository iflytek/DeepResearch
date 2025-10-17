# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

import os
import importlib
import sys
from typing import Dict, List, Any
from langchain.schema import HumanMessage, SystemMessage

# Define directories containing prompt templates (relative or absolute paths)
PROMPTS_DIRS = [
    os.path.join(os.path.dirname(__file__), "generate"),
    os.path.join(os.path.dirname(__file__), "learning"),
    os.path.join(os.path.dirname(__file__), "outline"),
    os.path.join(os.path.dirname(__file__), "prep"),
]

# Get current directory and ensure it's in system path for proper module import
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def load_prompt_templates() -> Dict[str, str]:
    """
    Dynamically loads prompt templates from specified directories.

    Scans through all .py files in PROMPTS_DIRS (excluding __init__.py),
    imports them, and extracts PROMPT and SYSTEM_PROMPT variables.

    Returns:
        Dict[str, str]: Mapping of template names to their content
    """
    prompt_templates: Dict[str, str] = {}

    for prompts_dir in PROMPTS_DIRS:
        # Skip if directory doesn't exist
        if not os.path.isdir(prompts_dir):
            print(f"Warning: Prompt directory not found - {prompts_dir}")
            continue

        # Calculate relative path for proper module naming
        relative_root = os.path.relpath(prompts_dir, current_dir).replace(os.sep, ".")

        # Process each Python file in the directory
        for filename in os.listdir(prompts_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                # Extract base name and create module path
                prompt_base = filename[:-3]
                module_name = f"{relative_root}.{prompt_base}"
                template_key = f"{relative_root}/{prompt_base}"

                try:
                    # Dynamically import the module
                    module = importlib.import_module(module_name)

                    # Extract PROMPT if exists
                    if hasattr(module, "PROMPT"):
                        prompt_templates[template_key] = str(module.PROMPT).strip()

                    # Extract SYSTEM_PROMPT if exists
                    if hasattr(module, "SYSTEM_PROMPT"):
                        system_key = f"{template_key}_system"
                        prompt_templates[system_key] = str(module.SYSTEM_PROMPT).strip()

                except Exception as e:
                    print(f"Error loading {module_name}: {str(e)}")

    return prompt_templates


# Global storage for all loaded prompt templates
PROMPT_TEMPLATES: Dict[str, str] = load_prompt_templates()


def apply_prompt_template(
        prompt_name: str,
        state: Dict[str, Any]
) -> List:
    """
    Applies variables to a prompt template and returns formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Dictionary containing variables to inject into the template

    Returns:
        List of message dictionaries with "role" and "content"

    Raises:
        ValueError: If template is not found or missing required variables
    """
    messages = []

    # Process system prompt if available
    system_template_key = f"{prompt_name}_system"
    system_template = PROMPT_TEMPLATES.get(system_template_key)

    if system_template:
        try:
            system_content = system_template.format_map(state)
            messages.append(SystemMessage(content=system_content))
        except KeyError as e:
            raise ValueError(f"System prompt {prompt_name} missing variable: {str(e)}")

    user_template = PROMPT_TEMPLATES.get(prompt_name)
    if user_template:
        try:
            user_content = user_template.format_map(state)
            messages.append(HumanMessage(content=user_content))
        except KeyError as e:
            raise ValueError(f"Prompt {prompt_name} missing variable: {str(e)}")
    if "messages" in state:
        return messages + state["messages"]
    return messages


if __name__ == "__main__":
    # Example usage with generate template
    try:
        generate_messages = apply_prompt_template(
            prompt_name="generate/generate",
            state={
                "now": "2025-10-9",
                "query": "this is a query",
                "chapter_outline": "# report\n## chapter 1",
                "above": "",
                "outline": "# report\n## chapter 1\n## chapter 2",
                "reference": "some knowledge",
                "domain": "unknown",
            }
        )
        print("Results for generate/generate template:")
        for msg in generate_messages:
            print(f"{msg.type}: {msg.content[:50]}...")  # Truncated for display

    except Exception as e:
        print(f"Error with generate template: {str(e)}")

    # Example usage with classify template
    try:
        classify_messages = apply_prompt_template(
            prompt_name="prep/classify",
            state={
                "query": "this is a query",
                "messages": [HumanMessage("test")]
            }
        )
        print("\n---\nResults for classify/classify template:")
        for msg in classify_messages:
            print(f"{msg.type}: {msg.content[:50]}...")  # Truncated for display

    except Exception as e:
        print(f"Error with classify template: {str(e)}")


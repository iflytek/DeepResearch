# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

import toml
from pathlib import Path


def load_workflow_configs(config_path: Path = None) -> dict:
    """
    Load and parse LLM configuration file, return dictionary of all LLM config instances

    Args:
        config_path: Path to the configuration file. Defaults to 'llms.toml' in the current directory.

    Returns:
        Dictionary with configuration names as keys and BaseLLMConfig instances as values

    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file has an invalid format
    """
    config_path = config_path or Path(__file__).parent / "workflow.toml"

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load and validate raw configuration
    raw_config = toml.load(config_path)
    if not isinstance(raw_config, dict):
        raise ValueError("Invalid configuration file format. Expected a dictionary structure.")

    # Batch create configuration instances

    return raw_config


# Initialize configurations for import by other modules
workflow_configs = load_workflow_configs()

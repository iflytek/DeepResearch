# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

import toml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Type, TypeVar, Literal


# Define generic type variable for type hinting
T = TypeVar('T', bound='BaseLLMConfig')


@dataclass(kw_only=True)
class BaseLLMConfig:
    """Base LLM configuration class containing common configuration items for all LLMs"""
    base_url: str
    api_base: str
    model: str
    api_key: str

    @classmethod
    def from_dict(cls: Type[T], config_dict: Dict[str, str]) -> T:
        """
        Create an instance from a dictionary with type safety validation

        Args:
            config_dict: Dictionary containing LLM configuration parameters

        Returns:
            Instance of BaseLLMConfig or its subclass

        Raises:
            ValueError: If required fields are missing in the configuration
        """
        try:
            return cls(
                base_url=config_dict.get('base_url'),
                api_base=config_dict.get('api_base'),
                model=config_dict['model'],
                api_key=config_dict['api_key']
            )
        except KeyError as e:
            raise ValueError(f"Configuration missing required field: {e}") from e


def load_llm_configs(config_path: Path = None) -> Dict[str, BaseLLMConfig]:
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
    config_path = config_path or Path(__file__).parent / "llms.toml"

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load and validate raw configuration
    raw_config = toml.load(config_path)
    if not isinstance(raw_config, dict):
        raise ValueError("Invalid configuration file format. Expected a dictionary structure.")

    # Batch create configuration instances
    configs = {}
    for config_name, config_data in raw_config.items():
        configs[config_name] = BaseLLMConfig.from_dict(config_data)

    return configs


# Initialize configurations for import by other modules
llm_configs = load_llm_configs()

# Define LLM types
LLMType = Literal["basic", "clarify", "planner", "query_generation", "evaluate", "report"]

# Convenient access to individual configurations (optional, based on usage preferences)
basic_llm = llm_configs['basic']
clarify_llm = llm_configs['clarify']
planner_llm = llm_configs['planner']
query_generation_llm = llm_configs['query_generation']
evaluate_llm = llm_configs['evaluate']
report_llm = llm_configs['report']
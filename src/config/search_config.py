# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License


import toml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Type, TypeVar


# Define generic type variable for type hinting
T = TypeVar('T', bound='SearchConfig')


@dataclass(kw_only=True)
class SearchConfig:
    """Search engine configuration class containing search service parameters"""
    engine: str
    jina_api_key: str
    tavily_api_key: str
    timeout: int = 30  # Default timeout of 30 seconds

    @classmethod
    def from_dict(cls: Type[T], config_dict: Dict[str, str]) -> T:
        """
        Create an instance from a dictionary with validation

        Args:
            config_dict: Dictionary containing search configuration parameters

        Returns:
            Instance of SearchConfig

        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['engine']
        for field in required_fields:
            if field not in config_dict:
                raise ValueError(f"Configuration missing required field: {field}")

        # Validate timeout if provided
        timeout = config_dict.get('timeout', 30)
        try:
            timeout = int(timeout)
            if timeout < 1 or timeout > 300:
                raise ValueError("Timeout must be between 1 and 300 seconds")
        except (ValueError, TypeError):
            raise ValueError("Timeout must be a valid integer")

        return cls(
            engine=config_dict['engine'],
            jina_api_key=config_dict['jina_api_key'],
            tavily_api_key=config_dict['tavily_api_key'],
            timeout=timeout
        )


def load_search_config(config_path: Path = None) -> SearchConfig:
    """
    Load and parse search configuration file, return SearchConfig instance

    Args:
        config_path: Path to the configuration file.
                     Defaults to 'search.toml' in the current directory.

    Returns:
        SearchConfig instance containing search service configuration

    Raises:
        FileNotFoundError: If the configuration file does not exist
        ValueError: If the configuration file has an invalid format
    """
    config_path = config_path or Path(__file__).parent / "search.toml"

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load and validate raw configuration
    raw_config = toml.load(config_path)
    if not isinstance(raw_config, dict) or 'search' not in raw_config:
        raise ValueError("Invalid configuration file format. Expected [search] section.")

    # Create configuration instance from the [search] section
    return SearchConfig.from_dict(raw_config['search'])


# Initialize configurations for import by other modules
search_config = load_search_config()


# Example usage
if __name__ == "__main__":
    try:
        config = load_search_config()
        print("Loaded search configuration:")
        print(f"Engine: {config.engine}")
        print(f"API Key: {config.api_key[:4]}...{config.api_key[-4:]}")  # Masked for security
        print(f"Timeout: {config.timeout}s")
    except Exception as e:
        print(f"Error loading configuration: {e}")

"""
Configuration loading utilities for the newsfeed application.

This module centralizes all YAML configuration loading functionality,
providing a single place to manage how configuration files are read
and parsed throughout the application.
"""

import yaml
import importlib.resources


def load_sources_config() -> list:
    """
    Load news source configurations from the YAML configuration file.
    
    Returns:
        list: A list of dictionaries, where each dictionary represents a news
              source configuration with keys like 'name', 'type', 'url', etc.
    """
    config_path = importlib.resources.files("newsfeed.config").joinpath("sources_config.yaml")
    with config_path.open("r", encoding="utf-8") as f:
        # Parse YAML file content into Python data structures (list/dict)
        # safe_load() prevents execution of arbitrary Python code for security
        return yaml.safe_load(f)


def load_keywords_config() -> dict:
    """
    Load keywords configuration from the YAML configuration file.
    
    Returns:
        dict: A dictionary containing keyword lists organized by priority level:
              - high_priority_keywords: List of critical/urgent keywords
              - medium_priority_keywords: List of important keywords  
              - low_priority_keywords: List of general information keywords
    """
    config_path = importlib.resources.files("newsfeed.config").joinpath("keywords_config.yaml")
    with config_path.open("r", encoding="utf-8") as f:
        # Parse YAML file content into Python data structures (list/dict)
        # safe_load() prevents execution of arbitrary Python code for security
        return yaml.safe_load(f) 
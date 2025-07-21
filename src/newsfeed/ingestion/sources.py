import yaml
import importlib.resources

def load_sources_config() -> list:    
    config_path = importlib.resources.files("newsfeed.config").joinpath("sources_config.yaml")
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

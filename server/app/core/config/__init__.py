from .config import settings as config_settings
from .agriculture_config import AgricultureConfig, agriculture_config

# For backwards compatibility
settings = config_settings

__all__ = ["settings", "config_settings", "AgricultureConfig", "agriculture_config"]
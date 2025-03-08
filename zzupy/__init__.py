from .api import ZZUPy
from .log import logger, configure_logging
from loguru import logger

logger.remove()

__version__ = "4.0.0"
__all__ = ["ZZUPy", "logger", "configure_logging"]

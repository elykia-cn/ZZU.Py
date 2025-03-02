from .api import ZZUPy
from .log import logger, configure_logging
from loguru import logger

logger.remove()

__version__ = "2.0.1"
__all__ = ["ZZUPy", "logger", "configure_logging"]

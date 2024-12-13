import sys
import loguru

logger = loguru.logger


default_format: str = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    "<c><u>{name}</u></c> | "
    # "<c>{function}:{line}</c>| "
    "{message}"
)
"""默认日志格式"""


logger_id = logger.add(
    sys.stdout,
    level=0,
    diagnose=False,
    filter="WARNING",
    format=default_format,
)

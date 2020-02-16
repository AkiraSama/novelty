import logging
from pathlib import Path


# Bot Configuration
CORE_EXTENSIONS = [
    'novelty.core.error',
    'novelty.core.redis',
    'novelty.core.extensions',
]

DESCRIPTION = "Cutest bot of Lighthouse 9."
DEFAULT_CONFIG_PATH = Path('./config.toml')
DEFAULT_COG_DIR = './cogs/'
DEFAULT_PREFIX = ';'


# Logging Output
ANSI_RESET = '\x1b[0m'
ANSI_RED = '\x1b[31m'
ANSI_GREEN = '\x1b[32m'
ANSI_YELLOW = '\x1b[33m'
ANSI_BLUE = '\x1b[34m'
ANSI_MAGENTA = '\x1b[35m'
ANSI_CYAN = '\x1b[36m'

LOGGING_COLORS = (
    (logging.DEBUG, ANSI_CYAN),
    (logging.INFO, ANSI_GREEN),
    (logging.WARN, ANSI_YELLOW),
    (logging.ERROR, ANSI_RED)
)

LOG_FORMAT_STR = '{asctime} {name} [{levelname}] {message}'
LOG_FORMAT_STR_COLOR = (
    f'{ANSI_BLUE}{{asctime}}{ANSI_RESET} '
    f'{ANSI_MAGENTA}{{name}}{ANSI_RESET} '
    '[{levelname}] {message}'
)
LOG_DATE_FORMAT = '%m-%d %H:%M:%S'

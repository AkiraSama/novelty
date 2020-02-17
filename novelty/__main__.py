#!/usr/bin/env python3.8

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from discord.ext import commands

from novelty import config, constants


parser = argparse.ArgumentParser(
    prog='novelty',
    description=constants.DESCRIPTION,
)
parser.add_argument(
    '--config',
    default=constants.DEFAULT_CONFIG_PATH,
    type=Path,
    help="path to configuration file",
    metavar='PATH',
    dest='config_filepath',
)
parser.add_argument(
    '--token',
    help="bot user token",
)
parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help="increase output verbosity",
)


def main(cfg, log):
    """novelty's main method."""

    # Separate out bot config values.
    bot_cfg = cfg.get('bot', {})

    # Check for a token.
    try:
        token = bot_cfg['token']
    except KeyError:
        log.error("Please add bot.token to your configuration file "
                  "or pass it via the command line.")
        return

    # Set up bot object.
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(
            bot_cfg.get('default_prefix', constants.DEFAULT_PREFIX)
        ),
        description=constants.DESCRIPTION,
        owner_id=bot_cfg.get('owner_id'),
    )
    bot.novelty_config = cfg

    # Get default event loop.
    loop = asyncio.get_event_loop()

    try:
        # Load core extensions before startup.
        for extension in constants.CORE_EXTENSIONS:
            bot.load_extension(extension)

        # Run bot.
        loop.run_until_complete(bot.start(token))
    except (KeyboardInterrupt, Exception) as e:  # noqa: E722
        # Unload core extensions.
        for extension in reversed(constants.CORE_EXTENSIONS):
            bot.unload_extension(extension)

        # Run logout.
        loop.run_until_complete(bot.logout())

        # Report unexpected errors.
        if not isinstance(e, KeyboardInterrupt):
            log.error("novelty encountered an error and was forced "
                      "to shut down!")
            raise
        else:
            log.info("Goodbye!")
    finally:
        # Close event loop for kicks.
        loop.close()


if __name__ == '__main__':
    # Parse command line arguments and combine with configuration file.
    args = parser.parse_args(sys.argv[1:])
    cfg = config.ConfigNamespace(args.config_filepath, args)

    # Set up colored logging.
    if cfg.get('bot', {}).get('use_ansi_log_colors', False):
        for level, color in constants.LOGGING_COLORS:
            name = logging.getLevelName(level)
            logging.addLevelName(
                level,
                f'{color}{name}{constants.ANSI_RESET}',
            )
        format_str = constants.LOG_FORMAT_STR_COLOR
    else:
        format_str = constants.LOG_FORMAT_STR

    # Set up StreamHandler for stdout.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(
        logging.DEBUG
        if cfg['verbose']
        else logging.INFO
    )
    formatter = logging.Formatter(
        fmt=format_str,
        datefmt=constants.LOG_DATE_FORMAT,
        style='{',
    )
    console_handler.setFormatter(formatter)

    # Set up the root logger.
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    log.addHandler(console_handler)

    # Call main.
    main(cfg, log)

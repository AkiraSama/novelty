import logging
import sys
from datetime import datetime
from random import choice
from traceback import format_exception

from discord import Color, Embed, HTTPException
from discord.ext.commands import (
    Bot,
    CommandInvokeError,
    Context,
    DefaultHelpCommand,
    MissingRequiredArgument,
    NotOwner,
)


log = logging.getLogger(__name__)


CMD_NOT_FOUND = [
    '"{name}"? Sorry, I don\'t know that one!',
    'You\'re confusing me. "{name}" isn\'t a command!',
    'Nope, "{name}" doesn\'t exist.',
    '"{name}" is definitely not a command that I know.',
    '"{name}", "{name}"... No, sorry, I do not have it.',
    'Nope, nope, nope! "{name}" isn\'t on my list.',
]


def cmd_not_found(name: str):
    return choice(CMD_NOT_FOUND).format(name=name)


class NoveltyHelpCommand(DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    def command_not_found(self, name: str):
        return cmd_not_found(name)


def setup(bot: Bot):
    log.info("Swapping out help_command for Novelty custom class.")

    bot.help_command = NoveltyHelpCommand()

    log.info("Registering global error handling events.")

    @bot.event
    async def on_error(event: str, *args, **kwargs):
        tcb = ''.join(format_exception(*sys.exc_info()))
        log.warning(f"Exception in event {event}:\n{tcb}")

    @bot.event
    async def on_command_error(ctx: Context, exception: Exception):
        if ctx.command is None:
            await ctx.send(cmd_not_found(ctx.invoked_with))
            return

        if isinstance(exception, MissingRequiredArgument):
            await ctx.send_help(ctx.command)
            return

        if isinstance(exception, NotOwner):
            await ctx.send("Sorry, you're not allowed to use that one!")
            return

        if (
                isinstance(exception, CommandInvokeError)
                and isinstance(exception.original, HTTPException)
        ):
            exception = exception.original

        tcb = ''.join(format_exception(
            type(exception),
            exception,
            exception.__traceback__,
        ))
        log.warning(f"Exception in command {ctx.command.name}:\n{tcb}")
        await ctx.send(embed=Embed(
            title=type(exception).__name__,
            description=str(exception),
            timestamp=datetime.now(),
            color=Color.red(),
        ))

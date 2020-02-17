import asyncio  # noqa: F401
import datetime  # noqa: F401
import functools  # noqa: F401
import inspect  # noqa: F401
import itertools  # noqa: F401
import logging
import operator  # noqa: F401
import random  # noqa: F401
import re  # noqa: F401
import shlex  # noqa: F401
import unicodedata  # noqa: F401

import discord  # noqa: F401
import discord.utils  # noqa: F401
import discord.ext.commands  # noqa: F401
from discord.ext.commands import (
    Bot,
    Cog,
    Context,
    NotOwner,
    Paginator,
    command,
)

from novelty import (  # noqa: F401
    constants,
)


log = logging.getLogger(__name__)


COG_NAME = "Owner Tools"


class OwnerCog(Cog, name=COG_NAME):
    MAX_LINE_SIZE = 1991

    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if not await self.bot.is_owner(ctx.author):
            raise NotOwner()
        return True

    @command()
    async def eval(self, ctx: Context, *, code: str):
        """Owner evaluation.

        With great power comes great responsibility."""

        bot = self.bot  # noqa: F841
        eval_paginator = Paginator(prefix='```\n')

        try:
            out = str(eval(code))

            if not out:
                await ctx.send('\u200b')
                return

            for line in itertools.zip_longest(*(
                    [iter(out)] * self.MAX_LINE_SIZE
            )):
                eval_paginator.add_line(
                    ''.join(c for c in line if c).replace('```', '\\`\\`\\`')
                )

        except Exception as exception:
            eval_paginator.add_line(
                f"{type(exception).__name__}: {exception}"
            )

        for page in eval_paginator.pages:
            await ctx.send(page)


def setup(bot: Bot):
    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(OwnerCog(bot))


def teardown(bot: Bot):
    log.info(f"Removing {COG_NAME} cog.")
    bot.remove_cog(COG_NAME)

import logging

from discord.ext.commands import (
    Bot,
    Cog,
    Context,
    NotOwner,
    command,
)


log = logging.getLogger(__name__)


COG_NAME = "Owner Tools"


class OwnerCog(Cog, name=COG_NAME):
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

        try:
            out = eval(code)
        except Exception as exception:
            out = f"{type(exception).__name__}: {exception}"

        if out == '':
            out = '\u200b'

        await ctx.send(f"```\n{out}```")


def setup(bot: Bot):
    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(OwnerCog(bot))

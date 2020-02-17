import logging

from discord.ext.commands import (
    Bot,
    Cog,
)


log = logging.getLogger(__name__)


COG_NAME = "Ranks"


class RanksCog(Cog, name=COG_NAME):
    class Keys:
        # SADD ranks:guilds <guild_id>
        TRACKED_GUILDS = 'ranks:guilds'

        # ZADD ranks:<guild_id>:roles CH <xp_threshold> <role_id>
        GUILD_ROLES = 'ranks:{guild_id}:roles'

        # ZADD ranks:<guild_id>:scores CH <xp> <user_id>
        GUILD_SCORES = 'ranks:{guild_id}:scores'

    def __init__(self, bot: Bot):
        self.bot = bot

    async def _init(self):
        pass


async def _setup(bot: Bot):
    cog = RanksCog(bot)
    await cog._init()
    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(cog)


def setup(bot: Bot):
    log.info("Running Ranks setup until complete.")
    bot.loop.run_until_complete(_setup(bot))


def teardown(bot: Bot):
    log.info(f"Removing {COG_NAME} cog.")
    bot.remove_cog(COG_NAME)

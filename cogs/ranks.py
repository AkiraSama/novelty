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
        self.redis = bot.redis_pool

    async def _init(self):
        tracked_guilds = set()
        async for guild_id in self.redis.isscan(self.Keys.TRACKED_GUILDS):
            tracked_guilds.add(int(guild_id))

        for guild in self.bot.guilds:

            tracked_guilds.discard(guild.id)

        for guild_id in tracked_guilds:
            log.info(f'Clearing tracked information for guild "{guild_id}".')
            await self.redis.delete(
                self.Keys.GUILD_SCORES.format(guild_id=guild_id)
            )
            await self.redis.delete(
                self.Keys.GUILD_ROLES.format(guild_id=guild_id)
            )
            await self.redis.srem(
                self.Keys.TRACKED_GUILDS,
                guild_id,
            )


async def _setup(bot: Bot):
    await bot.wait_until_ready()

    cog = RanksCog(bot)
    await cog._init()
    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(cog)


def setup(bot: Bot):
    log.info("Scheduling Ranks setup.")
    bot.loop.create_task(_setup(bot))


def teardown(bot: Bot):
    log.info(f"Removing {COG_NAME} cog.")
    bot.remove_cog(COG_NAME)

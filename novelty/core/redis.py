import logging

import aioredis
from discord.ext.commands import Bot, Cog


log = logging.getLogger(__name__)


COG_NAME = "Redis"
REQUIRED_KEYS = {'host', 'port'}


class RedisCog(Cog, name=COG_NAME):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def _init(self):
        db_info = self.bot.novelty_config.get('redis', {})

        needed = REQUIRED_KEYS - db_info.keys()

        if needed:
            missing_keys = f"Missing keys: {', '.join(needed)}"
            log.error("Please fully congiure your Redis information "
                      f"in your configuration file. {missing_keys}")
            raise ValueError(f"Redis config. {missing_keys}")

        self.bot.redis_pool = await aioredis.create_redis_pool(
            (db_info['host'], db_info['port']),
            db=db_info.get('db', 0),
            password=db_info.get('password'),
            maxsize=db_info.get('pool_size', 10),
        )
        log.info("Redis connection established.")

    def cog_unload(self):
        log.info("Closing Redis pool.")
        self.bot.redis_pool.close()


async def _setup(bot: Bot):
    cog = RedisCog(bot)
    await cog._init()
    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(cog)


def setup(bot: Bot):
    log.info("Running Redis setup until complete.")
    bot.loop.run_until_complete(_setup(bot))


def teardown(bot: Bot):
    log.info(f"Removing {COG_NAME} cog.")
    bot.remove_cog(COG_NAME)

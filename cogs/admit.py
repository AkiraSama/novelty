import datetime
import logging

from discord import (
    Member,
)
from discord.ext.commands import (
    Bot,
    Cog,
)


log = logging.getLogger(__name__)


COG_NAME = "Admit"
REJECTION_MESSAGE = """\
Sorry! Your account isn't currently old enough to join \
{guild_name}!"""


class AdmitCog(Cog, name=COG_NAME):
    AGES_KEY = 'admit-ages'

    def __init__(self, bot: Bot):
        self.bot = bot
        self.redis = bot.redis_pool
        self.age_thresholds = {}

    async def _init(self):
        self.age_thresholds = {
            int(guild_id): int(age)
            for guild_id, age
            in (await self.redis.hgetall(self.AGES_KEY)).items()
        }

    @Cog.listener()
    async def on_member_join(self, member: Member):
        min_age = self.age_thresholds.get(member.guild.id)

        if not min_age:
            return

        if (
                (datetime.datetime.now() - member.created_at)
                < datetime.timedelta(hours=min_age)
        ):
            log.info(f"Rejecting user {member} due to inadequate "
                     "account age.")
            try:
                await member.send(REJECTION_MESSAGE.format(
                    guild_name=member.guild.name
                ))
            except Exception:  # Really don't care what happens.
                log.exception(f"Failed to DM user {member}.")
            finally:
                await member.kick()


async def _setup(bot: Bot):
    await bot.wait_until_ready()

    cog = AdmitCog(bot)
    await cog._init()

    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(cog)


def setup(bot: Bot):
    log.info("Scheduling Admission setup.")
    bot.loop.create_task(_setup(bot))


def teardown(bot: Bot):
    log.info(f"Removing {COG_NAME} cog.")
    bot.remove_cog(COG_NAME)

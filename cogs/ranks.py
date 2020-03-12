import asyncio
import logging
import string
from enum import IntEnum

from discord import (
    Message,
)
from discord.ext.commands import (
    Bot,
    Cog,
)


log = logging.getLogger(__name__)


COG_NAME = "Ranks"


class MaxGain(IntEnum):
    COUNT = 1
    LENGTH = 2
    VARIETY = 3


class GainKeys:
    COUNT = 'count'
    LENGTH = 'len'
    VARIETY = 'var'


class GainThresholds:
    LENGTH = 50
    VARIETY = 13


class RanksCog(Cog, name=COG_NAME):
    RESET_INTERVAL = 10
    CHARS = frozenset(string.ascii_letters + string.punctuation)

    class Keys:
        # SADD ranks:guilds <guild_id>
        TRACKED_GUILDS = 'ranks:guilds'

        # ZADD ranks:<guild_id>:roles CH <xp_threshold> <role_id>
        GUILD_ROLES = 'ranks:{guild_id}:roles'

        # ZINCRBY ranks:<guild_id>:scores <xp_gain> <user_id>
        GUILD_SCORES = 'ranks:{guild_id}:scores'

    def __init__(self, bot: Bot):
        self.bot = bot
        self.redis = bot.redis_pool
        self.counts = {}
        self.reset_task = None

    async def _init(self):
        # Populate set of tracked guilds.
        tracked_guilds = set()
        async for guild_id in self.redis.isscan(self.Keys.TRACKED_GUILDS):
            tracked_guilds.add(int(guild_id))

        for guild in self.bot.guilds:

            tracked_guilds.discard(guild.id)

        # Any guilds we're not in should be cleaned up.
        for guild_id in tracked_guilds:
            log.info(f'Clearing tracked information for guild "{guild_id}".')

            # Clear scores.
            await self.redis.delete(
                self.Keys.GUILD_SCORES.format(guild_id=guild_id)
            )

            # Clear roles.
            await self.redis.delete(
                self.Keys.GUILD_ROLES.format(guild_id=guild_id)
            )

            # Finally, pull guild from tracking set.
            await self.redis.srem(
                self.Keys.TRACKED_GUILDS,
                guild_id,
            )

        self._initialize_counts()
        self.reset_task = self.bot.loop.create_task(
            self._reset_timer()
        )

    def cog_unload(self):
        if self.reset_task:
            self.reset_task.cancel()

    async def _reset_timer(self):
        await asyncio.sleep(self.RESET_INTERVAL)
        log.info("Resetting THz gain counts.")
        self._initialize_counts()

        # Reschedule self.
        self.reset_task = self.bot.loop.create_task(
            self._reset_timer()
        )

    def _initialize_counts(self):
        self.counts = {guild.id: {} for guild in self.bot.guilds}

    def _calculate_gain(self, message: Message):
        # In this case "counts" are THz points left to gain.
        member_counts = (
            self.counts[message.guild.id].setdefault(
                message.author.id,
                {
                    GainKeys.COUNT: MaxGain.COUNT.value,
                    GainKeys.LENGTH: MaxGain.LENGTH.value,
                    GainKeys.VARIETY: MaxGain.VARIETY.value,
                },
            )
        )

        # If the member has gained all possible THz points for this
        # period, no gain. Do this before performing more expensive
        # calculations.
        if member_counts is None:
            return 0

        length = len(message.content)
        characters = set(message.content)
        variety = len(self.CHARS & characters)

        gain = 0

        if member_counts[GainKeys.COUNT] > 0:
            gain += 1
            member_counts[GainKeys.COUNT] -= 1

        if (
                (length >= GainThresholds.LENGTH)
                and (member_counts[GainKeys.LENGTH] > 0)
        ):
            gain += 1
            member_counts[GainKeys.LENGTH] -= 1

        if (
                (variety >= GainThresholds.VARIETY)
                and (member_counts[GainKeys.VARIETY] > 0)
        ):
            gain += 1
            member_counts[GainKeys.VARIETY] -= 1

        if (
                (member_counts[GainKeys.VARIETY] == 0)
                and (member_counts[GainKeys.LENGTH] == 0)
                # Don't need to bother checking GainKeys.COUNT
                # because it will have obviously been consumed.
        ):
            self.counts[message.guild.id][message.author.id] = None

        return gain

    @Cog.listener()
    async def on_message(self, message: Message):
        # Sorry but bots can't earn THz.
        if message.author.bot:
            return

        gain = self._calculate_gain(message)

        if gain > 0:
            score = await self.redis.zincrby(
                self.Keys.GUILD_SCORES.format(guild_id=message.guild.id),
                gain,
                message.author.id,
            )
            print(f"{message.author.name}'s score is now {score}.")


async def _setup(bot: Bot):
    await bot.wait_until_ready()

    cog = RanksCog(bot)
    await cog._init()

    # We don't have to worry about our events counting THz before
    # we're ready because they only kick in once the cog is added
    # to the bot.
    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(cog)


def setup(bot: Bot):
    log.info("Scheduling Ranks setup.")
    bot.loop.create_task(_setup(bot))


def teardown(bot: Bot):
    log.info(f"Removing {COG_NAME} cog.")
    bot.remove_cog(COG_NAME)

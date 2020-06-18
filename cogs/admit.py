import datetime
import logging

from discord import (
    Member,
)
from discord.ext.commands import (
    Bot,
    Cog,
    Context,
    group,
    has_guild_permissions,
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

    @group()
    @has_guild_permissions(manage_guild=True)
    async def admit(self, ctx: Context):
        """Manage server admission."""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @admit.group(name='age')
    async def admit_age(self, ctx: Context):
        """Manage admission age threshold."""

        if ctx.invoked_subcommand is None:
            await ctx.invoke(ctx.command.get_command('get'))

    @admit_age.command(name='get')
    async def admit_age_get(self, ctx: Context):
        """Get admission age threshold."""

        min_hours = self.age_thresholds.get(ctx.guild.id)

        if not min_hours:
            await ctx.send(
                f"No admission age threshold set for {ctx.guild.name}."
            )
            return

        await ctx.send(
            f"Admission age threshold for {ctx.guild.name} "
            f"is {self.age_thresholds.get(ctx.guild.id)} hours."
        )

    @admit_age.command(name='set')
    async def admit_age_set(self, ctx: Context, hours: int):
        """Set admission age threshold."""

        if hours <= 0:
            await ctx.invoke(
                ctx.command.parent.get_command('remove'),
            )
            return

        await self.redis.hset(self.AGES_KEY, ctx.guild.id, hours)
        self.age_thresholds[ctx.guild.id] = hours

        await ctx.send(
            f"Successfully updated admission age threshold to {hours} hours."
        )

    @admit_age.command(
        name='remove',
        aliases=('reset', 'del', 'delete', 'disable'),
    )
    async def admit_age_reset(self, ctx: Context):
        """Remove admission age threshold."""

        await self.redis.hdel(self.AGES_KEY, ctx.guild.id)
        self.age_thresholds.pop(ctx.guild.id, None)

        await ctx.send("Sucessfully removed admission age threshold.")

    @Cog.listener()
    async def on_member_join(self, member: Member):
        min_hours = self.age_thresholds.get(member.guild.id)

        if not min_hours:
            return

        member_hours = (
            datetime.datetime.now() - member.created_at
        ) // datetime.timedelta(hours=1)

        if member_hours < min_hours:
            log.info(f"Rejecting user {member} due to inadequate "
                     f"account age. ({member_hours}h, server minimum"
                     f"is {min_hours}h.)")
            try:
                await member.send(REJECTION_MESSAGE.format(
                    guild_name=member.guild.name
                ))
            except Exception:  # Really don't care what happens.
                log.exception(f"Failed to DM user {member}.")
            finally:
                await member.kick(
                    reason=(f"Account age of {member_hours} hours "
                            f"is insufficient to meet {min_hours} "
                            "threshold.")
                )


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

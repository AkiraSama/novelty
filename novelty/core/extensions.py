import logging
from pathlib import Path

from discord.ext.commands import (
    Bot,
    Cog,
    Context,
    NoEntryPointError,
    Paginator,
    group,
    is_owner,
)

from novelty import constants


log = logging.getLogger(__name__)


COG_NAME = "ExtensionManager"


class ExtensionManager(Cog):
    """test 1"""

    def __init__(self, bot: Bot):
        """test 2"""

        self.bot = bot
        self.ext_dir = Path(bot.novelty_config.get('bot', {}).get(
            'cogs_directory', constants.DEFAULT_COG_DIR,
        ))
        self.ext_prefix = '.'.join(self.ext_dir.parts)

        for extension in self.ext_dir.iterdir():
            if extension.suffix == '.py':
                path = '.'.join(extension.with_suffix('').parts)
                log.info(f'Attempting to load extension "{path}".')
                try:
                    bot.load_extension(path)
                except NoEntryPointError:
                    log.info(f'Skipping over invalid extension "{path}".')

    def _get_name(self, ext_name):
        return f'{self.ext_prefix}.{ext_name}'

    @group(aliases=('ext',))
    @is_owner()
    async def extension(self, ctx: Context):
        """Manage extensions."""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @extension.command(name='list')
    async def extension_list(self, ctx: Context):
        """List all loaded extensions."""

        paginator = Paginator(prefix='')
        paginator.add_line("Extensions loaded: ```\n")

        for name in sorted(self.bot.extensions):
            paginator.add_line(name)

        for page in paginator.pages:
            await ctx.send(page)

    @extension.command(name='load')
    async def extension_load(self, ctx: Context, name: str):
        """Load an extension by name."""

        ext_name = self._get_name(name)

        if ext_name in self.bot.extensions:
            await ctx.send(f"Extension `{name}` is already loaded.")
        else:
            log.info(f"Attempting to load extension {name}.")
            self.bot.load_extension(ext_name)
            log.info(f"Loaded extension {name}.")
            await ctx.send(f"Loaded extension `{name}`.")

    @extension.command(name='unload')
    async def extension_unload(self, ctx: Context, name: str):
        """Unload an extension by name."""

        ext_name = self._get_name(name)

        if ext_name in self.bot.extensions:
            log.info(f"Attempting to unload extension {name}.")
            self.bot.unload_extension(ext_name)
            log.info(f"Unloaded extension {name}.")
            await ctx.send(f"Unloaded extension `{name}`.")
        else:
            await ctx.send(f"Extension `{name}` is not loaded.")

    @extension.command(name='reload')
    async def extension_reload(self, ctx: Context, name: str):
        """Reload an extension by name."""

        ext_name = self._get_name(name)

        if ext_name in self.bot.extensions:
            log.info(f"Attempting to reload extension {name}.")
            self.bot.reload_extension(ext_name)
            log.info(f"Reloaded extension {name}.")
            await ctx.send(f"Reloaded extension `{name}`.")
        else:
            await ctx.send(f"Extension `{name}` is not loaded.")


def setup(bot: Bot):
    log.info(f"Adding {COG_NAME} cog.")
    bot.add_cog(ExtensionManager(bot))

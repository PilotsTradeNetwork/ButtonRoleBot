"""
Our main Cog for BRB commands.

"""

import logging

# discord.py
import discord
from discord.ext import commands

import ptn.buttonrolebot.constants as constants

# local constants
from ptn.buttonrolebot._metadata import __version__

# import bot
from ptn.buttonrolebot.bot import bot
from ptn.buttonrolebot.constants import LOG_LEVEL, role_council, role_mod

# local modules
# from ptn.buttonrolebot.modules.Embeds import None
from ptn.buttonrolebot.modules.ErrorHandler import on_app_command_error

"""
A primitive global error handler for text commands.

returns: error message to user and log
"""


@bot.listen()
async def on_command_error(ctx, error):
    logging.error(error)
    if isinstance(error, commands.BadArgument):
        message = f"Bad argument: {error}"

    elif isinstance(error, commands.CommandNotFound):
        message = f"Sorry, were you talking to me? I don't know that command."

    elif isinstance(error, commands.MissingRequiredArgument):
        message = (
            f"Sorry, that didn't work.\n• Check you've included all required arguments."
            "\n• If using quotation marks, check they're opened *and* closed, and are in the proper place.\n• Check quotation"
            " marks are of the same type, i.e. all straight or matching open/close smartquotes."
        )

    elif isinstance(error, commands.MissingPermissions):
        message = "Sorry, you're missing the required permission for this command."

    elif isinstance(error, commands.MissingAnyRole):
        message = f"You require one of the following roles to use this command:\n<@&{role_council()}> • <@&{role_mod()}>"  # TODO: update with actual roles

    else:
        message = f"Sorry, that didn't work: {error}"

    embed = discord.Embed(description=f"❌ {message}", color=constants.EMBED_COLOUR_ERROR)
    await ctx.send(embed=embed)


"""
ADMIN COMMANDS

"""


# define the Cog we'll use for our mod commands
class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # custom global error handler
    # attaching the handler when the cog is loaded
    # and storing the old handler
    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = on_app_command_error

    # detaching the handler when the cog is unloaded
    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    """
    ADMIN COMMANDS
    """

    # ping command to check if the bot is responding
    @commands.command(
        name="ping", aliases=["hello", "ehlo", "helo"], help="Use to check if BRB is online and responding."
    )
    @commands.has_any_role(*constants.any_elevated_role)
    async def ping(self, ctx):
        logging.info(f"{ctx.author} used PING in {ctx.channel.name}")
        embed = discord.Embed(
            title="🟢 BUTTON ROLE BOT ONLINE",
            description=f"🎢<@{bot.user.id}> connected, version **{__version__}**.",
            color=constants.EMBED_COLOUR_OK,
        )
        await ctx.send(embed=embed)

    # command to sync interactions - must be done whenever the bot has appcommands added/removed
    @commands.command(name="sync", help="Synchronise BRB interactions with server")
    @commands.has_any_role(*constants.any_elevated_role)
    async def sync(self, ctx):
        logging.info(f"Interaction sync called from {ctx.author.display_name}")
        async with ctx.typing():
            try:
                bot.tree.copy_global_to(guild=constants.guild_obj)
                await bot.tree.sync(guild=constants.guild_obj)
                logging.info("Synchronised bot tree.")
                await ctx.send("Synchronised bot tree.")
            except Exception as e:
                logging.error(f"Tree sync failed: {e}.")
                logging.exception(e)
                return await ctx.send(f"Failed to sync bot tree: {e}")

    @commands.command(name="enabledebug", help="Enables debug logging for Rolercoaster application (not discord.py).")
    @commands.has_any_role(*constants.any_elevated_role)
    async def enabledebug(self, ctx):
        logging.info(f"Interaction enabledebug called from {ctx.author.display_name}")
        async with ctx.typing():
            try:
                logger = logging.getLogger("root")
                logger.setLevel(logging.DEBUG)
                dpy = logging.getLogger("discord")
                dpy.setLevel(LOG_LEVEL)
                logging.info("Rolercoaster Application debug logging enabled.")
                await ctx.send("Rolercoaster Application debug logging enabled.")
            except Exception as e:
                logging.error(f"Debug log enable failed: {e}.")
                logging.exception(e)
                return await ctx.send(f"Failed to enable debug logging: {e}")

    @commands.command(name="disabledebug", help="Disables debug logging for Rolercoaster application (not discord.py).")
    @commands.has_any_role(*constants.any_elevated_role)
    async def disabledebug(self, ctx):
        logging.info(f"Interaction disabledebug called from {ctx.author.display_name}")
        async with ctx.typing():
            try:
                logger = logging.getLogger("root")
                logger.setLevel(LOG_LEVEL)
                logging.info("Rolercoaster Application debug logging disabled.")
                await ctx.send("Rolercoaster Application debug logging disabled.")
            except Exception as e:
                logging.error(f"Debug log disable failed: {e}.")
                logging.exception(e)
                return await ctx.send(f"Failed to disable debug logging: {e}")

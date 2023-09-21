"""
Our main Cog for BRB commands.

"""

# libraries
import asyncio
from datetime import datetime, timezone

# discord.py
import discord
from discord.ext import commands
from discord import app_commands

# bot object
from ptn.buttonrolebot.bot import bot

# local constants
from ptn.buttonrolebot._metadata import __version__
import ptn.buttonrolebot.constants as constants
from ptn.buttonrolebot.constants import channel_botspam, channel_botdev, role_council, role_mod, any_elevated_role

# local views
from ptn.buttonrolebot.views.EmbedCreator import EmbedGenButtons
from ptn.buttonrolebot.views.ButtonCreator import DynamicButton

# local modules
from ptn.buttonrolebot.modules.ErrorHandler import on_app_command_error, GenericError, on_generic_error, CustomError
from ptn.buttonrolebot.modules.Helpers import check_roles


error_handler_generic = GenericError()
error_handler_custom = CustomError(None)

"""
A primitive global error handler for text commands.

returns: error message to user and log
"""

@bot.listen()
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.BadArgument):
        message=f'Bad argument: {error}'

    elif isinstance(error, commands.CommandNotFound):
        message=f"Sorry, were you talking to me? I don't know that command."

    elif isinstance(error, commands.MissingRequiredArgument):
        message=f"Sorry, that didn't work.\n• Check you've included all required arguments." \
                 "\n• If using quotation marks, check they're opened *and* closed, and are in the proper place.\n• Check quotation" \
                 " marks are of the same type, i.e. all straight or matching open/close smartquotes."

    elif isinstance(error, commands.MissingPermissions):
        message='Sorry, you\'re missing the required permission for this command.'

    elif isinstance(error, commands.MissingAnyRole):
        message=f'You require one of the following roles to use this command:\n<@&{role_council()}> • <@&{role_mod()}>' # TODO: update with actual roles

    else:
        message=f'Sorry, that didn\'t work: {error}'

    embed = discord.Embed(description=f"❌ {message}", color=constants.EMBED_COLOUR_ERROR)
    await ctx.send(embed=embed)


"""
CONTEXT COMMANDS
Cannot be placed in a Cog
Uses @bot.tree instead of @command.tree
"""

@bot.tree.context_menu(name='Add Role Button')
@check_roles(any_elevated_role)
async def add_role_button(interaction: discord.Interaction, message: discord.Message):
    try:
        role_id = 1 # TODO
        view = discord.ui.View(timeout=None)
        view.add_item(DynamicButton(message.id, role_id))

        await message.edit(view=view)

        await interaction.response.send_message("Button created!", ephemeral=True) # TODO

    except Exception as e:
        print(e)
        try:
            raise GenericError(e)
        except Exception as e:
            await on_generic_error(interaction, e)



"""
BRB COMMANDS COG

"""

# define the Cog we'll use for our mod commands
class ButtonRoleCommands(commands.Cog):
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
    BRB COMMANDS
    """

    # send an embed which we can use to attach a button
    @app_commands.command(
        name="send_embed",
        description="Prepare an Embed to send to this channel. This can be used to attach role buttons to."
        )
    @check_roles([role_council(), role_mod()]) # TODO: full permissions
    async def _send_embed(self, interaction:  discord.Interaction):
        print(f"{interaction.user.name} used /send_embed in {interaction.channel.name}")

        embed = discord.Embed(
            title='Generate an Embed',
            description='Send a message with an Embed to this channel. Buttons can be attached to this embed to grant/remove roles.',
            color=constants.EMBED_COLOUR_QU
        )

        view = EmbedGenButtons(embed)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


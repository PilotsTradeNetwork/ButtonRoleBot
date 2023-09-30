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
from discord.ui import View

# bot object
from ptn.buttonrolebot.bot import bot

# local constants
from ptn.buttonrolebot._metadata import __version__
import ptn.buttonrolebot.constants as constants
from ptn.buttonrolebot.constants import channel_botspam, channel_botdev, role_council, role_mod, any_elevated_role

# local classes
from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData
from ptn.buttonrolebot.classes.EmbedData import EmbedData

# local views
from ptn.buttonrolebot.ui_elements.EmbedCreator import EmbedGenButtons
from ptn.buttonrolebot.ui_elements.ButtonConfig import NewButton, MasterCancelButton, MasterAddButton
from ptn.buttonrolebot.ui_elements.ButtonRemove import ConfirmRemoveButtonsView

# local modules
from ptn.buttonrolebot.modules.ErrorHandler import on_app_command_error, GenericError, on_generic_error, CustomError
from ptn.buttonrolebot.modules.Embeds import button_config_embed, _generate_embed_from_dict
from ptn.buttonrolebot.modules.Helpers import check_roles, check_channel_permissions, _get_embed_from_message

spamchannel = bot.get_channel(channel_botspam())

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
# remove view from a bot message
@bot.tree.context_menu(name='Remove Buttons')
@check_roles(any_elevated_role)
@check_channel_permissions()
async def remove_role_buttons(interaction: discord.Interaction, message: discord.Message):
    print(f"Received Remove Buttons context interaction from {interaction.user} in {interaction.channel}")
    # check message was sent by bot
    if not message.author == bot.user:
        try:
            raise CustomError(f"Buttons can only be added to messages sent by <@{bot.user.id}>")
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)
        return

    # confirm removal
    embed = discord.Embed(
        description=f"Confirm removal of buttons from {message.jump_url}? **This cannot be undone**.",
        color=constants.EMBED_COLOUR_QU
    )

    view = ConfirmRemoveButtonsView(message)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# add role button
@bot.tree.context_menu(name='Add Role Button')
@check_roles(any_elevated_role)
@check_channel_permissions()
async def add_role_button(interaction: discord.Interaction, message: discord.Message):
    print(f"Received Add Role Button context interaction from {interaction.user} in {interaction.channel}")
    # check message was sent by bot
    if not message.author == bot.user:
        try:
            raise CustomError(f"Buttons can only be added to messages sent by <@{bot.user.id}>")
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)
        return

    try: 
        # generate our preview message/embeds
        heading_embed = discord.Embed(
            title='🔘 ADD BUTTONS: PREVIEW',
            description=f"This is a preview of {message.jump_url} with your buttons attached. " \
                         "When you have added at least one button, use ✅ to add them to the message.",
            color=constants.EMBED_COLOUR_QU
        )

        # get the embed from the message
        embed_data = _get_embed_from_message(message)

        preview_embed = _generate_embed_from_dict(embed_data)

        embeds = [heading_embed, preview_embed]

        # send our preview
        print("▶ Sending preview message...")
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

        # create default button_data instance to start us off
        button_data_info_dict = {
            'message': message,
            'preview_message': interaction
        }
        button_data = RoleButtonData(button_data_info_dict)
        print(button_data)

        print("⏳ Defining view...")
        view = View(timeout=None)
        # button = NewButton(button_data)
        buttons = []
        # view.add_item(button)

        # add master buttons
        cancelbutton = MasterCancelButton()
        addbutton = MasterAddButton(buttons, button_data)
        view.add_item(cancelbutton)
        view.add_item(addbutton)
        # view.add_item(MasterAddButton(buttons, button_data))

        print("▶ Adding view to original response...")
        await interaction.edit_original_response(view=view)

    except Exception as e:
        print(e)
        try:
            raise GenericError(e)
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)


# edit sent embed
@bot.tree.context_menu(name='Edit Bot Embed')
@check_roles(any_elevated_role)
@check_channel_permissions()
async def edit_bot_embed(interaction: discord.Interaction, message: discord.Message):
    print(f"Received Edit Bot Embed context interaction from {interaction.user} in {interaction.channel}")
    # check message was sent by bot
    if not message.author == bot.user:
        try:
            raise CustomError(f"Buttons can only be added to messages sent by <@{bot.user.id}>")
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)
        return
    
    instruction_embed = discord.Embed(
        title='⚙ EDITING EMBED',
        color=constants.EMBED_COLOUR_QU
    )

    # get the embed from the message
    embed_data = await _get_embed_from_message(message)

    preview_embed = _generate_embed_from_dict(embed_data)

    view = EmbedGenButtons(instruction_embed, embed_data, message, 'edit')

    embeds = [instruction_embed, preview_embed]

    await interaction.response.send_message(embeds=embeds, view=view, ephemeral=True)

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
    @check_roles(any_elevated_role)
    @check_channel_permissions()
    async def _send_embed(self, interaction:  discord.Interaction):
        print(f"{interaction.user.name} used /send_embed in {interaction.channel.name}")

        instruction_embed = discord.Embed(
            title='🎨 CREATING EMBED',
            # description='Send a message with an Embed to this channel. Buttons can be attached to this message to grant/remove roles.',
            color=constants.EMBED_COLOUR_QU
        )

        # generate a blank version of embed_data
        embed_data = EmbedData()

        preview_embed = discord.Embed(
            description=embed_data.embed_description,
            color=embed_data.embed_color
        )

        view = EmbedGenButtons(instruction_embed, embed_data, None, 'create')

        embeds = [instruction_embed, preview_embed]

        await interaction.response.send_message(embeds=embeds, view=view, ephemeral=True)



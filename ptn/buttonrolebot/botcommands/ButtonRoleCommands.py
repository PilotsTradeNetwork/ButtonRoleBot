"""
Our main Cog for BRB commands.

"""

# libraries
import re
import traceback
import uuid

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
from ptn.buttonrolebot.ui_elements.ButtonConfig import MasterCancelButton, MasterAddButton, MasterCommitButton, NewButton
from ptn.buttonrolebot.ui_elements.ButtonRemove import ConfirmRemoveButtonsView

# local modules
from ptn.buttonrolebot.modules.ErrorHandler import on_app_command_error, GenericError, on_generic_error, CustomError
from ptn.buttonrolebot.modules.Embeds import _generate_embed_from_dict, button_edit_heading_embed
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
@bot.tree.context_menu(name='Manage Role Buttons')
@check_roles(any_elevated_role)
@check_channel_permissions()
async def manage_role_buttons(interaction: discord.Interaction, message: discord.Message):
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
        heading_embed = button_edit_heading_embed(message)

        # get the embed from the message
        embed_data = _get_embed_from_message(message)

        preview_embed = _generate_embed_from_dict(embed_data)

        embeds = [heading_embed, preview_embed]

        # send our preview
        print("▶ Sending preview message...")
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

        # define empty list to hold our button_data instances
        buttons = []

        role_id_pattern = r':role:(\d+):' # match our role ID 
        action_pattern = r':action:(\w+)' # match our action

        # check if message has a view already
        if message.components:
            print("⚠ Existing view found on message, adding its buttons to our edit view.")
            view = View.from_message(message)
            # use existing buttons to populate button_data and add to buttons
            for child in view.children:
                if isinstance(child, discord.ui.Button):
                    print(f"Found button: {child.emoji} {child.label} | {child.custom_id}")
                    unique_id = str(uuid.uuid4()) # generate a unique ID for each button_data instance

                    # use re to extract role ID and action from custom ID
                    match_role_id = re.search(role_id_pattern, child.custom_id)
                    match_action = re.search(action_pattern, child.custom_id)

                    role_id = int(match_role_id.group(1)) if match_role_id else None
                    action = str(match_action.group(1)) if match_action else None

                    # resolve role on the server if possible
                    role_object = None
                    if role_id:
                        try:
                            role_object = discord.utils.get(interaction.guild.roles, id=role_id)
                        except:
                            print(f"No role object found for {role_id}")
                            pass # we'll handle this on the button manager side

                    button_data_info_dict = {
                        'message': message,
                        'preview_message': interaction,
                        'role_id': role_id,
                        'role_object': role_object,
                        'button_label': child.label,
                        'button_emoji': child.emoji,
                        'button_style': child.style,
                        'unique_id': unique_id,
                        'button_action': action
                    }
                    # generate button_data
                    print("▶ Generating RoleButtonData instance from button.")
                    button_data = RoleButtonData(button_data_info_dict)
                    # append to our button list
                    buttons.append(button_data)

        else:
            # create a default button_data instance to start us off
            button_data_info_dict = {
                'message': message,
                'preview_message': interaction,
                'role_id': None
            }
            button_data = RoleButtonData(button_data_info_dict)
            print(button_data)

        print("⏳ Defining view...")
        view = View(timeout=None)

        print(f'Buttons list: {buttons}')
        if buttons:
            for button_data_instance in buttons:
                button = NewButton(buttons, button_data_instance)
                print(f"🔘 Generated button from set {button_data_instance.unique_id}")
                view.add_item(button)

        # add master buttons
        view.add_item(MasterCancelButton())
        view.add_item(MasterAddButton(buttons, button_data))
        if buttons:
            view.add_item(MasterCommitButton(buttons, button_data))

        print("▶ Adding view to original response...")
        await interaction.edit_original_response(view=view)

    except Exception as e:
        print(e)
        traceback.print_exc()
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



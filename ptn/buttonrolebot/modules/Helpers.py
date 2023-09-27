"""
A module for helper functions called by other modules.

Depends on: ErrorHandler, Constants

"""
# import os
import os

#import validators
import validators

# import discord.py
import discord
from discord import app_commands
from discord.ui import View

# import bot
from ptn.buttonrolebot.bot import bot, DynamicButton

# import constants
from ptn.buttonrolebot.constants import bot_guild, channel_botspam, VALID_EXTENSIONS, EMBED_COLOUR_OK

# import classes
from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData

# import local modules
from ptn.buttonrolebot.modules.ErrorHandler import CommandRoleError, CustomError, on_generic_error, CommandPermissionError


"""
PERMISSION CHECKS

Used for application commands
"""

spamchannel = bot.get_channel(channel_botspam())

# trio of helper functions to check a user's permission to run a command based on their roles, and return a helpful error if they don't have the correct role(s)
def getrole(ctx, id): # takes a Discord role ID and returns the role object
    role = discord.utils.get(ctx.guild.roles, id=id)
    return role

async def checkroles_actual(interaction: discord.Interaction, permitted_role_ids):
    try:
        """
        Check if the user has at least one of the permitted roles to run a command
        """
        print(f"checkroles called.")
        author_roles = interaction.user.roles
        permitted_roles = [getrole(interaction, role) for role in permitted_role_ids]
        print(author_roles)
        print(permitted_roles)
        permission = True if any(x in permitted_roles for x in author_roles) else False
        print(permission)
        return permission, permitted_roles
    except Exception as e:
        print(e)
    return permission


def check_roles(permitted_role_ids):
    async def checkroles(interaction: discord.Interaction):
        permission, permitted_roles = await checkroles_actual(interaction, permitted_role_ids)
        print("Inherited permission from checkroles")
        if not permission: # raise our custom error to notify the user gracefully
            role_list = []
            for role in permitted_role_ids:
                role_list.append(f'<@&{role}> ')
                formatted_role_list = " • ".join(role_list)
            try:
                raise CommandRoleError(permitted_roles, formatted_role_list)
            except CommandRoleError as e:
                print(e)
                raise
        return permission
    return app_commands.check(checkroles)


def check_channel_permissions(): # does this work? I have no idea. Discord seems to disable interactions in channels you don't have send permissions in, even if explicitly enabled. 🤷‍♀️
    async def checkuserperms(interaction: discord.Interaction):
        member: discord.Member = interaction.guild.get_member(interaction.user.id)
        user_permissions: discord.Permissions = interaction.channel.permissions_for(member)
        permission = user_permissions.send_messages
        if not permission:
            try:
                raise CommandPermissionError()
            except CommandPermissionError as e:
                print(e)
                raise
        return permission
    return app_commands.check(checkuserperms)

"""
Helpers
"""

async def get_guild():
    """
    Return bot guild instance for use in get_member()
    """
    return bot.get_guild(bot_guild())


def is_valid_extension(url):
    _, ext = os.path.splitext(url)
    return ext.lower() in VALID_EXTENSIONS and validators.url(url)


# remove a field from an embed
def _remove_embed_field(embed, field_name_to_remove):
    print(f"Called _remove_embed_field for {field_name_to_remove}")
    try:
        embed.remove_field(field_name_to_remove)
        print(f"Removed {field_name_to_remove}")

    except:
        print(f"No field found for {field_name_to_remove}")
        pass

    return embed

# check if a role exists
async def check_role_exists(interaction, role_id):
    print(f"Called check_role_exists for {role_id}")
    try:
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        print(f"Role exists with name {role.name}")
        return role
    except Exception as e:
        print("No role exists for this ID.")
        try:
            raise CustomError(f"No role found on this server matching ```{role_id}```")
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)
        return None
    
# add role button to message
# this one is kind of a big deal
async def _add_role_button_to_view(interaction: discord.Interaction, button_data: RoleButtonData):
    print("Called _add_role_button_to_view")
    print(button_data)
    message: discord.Message = button_data.message
    style: discord.ButtonStyle = button_data.button_style
    # role: discord.Role = button_data.role_object

    print("Instantiating DynamicButton component")
    button = DynamicButton(button_data.button_action, button_data.role_id, message.id)

    print("Setting button properties")
    button.item.label = button_data.button_label if button_data.button_label else None
    button.item.emoji = button_data.button_emoji if button_data.button_emoji else None
    button.item.style = style

    print("Checking if message has a view")
    if message.components:
        print("Existing view detected, we will add our button to it")
        view = View.from_message(message)
        view.timeout=None
    else:
        print("Defining empty view")
        view = discord.ui.View(timeout=None)

    print("Adding dynamic button component")
    view.add_item(button)

    print("Logging to bot-spam")
    embed = discord.Embed(
        description=f"🔘 <@{interaction.user.id}> added a button to {message.jump_url} to {button_data.button_action} the <@&{button_data.role_id}> role.",
        color=EMBED_COLOUR_OK
    )

    spamchannel = bot.get_channel(channel_botspam())
    await spamchannel.send(embed=embed)

    return view
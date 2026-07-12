"""
A module for helper functions called by other modules.

Depends on: ErrorHandler, Constants

"""

import json
import logging
import os
import traceback

# import libraries
from collections import OrderedDict
from urllib.parse import urlparse

# import discord.py
import discord
import validators
from discord import app_commands

# import bot
from ptn.buttonrolebot.bot import DynamicButton, bot
from ptn.buttonrolebot.classes.EmbedData import EmbedData

# import classes
from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData

# import constants
from ptn.buttonrolebot.constants import (
    EMBED_COLOUR_OK,
    EMBED_DICT_SCHEMA,
    VALID_EXTENSIONS,
    bot_guild,
    channel_botspam,
    role_brb,
    role_council,
    role_mod,
)

# import local modules
from ptn.buttonrolebot.modules.ErrorHandler import (
    CommandPermissionError,
    CommandRoleError,
    CustomError,
    on_generic_error,
)
from ptn.buttonrolebot.utils import get_member

"""
PERMISSION CHECKS

Used for application commands
"""

spamchannel = bot.get_channel(channel_botspam())


# trio of helper functions to check a user's permission to run a command based on their roles, and return a helpful error if they don't have the correct role(s)
def getrole(ctx, id):  # takes a Discord role ID and returns the role object
    role = discord.utils.get(ctx.guild.roles, id=id)
    return role


async def checkroles_actual(interaction: discord.Interaction, permitted_role_ids):
    try:
        """
        Check if the user has at least one of the permitted roles to run a command
        """
        logging.debug(f"checkroles called.")
        author_roles = interaction.user.roles
        permitted_roles = [getrole(interaction, role) for role in permitted_role_ids]
        logging.debug(author_roles)
        logging.debug(permitted_roles)
        permission = True if any(x in permitted_roles for x in author_roles) else False
        logging.debug(f"Permission: {permission}")
        return permission, permitted_roles
    except Exception as e:
        logging.exception(e)
    return permission


def check_roles(permitted_role_ids):
    async def checkroles(interaction: discord.Interaction):
        permission, permitted_roles = await checkroles_actual(interaction, permitted_role_ids)
        logging.debug("Inherited permission from checkroles")
        if not permission:  # raise our custom error to notify the user gracefully
            role_list = []
            for role in permitted_role_ids:
                role_list.append(f"<@&{role}> ")
                formatted_role_list = " • ".join(role_list)
            try:
                raise CommandRoleError(permitted_roles, formatted_role_list)
            except CommandRoleError as e:
                logging.exception(e)
                raise
        return permission

    return app_commands.check(checkroles)


def check_channel_permissions():
    """
    does this work? I have no idea. Discord seems to disable interactions in channels you don't have send permissions in, even if explicitly enabled. 🤷‍♀️
    """

    async def checkuserperms(interaction: discord.Interaction):
        member: discord.Member = await get_member(bot, interaction.user.id)
        user_permissions: discord.Permissions = interaction.channel.permissions_for(member)
        permission = user_permissions.send_messages
        if not permission:
            try:
                raise CommandPermissionError()
            except CommandPermissionError as e:
                logging.exception(e)
                raise
        return permission

    return app_commands.check(checkuserperms)


async def button_role_checks(interaction: discord.Interaction, role: discord.Role, button_data: RoleButtonData):
    logging.debug(f"Called button_role_checks for {role}")
    try:
        # check if we have permission to manage this role
        bot_member: discord.Member = await get_member(bot, bot.user.id)
        if bot_member.top_role <= role or role.managed:
            logging.debug("We don't have permission for this role")
            try:
                raise CustomError(
                    f"I don't have permission to manage <@&{role.id}> on **{button_data.button_emoji} {button_data.button_label}** ."
                )
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return False

        bot_role = discord.utils.get(interaction.guild.roles, id=role_brb())
        logging.debug(bot_role)
        if bot_role < role:
            permitted_role_ids = [role_council(), role_mod()]
            result = await checkroles_actual(interaction, permitted_role_ids)
            permission = result[0]
            if not permission:
                logging.debug("User doesn't have permission to manage this role.")
                try:
                    error = (
                        f"To manage <@&{role.id}> on **{button_data.button_emoji} {button_data.button_label}** "
                        f"you require one of the following roles: <@&{role_mod()}>  •  <@&{role_council()}>"
                    )
                    raise CustomError(error)
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                return False

        logging.debug("Permission OK")
        return True
    except Exception as e:
        logging.exception(e)


"""
Helpers
"""


async def get_guild():
    """
    Return bot guild instance for use in get_member()
    """
    return bot.get_guild(bot_guild())


def is_valid_extension(url):
    parsed_url = urlparse(url)
    _, ext = os.path.splitext(parsed_url.path)  # Only consider the path of the URL
    return ext.lower() in VALID_EXTENSIONS and validators.url(url)


# remove a field from an embed
def _remove_embed_field(embed, field_name_to_remove):
    logging.debug(f"Called _remove_embed_field for {field_name_to_remove}")
    try:
        embed.remove_field(field_name_to_remove)
        logging.debug(f"Removed {field_name_to_remove}")

    except:
        logging.debug(f"No field found for {field_name_to_remove}")
        pass

    return embed


def _get_embed_from_message(message: discord.Message):
    """
    populate embed_fields from an embed in a message
    """
    logging.debug("Called _get_embed_from_message")
    for embed in message.embeds:
        embed_fields = {
            "embed_title": embed.title,
            "embed_description": embed.description,
            "embed_image_url": embed.image.url,
            "embed_footer": embed.footer.text,
            "embed_thumbnail_url": embed.thumbnail.url,
            "embed_author_name": embed.author.name,
            "embed_author_avatar_url": embed.author.icon_url,
            "embed_color": embed.color,
            "embed_json": _format_embed_dict(embed),
        }
    # generate embed_data from the sent embed
    embed_data = EmbedData(embed_fields)
    logging.debug(f"Instantiated embed_data as: {embed_data}")
    # return embed_data instance to function
    return embed_data


async def check_role_exists(interaction, role_id):
    """
    check if a role exists
    """
    logging.debug(f"Called check_role_exists for {role_id}")
    try:
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        logging.debug(f"Role exists with name {role.name}")
        return role
    except Exception as e:
        logging.debug("No role exists for this ID.")
        try:
            raise CustomError(f"No role found on this server matching ```{role_id}```")
        except Exception as e:
            logging.exception(e)
            await on_generic_error(spamchannel, interaction, e)
        return None


async def _add_role_buttons_to_view(interaction: discord.Interaction, buttons, message: discord.Message):
    """
    add role button to message
    this one is kind of a big deal
    """
    logging.debug("Called _add_role_buttons_to_view")

    logging.debug("Defining empty view")
    view = discord.ui.View(timeout=None)

    for button_data_instance in buttons:
        logging.debug(button_data_instance)
        style: discord.ButtonStyle = button_data_instance.button_style
        logging.debug("Instantiating DynamicButton component")
        button = DynamicButton(
            button_data_instance.button_action, button_data_instance.role_id, button_data_instance.message.id
        )
        logging.debug(f"🔘 Generated DynamicButton from set {button_data_instance.unique_id}")

        logging.debug("Setting button properties")
        button.item.label = button_data_instance.button_label if button_data_instance.button_label else None
        button.item.emoji = button_data_instance.button_emoji if button_data_instance.button_emoji else None
        button.item.style = style
        button.item.row = button_data_instance.button_row

        logging.debug("Adding dynamic button component")
        view.add_item(button)

        logging.debug("Logging to bot-spam")
        embed = discord.Embed(
            description=f"🔘 <@{interaction.user.id}> added a button to {message.jump_url} to {button_data_instance.button_action} the <@&{button_data_instance.role_id}> role.",
            color=EMBED_COLOUR_OK,
        )

        spamchannel = bot.get_channel(channel_botspam())
        await spamchannel.send(embed=embed)

    # this no longer necessary but we'll keep it around for now
    """print("Checking if message has a view")
    if message.components:
        print("Existing view detected, we will add our button to it")
        view = View.from_message(message)
        view.timeout=None
    else:
        print("Defining empty view")
        view = discord.ui.View(timeout=None)"""

    return view


def _format_embed_dict(embed: discord.Embed):
    embed_dict = embed.to_dict()
    ordered_dict = OrderedDict((key, embed_dict[key]) for key in EMBED_DICT_SCHEMA if key in embed_dict)
    formatted_dict = json.dumps(ordered_dict, ensure_ascii=False, indent=4)
    logging.debug("✅ Formatted dict: %s" % (formatted_dict))
    return formatted_dict

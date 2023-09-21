"""
A module for helper functions called by other modules.

Depends on: ErrorHandler, Constants

"""

# import discord.py
import discord
from discord import app_commands

# import bot
from ptn.buttonrolebot.bot import bot

# import constants
from ptn.buttonrolebot.constants import bot_guild

# import local modules
from ptn.buttonrolebot.modules.ErrorHandler import CommandRoleError


"""
PERMISSION CHECKS

Used for application commands
"""

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


"""
Helpers
"""

async def get_guild():
    """
    Return bot guild instance for use in get_member()
    """
    return bot.get_guild(bot_guild())


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


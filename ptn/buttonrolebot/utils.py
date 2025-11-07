from typing import Optional

from discord import Guild, Member, NotFound, User
from discord.ext.commands import Bot

from ptn.buttonrolebot.constants import bot_guild


async def get_user(bot: Bot, user_id: int) -> Optional[User]:
    """Fetch a user from the cache or API."""
    try:
        return bot.get_user(user_id) or await bot.fetch_user(user_id)
    except NotFound:
        return None


async def get_guild(bot: Bot, guild: int = bot_guild()) -> Optional[Guild]:
    """Return bot guild instance for use in get_member()"""
    return bot.get_guild(guild) or await bot.fetch_guild(guild)


async def get_member(bot: Bot, member_id: int) -> Optional[Member]:
    """Fetch a member from the cache or API."""
    guild = await get_guild(bot)
    try:
        return guild.get_member(member_id) or await guild.fetch_member(member_id)
    except NotFound:
        return None

"""
Embeds.py

Generates embeds for use by the bot

Dependencies: ErrorHandler
"""

# import discord
import discord

# import ErrorHandler
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error

# generate an embed from a dict
async def _generate_embed_from_dict(interaction, embed_data):
    print("Called _generate_embed_from_dict")
    print(embed_data)

    # create empty embed
    embed = discord.Embed()

    try:
        # Populate the embed with values from embed_data
        print("Add title")
        if embed_data.embed_title:
            embed.title = embed_data.embed_title
        print("Add description")
        if embed_data.embed_description:
            embed.description = embed_data.embed_description
        print("Add image")
        if embed_data.embed_image:
            embed.set_image(url=embed_data.embed_image)
        print("Add thumbnail")
        if embed_data.embed_thumbnail:
            embed.set_thumbnail(url=embed_data.embed_thumbnail)
        print("Add author")
        if embed_data.embed_author_name:
            print("Add author avatar")
            if embed_data.embed_author_avatar:
                embed.set_author(name=embed_data.embed_author_name, icon_url=embed_data.embed_author_avatar)
            else:
                embed.set_author(name=embed_data.embed_author_name)
        print("Set color")
        if embed_data.embed_color:
            embed.color = embed_data.embed_color

    except Exception as e:
        try:
            raise GenericError(e)
        except Exception as e:
            await on_generic_error(interaction, e)

    return embed
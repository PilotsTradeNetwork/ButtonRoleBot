
"""
Embeds.py

Generates embeds for use by the bot

Dependencies: constants
Error Handling should be dealt with from calling functions
"""

# import discord
import discord

# import constants
from ptn.buttonrolebot.constants import EMBED_COLOUR_ERROR, EMBED_COLOUR_OK, EMBED_COLOUR_QU, channel_botspam


# generate an embed from a dict
async def _generate_embed_from_dict(embed_data):
    print("Called _generate_embed_from_dict")
    print(embed_data)

    # create empty embed
    embed = discord.Embed()


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


    return embed

def button_config_embed(index, button_data):
    if index == 0:
        embed = discord.Embed(
        description=f':rocket: Let\'s add a role button to {button_data.message.jump_url}\n\n' \
                    'First, enter the 🎢 **role ID** of the role you wish the button to add/remove. ' \
                    'You can find a role ID using Discord\'s developer mode, by right-clicking on a role ' \
                    'in a user\'s role list, or in the server\'s roles menu.',
                    color=EMBED_COLOUR_QU
        )
        return embed

    elif index == 1:
        embed = discord.Embed(
            description=f'Please ✅ confirm you want to use your button to add the following role:\n' \
                        f'<@&{button_data.role_id}>',
            color=EMBED_COLOUR_QU
        )
        return embed

    elif index == 2:
        embed = discord.Embed(
            description=f'Now choose which 🎨 **style of button** you want to add.',
            color=EMBED_COLOUR_QU
        )
        return embed
    
    elif index == 3:
        embed = discord.Embed(
            description=f'Now choose your button\'s 📄 **label** and 🤪 **emoji**.\n\n' \
                        '- Custom emojis should be in the format `<:name:ID>`\n' \
                        '- Default emojis should be in the format `:name:`',
            color=EMBED_COLOUR_QU
        )
        return embed

    elif index == 4:
        embed = discord.Embed(
            description=f'Congratulations! you win a button', # TODO: show details for confirmation
            color=EMBED_COLOUR_QU
        )
        return embed
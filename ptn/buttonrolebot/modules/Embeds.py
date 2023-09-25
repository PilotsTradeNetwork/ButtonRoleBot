
"""
Embeds.py

Generates embeds for use by the bot

Dependencies: constants
Error Handling should be dealt with from calling functions
"""
# import libraries
import random

# import discord
import discord

# import constants
from ptn.buttonrolebot.constants import EMBED_COLOUR_ERROR, EMBED_COLOUR_OK, EMBED_COLOUR_QU, channel_botspam, \
    HOORAY_GIFS, BUTTON_CHOOSE_THUMBNAIL, BUTTON_SWEAT_THUMBNAIL, THERE_THERE, STRESS_GIFS, YOU_GO_GIRL, AMAZING_GIFS

from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData
from ptn.buttonrolebot.classes.EmbedData import EmbedData


# generate an embed from a dict
def _generate_embed_from_dict(embed_data: EmbedData):
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
    print("Add footer")
    if embed_data.embed_footer:
        embed.set_footer(text=embed_data.embed_footer)
    print("Add image")
    if embed_data.embed_image_url:
        embed.set_image(url=embed_data.embed_image_url)
    print("Add thumbnail")
    if embed_data.embed_thumbnail_url:
        embed.set_thumbnail(url=embed_data.embed_thumbnail_url)
    print("Add author")
    if embed_data.embed_author_name:
        print("Add author avatar")
        if embed_data.embed_author_avatar_url:
            embed.set_author(name=embed_data.embed_author_name, icon_url=embed_data.embed_author_avatar_url)
        else:
            embed.set_author(name=embed_data.embed_author_name)
    print("Set color")
    if embed_data.embed_color:
        embed.color = embed_data.embed_color


    return embed

def button_config_embed(index, button_data: RoleButtonData):
    print("called button_config_embed")
    message: discord.Message = button_data.message

    if index <= 4:
        footer = f"Step {index + 1} of 5"
    else:
        footer = "All done!"

    embed = discord.Embed(color=EMBED_COLOUR_QU)

    embed.set_thumbnail(url=BUTTON_CHOOSE_THUMBNAIL)
    embed.set_footer(text=footer)

    if index >= 4:
        # add summary fields
        if button_data.button_label is not None:
            label = button_data.button_label
        else:
            label = '*None*'
        embed.add_field(name="Label", value=label)

        if button_data.button_emoji is not None:
            emoji = button_data.button_emoji
        else:
            emoji = '*None*'
        embed.add_field(name="Emoji", value=emoji)

        style = button_data.get_button_style_name()
        embed.add_field(name="Style", value=style)

        role_id = button_data.role_id
        embed.add_field(name="Target Role", value=f'<@&{role_id}>\n`{role_id}`')

        message = button_data.message
        embed.add_field(name="Target Message", value=f'{message.jump_url}\n`{message.id}`')

    if index == 0:
        print("Returning embed for index 0")
        # embed.title="Add Role Button to Message"
        embed.description = \
            '# Add Role Button to Message\n' \
            f'Let\'s :rocket: **add a role button** to {message.jump_url}\n\n' \
            'First, enter the 🎢 **role ID** of the role you wish the button to add/remove. ' \
            'You can find a role ID using Discord\'s developer mode, by right-clicking on a role ' \
            'in a user\'s role list, or in the server\'s roles menu.'

        return embed

    elif index == 1:
        print("Returning embed for index 1")
        # embed.title="Confirm Button Role"
        embed.set_thumbnail(url=BUTTON_SWEAT_THUMBNAIL)
        embed.description = \
            '# Confirm Button Role\n' \
            f'Please ✅ **confirm** you want to use your button to add the following role:\n' \
            f'## <@&{button_data.role_id}>'

        return embed

    elif index == 2:
        print("Returning embed for index 2")
        # embed.title="Button Style"
        embed.description = \
            '# Button Style\n' \
            f'Now choose which 🎨 **style of button** you want to add.'

        return embed
    
    elif index == 3:
        print("Returning embed for index 3")
        # embed.title="Button Label & Emoji"
        embed.description = \
            '# Button Label & Emoji\n' \
            f'Now choose your button\'s 🏷 **label** and 🤪 **emoji**.\n\n' \
            '- Buttons can have both a label and an emoji, but need *at least one or the other* to be valid.\n' \
            '- Custom emojis should be in the format: `<:name:id>`\n' \
            '- Default emojis can be entered using an emoji keyboard (Windows: `Win`+`.`) '\
            'or copy/pasting from a sent Discord message.`'

        return embed

    elif index == 4:
        print("Returning embed for index 4")
        print(button_data)
        # embed.title="Confirm Button Details"
        embed.set_thumbnail(url=BUTTON_SWEAT_THUMBNAIL)

        embed.description = \
            '# Confirm Button Details\n' \
            'Congratulations! You win a button! Here is your prize. Please indicate if you wish to accept it:' 

        return embed

    elif index == 5:
        print("Returning embed for index 5")
        # embed.title="Confirm Button Details"
        embed.set_thumbnail(url=BUTTON_SWEAT_THUMBNAIL)

        gif = random.choice(HOORAY_GIFS)

        embed.description = \
            '# Button Created!'
        
        embed.set_image(url=gif)

        return embed


def stress_embed():
    print("called stress_embed")
    # attach a random image from the "there, there" category
    gif = random.choice(STRESS_GIFS)

    embed = discord.Embed(
        description=random.choice(THERE_THERE),
        color=EMBED_COLOUR_OK
    )
    embed.set_image(url=gif)
    return embed


def amazing_embed():
    print("called amazing_embed")
    # attach a random image from the "there, there" category
    gif = random.choice(AMAZING_GIFS)

    embed = discord.Embed(
        description=random.choice(YOU_GO_GIRL),
        color=EMBED_COLOUR_OK
    )
    embed.set_image(url=gif)
    return embed
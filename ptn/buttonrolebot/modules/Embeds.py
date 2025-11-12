"""
Embeds.py

Generates embeds for use by the bot

Dependencies: constants
Error Handling should be dealt with from calling functions
"""

# import libraries
import json
import logging
import random

# import discord
import discord

from ptn.buttonrolebot.classes.EmbedData import EmbedData
from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData

# import constants
from ptn.buttonrolebot.constants import (
    AMAZING_GIFS,
    BUTTON_CHOOSE_THUMBNAIL,
    BUTTON_SWEAT_THUMBNAIL,
    EMBED_COLOUR_OK,
    EMBED_COLOUR_QU,
    STRESS_GIFS,
    THERE_THERE,
    YOU_GO_GIRL,
)


# convert hex color to int
async def _color_hex_to_int(color_input):
    logging.debug(color_input)
    if type(color_input) != int:
        color_input = str(color_input)
        if color_input.startswith("#"):  # check if we have an HTML color code
            logging.debug(f"Received web color code with #: {color_input}, stripping leading #...")
            color_input = color_input.lstrip("#")
            logging.debug(f"New value: {color_input}")

        color_int = int(color_input, 16)  # Convert hex string to integer
        logging.debug(f"Converted {color_input} to {color_int}")

        return color_int

    else:
        logging.debug("Received int, passing value through: %s" % (color_input))
        return color_input


# generate an embed from a dict
async def _generate_embed_from_dict(embed_data: EmbedData, from_json=False):
    logging.debug("Called _generate_embed_from_dict")
    logging.debug(embed_data)

    # Populate the embed with values from embed_data

    # load JSON
    # convert str to dict if needed
    if type(embed_data.embed_json) == str:
        logging.debug("Received JSON in string format.")
        # embed_data.embed_json = embed_data.embed_json.replace('\'', '\"')
        embed_json: dict = json.loads(embed_data.embed_json)
    else:
        embed_json: dict = embed_data.embed_json

    logging.debug("embed_json type: %s" % (type(embed_json)))

    if not from_json:
        logging.debug("▶ Add title")
        if embed_data.embed_title:
            embed_json["title"] = embed_data.embed_title
        else:
            if "title" in embed_json:
                del embed_json["title"]

        logging.debug("▶ Add description")
        if embed_data.embed_description:
            embed_json["description"] = embed_data.embed_description

        logging.debug("▶ Add footer")
        footer_dict = embed_json.get("footer", {})
        if embed_data.embed_footer:
            footer_dict["text"] = embed_data.embed_footer
        else:
            if "text" in footer_dict:
                del footer_dict["text"]
        if footer_dict:
            embed_json["footer"] = footer_dict

        logging.debug("▶ Add image")
        image_dict = embed_json.get("image", {})
        if embed_data.embed_image_url:
            image_dict["url"] = embed_data.embed_image_url
        else:
            if "url" in image_dict:
                del image_dict["url"]
        if image_dict:
            embed_json["image"] = image_dict

        logging.debug("▶ Add thumbnail")
        thumbnail_dict = embed_json.get("thumbnail", {})
        if embed_data.embed_thumbnail_url:
            thumbnail_dict["url"] = embed_data.embed_thumbnail_url
        else:
            if "url" in thumbnail_dict:
                del thumbnail_dict["url"]
        if thumbnail_dict:
            embed_json["thumbnail"] = thumbnail_dict

        logging.debug("▶ Add author")
        author_dict = embed_json.get("author", {})
        if embed_data.embed_author_name:
            author_dict["name"] = embed_data.embed_author_name
            if embed_data.embed_author_avatar_url:
                author_dict["icon_url"] = embed_data.embed_author_avatar_url
            else:
                if "icon_url" in author_dict:
                    del author_dict["icon_url"]
        else:
            if "name" in author_dict:
                del author_dict["name"]
        if author_dict:
            embed_json["author"] = author_dict

        logging.debug("▶ Set color")
        if embed_data.embed_color:
            color = await _color_hex_to_int(embed_data.embed_color)
            embed_json["color"] = color
        else:
            if "color" in embed_json:
                del embed_json["color"]

        logging.info("✅ Finished updating dict.")

    logging.info("⌛ Populating embed from JSON")
    embed = discord.Embed.from_dict(embed_json)

    logging.info("✅ Completed.")
    return embed


def button_config_embed(index, button_data: RoleButtonData):
    logging.debug("called button_config_embed")
    message: discord.Message = button_data.message

    if index < 5:
        footer = f"Step {index + 1} of 5. Use 🔀 to reposition button."
    else:
        footer = "Use ↩️ to return to Button Editor"

    embed = discord.Embed(color=EMBED_COLOUR_QU)

    embed.set_thumbnail(url=BUTTON_CHOOSE_THUMBNAIL)
    embed.set_footer(text=footer)

    if index == 0:
        logging.debug("Returning embed for index 0")
        # embed.title="ADD ROLE BUTTON TO MESSAGE"
        embed.description = (
            ":one: :rocket: **Enter the ROLE ID of the role you wish the button to add/remove**.\n\n"
            "*You can find a role ID using `Discord's developer mode` by right-clicking on a role "
            "in a user's role list or in the server's roles menu. Or, you can `mention the role "
            "in a message` and put a backslash `\\` in front of it before sending to get its ID: Put the mention in "
            "an edit so it doesn't ping, and remove the `<@&>` to get the numeric ID.*"
        )

        return embed

    elif index == 1:
        logging.debug("Returning embed for index 1")
        # embed.title="CONFIRM BUTTON ROLE"
        embed.set_thumbnail(url=BUTTON_SWEAT_THUMBNAIL)
        embed.description = (
            f":two: ✅ **CONFIRM you want to use your button to manage the following role**:\n"
            f"# <@&{button_data.role_id}>"
        )

        return embed

    elif index == 2:
        logging.debug("Returning embed for index 2")
        # embed.title="BUTTON STYLE"
        embed.description = f":three: 🛠 **CHOOSE what you want your button to DO**:"

        return embed

    elif index == 3:
        logging.debug("Returning embed for index 3")
        # embed.title="BUTTON STYLE"
        embed.description = f":four: :art: **CHOOSE which STYLE OF BUTTON you want to add**."

        return embed

    elif index == 4:
        logging.debug("Returning embed for index 4")
        # embed.title="LABEL & EMOJI"
        embed.description = (
            f":five: :label: **Choose your button's LABEL and/or EMOJI**.\n\n"
            "- Buttons can have both a label and an emoji, but need at least one or the other to be valid.\n"
            "- Custom emojis should be in the format: `<:name:id>` You can get a custom emoji code by entering "
            "the emoji in a message, and putting a backslash `\` in front of it before sending.\n"
            "- Default emojis can be entered using an emoji keyboard (Windows: `Win`+`.`) "
            "or copy/pasting from a sent Discord message."
        )

        return embed

    elif index == 5:
        logging.debug("Returning embed for index 5")
        # embed.title="LABEL & EMOJI"
        embed.description = (
            f":twisted_rightwards_arrows: **REPOSITION your button** .\n\n"
            "- You can have up to 4 rows with up to 5 buttons each.\n"
            "- Mobile apps :mobile_phone: can't fit full rows, so buttons will "
            "display differently, and positioning buttons may not work as expected.\n"
            "- Use ↩️ to return to Button Editor."
        )

        return embed


def stress_embed():
    logging.debug("called stress_embed")
    # attach a random image from the "there, there" category
    gif = random.choice(STRESS_GIFS)

    embed = discord.Embed(description=random.choice(THERE_THERE), color=EMBED_COLOUR_OK)
    embed.set_image(url=gif)
    return embed


def amazing_embed():
    logging.debug("called amazing_embed")
    # attach a random image from the "there, there" category
    gif = random.choice(AMAZING_GIFS)

    embed = discord.Embed(description=random.choice(YOU_GO_GIRL), color=EMBED_COLOUR_OK)
    embed.set_image(url=gif)
    return embed


def button_edit_heading_embed(message: discord.Message):
    embed = discord.Embed(
        title="🔘 MANAGE MESSAGE BUTTONS: PREVIEW",
        description=f"This is a preview of {message.jump_url} with your buttons attached.\n\n"
        "In the __Button Manager__ view (this view):\n"
        "✗ Cancel\n+ Add button\n✔ Confirm previewed buttons and add to message\n\n"
        "In the __Button Edit__ view (click on any button):\n"
        "◀ / ▶ Previous/Next page\n💥 Delete button\n✅ Commit button settings\n🔀 Reposition button\n\n"
        "Once you have added a button, click on it at any time to edit it. When finished, "
        " use ✔ in the Button Manager view to change the message's buttons to those previewed.",
        color=EMBED_COLOUR_QU,
    )
    embed.set_thumbnail(url=BUTTON_CHOOSE_THUMBNAIL)
    return embed

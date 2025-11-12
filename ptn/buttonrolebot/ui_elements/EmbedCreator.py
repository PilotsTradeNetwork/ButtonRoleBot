"""
Define classes for Embed Creator

Depends on: constants, Embeds, ErrorHandler, Helpers

"""
# import libraries
import json
import re
import traceback
import logging

# import discord.py
import discord
from discord.ui import View, Modal

# import bot
from ptn.buttonrolebot.bot import bot

# import local constants
import ptn.buttonrolebot.constants as constants
from ptn.buttonrolebot.constants import channel_botspam, EMBED_COLOUR_PTN_DEFAULT, DEFAULT_EMBED_DESC

# import local classes
from ptn.buttonrolebot.classes.EmbedData import EmbedData
from ptn.buttonrolebot.classes.FieldData import FieldData

# import local modules
from ptn.buttonrolebot.modules.Embeds import  _generate_embed_from_dict, _color_hex_to_int
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error, CustomError
from ptn.buttonrolebot.modules.Helpers import is_valid_extension, _get_embed_from_message, _format_embed_dict


# function shared by Edit Bot Embed and /edit_embed to edit an embed sent by the bot
async def _edit_bot_embed(interaction: discord.Interaction, message: discord.Message):
    logging.debug("Called _edit_bot_embed")
    spamchannel = bot.get_channel(channel_botspam())
    try:
        instruction_embed = discord.Embed(
            title='⚙ EDITING EMBED',
            color=constants.EMBED_COLOUR_QU
        )

        # get the embed from the message
        embed_data = _get_embed_from_message(message)

        preview_embed = await _generate_embed_from_dict(embed_data, from_json = True)

        view = EmbedGenButtons(instruction_embed, embed_data, message, 'edit')

        embeds = [instruction_embed, preview_embed]

        await interaction.response.send_message(embeds=embeds, view=view, ephemeral=True)

    except Exception as e:
        logging.exception(e)
        try:
            raise GenericError(e)
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)
        return


"""
EMBED CREATOR

Give the user all the tools to create and customise an embed using buttons and modals.
BUTTONS
Row 1:
- Title
- Description - mandatory
- Footer
- Image URL
Row 2:
- Color
- Thumbnail URL
- Author Name
- Author Avatar URL
Row 3:
- JSON

MODALS
Each button opens a modal that accepts user input for that field and saves it to an instance of EmbedData via set_attribute().

Modal is a common function that uses calling function to decide its parameters.

Default value for the modal is the existing content of the class attribute, allowing users to edit their input post-hoc.

EMBEDS
- explanation embed as instruction_embed - remains unchanged
- preview Embed as preview_embed:
  - appended to embed list after instruction_embed
  - placeholder: "Preview"
  - updated with embed_data each time modal is submitted
"""


# buttons for embed generator
class EmbedGenButtons(View):
    def __init__(self, instruction_embed, embed_data, message, action):
        self.action = action
        self.message: discord.Message = message
        self.spamchannel: discord.TextChannel = bot.get_channel(channel_botspam())
        self.instruction_embed: discord.Embed = instruction_embed # our original embed
        self.embed_data: EmbedData = embed_data # an instance of EmbedData to send to our embed creators
        super().__init__(timeout=None)
        self.set_embed_author_button.style=discord.ButtonStyle.success if self.embed_data.embed_author_name else discord.ButtonStyle.secondary
        self.set_embed_avatar_button.style=discord.ButtonStyle.success if self.embed_data.embed_author_avatar_url else discord.ButtonStyle.secondary
        self.set_embed_color_button.style=discord.ButtonStyle.success if int(self.embed_data.embed_color) != EMBED_COLOUR_PTN_DEFAULT else discord.ButtonStyle.secondary
        self.set_embed_desc_button.style=discord.ButtonStyle.success if self.embed_data.embed_description != DEFAULT_EMBED_DESC else discord.ButtonStyle.primary
        self.set_embed_footer_button.style=discord.ButtonStyle.success if self.embed_data.embed_footer else discord.ButtonStyle.secondary
        self.set_embed_img_button.style=discord.ButtonStyle.success if self.embed_data.embed_image_url else discord.ButtonStyle.secondary
        self.set_embed_thumb_button.style=discord.ButtonStyle.success if self.embed_data.embed_thumbnail_url else discord.ButtonStyle.secondary
        self.set_embed_title_button.style=discord.ButtonStyle.success if self.embed_data.embed_title else discord.ButtonStyle.secondary
        # self.remove_item(self.set_embed_send_button) # remove the send button until we have something to send


    @discord.ui.button(label="Title", style=discord.ButtonStyle.secondary, emoji="🏷", custom_id="embed_gen_title_button", row=0)
    async def set_embed_title_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_title_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_title',
            'title': 'Set Title',
            'label': 'Enter Title',
            'placeholder': 'Titles and footers accept text and unicode emojis only.',
            'max_length': 256,
            'default': self.embed_data.embed_title
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))


    @discord.ui.button(label="Main Text", style=discord.ButtonStyle.primary, emoji="📄", custom_id="embed_gen_desc_button", row=0)
    async def set_embed_desc_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_desc_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_description',
            'title': 'Set Main Content',
            'label': 'Enter Main Text',
            'placeholder': 'Normal Discord markdown works, but mentions and custom emojis require full code.',
            'style': discord.TextStyle.paragraph,
            'required': True,
            'max_length': 4000,
            'default': self.embed_data.embed_description
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))


    @discord.ui.button(label="Main Image", style=discord.ButtonStyle.secondary, emoji="🖼", custom_id="embed_gen_img_button", row=0)
    async def set_embed_img_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_img_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_image_url',
            'title': 'Set Main Image',
            'label': 'Enter Image URL',
            'placeholder': 'Enter the image\'s URL or leave blank for none.',
            'default': self.embed_data.embed_image_url
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.secondary, emoji="🦶", custom_id="embed_gen_footer_button", row=0)
    async def set_embed_footer_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_footer_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_footer',
            'title': 'Set Footer',
            'label': 'Enter Footer Text',
            'placeholder': 'Titles and footers accept text and unicode emojis only.',
            'max_length': 2000,
            'default': self.embed_data.embed_footer
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))


    @discord.ui.button(label="Color", style=discord.ButtonStyle.secondary, emoji="🎨", custom_id="embed_gen_color_button", row=1)
    async def set_embed_color_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_color_button click")

        try:
            if callable(getattr(self.embed_data.embed_color, 'to_rgb', None)):
                # we got a Discord color object
                logging.debug(f"⏳ Discord color object {self.embed_data.embed_color} returned, converting to int...")
                red, green, blue = self.embed_data.embed_color.to_rgb()
                logging.debug(f'🎨 RGB values: {red} {green} {blue}')
                hex_color = "0x{:02x}{:02x}{:02x}".format(red, green, blue)
                logging.debug(f'▶ Hex code: {hex_color}')
            else:
                logging.debug("⏳ Converting existing color to hex in format 0x000000...")
                hex_color = '0x{:06X}'.format(self.embed_data.embed_color)
                logging.debug(f'▶ Hex color: {hex_color}')
        except Exception as e:
            logging.exception(e)

        # set our modal field info
        field_info = {
            'attr': 'embed_color',
            'title': 'Set Embed Border Color',
            'label': 'Color',
            'placeholder': 'Enter a hex colour code in the format 0x00AA00 to use for the embed border.',
            'style': discord.TextStyle.short,
            'max_length': 8,
            'default': hex_color
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Thumbnail", style=discord.ButtonStyle.secondary, emoji="🖼", custom_id="embed_gen_thumb_button", row=1)
    async def set_embed_thumb_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_thumb_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_thumbnail_url',
            'title': 'Set Thumbnail Image',
            'label': 'Enter Thumbnail URL',
            'placeholder': 'Enter the image\'s URL or leave blank for none.',
            'default': self.embed_data.embed_thumbnail_url
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Author", style=discord.ButtonStyle.secondary, emoji="🧑", custom_id="embed_gen_author_button", row=1)
    async def set_embed_author_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embedset_embed_author_button_avatar_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_author_name',
            'title': 'Set Author Name',
            'label': 'Enter Author Name',
            'placeholder': 'Adds an Author field to the embed above the Title.',
            'style': discord.TextStyle.short,
            'max_length': 128,
            'default': self.embed_data.embed_author_name
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Avatar", style=discord.ButtonStyle.secondary, emoji="🖼", custom_id="embed_gen_avatar_button", row=1)
    async def set_embed_avatar_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_avatar_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_author_avatar_url',
            'title': 'Set Author Avatar',
            'label': 'Enter Avatar URL',
            'placeholder': 'Avatars will only display if an Author is also set.',
            'default': self.embed_data.embed_author_avatar_url
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="📤 JSON Export", style=discord.ButtonStyle.success, custom_id="embed_gen_json_export_button", row=2)
    async def set_embed_json_export_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_json_export_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_json_export',
            'title': 'Export JSON',
            'label': 'JSON data for export:',
            'style': discord.TextStyle.long,
            'max_length': 4000,
            'default': str(self.embed_data.embed_json)
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="📥 JSON Import", style=discord.ButtonStyle.danger, custom_id="embed_gen_json_import_button", row=2)
    async def set_embed_json_import_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_json_import_button click")

        # set our modal field info
        field_info = {
            'attr': 'embed_json',
            'title': 'Import JSON',
            'label': 'JSON data for import:',
            'style': discord.TextStyle.long,
            'max_length': 4000,
            'placeholder': '⚠ WARNING: This will OVERWRITE your existing embed ⚠'
        }

        # instantiate it into FieldData to send to the modal
        field_data = FieldData(field_info)
        logging.debug(f'Sending modal field data: {field_data}')

        logging.debug(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))


    @discord.ui.button(label="✗ Cancel", style=discord.ButtonStyle.danger, custom_id="embed_gen_cancel_button", row=3)
    async def set_embed_cancel_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_cancel_button click")
        embed = discord.Embed(
            description="❎ **Embed generation cancelled**.",
            color=constants.EMBED_COLOUR_QU
        )
        embed.set_footer(text="You can dismiss this message.")
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="✔ Send Embed", style=discord.ButtonStyle.success, custom_id="embed_gen_send_button", row=3)
    async def set_embed_send_button(self, interaction: discord.Interaction, button):
        logging.debug("Received set_embed_send_button click")

        if not self.embed_data.embed_title and not self.embed_data.embed_description:
            error = 'Your embed must have at least a title or main text to be valid.'
            try:
                raise CustomError(error)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)       

        try:
            logging.debug("Calling function to generate Embed...")
            send_embed = await _generate_embed_from_dict(self.embed_data, from_json = True)


            if self.action == 'edit':
                logging.debug("Updating edited Embed...")
                await self.message.edit(embed=send_embed)

                embed = discord.Embed(
                    description=f"✅ **Embed updated**: {self.message.jump_url}",
                    color=constants.EMBED_COLOUR_OK
                )
                embed.set_footer(text="You can dismiss this message.")

            else:
                logging.debug("Sending completed Embed...")
                message = await interaction.channel.send(embed=send_embed)
                logging.debug(f"Embed sent to {interaction.channel} by {interaction.user}")
                
                embed = discord.Embed(
                    description=f"✅ **Embed sent**. Message ID of containing message:\n"
                                f"```{message.id}```",
                    color=constants.EMBED_COLOUR_OK
                )
                embed.set_footer(text="You can dismiss this message.")

            logging.debug("Updating interaction response...")
            await interaction.response.edit_message(embed=embed, view=None)

            logging.debug("Notifying bot-spam...")
            embed = discord.Embed(
                description=f"📄 <@{interaction.user.id}> sent or edited the bot Embed at {interaction.message.jump_url}",
                color=constants.EMBED_COLOUR_OK
            )
            await self.spamchannel.send(embed=embed)

        except Exception as e:
            logging.exception(e)
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)


# modal for embed parameters
class EmbedContentModal(Modal):
    def __init__(self, instruction_embed, field_data: FieldData, embed_data, button, view, timeout = None) -> None:
        super().__init__(title=field_data.title, timeout=timeout)
        logging.debug('▶ Defining variables')
        self.spamchannel: discord.TextChannel = bot.get_channel(channel_botspam())
        self.instruction_embed: discord.Embed = instruction_embed
        self.embed_data: EmbedData = embed_data
        self.view: View = view
        self.field_data: FieldData = field_data
        self.button: discord.ui.Button = button
        # define our field data
        logging.debug('▶ Defining field data')
        self.embed_field.label = self.field_data.label
        self.embed_field.placeholder = self.field_data.placeholder
        self.embed_field.style = self.field_data.style
        self.embed_field.required = self.field_data.required
        self.embed_field.max_length = self.field_data.max_length
        self.embed_field.default = self.field_data.default
        logging.debug('☑ Finished definitions.')

    embed_field = discord.ui.TextInput(
        label="Label"
    )

    async def on_submit(self, interaction: discord.Interaction):
        logging.debug(f'Received EmbedContentModal submit for {self.field_data.attr}')

        if self.field_data.attr == 'embed_json_export':
            # this is read-only, we don't need to do anything
            logging.debug("Export JSON complete.")
            await interaction.response.defer()
            return

        elif self.field_data.attr == 'embed_json':
            # check for empty input
            if self.embed_field.value == "":
                logging.debug("User left this field blank, doing nothing.")
                try:
                    # notify user
                    raise CustomError(f"Please input a valid JSON to import.")
                except Exception as e:
                    await on_generic_error(self.spamchannel, interaction, e)
                return

            else:
                # we need to rebuild the embed from the new json
                try:
                    # update embed data
                    self.embed_data.embed_json = self.embed_field.value

                    # update our preview embed
                    logging.debug('Updating preview embed')
                    preview_embed = await _generate_embed_from_dict(self.embed_data, from_json = True)

                    # repopulate embed_data from new embed
                    embed_fields = {
                        'embed_title': preview_embed.title,
                        'embed_description': preview_embed.description,
                        'embed_image_url': preview_embed.image.url,
                        'embed_footer': preview_embed.footer.text,
                        'embed_thumbnail_url': preview_embed.thumbnail.url,
                        'embed_author_name': preview_embed.author.name,
                        'embed_author_avatar_url': preview_embed.author.icon_url,
                        'embed_color': preview_embed.color,
                        'embed_json': _format_embed_dict(preview_embed)
                    }
                    for key, value in embed_fields.items():
                        setattr(self.embed_data, key, value)

                    logging.debug(f'▶ Updated embed_data: {self.embed_data}')

                except json.JSONDecodeError as e:
                    try:
                        logging.exception(e)
                        # notify user
                        raise CustomError(f"Entry does not appear to be a valid Discord embed JSON: {e}")
                    except Exception as e:
                        await on_generic_error(self.spamchannel, interaction, e)
                    return

                except Exception as e:
                    try:
                        logging.exception(e)
                        # notify user
                        raise GenericError(e)
                    except Exception as e:
                        await on_generic_error(self.spamchannel, interaction, e)
                    return


        elif self.field_data.attr == 'embed_color':
            logging.debug('Received COLOR input')
        # turn color input into an INT and store it
            if self.embed_field.value:
                logging.debug(f"User entered color as {self.embed_field.value}, we'll check it's valid and convert it to int")
                if re.match(constants.HEX_COLOR_PATTERN, self.embed_field.value):
                    logging.debug('Received valid hex match')
                    try:
                        color_int = await _color_hex_to_int(self.embed_field.value)
                        self.embed_data.embed_color = color_int
                        logging.debug(self.embed_data.embed_color)

                    except ValueError as e:
                        logging.exception(e)
                        try:
                            raise GenericError(e)
                        except Exception as e:
                            await on_generic_error(self.spamchannel, interaction, e)
                        pass

                else:
                    error = f"'{self.embed_field.value}' is not a valid hex color code."
                    try:
                        raise CustomError(error)
                    except Exception as e:
                        await on_generic_error(self.spamchannel, interaction, e)
                    return
            else:
                logging.debug("No user color entry, re-assigning default.")
                self.embed_data.embed_color = constants.EMBED_COLOUR_PTN_DEFAULT
                logging.debug(self.embed_data.embed_color)

        else: # i.e. if anything else is being set
            if self.embed_field.value == "":
                logging.debug("User left this field blank.")
                self.embed_data.set_attribute(self.field_data.attr, None)
            else:
                logging.debug('Checking if URL type')
                string_to_check = str(self.field_data.attr)
                if "url" in string_to_check:
                    logging.debug('Validating URLs')
                    # validate image URLs
                    if not is_valid_extension(self.embed_field.value) and self.embed_field.value is not None:
                        error = f"Image not valid: {self.embed_field.value}"
                        logging.debug(error)
                        try:
                            raise CustomError(error)
                        except Exception as e:
                            await on_generic_error(self.spamchannel, interaction, e)
                        return

            logging.debug('Updating embed_data')
            # define our embed_data attribute to the user-inputted value
            if self.embed_field.value:
                self.embed_data.set_attribute(self.field_data.attr, self.embed_field.value)
            else:
                self.embed_data.set_attribute(self.field_data.attr, None)


        if 'json' not in self.field_data.attr:
            # update the embed the old-fashioned way
            logging.debug(f'▶ Updated embed_data: {self.embed_data}')

            # update our preview embed
            logging.debug('Updating preview embed')
            preview_embed = await _generate_embed_from_dict(self.embed_data)

            # tidy up our json field so it's in the right order
            self.embed_data.embed_json = _format_embed_dict(preview_embed)

        embeds = [self.instruction_embed, preview_embed]

        # update button style
        logging.debug("Updating button style...")
        if self.embed_field.value:
            self.button.style = discord.ButtonStyle.success
        else:
            self.button.style = discord.ButtonStyle.secondary

        # update the view in case we added the send button
        logging.debug("Sending updated embeds")
        await interaction.response.edit_message(embeds=embeds, view=self.view)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            logging.exception(error)
            raise GenericError(error)
        except Exception as e:
            await on_generic_error(self.spamchannel, interaction, e)
        return


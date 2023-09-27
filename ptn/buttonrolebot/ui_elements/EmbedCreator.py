"""
Define classes for Embed Creator

Depends on: constants, Embeds, ErrorHandler, Helpers

"""
# import libraries
import re
from discord.interactions import Interaction
import validators

# import discord.py
import discord
from discord.ui import View, Modal

# import bot
from ptn.buttonrolebot.bot import bot

# import local constants
import ptn.buttonrolebot.constants as constants
from ptn.buttonrolebot.constants import channel_botspam

# import local classes
from ptn.buttonrolebot.classes.EmbedData import EmbedData
from ptn.buttonrolebot.classes.FieldData import FieldData

# import local modules
from ptn.buttonrolebot.modules.Embeds import  _generate_embed_from_dict
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error, CustomError
from ptn.buttonrolebot.modules.Helpers import _remove_embed_field, is_valid_extension

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
        super().__init__(timeout=None)
        self.instruction_embed: discord.Embed = instruction_embed # our original embed
        self.embed_data: EmbedData = embed_data # an instance of EmbedData to send to our embed creators
        # self.remove_item(self.set_embed_send_button) # remove the send button until we have something to send


    @discord.ui.button(label="Title", style=discord.ButtonStyle.secondary, emoji="🏷", custom_id="embed_gen_title_button", row=0)
    async def set_embed_title_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_title_button click")

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))


    @discord.ui.button(label="Main Text", style=discord.ButtonStyle.primary, emoji="📄", custom_id="embed_gen_desc_button", row=0)
    async def set_embed_desc_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_desc_button click")

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))


    @discord.ui.button(label="Main Image", style=discord.ButtonStyle.secondary, emoji="🖼", custom_id="embed_gen_img_button", row=0)
    async def set_embed_img_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_img_button click")

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.secondary, emoji="🦶", custom_id="embed_gen_footer_button", row=0)
    async def set_embed_footer_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_footer_button click")

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))


    @discord.ui.button(label="Color", style=discord.ButtonStyle.secondary, emoji="🎨", custom_id="embed_gen_color_button", row=1)
    async def set_embed_color_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_color_button click")

        try:
            if callable(getattr(self.embed_data.embed_color, 'to_rgb', None)):
                # we got a Discord color object
                print(f"⏳ Discord color object {self.embed_data.embed_color} returned, converting to int...")
                red, green, blue = self.embed_data.embed_color.to_rgb()
                print(f'🎨 RGB values: {red} {green} {blue}')
                hex_color = "0x{:02x}{:02x}{:02x}".format(red, green, blue)
                print(f'▶ Hex code: {hex_color}')
            else:
                print("⏳ Converting existing color to hex in format 0x000000...")
                hex_color = '0x{:06X}'.format(self.embed_data.embed_color)
                print(f'▶ Hex color: {hex_color}') 
        except Exception as e:
            print(e)

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Thumbnail", style=discord.ButtonStyle.secondary, emoji="🖼", custom_id="embed_gen_thumb_button", row=1)
    async def set_embed_thumb_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_thumb_button click")

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Author", style=discord.ButtonStyle.secondary, emoji="🧑", custom_id="embed_gen_author_button", row=1)
    async def set_embed_author_button(self, interaction: discord.Interaction, button):
        print("Received set_embedset_embed_author_button_avatar_button click")

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="Avatar", style=discord.ButtonStyle.secondary, emoji="🖼", custom_id="embed_gen_avatar_button", row=1)
    async def set_embed_avatar_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_avatar_button click")

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
        print(f'Sending modal field data: {field_data}')

        print(f'Sending modal embed data: {self.embed_data}')

        await interaction.response.send_modal(EmbedContentModal(self.instruction_embed, field_data, self.embed_data, button, view=self))

    @discord.ui.button(label="✗ Cancel", style=discord.ButtonStyle.danger, custom_id="embed_gen_cancel_button", row=2)
    async def set_embed_cancel_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_cancel_button click")
        embed = discord.Embed(
            description="❎ **Embed generation cancelled**.",
            color=constants.EMBED_COLOUR_QU
        )
        embed.set_footer(text="You can dismiss this message.")
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="✔ Send Embed", style=discord.ButtonStyle.success, custom_id="embed_gen_send_button", row=2)
    async def set_embed_send_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_send_button click")

        if not self.embed_data.embed_title and not self.embed_data.embed_description:
            error = 'Your embed must have at least a title or main text to be valid.'
            try:
                raise CustomError(error)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)       

        try:
            print("Calling function to generate Embed...")
            send_embed = _generate_embed_from_dict(self.embed_data)


            if self.action == 'edit':
                print("Updating edited Embed...")
                await self.message.edit(embed=send_embed)

                embed = discord.Embed(
                    description=f"✅ **Embed updated**: {self.message.jump_url}",
                    color=constants.EMBED_COLOUR_OK
                )
                embed.set_footer(text="You can dismiss this message.")

            else:
                print("Sending completed Embed...")
                message = await interaction.channel.send(embed=send_embed)
                print(f"Embed sent to {interaction.channel} by {interaction.user}")
                
                embed = discord.Embed(
                    description=f"✅ **Embed sent**. Message ID of containing message:\n"
                                f"```{message.id}```",
                    color=constants.EMBED_COLOUR_OK
                )
                embed.set_footer(text="You can dismiss this message.")

            print("Updating interaction response...")
            await interaction.response.edit_message(embed=embed, view=None)

            print("Notifying bot-spam...")
            embed = discord.Embed(
                description=f"📄 <@{interaction.user.id}> sent or edited the bot Embed at {interaction.message.jump_url}",
                color=constants.EMBED_COLOUR_OK
            )
            await self.spamchannel.send(embed=embed)

        except Exception as e:
            print(e)
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)


# modal for embed parameters
class EmbedContentModal(Modal):
    def __init__(self, instruction_embed, field_data: FieldData, embed_data, button, view, timeout = None) -> None:
        super().__init__(title=field_data.title, timeout=timeout)
        print('Defining variables')
        self.spamchannel: discord.TextChannel = bot.get_channel(channel_botspam())
        self.instruction_embed: discord.Embed = instruction_embed
        self.embed_data: EmbedData = embed_data
        self.view: View = view
        self.field_data: FieldData = field_data
        self.button: discord.ui.Button = button
        # define our field data
        print('Defining field data')
        self.embed_field.label = self.field_data.label
        self.embed_field.placeholder = self.field_data.placeholder
        self.embed_field.style = self.field_data.style
        self.embed_field.required = self.field_data.required
        self.embed_field.max_length = self.field_data.max_length
        self.embed_field.default = self.field_data.default

    embed_field = discord.ui.TextInput(
        label="Label"
    )

    async def on_submit(self, interaction: discord.Interaction):
        print(f'Received EmbedContentModal submit for {self.field_data.attr}')

        if self.field_data.attr == 'embed_color':
            print('Received COLOR input')
        # turn color input into an INT and store it
            if self.embed_field.value:
                color_input = self.embed_field.value
                print(f"User entered color as {color_input}, we'll check it's valid and convert it to int")
                if re.match(constants.HEX_COLOR_PATTERN, color_input):
                    print('Received valid hex match')
                    if color_input.startswith('#'): # check if we have an HTML color code
                        print(f"Received web color code with #: {color_input}, stripping leading #...")
                        color_input = color_input.lstrip('#')
                        print(f"New value: {color_input}")
                    try:
                        color_int = int(color_input, 16)  # Convert hex string to integer
                        print(f'Converted {color_input} to {color_int}')
                        self.embed_data.embed_color = color_int
                        print(self.embed_data.embed_color)
                    except ValueError as e:
                        print(e)
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
                print("No user color entry, re-assigning default.")
                self.embed_data.embed_color = constants.EMBED_COLOUR_PTN_DEFAULT
                print(self.embed_data.embed_color)

        else: # i.e. if anything other than color is being set
            print('Checking if URL type')
            string_to_check = str(self.field_data.attr)
            if "url" in string_to_check:
                print('Validating URLs')
                # validate image URLs
                if not is_valid_extension(self.embed_field.value) and self.embed_field.value is not None:
                    error = f"Image not valid: {self.embed_field.value}"
                    print(error)
                    try:
                        raise CustomError(error)
                    except Exception as e:
                        await on_generic_error(self.spamchannel, interaction, e)
                    return

            print('Updating embed_data')
            # define our embed_data attribute to the user-inputted value
            if self.embed_field.value:
                self.embed_data.set_attribute(self.field_data.attr, self.embed_field.value)
            else:
                self.embed_data.set_attribute(self.field_data.attr, None)


        print(f'▶ Updated embed_data: {self.embed_data}')

        # update our preview embed
        print('Updating preview embed')
        preview_embed = _generate_embed_from_dict(self.embed_data)

        embeds = [self.instruction_embed, preview_embed]

        # update button style
        if self.embed_field.value:
            print("Updating button style...")
            self.button.style = discord.ButtonStyle.success

        # update the view in case we added the send button
        print("Sending updated embeds")
        await interaction.response.edit_message(embeds=embeds, view=self.view)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            raise GenericError(error)
        except Exception as e:
            await on_generic_error(self.spamchannel, interaction, e)
        return


"""
Define classes for Embed Creator

Depends on: constants, Embeds, ErrorHandler, Helpers

"""
import os
# import libraries
import re
import validators

# import discord.py
import discord
from discord.ui import View, Modal

# import bot
from ptn.buttonrolebot.bot import bot

# import local constants
import ptn.buttonrolebot.constants as constants
from ptn.buttonrolebot.constants import channel_botspam, VALID_EXTENSIONS

# import local classes
from ptn.buttonrolebot.classes.EmbedData import EmbedData

# import local modules
from ptn.buttonrolebot.modules.Embeds import  _generate_embed_from_dict
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error, CustomError
from ptn.buttonrolebot.modules.Helpers import _remove_embed_field, is_valid_extension

spamchannel = bot.get_channel(channel_botspam())

# buttons for embed generator
class EmbedGenButtons(View):
    def __init__(self, original_embed):
        super().__init__(timeout=None)
        self.original_embed = original_embed # our original embed to play around with
        self.embed_data = EmbedData() # an instance of EmbedData to send to our embed creators
        self.embed_data.embed_color = constants.EMBED_COLOUR_PTN_DEFAULT # set default color
        self.remove_item(self.set_embed_send_button) # remove the send button until we have something to send

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖", custom_id="embed_gen_cancel_button")
    async def set_embed_cancel_button(self, interaction, button):
        print("Received set_embed_cancel_button click")
        embed = discord.Embed(
            description="❎ **Embed generation cancelled**.",
            color=constants.EMBED_COLOUR_QU
        )
        embed.set_footer(text="You can dismiss this message.")
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Set Params", style=discord.ButtonStyle.secondary, emoji="⚙", custom_id="embed_params_button")
    async def set_embed_params_button(self, interaction, button):
        print("Received set_embed_params_button click")

        await interaction.response.send_modal(EmbedParamsModal(self.original_embed, self.embed_data, view=self))
        print(self.embed_data)

    @discord.ui.button(label="Set Content", style=discord.ButtonStyle.primary, emoji="🖼", custom_id="embed_content_button")
    async def set_embed_content_button(self, interaction, button):
        print("Received set_embed_content_button click")

        await interaction.response.send_modal(EmbedContentModal(self.original_embed, self.embed_data, view=self))
        print(self.embed_data)

    @discord.ui.button(label="Send Embed", style=discord.ButtonStyle.success, emoji="✅", custom_id="embed_gen_send_button")
    async def set_embed_send_button(self, interaction: discord.Interaction, button):
        print("Received set_embed_send_button click")
        try:
            print("Calling function to generate Embed...")
            send_embed = await _generate_embed_from_dict(self.embed_data)
            message = await interaction.channel.send(embed=send_embed)
            embed = discord.Embed(
                description=f"✅ **Embed sent**. Message ID of containing message:\n"
                            f"```{message.id}```",
                color=constants.EMBED_COLOUR_OK
            )
            embed.set_footer(text="You can dismiss this message.")
            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            print(e)
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)


# modal for embed parameters
class EmbedParamsModal(Modal):
    def __init__(self, original_embed, embed_data, view, title = 'Set Embed Parameters', timeout = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.original_embed = original_embed
        self.embed_data: EmbedData = embed_data
        self.view = view


    color = discord.ui.TextInput(
        label='Set the Embed border colour',
        placeholder='Enter a hex colour code in the format 0x00AA00 to use for the embed border.',
        required=False,
        max_length=8,
    )
    thumbnail = discord.ui.TextInput(
        label='Thumbnail Image URL.',
        placeholder='Enter the URL of the image you want to use, or leave blank for none.',
        required=False,
        max_length=512,
    )
    author_name = discord.ui.TextInput(
        label='Author Name',
        placeholder='Enter an author name for the Embed.',
        required=False,
        max_length=256,
    )
    author_avatar = discord.ui.TextInput(
        label='Author Avatar Image URL',
        placeholder='Requires Author Name to be set.',
        required=False,
        max_length=512,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # turn color input into an INT and store it
        if self.color.value:
            print(f"User entered color as {self.color.value}, we'll check it's valid and convert it to int")
            if re.match(constants.HEX_COLOR_PATTERN, self.color.value):
                try:
                    color_int = int(self.color.value, 16)  # Convert hex string to integer
                    self.embed_data.embed_color = color_int
                except ValueError as e:
                    print(e)
                    try:
                        raise GenericError(e)
                    except Exception as e:
                        await on_generic_error(spamchannel, interaction, e)
                    pass
            else:
                error = f"'{self.color.value}' is not a valid hex color code."
                try:
                    raise CustomError(error)
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                return
        else:
            print("No user color entry, assigning default.")
            self.embed_data.embed_color = constants.EMBED_COLOUR_PTN_DEFAULT
            print(self.embed_data.embed_color)

        # store data from the form fields into our EmbedData instance
        self.embed_data.embed_thumbnail = self.thumbnail.value if self.thumbnail.value else None
        self.embed_data.embed_author_name = self.author_name.value if self.author_name.value else None
        self.embed_data.embed_author_avatar = self.author_avatar.value if self.author_avatar.value else None

        # validate URLs
        if not is_valid_extension(self.embed_data.embed_thumbnail) and self.embed_data.embed_thumbnail is not None:
            error = f"Thumbnail URL not valid: {self.embed_data.embed_thumbnail}"
            print(error)
            try:
                raise CustomError(error)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return

        if not is_valid_extension(self.embed_data.embed_author_avatar) and self.embed_data.embed_author_avatar is not None:
            error = f"Author Avatar URL not valid: {self.embed_data.embed_author_avatar}"
            print(error)
            try:
                raise CustomError(error)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return

        field_data = ""

        if self.embed_data.embed_color is not None and self.embed_data.embed_color != constants.EMBED_COLOUR_PTN_DEFAULT:
            field_data += f'{constants.EMOJI_DONE} Color'
        else:
            field_data += f'{constants.EMOJI_NOT_DONE} Color'
        if self.embed_data.embed_thumbnail is not None:
            field_data += f'\n{constants.EMOJI_DONE} Thumbnail URL'
        else:
            field_data += f'\n{constants.EMOJI_NOT_DONE} Thumbnail URL'
        if self.embed_data.embed_author_name is not None:
            field_data += f'\n{constants.EMOJI_DONE} Author Name'
            if self.embed_data.embed_author_avatar is not None:
                field_data += f'\n{constants.EMOJI_DONE} Author Avatar'
            else:
                field_data += f'\n{constants.EMOJI_NOT_DONE} Author Avatar'
        else:
            field_data += f'\n{constants.EMOJI_NOT_DONE} Author Name'
            field_data += f'\n{constants.EMOJI_NOT_DONE} Author Avatar'

        # remove old params field if necessary
        embed = _remove_embed_field(self.original_embed, 'Embed Parameters')

        self.original_embed.add_field(name="Embed Parameters", value=field_data)

        # Edit embed fields to detail contents of params TODO
        # remove the button we pressed to get here
        self.view.remove_item(self.view.set_embed_params_button)

        # update the view in case we added the send button
        await interaction.response.edit_message(embed=self.original_embed, view=self.view)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            raise GenericError(error)
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)
        return


# modal for embed content
class EmbedContentModal(Modal):
    def __init__(self, original_embed, embed_data, view, title = 'Set Embed Content', timeout = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.original_embed = original_embed
        self.view = view
        self.embed_data: EmbedData = embed_data

    embed_title = discord.ui.TextInput(
        label='Embed title',
        placeholder='Leave blank for none.',
        required=False,
        max_length=256,
    )
    embed_description = discord.ui.TextInput(
        label='Embed main text.',
        style=discord.TextStyle.long,
        placeholder='Normal Discord markdown works, but mentions and custom emojis require full code.',
        required=True,
        max_length=4000,
    )
    embed_footer = discord.ui.TextInput(
        label='Embed footer text.',
        style=discord.TextStyle.long,
        placeholder='Titles and footers accept text and unicode emojis only.',
        required=False,
        max_length=2000,
    )
    embed_image = discord.ui.TextInput(
        label='Embed image',
        placeholder='Enter the image\'s URL or leave blank for none.',
        required=False,
        max_length=512,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # store data from the form fields into our EmbedData instance
        self.embed_data.embed_title = self.embed_title.value if self.embed_title.value else None
        self.embed_data.embed_description = self.embed_description.value if self.embed_description.value else None
        self.embed_data.embed_footer = self.embed_footer.value if self.embed_footer.value else None
        self.embed_data.embed_image = self.embed_image.value if self.embed_image.value else None
        print(self.embed_data)

        # validate URLs
        if self.embed_data.embed_image is not None and not validators.url(self.embed_data.embed_image):
            error = f"Image URL not valid: {self.embed_data.embed_image}"
            print(error)
            try:
                raise CustomError(error)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return

        field_data = ""

        if self.embed_data.embed_title is not None:
            field_data += f'{constants.EMOJI_DONE} Title'
        else:
            field_data += f'{constants.EMOJI_NOT_DONE} Title'
        if self.embed_data.embed_description is not None:
            field_data += f'\n{constants.EMOJI_DONE} Main text'
        else:
            field_data += f'\n{constants.EMOJI_NOT_DONE} Main text'
        if self.embed_data.embed_footer is not None:
            field_data += f'\n{constants.EMOJI_DONE} Footer'
        else:
            field_data += f'\n{constants.EMOJI_NOT_DONE} Footer'
        if self.embed_data.embed_image is not None:
            field_data += f'\n{constants.EMOJI_DONE} Main Image URL'
        else:
            field_data += f'\n{constants.EMOJI_NOT_DONE} Main Image URL'

        # remove old content field if necessary
        embed = _remove_embed_field(self.original_embed, 'Embed Content')

        self.original_embed.add_field(name="Embed Content", value=field_data)

        # check if we have a send button yet
        button_already_exists = any(isinstance(item, discord.ui.Button) and item.custom_id == 'embed_gen_send_button' for item in self.view.children)

        if not button_already_exists:
            # attach a send button
            self.view.add_item(self.view.set_embed_send_button)

        # remove the button we pressed to get here
        self.view.remove_item(self.view.set_embed_content_button)

        # update the view in case we added the send button
        await interaction.response.edit_message(embed=self.original_embed, view=self.view)

        # TODO Edit embed fields to confirm we have content TODO

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            raise GenericError(error)
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)
        return
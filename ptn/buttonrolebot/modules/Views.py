"""
Define classes for Views used by Interactions

Depends on: constants, Embeds, ErrorHandler

"""

# import libraries
from datetime import datetime
from typing import Optional

# import discord.py
import discord
from discord.ui import View, Modal

# import local constants
import ptn.buttonrolebot.constants as constants

# import local classes
from ptn.buttonrolebot.classes.EmbedData import EmbedData

# import local modules
from ptn.buttonrolebot.modules.Embeds import  _generate_embed_from_dict
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error


# buttons for embed generator
class EmbedGenButtons(View):
    def __init__(self, original_embed):
        super().__init__(timeout=None)
        self.original_embed = original_embed # our original embed to play around with
        self.embed_data = EmbedData() # an instance of EmbedData to send to our embed creators
        self.remove_item(self.set_embed_send_button) # remove the send button until we have something to send

    @discord.ui.button(label="Set Params", style=discord.ButtonStyle.secondary, emoji="⚙", custom_id="embed_meta_button")
    async def set_embed_params_button(self, interaction, button):
        print("Received set_embed_params_button click")

        await interaction.response.send_modal(EmbedMetaModal(self.embed_data))
        print(self.embed_data)

    @discord.ui.button(label="Set Content", style=discord.ButtonStyle.primary, emoji="🖼", custom_id="embed_content_button")
    async def set_embed_content_button(self, interaction, button):
        print("Received set_embed_content_button click")

        await interaction.response.send_modal(EmbedContentModal(self.embed_data, view=self))
        print(self.embed_data)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖", custom_id="embed_gen_cancel_button")
    async def set_embed_cancel_button(self, interaction, button):
        print("Received set_embed_cancel_button click")
        embed = discord.Embed(
            description="Embed generation cancelled.",
            color=constants.EMBED_COLOUR_QU
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Send Embed", style=discord.ButtonStyle.success, emoji="✅", custom_id="embed_gen_send_button")
    async def set_embed_send_button(self, interaction, button):
        print("Received set_embed_send_button click")
        try:
            print("Calling function to generate Embed...")
            send_embed = await _generate_embed_from_dict(interaction, self.embed_data)
            await interaction.channel.send(embed=send_embed)
            embed = discord.Embed(
                description="Embed sent. You can now dismiss this message.",
                color=constants.EMBED_COLOUR_OK
            )
            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            print(e)
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(interaction, e)


# modal for embed parameters
class EmbedMetaModal(Modal):
    def __init__(self, embed_data, title = 'Set Embed Parameters', timeout = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.embed_data = embed_data

    
    color = discord.ui.TextInput(
        label='Set the Embed border colour',
        placeholder='Enter a hex colour code in the format 0x00AA00 to use for the embed border.',
        required=False,
        max_length=8,
    )
    thumbnail = discord.ui.TextInput(
        label='Include a thumbnail.',
        placeholder='Enter the URL of the image you want to use, or leave blank for none.',
        required=False,
        max_length=512,
    )
    author_name = discord.ui.TextInput(
        label='Author name',
        placeholder='Enter an author name for the Embed.',
        required=False,
        max_length=256,
    )
    author_avatar = discord.ui.TextInput(
        label='Author avatar',
        placeholder='Enter the URL of an image to use as the Embed\'s author avatar.',
        required=False,
        max_length=512,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # turn color input into an INT
        try:
            color_int = int(self.color.value, 16)  # Convert hex string to integer
        except ValueError as e:  # TODO: Actual error handling
            print(e)
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(interaction, e)
            pass

        # store data from the form fields into our EmbedData instance
        self.embed_data.embed_color = color_int
        self.embed_data.embed_thumbnail = self.thumbnail.value
        self.embed_data.embed_author_name = self.author_name.value
        self.embed_data.embed_author_avatar = self.author_avatar.value 
        
        # Edit embed fields to detail contents of params TODO
        await interaction.response.send_message("OK", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: # TODO: move to Error Handler
        await interaction.response.send_message(f'Oops! Something went wrong: {error}', ephemeral=True)


# modal for embed content
class EmbedContentModal(Modal):
    def __init__(self, embed_data, view, title = 'Set Embed Content', timeout = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.view = view
        self.embed_data = embed_data

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
    embed_image = discord.ui.TextInput(
        label='Embed image',
        placeholder='Enter the image\'s URL or leave blank for none.',
        required=False,
        max_length=512,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # store data from the form fields into our EmbedData instance
        self.embed_data.embed_title = self.embed_title.value
        self.embed_data.embed_description = self.embed_description.value
        self.embed_data.embed_image = self.embed_image.value
        
        # check if we have a send button yet
        button_already_exists = any(isinstance(item, discord.ui.Button) and item.custom_id == 'embed_gen_send_button' for item in self.view.children)

        if not button_already_exists:
            # attach a send button
            self.view.add_item(self.view.set_embed_send_button)

        # update the view in case we added the send button
        await interaction.response.edit_message(view=self.view)

        # TODO Edit embed fields to confirm we have content TODO

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: # TODO: move to Error Handler
        await interaction.response.send_message(f'Oops! Something went wrong: {error}', ephemeral=True)
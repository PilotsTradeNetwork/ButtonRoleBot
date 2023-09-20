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

# import local modules
from ptn.buttonrolebot.modules.Embeds import  _generate_embed_from_dict
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error


# buttons for embed generator
class EmbedGenButtons(View):
    def __init__(self, embed_dict):
        super().__init__(timeout=None)
        self.embed_dict = embed_dict

    @discord.ui.button(label="Set Params", style=discord.ButtonStyle.secondary, emoji="📅", custom_id="embed_meta_button")
    async def set_embed_params_button(self, interaction, button):
        print("Received set_embed_params_button click")
        # check whether the meta dict exists yet, create if not
        if 'meta_dict' not in self.embed_dict:
            print("Creating empy sub-dictionary")
            self.embed_dict['meta_dict'] = {}
        await interaction.response.send_modal(EmbedMetaModal(self.embed_dict['meta_dict']))

    @discord.ui.button(label="Set Content", style=discord.ButtonStyle.primary, emoji="🖼", custom_id="embed_content_button")
    async def set_embed_content_button(self, interaction, button):
        print("Received set_embed_content_button click")
        # check whether content dict exists yet, create if not
        if 'content_dict' not in self.embed_dict:
            print("Creating empy sub-dictionary")
            self.embed_dict['content_dict'] = {}
        await interaction.response.send_modal(EmbedContentModal(self.embed_dict['content_dict']))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌", custom_id="embed_gen_cancel_button")
    async def set_embed_cancel_button(self, interaction, button):
        print("Received set_embed_cancel_button click")
        embed = discord.Embed(
            description="Embed generation cancelled.",
            color=constants.EMBED_COLOUR_QU
        )
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Send Embed", style=discord.ButtonStyle.success, emoji="✅", custom_id="embed_gen_send_button")
    async def set_embed_send_button(self, interaction, button):
        print("Received set_embed_send_button click")
        # check we have a sendable embed with content
        if 'content_dict' not in self.embed_dict:
            print("Creating empy sub-dictionary")
            self.embed_dict['content_dict'] = {}
        if not 'embed_message' in self.embed_dict['content_dict']:
            await interaction.response.send_modal(EmbedContentModal(self.embed_dict['content_dict']))
        else:
            send_embed = await _generate_embed_from_dict(self.embed_dict)
            await interaction.channel.send(embed=send_embed)
            embed = discord.Embed(
                description="Embed sent. You can now dismiss this message.",
                color=constants.EMBED_COLOUR_OK
            )
            await interaction.response.edit_message(embed=embed)


# modal for embed parameters
class EmbedMetaModal(Modal):
    def __init__(self, meta_dict, title = 'Set Embed Parameters', timeout = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.meta_dict = meta_dict # a dictionary to store the input

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
        # Collect data from the form fields
        embed_color = self.color.value
        embed_thumbnail = self.thumbnail.value
        embed_author_name = self.author_name.value
        embed_author_avatar = self.author_avatar.value 
        
        # Store the collected data in the data_dict
        self.meta_dict['embed_color'] = embed_color
        self.meta_dict['embed_thumbnail'] = embed_thumbnail
        self.meta_dict['embed_author_name'] = embed_author_name
        self.meta_dict['embed_author_avatar'] = embed_author_avatar

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: # TODO: move to Error Handler
        await interaction.response.send_message(f'Oops! Something went wrong: {error}', ephemeral=True)


# modal for embed content
class EmbedContentModal(Modal):
    def __init__(self, content_dict, title = 'Set Embed Content', timeout = None) -> None:
        super().__init__(title=title, timeout=timeout)
        self.content_dict = content_dict

    title = discord.ui.TextInput(
        label='Embed title',
        placeholder='Leave blank for none.',
        required=False,
        max_length=256,
    )
    description = discord.ui.TextInput(
        label='Embed main text.',
        style=discord.TextStyle.long,
        placeholder='Normal Discord markdown works, but mentions and custom emojis require full code.',
        required=True,
        max_length=4000,
    )
    image = discord.ui.TextInput(
        label='Embed image',
        placeholder='Enter the image\'s URL or leave blank for none.',
        required=False,
        max_length=512,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Collect data from the form fields
        embed_title = self.title.value
        embed_description = self.description.value
        embed_image = self.image.value
        
        # Store the collected data in the data_dict
        self.content_dict['embed_title'] = embed_title
        self.content_dict['embed_description'] = embed_description
        self.content_dict['embed_image'] = embed_image

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None: # TODO: move to Error Handler
        await interaction.response.send_message(f'Oops! Something went wrong: {error}', ephemeral=True)
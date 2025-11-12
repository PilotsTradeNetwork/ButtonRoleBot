"""
A view for previewing buttons before adding them.

"""
import logging
# import libraries
from typing import Optional
import emoji
import logging

# import discord
import discord
from discord import HTTPException
from discord.interactions import Interaction
from discord.ui import View, Modal, Button

# import bot
from ptn.buttonrolebot.bot import bot

# import local classes
from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData

# import local constants
import ptn.buttonrolebot.constants as constants
from ptn.buttonrolebot.constants import channel_botspam

# import local views
from ptn.buttonrolebot.ui_elements.ButtonConfig import ChooseRoleView

# import local modules
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error, CustomError, BadRequestError
from ptn.buttonrolebot.modules.Embeds import button_config_embed, stress_embed, amazing_embed
from ptn.buttonrolebot.modules.Helpers import check_role_exists, _add_role_button_to_view

"""
1. Generate an embed, heading_embed, declaring the below embed to be our preview.
   (Done in ButtonRoleCommands.py)
2. Generate a second embed, preview_embed, showing the content of the message-embed
   the buttons are to be added to. To this message, containing two embeds, we attach a
   button, "New button", and a button in the final row, "Cancel". Both of these embeds
   are attached to our initial interaction.response
   (Done in ButtonRoleCommands.py)
3. Clicking "New button" displays the existing button creator interface as an
   interaction.response to the button press. "New button" is updated as the user moves
   back and forward through the creator.
4. Confirming a button via this interface adds it to our list of buttons to be added,
   but does not add them until we confirm all buttons.
5. The user can edit a button they've already added by clicking on it in the preview.
6. Once at least one button has been added to the preview, an "Add button(s) to message"
   button will appear in the final row.
7. We allow the creation of up to 23 buttons, as we need the final two slots for "Cancel"
   and "Add to message".
8. The existing final page of the button creator is removed from individual button
   creation and repurposed for when all buttons are sent using the Add to message button.
9. ~~Each preview button would require its own unique instance of button_data and a unique
   identifier so it can be selected and edited.~~ ETA: Actually, we can just pull all the
   necessary data from the preview buttons themselves
10. This interface could also be used for a button editor #18 
"""


class ButtonPreviewView(View):
    def __init__(self, message, timeout: None):
        self.message: discord.Message = message
        self.spamchannel = bot.get_channel(channel_botspam())
        super().__init__(timeout=timeout)

    @discord.ui.button(label='New Button', emoji='👋', style=discord.ButtonStyle.secondary)
    async def new_button(self, interaction: discord.Interaction, button):
        try:
            # instantiate an empty instance of our RoleButtonData
            button_data = RoleButtonData()
            # add our message object
            button_data.message = self.message
            # define our index point for content
            index = 0
            # generate our first embed
            embed = button_config_embed(index, button_data)
            # define our first view
            view = ChooseRoleView(button_data)
            # send message with view and embed
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logging.exception(e)
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)
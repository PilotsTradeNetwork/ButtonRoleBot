# from __future__ import annotations

"""
A set of classes to add buttons to a message

Depends on: constants

ErrorHandler cannot be imported directly because of dependency on bot.py
Instead, pass it through to the class if needed (e.g. self.error_handler)

"""

# import libraries
import re

# import discord.py
import discord

# import local constants
import ptn.buttonrolebot.constants as constants

# import classes
from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData

class DynamicButton(discord.ui.DynamicItem[discord.ui.Button], template = r'button:message:(?P<message_id>[0-9]+):role:(?P<role_id>[0-9]+)'):
    def __init__(self, button_data: RoleButtonData) -> None:
        self.button_data = button_data
        self.message: discord.Message = button_data.message
        self.style: discord.ButtonStyle = button_data.button_style
        self.role: discord.Role = button_data.role_object
        super().__init__(
            discord.ui.Button(
                label=self.button_data.label,
                style=self.style,
                custom_id=f'button:message:{self.message.id}:role:{self.role.id}',
                emoji='🎇',
            )
        )
        self.message_id: int = message_id
        self.role_id: int = role_id
        print("DynamicButton: create called")
        # TODO: - Modal to select button attributes

    # This is called when the button is clicked and the custom_id matches the template.
    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        print("DynamicButton: from_custom_id called")
        message_id = int(match['message_id'])
        role_id = int(match['role_id'])
        return cls(message_id, role_id)

    async def callback(self, interaction: discord.Interaction) -> None:
        print("DynamicButton: callback from:")
        print(f'button:message:{self.message_id}:role:{self.role_id}')
        await interaction.response.send_message(f'message ID: {self.message_id} | role ID: {self.role_id}', ephemeral=True)

# TODO: attach buttons to a message, see if they work persistently
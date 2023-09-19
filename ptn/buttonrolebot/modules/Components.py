"""
Components.py

Defines the dynamic buttons added by the bot

Dependencies: none
"""

from __future__ import annotations

from discord.ext import commands
import discord
import re

class DynamicButton(discord.ui.DynamicItem[discord.ui.Button], template = r'button:role:(?P<role_id>[0-9]+):message:(?P<message_id>[0-9]+)'):
    def __init__(self, role_id, msg_id: int) -> None:
        super().__init__(
            discord.ui.Button(
                label='Do Thing',
                style=discord.ButtonStyle.blurple,
                custom_id=f'button:role:{role_id}:message:{msg_id}',
                emoji='🎇',
            )
        )
        self.role_id: int = role_id
        self.msg_id: int = msg_id

    # This is called when the button is clicked and the custom_id matches the template.
    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        print("from_custom_id")
        role_id = int(match['role_id'])
        print(role_id)
        message_id = int(match['message_id'])
        print(message_id)
        return cls(role_id, message_id)

    async def callback(self, interaction: discord.Interaction) -> None:
        print("Callback")
        await interaction.response.send_message(f'role ID: {self.role_id} | msg ID: {self.msg_id}', ephemeral=True)
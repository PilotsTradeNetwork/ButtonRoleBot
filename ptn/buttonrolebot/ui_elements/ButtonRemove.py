"""
A discord.ui element for removing buttons added by BRB.

"""
# import discord
import discord
from discord.interactions import Interaction
from discord.ui import View, Modal, Button

# import bot
from ptn.buttonrolebot.bot import bot

# import local classes
from ptn.buttonrolebot.classes.RoleButtonData import RoleButtonData

# import local constants
import ptn.buttonrolebot.constants as constants
from ptn.buttonrolebot.constants import channel_botspam

# import local modules
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error, CustomError


class ConfirmRemoveButtonsView(View):
    def __init__(self, message: discord.Message):
        self.message = message
        super().__init__(timeout=None)

    @discord.ui.button(
        label='✗ Cancel',
        custom_id='cancel_remove_button',
        style=discord.ButtonStyle.secondary,
    )
    async def cancel_remove_button(self, interaction: discord.Interaction, button):
        print(f"User cancelled button removal from {self.message}")
        embed = discord.Embed(
            description='❎ **Cancelled**.',
            color=constants.EMBED_COLOUR_OK
        )
        embed.set_footer(text="You can dismiss this message.")

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        label='✔ Confirm',
        custom_id='confirm_remove_button',
        style=discord.ButtonStyle.danger,
    )

    async def confirm_remove_button(self, interaction: discord.Interaction, button):
        print(f"User confirmed button removal from {self.message}")
        try:
            print("Removing the view")
            await self.message.edit(view=None)

            print("Notifying bot-spam")
            spamchannel = bot.get_channel(channel_botspam())
      
            embed = discord.Embed(
                description=f':warning: <@{interaction.user.id}> removed buttons from {self.message.jump_url} using `Remove Buttons`.',
                color=constants.EMBED_COLOUR_QU
            )

            await spamchannel.send(embed=embed)

            print("Notifying user")
            embed = discord.Embed(
                description=f'✅ **Buttons removed from {self.message.jump_url}**.',
                color=constants.EMBED_COLOUR_OK
            )
            embed.set_footer(text="You can dismiss this message.")

            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)


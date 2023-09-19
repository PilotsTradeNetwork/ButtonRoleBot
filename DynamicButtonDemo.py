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

"""
Yay we successfully got a role ID and message ID through a dynamic persistent button.

Next steps:
- lookup the role ID from the server list of roles
- add it if the user hasn't got it, remove if they do
- change the dynamic_button function to add the button to the message with the given ID, instead of sending a new message
"""


class DynamicButtonDemoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def setup_hook(self) -> None:

        # For dynamic items, we must register the classes instead of the views.
        self.add_dynamic_items(DynamicButton)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = DynamicButtonDemoBot()


@bot.command()
async def send_message(ctx, *message):
    # Join the strings in the message argument into a single string, using the space character as the separator
    message_string = " ".join(message)

    # Send the message string back to the channel
    await ctx.send(message_string)



@bot.command()
async def dynamic_button(ctx: commands.Context, role_id: int, msg_id: int):
    """Starts a dynamic button."""

    view = discord.ui.View(timeout=None)
    view.add_item(DynamicButton(role_id, msg_id))
    await ctx.send('Here is your very own button!', view=view)


bot.run('token')

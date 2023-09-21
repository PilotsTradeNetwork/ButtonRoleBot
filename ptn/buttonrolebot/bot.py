"""
bot.py

This is where we define our bot object and setup_hook (replacement for on_ready)

Dependencies: Constants, Components, Metadata

"""
import discord
from discord.ext import commands

# import constants
from ptn.buttonrolebot._metadata import __version__
from ptn.buttonrolebot.constants import channel_botdev, channel_botspam, EMBED_COLOUR_OK

# import persistent buttons
from ptn.buttonrolebot.ui_elements.ButtonCreator import DynamicButton

# define bot object
class ButtonRoleBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('🎢'), intents=intents)

    async def setup_hook(self) -> None:

        # For dynamic items, we must register the classes instead of the views.
        self.add_dynamic_items(DynamicButton)

    async def on_ready(self):
        try:
            # TODO: this should be moved to an on_setup hook
            print('-----')
            print(f'{bot.user.name} version: {__version__} has connected to Discord!')
            print('-----')
            devchannel = bot.get_channel(channel_botdev())
            spamchannel = bot.get_channel(channel_botspam())
            embed = discord.Embed(
                title="🟢 BUTTON ROLE BOT ONLINE",
                description=f"🎢<@{bot.user.id}> connected, version **{__version__}**.",
                color=EMBED_COLOUR_OK
            )
            await devchannel.send(embed=embed)

        except Exception as e:
            print(e)

    async def on_disconnect(self):
        print('-----')
        print(f'🔌ButtonRoleBot has disconnected from discord server, version: {__version__}.')
        print('-----')


bot = ButtonRoleBot()
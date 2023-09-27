"""
bot.py

This is where we define our bot object and setup_hook (replacement for on_ready)

Dependencies: Constants, Metadata

"""
# import libraries
import re

# import discord
import discord
from discord.ext import commands

# import constants
from ptn.buttonrolebot._metadata import __version__
from ptn.buttonrolebot.constants import channel_botdev, channel_botspam, EMBED_COLOUR_OK, role_council, role_mod

# import classes
# from ptn.buttonrolebot.ui_elements.ButtonCreator import DynamicButton

# import modules
from ptn.buttonrolebot.modules.ErrorHandler import CustomError, on_generic_error


"""
Dynamic Button

Depends on bot (for error handling), bot depends on it, can't figure out any other way to organise except putting it in here 🤷‍♀️
I mean I could write a separate error handler for this, or I could NOT

i'm so sorry kutu
"""
class DynamicButton(discord.ui.DynamicItem[discord.ui.Button], template = r'button:role:(?P<role_id>[0-9]+):message:(?P<message_id>[0-9]+):action:(?P<action>[a-z]+)'):
    def __init__(self, action: str, role_id: int, message_id: int) -> None:
        print("DynamicButton init")
        super().__init__(
            discord.ui.Button(
                label='Assign Role',
                style=discord.ButtonStyle.blurple,
                custom_id=f'button:role:{role_id}:message:{message_id}:action:{action}'
            )
        )
        self.action: str = action
        self.role_id: int = role_id
        self.message_id: int = message_id


    # This is called when the button is clicked and the custom_id matches the template.
    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        print("DynamicButton: from_custom_id called")
        action = str(match['action']) if match else 'toggle'
        role_id = int(match['role_id'])
        message_id = int(match['message_id'])
        return cls(action, role_id, message_id)

    async def callback(self, interaction: discord.Interaction) -> None:
        print("DynamicButton: callback from:")
        print(f'action:{self.action}:message:{self.message_id}:role:{self.role_id}')

        print(f"Spamchannel is {spamchannel}")

        try:
            # get role object
            role = discord.utils.get(interaction.guild.roles, id=self.role_id)

            # check if user has it
            print(f'Check whether user has role: "{role}"')
            
            if role not in interaction.user.roles and self.action != 'take':
                print('User doesn\'t have role and action is not take')
                # rolercoaster giveth
                await interaction.user.add_roles(role)
                print(f'➕ Gave {interaction.user} the {role} role')
                adverb = "now"

            elif role in interaction.user.roles and self.action != 'give':
                print('User has role and action is not give')
                # ...and rolercoaster taketh away
                await interaction.user.remove_roles(role)
                print(f'➖ Removed {interaction.user} from the {role} role')
                adverb = "no longer"

            elif role not in interaction.user.roles and self.action == 'take':
                print('No action required: user hasn\'t got role and action is take')
                adverb = 'don\'t'

            elif role in interaction.user.roles and self.action == 'give':
                print('No action required: user already has role and action is give')
                adverb = 'already'

            embed = discord.Embed(
                description=f'You {adverb} have the <@&{role.id}> role.',
                color=EMBED_COLOUR_OK
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print(e)
            try:
                error = f"Role not granted. Please contact a member of the <@&{role_mod()}> team or <@&{role_council()}>"
                raise CustomError(error)
            except Exception as e2:
                print(e2)
                error= f"User received message: {error}\nOriginal Error: ({e})"
                await on_generic_error(spamchannel, interaction, error)
            return


"""
Bot object
"""
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
            global spamchannel
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


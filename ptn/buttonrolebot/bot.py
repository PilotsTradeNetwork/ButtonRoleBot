"""
bot.py

This is where we define our bot object and setup_hook (replacement for on_ready)

Dependencies: Constants, Metadata

"""
# import libraries
import asyncio
import re

# import discord
import discord
from discord import Forbidden
from discord.ext import commands

# import constants
from ptn.buttonrolebot._metadata import __version__
from ptn.buttonrolebot.constants import channel_botdev, channel_botspam, EMBED_COLOUR_OK, role_council, role_mod, EMBED_COLOUR_ERROR, EMBED_COLOUR_QU

# import classes
# from ptn.buttonrolebot.ui_elements.ButtonCreator import DynamicButton

# import modules
from ptn.buttonrolebot.modules.ErrorHandler import CustomError, on_generic_error
from ptn.buttonrolebot.utils import get_member


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

        embed = discord.Embed(
            description="⏳ Processing...",
            color=EMBED_COLOUR_QU
        )

        # quickly send off a message so we don't miss our 3 second response window
        await interaction.response.send_message(embed=embed, ephemeral=True)

        timeout = 30 # timeout in seconds for administering role

        async def manage_user_role():
            try:
                print(f"Spamchannel is {spamchannel}")

                # get role object
                role = discord.utils.get(interaction.guild.roles, id=self.role_id)

                # check if we have permissions for this role
                bot_member: discord.Member = await get_member(bot, bot.user.id)
                if bot_member.top_role <= role or role.managed:
                    print(f"⚠ We don't have permission for {role}")
                    try:
                        # notify bot-spam
                        message: discord.Message = await interaction.channel.fetch_message(self.message_id)
                        embed = discord.Embed(
                            description=f':warning: <@{bot_member.id}> does not have permission to manage <@&{role.id}>. Called from {message.jump_url}.\n\n'
                                        'Bot role is not high enough in role hierarchy to grant this role. **Please move the bot role higher or edit the offending button**.',
                            color=EMBED_COLOUR_ERROR
                        )
                        content = f'🔔 <@&{role_mod()}>: Button failed to grant role <@&{role.id}>'
                        await spamchannel.send(content=content, embed=embed)
                    except Exception as e:
                        print(f'Error notifying bot-spam: {e}')

                    try:
                        # notify user
                        raise CustomError(f"Sorry, I don't have permission to manage <@&{role.id}>. Please contact a <@&{role_mod()}> or <@&{role_council()}> member.")
                    except Exception as e:
                        await on_generic_error(spamchannel, interaction, e)
                    return False

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

                await interaction.edit_original_response(embed=embed)

            except Forbidden as e:
                print(e)
                try:
                    # notify bot-spam
                    message: discord.Message = await interaction.channel.fetch_message(self.message_id)
                    embed = discord.Embed(
                        description=f':warning: <@{bot_member.id}> does not have permission to manage <@&{role.id}> for <@{interaction.user.id}>. Called from {message.jump_url}. **Bot role needs Manage Roles permission**.',
                        color=EMBED_COLOUR_ERROR
                    )
                    embed.set_footer(text=e)
                    await spamchannel.send(embed=embed)
                except Exception as e:
                    print(f'Error notifying bot-spam: {e}')

                print("Raising error for user")
                # raise error
                try:
                    error = f"Role <@&{role.id}> not granted. Please contact a member of the <@&{role_mod()}> team or <@&{role_council()}> for assistance."
                    raise CustomError(error)
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                return 

            except Exception as e:
                print(e)
                try:
                    # notify bot-spam
                    message: discord.Message = await interaction.channel.fetch_message(self.message_id)
                    embed = discord.Embed(
                        description=f':warning: <@{bot_member.id}> failed administering <@&{role.id}> for <@{interaction.user.id}>. Called from {message.jump_url}. Error given:\n{e}',
                        color=EMBED_COLOUR_ERROR
                    )
                    await spamchannel.send(embed=embed)
                except Exception as e:
                    print(f'Error notifying bot-spam: {e}')

                print("Raising error for user")
                # raise error
                try:
                    error = f"Role <@&{role.id}> not granted. Please contact a member of the <@&{role_mod()}> team or <@&{role_council()}> for assistance."
                    raise CustomError(error)
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                return

        try:
            await asyncio.wait_for(manage_user_role(), timeout=timeout)

        except asyncio.TimeoutError: # TODO move to error handler
            print("User role management timed out")
            # notify user
            embed = discord.Embed(
                description=f"❌ Timed out. Please contact a member of the <@&{role_mod()}> team or <@&{role_council()}> for assistance.",
                color=EMBED_COLOUR_ERROR
            )
            await interaction.edit_original_response(embed=embed)

            # notify bot-spam
            message: discord.Message = await interaction.channel.fetch_message(self.message_id)

            embed = discord.Embed(
                description=f':warning: <@{bot.user.id}> **timed out** ({timeout}) while trying to {self.action} <@&{self.role_id}> for <@{interaction.user.id}>. Called from {message.jump_url}.',
                color=EMBED_COLOUR_ERROR
            )
            await spamchannel.send(embed=embed)

        except Exception as e:
            print(e)


"""
Bot object
"""
# define bot object
class ButtonRoleBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.none()
        intents.message_content = True
        intents.members = True
        intents.messages = True
        intents.guilds = True

        super().__init__(command_prefix=commands.when_mentioned_or('🎢'), intents=intents, chunk_guilds_at_startup=False)

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


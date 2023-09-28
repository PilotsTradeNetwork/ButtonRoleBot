"""
A set of discord.ui elements for customising buttons added by BRB.

"""
# import libraries
import emoji

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

# import local modules
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error, CustomError, BadRequestError
from ptn.buttonrolebot.modules.Embeds import button_config_embed, stress_embed, amazing_embed
from ptn.buttonrolebot.modules.Helpers import check_role_exists, _add_role_button_to_view, _create_button

"""
Multi-part message supported by embeds:
1. Choose role - click button to pop-up modal
 - View: button 'Enter Role ID'. On click: open Modal
 - Modal: one field: role ID. On submit: save role ID to class, next page
2. Confirm role - click OK button (next embed) / back button (previous embed)
 - Text: <@&role_id>.
 - View: button 'Confirm'. On click: next page. button: 'Back'. On click: previous page
3. Choose button appearance - 4x buttons corresponding to colour 
4. Choose button text and emoji - button to pop up modal, back button
5. Confirm choices - OK button, back button, cancel button

"""

spamchannel = bot.get_channel(channel_botspam())

"""
INDEX FUNCTIONS
"""


# a function to choose view based on index
def _select_view_from_index(index, button_data: RoleButtonData):
    print("Called _select_view_from_index")
    if index == 0:
        print("Assigning 0: ChooseRoleView")
        view = ChooseRoleView(button_data)
    elif index == 1:
        print("Assigning 1: ConfirmRoleView")
        view = ConfirmRoleView(button_data)
    elif index == 2:
        print("Assigning 2: ButtonActionView")
        view = ButtonActionView(button_data)
    elif index == 3:
        print("Assigning 3: ButtonStyleView")
        view = ButtonStyleView(button_data)
    elif index == 4:
        print("Assigning 4: LabelEmojiView")
        view = LabelEmojiView(button_data)
    elif index == 5:
        print("Assigning 5: ConfirmConfigView")
        view = ConfirmConfigView(button_data)
    return view


# function to increment index by one
def _increment_index(index, button_data: RoleButtonData):
    print("Called _increment_index")
    if index <= 5:  # TODO: actual max index number here
        index += 1
        # generate new embed
        embed = button_config_embed(index, button_data)
        # assign new view
        view = _select_view_from_index(index, button_data)
    return embed, view


# function to decrement index by one
def _decrement_index(index, button_data: RoleButtonData):
    print("Called _decrement_index")
    if index >= 1:
        index -= 1
        # generate new embed
        embed = button_config_embed(index, button_data)
        # assign new view
        view = _select_view_from_index(index, button_data)
    return embed, view


"""
GLOBAL COMPONENT BUTTONS
"""


class CancelButton(Button):
    def __init__(self, index):
        self.index = index
        super().__init__(
            label="✗",
            style=discord.ButtonStyle.danger,
            custom_id="generic_cancel_button",
            row=2 if self.index == 2 or self.index == 3 else 1
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✖ generic_cancel_button click")
        embed = discord.Embed(
            description="❎ **Button creation cancelled**.",
            color=constants.EMBED_COLOUR_QU
        )
        embed.set_footer(text="You can dismiss this message.")
        return await interaction.response.edit_message(embed=embed, view=None)


class PrevButton(Button):
    def __init__(self, index, button_data: RoleButtonData):
        self.index = index
        self.button_data = button_data
        super().__init__(
            label="◄",
            style=discord.ButtonStyle.secondary,
            custom_id="generic_previous_button",
            row=2 if self.index == 2 or self.index == 3 else 1
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ◄ generic_previous_button click")
        # decrement index by 1
        if self.index >= 1:
            embed, view = _decrement_index(self.index, self.button_data)
            # update message
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.defer()


class NextButton(Button):
    def __init__(self, index, button_data: RoleButtonData):
        self.index = index
        self.button_data = button_data
        super().__init__(
            label="►",
            style=discord.ButtonStyle.secondary,
            custom_id="generic_next_button",
            row=2 if self.index == 2 or self.index == 3 else 1
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ► generic_next_button click")
        # various checks that the user isn't getting ahead of themselves
        if self.index == 0:
            if self.button_data.role_id == None:
                try:
                    raise CustomError("You must enter a Role ID first.")
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                    return

            # check int corresponds to a role on this server
            role = None
            print(f'Role is {role}')
            role = await check_role_exists(interaction, self.button_data.role_id)

            if role == None:
                try:
                    raise CustomError(f"Can't find a role with ID `{self.button_data.role_id}`.")
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                return
            else:
                self.button_data.role_object = role

            # check if we have permission to manage this role
            bot_member: discord.Member = interaction.guild.get_member(bot.user.id)
            if bot_member.top_role <= role:
                print("We don't have permission for this role")
                try:
                    raise CustomError(f"I don't have permission to manage <@&{self.button_data.role_id}>.")
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                return

        elif self.index == 2:
            if self.button_data.button_action == None:
                try:
                    raise CustomError("You must choo-choo-choose a button action first 🚂")
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                    return

        elif self.index == 3:
            if self.button_data.button_style == None:
                try:
                    raise CustomError("You must choo-choo-choose a button style first 🚂")
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                    return

        elif self.index == 4:
            if not self.button_data.button_label and not self.button_data.button_emoji:
                try:
                    raise CustomError(f"You must give the button *at least one* of either **label** or **emoji**.")
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
                return

        # increment index by 1
        if self.index <= 7:
            embed, view = _increment_index(self.index, self.button_data)
            # update message
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.defer()


class ConfirmButton(Button):
    def __init__(self, index, button_data: RoleButtonData):
        self.index = index
        self.button_data = button_data
        super().__init__(
            label='✔',
            style=discord.ButtonStyle.success,
            custom_id="generic_confirm_button",
            row=2 if self.index == 2 or self.index == 3 else 1
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✅ generic_confirm_button click")
        # increment index by 1
        embed, view = _increment_index(self.index, self.button_data)
        # update message
        await interaction.response.edit_message(embed=embed, view=view)


"""
INDEXED VIEWS

"""

"""
Page 1: Input role ID
"""


class ChooseRoleView(View):
    def __init__(self, button_data: RoleButtonData):
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 0
        self.clear_items()
        self.add_item(PrevButton(self.index, self.button_data))
        self.add_item(CancelButton(self.index))
        self.add_item(self.button_enter_role_id)
        self.add_item(NextButton(self.index, self.button_data))

    @discord.ui.button(
        label='Enter Role ID',
        custom_id='enter_role_id_button',
        style=discord.ButtonStyle.primary,
        emoji='🎢',
        row=1)
    async def button_enter_role_id(self, interaction, button):
        try:
            await interaction.response.send_modal(EnterRoleIDModal(self.button_data))
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)


"""
Page 2: Confirm role
"""


class ConfirmRoleView(View):
    def __init__(self, button_data: RoleButtonData):
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 1
        self.clear_items()
        self.add_item(PrevButton(self.index, self.button_data))
        self.add_item(CancelButton(self.index))
        self.add_item(ConfirmButton(self.index, self.button_data))
        self.add_item(NextButton(self.index, self.button_data))

    pass


"""
Page 3: Set button action
"""


class ButtonActionView(View):
    def __init__(self, button_data: RoleButtonData):
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 2
        self.add_item(PrevButton(self.index, self.button_data))
        self.add_item(CancelButton(self.index))
        self.add_item(NextButton(self.index, self.button_data))

    @discord.ui.button(
        label='Give role',
        custom_id='give_action_button',
        style=discord.ButtonStyle.success,
        row=1
    )
    async def success_style_button(self, interaction: discord.Interaction, button):
        print("🔘 Chose give_action_button")
        try:
            self.button_data.button_action = 'give'
            embed, view = _increment_index(self.index, self.button_data)

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

    @discord.ui.button(
        label='Take role',
        custom_id='take_action_button',
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def primary_style_button(self, interaction: discord.Interaction, button):
        print("🔘 Chose take_action_button")
        try:
            self.button_data.button_action = 'take'
            embed, view = _increment_index(self.index, self.button_data)

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

    @discord.ui.button(
        label='Toggle role',
        custom_id='toggle_action_button',
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def secondary_style_button(self, interaction: discord.Interaction, button):
        print("Chose secondary button")
        try:
            self.button_data.button_action = 'toggle'
            embed, view = _increment_index(self.index, self.button_data)

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)


"""
Page 4: Set button style
"""


class ButtonStyleView(View):
    def __init__(self, button_data: RoleButtonData):
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 3
        self.add_item(PrevButton(self.index, self.button_data))
        self.add_item(CancelButton(self.index))
        self.add_item(NextButton(self.index, self.button_data))

    @discord.ui.button(
        label='Success',
        custom_id='success_style_button',
        style=discord.ButtonStyle.success,
        row=1
    )
    async def success_style_button(self, interaction, button):
        print("Chose green button")
        try:
            self.button_data.button_style = discord.ButtonStyle.success
            embed, view = _increment_index(self.index, self.button_data)

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

    @discord.ui.button(
        label='Primary',
        custom_id='primary_style_button',
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def primary_style_button(self, interaction, button):
        print("Chose primary button")
        try:
            self.button_data.button_style = discord.ButtonStyle.primary
            embed, view = _increment_index(self.index, self.button_data)

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

    @discord.ui.button(
        label='Secondary',
        custom_id='secondary_style_button',
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def secondary_style_button(self, interaction, button):
        print("Chose secondary button")
        try:
            self.button_data.button_style = discord.ButtonStyle.secondary
            embed, view = _increment_index(self.index, self.button_data)

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

    @discord.ui.button(
        label='Danger',
        custom_id='danger_style_button',
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def danger_style_button(self, interaction, button):
        print("Chose danger button")
        try:
            self.button_data.button_style = discord.ButtonStyle.danger
            embed, view = _increment_index(self.index, self.button_data)

            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)


"""
Page 5: Set label/emoji
"""


class LabelEmojiView(View):
    def __init__(self, button_data: RoleButtonData):
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 4
        self.clear_items()
        self.add_item(PrevButton(self.index, self.button_data))
        self.add_item(CancelButton(self.index))
        self.add_item(self.label_emoji_button)
        self.add_item(NextButton(self.index, self.button_data))

    @discord.ui.button(
        label='Choose',
        custom_id='label_emoji_button',
        style=discord.ButtonStyle.primary,
        emoji='🏷',
        row=1
    )
    async def label_emoji_button(self, interaction: discord.Interaction, button):
        print("🔘 Received label_emoji_button click")

        await interaction.response.send_modal(EnterLabelEmojiModal(self.button_data))


"""
Page 6: Confirm
"""


class ConfirmConfigView(View):
    def __init__(self, button_data: RoleButtonData):
        super().__init__(timeout=None)
        self.button_data = button_data
        self.message: discord.Message = self.button_data.message
        self.index = 5
        self.clear_items()
        self.add_item(PrevButton(self.index, self.button_data))
        self.add_item(CancelButton(self.index))
        self.add_item(self.final_submit_button)
        self.add_item(self.add_another_button)

    @discord.ui.button(
        label='✔ Create Button',
        style=discord.ButtonStyle.success,
        custom_id="final_submit_button",
        row=1
    )
    async def final_submit_button(self, interaction: discord.Interaction, button):
        print("Received ✅ final_submit_button click")
        try:
            # create the button!
            button = _create_button(self.button_data)
            self.button_data.button_list.append(button)

            # Initialize view outside loop
            if self.message.components:
                print("Existing view detected, we will add our button to it")
                view = View.from_message(self.message)
                view.timeout = None
            else:
                print("Defining empty view")
                view = discord.ui.View(timeout=None)

            for button in self.button_data.button_list:
                await _add_role_button_to_view(interaction, button, self.button_data,
                                               view)  # Modify this function to accept view as argument

            await self.message.edit(view=view)

            # TODO lol

            # increment index by 1
            final_index = self.index + 1
            embed = button_config_embed(final_index, self.button_data)
            view = StressButtonView()
            await interaction.response.edit_message(embed=embed, view=view)
        except HTTPException as e:
            try:
                raise BadRequestError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

    @discord.ui.button(
        label='+ Add Another Button',
        style=discord.ButtonStyle.primary,
        custom_id="add_another_button",
        row=1
    )
    async def add_another_button(self, interaction: discord.Interaction, button):
        print("Received add_another_button click")
        button = _create_button(self.button_data)
        self.button_data.button_list.append(button)

        print('Resetting data for a new button')
        self.button_data.reset()
        embed = button_config_embed(0, self.button_data)
        initial_view = ChooseRoleView(self.button_data)
        print('Going back to the beginning')
        await interaction.response.edit_message(embed=embed, view=initial_view)



"""
Final page: success!
"""


class StressButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label='That was stressful',
        style=discord.ButtonStyle.danger,
        custom_id="stress_button",
        emoji='😰'
    )
    async def stress_button(self, interaction: discord.Interaction, button):
        print("Received stress_button click")
        try:
            embed = stress_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label='I\'m amazing!',
        style=discord.ButtonStyle.success,
        custom_id="amazing_button",
        emoji='💪'
    )
    async def amazing_button(self, interaction: discord.Interaction, button):
        print("Received amazing_button click")
        try:
            embed = amazing_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)


"""
MODALS

"""


# modal to input role ID
class EnterRoleIDModal(Modal):
    def __init__(self, button_data: RoleButtonData, title='Set Role', timeout=None):
        self.button_data = button_data
        self.index = 0
        if self.button_data.role_id:
            self.role_id.default = self.button_data.role_id
        super().__init__(title=title, timeout=timeout)

    role_id = discord.ui.TextInput(
        label='Enter Role ID',
        placeholder='e.g. 800091021852803072',
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        # check user has entered an INT
        try:
            self.button_data.role_id = int(self.role_id.value)
            print(f'Stored Role ID: {self.button_data.role_id}')
        except ValueError as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return

        # check int corresponds to a role on this server
        role: discord.Role = None
        print(f'Role is {role}')
        role = await check_role_exists(interaction, self.button_data.role_id)

        if role == None:
            try:
                raise CustomError(f"Can't find a role with ID `{self.button_data.role_id}`.")
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return
        else:
            self.button_data.role_object = role

        # check if we have permission to manage this role
        bot_member: discord.Member = interaction.guild.get_member(bot.user.id)
        if bot_member.top_role <= role or role.managed:
            print("We don't have permission for this role")
            try:
                raise CustomError(f"I don't have permission to manage <@&{self.button_data.role_id}>.")
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return

        embed, view = _increment_index(self.index, self.button_data)

        # edit our message to next in sequence
        print("Updating message with new embed and view...")
        await interaction.response.edit_message(embed=embed, view=view)


# modal to input button label/emoji
class EnterLabelEmojiModal(Modal):
    def __init__(self, button_data: RoleButtonData, title='Set Label & Emoji', timeout=None):
        self.button_data = button_data
        self.index = 4
        if self.button_data.button_label:
            print(f'Default set to {self.button_data.button_label}')
            self.button_label.default = str(self.button_data.button_label)
        if self.button_data.button_emoji:
            print(f'Default set to {self.button_data.button_emoji}')
            self.button_emoji.default = str(self.button_data.button_emoji)
        # TODO: above caused some weirdness after latest update until specifying strings
        super().__init__(title=title, timeout=timeout)

    button_label = discord.ui.TextInput(
        label='Label',
        placeholder='The text that will appear on your button.',
        style=discord.TextStyle.short,
        required=False,
        max_length=80
    )
    button_emoji = discord.ui.TextInput(
        label='Emoji',
        placeholder='The emoji that will appear on your button.',
        style=discord.TextStyle.short,
        required=False,
        max_length=60
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.button_label.value == "" and self.button_emoji.value == "":
            try:
                raise CustomError(f"You must give the button *at least one* of either **label** or **emoji**.")
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)
            return

        if self.button_label.value == "":
            print("🔴 Received empty string for Label")
            self.button_data.button_label = None
        else:
            self.button_data.button_label = self.button_label

        print(f'Button label set: {self.button_data.button_label}')

        if self.button_emoji.value == "":
            print("🔴 Received empty string for Emoji")
            self.button_data.button_emoji = None
        else:
            # check if user has entered Discord emoji
            if ':' in self.button_emoji.value and not '<' in self.button_emoji.value:
                print(
                    f"⏳ User seems to have entered Discord emoji as {self.button_emoji.value}, attempting to resolve against library...")
                unicode_emoji = emoji.emojize(self.button_emoji.value)
                print(f"Updated emoji: {unicode_emoji}")
                self.button_data.button_emoji = str(unicode_emoji)
            else:
                self.button_data.button_emoji = str(self.button_emoji.value)

            if ':' in self.button_data.button_emoji and not '<' in self.button_data.button_emoji:  # triggered if we failed to convert a : to an emoji and its not custom
                print("Found Discord non-custom code in emoji value")
                try:
                    error = f'**Could not resolve the emoji you entered against its unicode name**.\n' \
                            'Not all Discord emojis have the same shortcode as the unicode name, for example `:heart:` in Discord is `:red_heart:` in unicode.\n' \
                            'You can try sending the emoji you want in a message, then copying the emoji from that message.'
                    raise CustomError(error)
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)

            elif emoji.emoji_count(
                    self.button_data.button_emoji) > 1:  # should trigger if we have a ZWJ emoji or too many emojis
                print("number of emojis in input is not 1")
                try:
                    error = f'The emoji you entered does not seem to be valid: {self.button_data.button_emoji}\n' \
                            'It may be a non-standard or unicode-unsupported emoji. ' \
                            'You can try sending the emoji you want in a message, then copying the emoji from that message.'
                    raise CustomError(error)
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)

        print(f'Button emoji set: {self.button_data.button_emoji}')

        if self.button_data.button_emoji:
            print("✅ Bot thinks we have an emoji")

        embed, view = _increment_index(self.index, self.button_data)

        # edit our message to next in sequence
        print("Updating message with new embed and view...")
        await interaction.response.edit_message(embed=embed, view=view)

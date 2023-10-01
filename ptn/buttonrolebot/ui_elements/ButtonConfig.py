"""
A set of discord.ui elements for customising buttons added by BRB.

"""
# import libraries
import emoji
import random
import traceback
import uuid

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
from ptn.buttonrolebot.constants import channel_botspam, DEFAULT_BUTTON_LABEL, HOORAY_GIFS

# import local modules
from ptn.buttonrolebot.modules.ErrorHandler import GenericError, on_generic_error, CustomError, BadRequestError
from ptn.buttonrolebot.modules.Embeds import button_config_embed, stress_embed, amazing_embed, button_edit_heading_embed
from ptn.buttonrolebot.modules.Helpers import check_role_exists, _add_role_buttons_to_view

spamchannel = bot.get_channel(channel_botspam())

async def _check_for_button_conflict(interaction: discord.Interaction, buttons: list, button_data: RoleButtonData):
    print(f"Called _check_for_button_conflict with  {button_data}")
    try:
        role_id = button_data.role_id
        action = button_data.button_action
        unique_id = button_data.unique_id

        conflicting_data = None

        print("⏳ Searching for conflicts in buttons list...")
        for i, button_data_instance in enumerate(buttons):
            if button_data_instance.role_id == role_id and button_data_instance.button_action == action:
                if button_data_instance.unique_id != unique_id:
                    print(f"⚠ Found conflict with {button_data_instance.unique_id}")
                    conflicting_data = button_data_instance
                    break

        if conflicting_data is not None:
            print("▶ Notifying user of conflict.")
            embed = discord.Embed(
                description="❌ Each message can only have one button with a given role and action combination. " \
                           f"You already have a button with role <@&{button_data_instance.role_id}> and "
                            f"action {button_data_instance.button_action} attached to this message as " \
                            f"**{button_data_instance.button_emoji} {button_data_instance.button_label}**",
                            
                color=constants.EMBED_COLOUR_ERROR
            )
            embed.set_footer(text="You can dismiss this message.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return True

        else:
            print("✅ No conflict detected.")
            return False

    except Exception as e:
        try:
            raise GenericError(e)
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)


async def _remove_button(interaction: discord.Interaction, buttons: list, button_data: RoleButtonData):
    print(f'Called _remove_button with {button_data}')
    try:
        original_interaction: discord.Interaction = button_data.preview_message
        view = View(timeout=None)

        target_id = button_data.unique_id

        index_to_delete = None

        print("⏳ Searching for current button in buttons list...")
        for i, button_data_instance in enumerate(buttons):
            if button_data_instance.unique_id == target_id:
                print(f"Found button {button_data_instance.unique_id}")
                index_to_delete = i
                break

        if index_to_delete is not None:
            print("▶ Removing this button_data instance")
            del buttons[index_to_delete]
            print(buttons)

        print("⏳ Updating view with remaining buttons...")
        for button_data_instance in buttons:
            button = NewButton(buttons, button_data_instance)
            print(f"🔘 Generated button from set {button_data_instance.unique_id}")
            view.add_item(button)

        view.add_item(MasterCancelButton())
        view.add_item(MasterAddButton(buttons, button_data))
        if buttons:
            view.add_item(MasterCommitButton(buttons, button_data))

        await original_interaction.edit_original_response(view=view)

    except Exception as e:
        try:
            raise GenericError(e)
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)


async def _update_preview(interaction, buttons: list, button_data: RoleButtonData):
    print(f'Called update_preview with {button_data}')
    try:
        original_interaction: discord.Interaction = button_data.preview_message
        view = View(timeout=None)

        target_id = button_data.unique_id

        index_to_replace = None

        # we need to differentiate our current button in the list of buttons attached to the view
        # we then need to replace it with our updated button, insert it into the list, and add them all back
        print("⏳ Searching for current button in buttons list...")
        for i, button_data_instance in enumerate(buttons):
            if button_data_instance.unique_id == target_id:
                print(f"Found button {button_data_instance.unique_id}")
                index_to_replace = i
                break

        if index_to_replace is not None:
            print("▶ Replacing existing button_data instance with updated button_data")
            buttons[index_to_replace] = button_data
        else:
            print("▶ No existing button_data instance found, appending to list")
            buttons.append(button_data)

        print("⏳ Adding list items to view...")
        for button_data_instance in buttons:
            button = NewButton(buttons, button_data_instance)
            print(f"🔘 Generated button from set {button_data_instance.unique_id}")
            view.add_item(button)

        view.add_item(MasterCancelButton())
        view.add_item(MasterAddButton(buttons, button_data))
        if buttons:
            view.add_item(MasterCommitButton(buttons, button_data))

        print("▶ Updating master view.")
        await original_interaction.edit_original_response(view=view)

    except Exception as e:
        print(e)
        traceback.print_exc()
        try:
            raise GenericError(e)
        except Exception as e:
            await on_generic_error(spamchannel, interaction, e)


class NewButton(Button):
    def __init__(self, buttons, button_data):
        self.buttons = buttons
        self.button_data: RoleButtonData = button_data
        self.spamchannel = bot.get_channel(channel_botspam())
        self.emoji_value = str(self.button_data.button_emoji) if self.button_data.button_emoji else None
        super().__init__(
            label=str(self.button_data.button_label) if self.button_data.button_label else None,
            emoji=self.emoji_value,
            style=self.button_data.button_style,
            custom_id=self.button_data.unique_id
        )

    async def callback(self, interaction: discord.Interaction):
        print(f"Received NewButton callback with {self.button_data}")
        try:
            """# instantiate an instance of our RoleButtonData based on current params
            button_params = {
                'message': self.button_data.message,
                'button_label': button.label,
                'button_emoji': button.emoji,
                'button_style': button.style,
                'button_action': self.button_data.button_action,
                'role_id': self.button_data.role_id,
                'role_object': self.button_data.role_object,
                'preview_message': self.button_data.preview_message
            }
            button_data = RoleButtonData(button_params)"""

            # generate our first embed
            embed = button_config_embed(0, self.button_data)

            # define our first view
            view = ChooseRoleView(self.buttons, self.button_data)

            # send message with view and embed
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            print(e)
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)


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
"""

"""
INDEX FUNCTIONS
"""
# a function to choose view based on index
def _select_view_from_index(index, buttons, button_data: RoleButtonData):
    print("Called _select_view_from_index")
    if index == 0:
        print("Assigning 0: ChooseRoleView")
        view = ChooseRoleView(buttons, button_data)
    elif index == 1:
        print("Assigning 1: ConfirmRoleView")
        view = ConfirmRoleView(buttons, button_data)
    elif index == 2:
        print("Assigning 2: ButtonActionView")
        view = ButtonActionView(buttons, button_data)
    elif index == 3:
        print("Assigning 3: ButtonStyleView")
        view = ButtonStyleView(buttons, button_data)
    elif index == 4:
        print("Assigning 4: LabelEmojiView")
        view = LabelEmojiView(buttons, button_data)
    return view


# function to increment index by one
def _increment_index(index, buttons, button_data: RoleButtonData):
    print("Called _increment_index")
    if index <= 4: 
        index += 1
        # generate new embed
        embed = button_config_embed(index, button_data)
        # assign new view
        view = _select_view_from_index(index, buttons, button_data)
    return embed, view


# function to decrement index by one
def _decrement_index(index, buttons, button_data: RoleButtonData):
    print("Called _decrement_index")
    if index >= 1:
        index -= 1
        # generate new embed
        embed = button_config_embed(index, button_data)
        # assign new view
        view = _select_view_from_index(index, buttons, button_data)
    return embed, view


"""
GLOBAL COMPONENT BUTTONS
"""
class MasterCommitButton(Button):
    def __init__(self, buttons, button_data):
        print("Initialising MasterCommitButton")
        self.buttons: list = buttons
        self.button_data: RoleButtonData = button_data
        self.message: discord.Message = self.button_data.message
        self.spamchannel = bot.get_channel(channel_botspam())
        super().__init__(
            label='✔',
            style=discord.ButtonStyle.success,
            custom_id="master_commit_button",
            row=4 # max row number
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✔ master_commit_button click")

        button_incomplete = False

        try:
            # make sure we have buttons!
            if not self.buttons:
                embed = discord.Embed(
                    description=f"❌ No buttons to commit! Use the **➕** button to add one.",
                                color=constants.EMBED_COLOUR_ERROR
                )
                embed.set_footer(text="You can dismiss this message.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                print("✔ Button list is populated.")

            # make sure our buttons have the needed data
            for button_data_instance in self.buttons:
                if button_data_instance.role_object == None:
                    button_incomplete = True
                    missing_information = 'missing an attached role'
                    pass
                elif button_data_instance.button_label == DEFAULT_BUTTON_LABEL:
                    button_incomplete = True
                    missing_information = 'using the default label'
                    pass

                if button_incomplete:
                    embed = discord.Embed(
                        description=f"❌ **{button_data_instance.button_emoji} {button_data_instance.button_label}** " \
                                    f"is {missing_information}. Please click on it to edit it and correct this.",
                                    color=constants.EMBED_COLOUR_ERROR
                    )
                    embed.set_footer(text="You can dismiss this message.")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    print("✔ No incomplete buttons found.")

            # create the buttons

            view = await _add_role_buttons_to_view(interaction, self.buttons, self.button_data.message)

            # edit it into the target message
            await self.message.edit(view=view)
            
            # display our success message TODO
            gif = random.choice(HOORAY_GIFS)

            embed = discord.Embed(
                description=f':partying_face: **Button(s) updated on {self.message.jump_url}**'
            )
       
            embed.set_image(url=gif)

            view = StressButtonView(self.button_data)
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

class MasterCancelButton(Button):
    def __init__(self):
        print("Initialising MasterCancelButton")
        super().__init__(
            label="✗",
            style=discord.ButtonStyle.danger,
            custom_id="master_cancel_button",
            row=4 # max row number
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✖ master_cancel_button click")
        embed = discord.Embed(
            description="❎ **Button creation cancelled**.",
            color=constants.EMBED_COLOUR_QU
        )
        embed.set_footer(text="You can dismiss this message.")
        return await interaction.response.edit_message(embed=embed, view=None)

class MasterAddButton(Button):
    def __init__(self, buttons, button_data):
        print("Initialising MasterAddButton")
        self.buttons: list = buttons
        self.button_data: RoleButtonData = button_data
        self.spamchannel = bot.get_channel(channel_botspam())
        super().__init__(
            label=None,
            emoji='➕',
            style=discord.ButtonStyle.primary,
            custom_id="master_add_button",
            row=4 # max row number
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ➕ master_add_button click")
        try:
            view = View(timeout=None)

            # check we don't have too many buttons
            if len(self.buttons) > 20:
                print("⚠ Too many buttons! Can't add any more.")
                embed = discord.Embed(
                    description="❌ This message already has the maximum amount of buttons this bot will allow (20).",
                    color=constants.EMBED_COLOUR_ERROR
                )
                embed.set_footer(text="You can dismiss this message.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                print(f"Number of buttons: {len(self.buttons)}")

            # create new default button_data instance with its own unique identifier
            print("⏳ Generating UUID and defining new button_data...")
            unique_id = str(uuid.uuid4())
            button_data_info_dict = {
                'message': self.button_data.message,
                'preview_message': self.button_data.preview_message,
                'unique_id': unique_id
            }
            button_data = RoleButtonData(button_data_info_dict)
            print(button_data)

            print("⏳ Appending to buttons list...")
            self.buttons.append(button_data)

            print("⏳ Adding list items to view...")
            for button_data_instance in self.buttons:
                button = NewButton(self.buttons, button_data_instance)
                print(f"🔘 Generated button from set {button_data_instance.unique_id}")
                view.add_item(button)

            view.add_item(MasterCancelButton())
            view.add_item(MasterAddButton(self.buttons, self.button_data))
            view.add_item(MasterCommitButton(self.buttons, button_data))

            print("▶ Updating message with view.")
            return await interaction.response.edit_message(view=view)

        except Exception as e:
            print(e)
            traceback.print_exc()
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)


class DeleteButton(Button):
    def __init__(self, index, buttons, button_data: RoleButtonData):
        self.index = index
        self.buttons = buttons
        self.button_data: RoleButtonData = button_data
        self.spamchannel = bot.get_channel(channel_botspam())
        super().__init__(
            label="",
            emoji='💥',
            style=discord.ButtonStyle.danger,
            custom_id="delete_button",
            row=1
            # row=1 if self.index == 2 or self.index == 3 else 0
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✖ delete_button click")
        try:
            await _remove_button(interaction, self.buttons, self.button_data)

            await interaction.response.defer()

            print("▶ Deleting button interface.")
            await interaction.delete_original_response()
        
        except Exception as e:
            print(e)
            traceback.print_exc()
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)

class PrevButton(Button):
    def __init__(self, index, buttons, button_data: RoleButtonData):
        self.index = index
        self.buttons = buttons
        self.button_data = button_data
        super().__init__(
            label="◄",
            style=discord.ButtonStyle.secondary,
            custom_id="generic_previous_button",
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ◄ generic_previous_button click")
        # decrement index by 1
        if self.index >= 1:
            embed, view = _decrement_index(self.index, self.buttons, self.button_data)
            # update message
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.defer()

class NextButton(Button):
    def __init__(self, index, buttons, button_data: RoleButtonData):
        self.index = index
        self.buttons = buttons
        self.button_data = button_data
        super().__init__(
            label="►",
            style=discord.ButtonStyle.secondary,
            custom_id="generic_next_button",
            row=1
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
            embed, view = _increment_index(self.index, self.buttons, self.button_data)
            # update message
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.defer()

class CommitButton(Button):
    def __init__(self, index, button_data: RoleButtonData):
        self.index = index
        self.button_data: RoleButtonData = button_data
        super().__init__(
            label='✔',
            style=discord.ButtonStyle.success,
            custom_id="generic_commit_button",
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✅ generic_commit_button click")
        # check we have needed input for a full button
        if self.button_data.button_label == DEFAULT_BUTTON_LABEL or \
           self.button_data.role_id == None or \
           self.button_data.role_object == None:
            print("Received commit button press but user has not entered all required data")
            embed = discord.Embed(
                description="❌ You must input all required elements before committing a button.",
                color=constants.EMBED_COLOUR_ERROR
            )
            embed.set_footer(text="You can dismiss this message.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            await interaction.response.defer()

            try:
                await interaction.delete_original_response()
            except Exception as e:
                print(e)

"""
INDEXED VIEWS

"""


"""
Page 1: Input role ID
"""
class ChooseRoleView(View):
    def __init__(self, buttons, button_data: RoleButtonData):
        super().__init__(timeout=None)
        self.buttons = buttons
        self.button_data = button_data
        self.index = 0
        self.clear_items()
        self.add_item(PrevButton(self.index, self.buttons, self.button_data))
        self.add_item(DeleteButton(self.index, self.buttons, self.button_data))
        self.add_item(self.button_enter_role_id)
        self.add_item(CommitButton(self.index, self.button_data))
        self.add_item(NextButton(self.index, self.buttons, self.button_data))

    @discord.ui.button(
        label='Enter Role ID',
        custom_id='enter_role_id_button',
        style=discord.ButtonStyle.primary,
        emoji='🎢',
        row=0)
    async def button_enter_role_id(self, interaction, button):
        try:
            await interaction.response.send_modal(EnterRoleIDModal(self.buttons, self.button_data))
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

"""
Page 2: Confirm role
"""
class ConfirmRoleView(View):
    def __init__(self, buttons, button_data: RoleButtonData):
        self.buttons = buttons
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 1
        self.clear_items()
        self.add_item(PrevButton(self.index, self.buttons, self.button_data))
        self.add_item(DeleteButton(self.index, self.buttons, self.button_data))
        self.add_item(self.confirm_role_button)
        self.add_item(CommitButton(self.index, self.button_data))
        self.add_item(NextButton(self.index, self.buttons, self.button_data))

    @discord.ui.button(
        label='Assign role to button',
        emoji='☑',
        style=discord.ButtonStyle.primary,
        custom_id="confirm_role_button",
        row=0
    )

    async def confirm_role_button(self, interaction: discord.Interaction, button):
        print("Received ✅ confirm_role_button click")
        # increment index by 1
        embed, view = _increment_index(self.index, self.buttons, self.button_data)
        # update message
        await interaction.response.edit_message(embed=embed, view=view)


"""
Page 3: Set button action
"""
class ButtonActionView(View):
    def __init__(self, buttons, button_data: RoleButtonData):
        self.buttons = buttons
        super().__init__(timeout=None)
        self.button_data: RoleButtonData = button_data
        self.index = 2
        self.add_item(PrevButton(self.index, self.buttons, self.button_data))
        self.add_item(DeleteButton(self.index, self.buttons, self.button_data))
        self.add_item(CommitButton(self.index, self.button_data))
        self.add_item(NextButton(self.index, self.buttons, self.button_data))

    @discord.ui.button(
        label='Give role',
        custom_id='give_action_button',
        style=discord.ButtonStyle.success,
        row=0
    )
    async def success_style_button(self, interaction: discord.Interaction, button):
        print("🔘 Chose give_action_button")
        try:
            self.button_data.button_action = 'give'
            # set some defaults for a role give button
            self.button_data.button_label = 'Give Role Button'
            self.button_data.button_style = discord.ButtonStyle.success

            # check for conflicts with existing buttons
            if await _check_for_button_conflict(interaction, self.buttons, self.button_data):
                return

            else:
                embed, view = _increment_index(self.index, self.buttons, self.button_data)

                await _update_preview(interaction, self.buttons, self.button_data)

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
        row=0
    )
    async def primary_style_button(self, interaction: discord.Interaction, button):
        print("🔘 Chose take_action_button")
        try:
            self.button_data.button_action = 'take'
            # set some defaults for a role take button
            self.button_data.button_label = 'Take Role Button'
            self.button_data.button_style = discord.ButtonStyle.danger
            embed, view = _increment_index(self.index, self.buttons, self.button_data)

            await _update_preview(interaction, self.buttons, self.button_data)

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
        row=0
    )
    async def secondary_style_button(self, interaction: discord.Interaction, button):
        print("Chose secondary button")
        try:
            self.button_data.button_action = 'toggle'
            # set some defaults for a role toggle button
            self.button_data.button_label = 'Toggle Role Button'
            self.button_data.button_style = discord.ButtonStyle.primary
            embed, view = _increment_index(self.index, self.buttons, self.button_data)

            await _update_preview(interaction, self.buttons, self.button_data)

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
    def __init__(self, buttons, button_data: RoleButtonData):
        self.buttons = buttons
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 3
        self.add_item(PrevButton(self.index, self.buttons, self.button_data))
        self.add_item(DeleteButton(self.index, self.buttons, self.button_data))
        self.add_item(CommitButton(self.index, self.button_data))
        self.add_item(NextButton(self.index, self.buttons, self.button_data))

    @discord.ui.button(
        label='Success',
        custom_id='success_style_button',
        style=discord.ButtonStyle.success,
        row=0
    )
    async def success_style_button(self, interaction, button):
        print("Chose green button")
        try:
            self.button_data.button_style = discord.ButtonStyle.success
            embed, view = _increment_index(self.index, self.buttons, self.button_data)

            await _update_preview(interaction, self.buttons, self.button_data)

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
        row=0
    )
    async def primary_style_button(self, interaction, button):
        print("Chose primary button")
        try:
            self.button_data.button_style = discord.ButtonStyle.primary
            embed, view = _increment_index(self.index, self.buttons, self.button_data)

            await _update_preview(interaction, self.buttons, self.button_data)

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
        row=0
    )
    async def secondary_style_button(self, interaction, button):
        print("Chose secondary button")
        try:
            self.button_data.button_style = discord.ButtonStyle.secondary
            embed, view = _increment_index(self.index, self.buttons, self.button_data)

            await _update_preview(interaction, self.buttons, self.button_data)

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
        row=0
    )
    async def danger_style_button(self, interaction, button):
        print("Chose danger button")
        try:
            self.button_data.button_style = discord.ButtonStyle.danger
            embed, view = _increment_index(self.index, self.buttons, self.button_data)

            await _update_preview(interaction, self.buttons, self.button_data)

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
    def __init__(self, buttons, button_data: RoleButtonData):
        self.buttons = buttons
        super().__init__(timeout=None)
        self.button_data = button_data
        self.index = 4
        self.clear_items()
        self.add_item(PrevButton(self.index, self.buttons, self.button_data))
        self.add_item(DeleteButton(self.index, self.buttons, self.button_data))
        self.add_item(self.label_emoji_button)
        self.add_item(CommitButton(self.index, self.button_data))
        self.add_item(NextButton(self.index, self.buttons, self.button_data))

    @discord.ui.button(
        label='Enter Label & Emoji',
        custom_id='label_emoji_button',
        style=discord.ButtonStyle.primary,
        emoji='🏷',
        row=0
    )
    async def label_emoji_button(self, interaction: discord.Interaction, button):
        print("🔘 Received label_emoji_button click")

        await interaction.response.send_modal(EnterLabelEmojiModal(self.buttons, self.button_data))


"""
After buttons sent view
"""

class StressButtonView(View):
    def __init__(self, button_data):
        self.button_data: RoleButtonData = button_data
        super().__init__(timeout=None)

    @discord.ui.button(
        label='That was stressful',
        style=discord.ButtonStyle.danger,
        custom_id="stress_button",
        emoji='😰',
        row=0
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
        emoji='💪',
        row=0
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
    def __init__(self, buttons, button_data: RoleButtonData, title = 'Set Role', timeout = None):
        self.buttons = buttons
        self.button_data = button_data
        self.index = 0
        if self.button_data.role_id:
            self.role_id.default = self.button_data.role_id
        else:
            self.role_id.default = None
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

        embed, view = _increment_index(self.index, self.buttons, self.button_data)

        # edit our message to next in sequence
        print("Updating message with new embed and view...")
        await interaction.response.edit_message(embed=embed, view=view)

# modal to input button label/emoji
class EnterLabelEmojiModal(Modal):
    def __init__(self, buttons, button_data: RoleButtonData, title = 'Set Label & Emoji', timeout = None):
        self.buttons = buttons
        self.button_data = button_data
        self.index = 4
        if self.button_data.button_label:
            print(f'Default set to {self.button_data.button_label}')
            self.button_label.default = str(self.button_data.button_label)
        else:
            self.button_label.default = None
        if self.button_data.button_emoji:
            print(f'Default set to {self.button_data.button_emoji}')
            self.button_emoji.default = str(self.button_data.button_emoji)
        else:
            self.button_emoji.default = None
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
                print(f"⏳ User seems to have entered Discord emoji as {self.button_emoji.value}, attempting to resolve against library...")
                unicode_emoji = emoji.emojize(self.button_emoji.value)
                print(f"Updated emoji: {unicode_emoji}")
                self.button_data.button_emoji = str(unicode_emoji)
            else:
                self.button_data.button_emoji = str(self.button_emoji.value)

            if ':' in self.button_data.button_emoji and not '<' in self.button_data.button_emoji: # triggered if we failed to convert a : to an emoji and its not custom
                print("Found Discord non-custom code in emoji value")
                try:
                    error = f'**Could not resolve the emoji you entered against its unicode name**.\n' \
                            'Not all Discord emojis have the same shortcode as the unicode name, for example `:heart:` in Discord is `:red_heart:` in unicode.\n' \
                            'You can try sending the emoji you want in a message, then copying the emoji from that message.'
                    raise CustomError(error)
                except Exception as e:
                    await on_generic_error(spamchannel, interaction, e)
            
            elif emoji.emoji_count(self.button_data.button_emoji) > 1: # should trigger if we have a ZWJ emoji or too many emojis
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

        # update preview then 'close' this interface by deleting message
        await _update_preview(interaction, self.buttons, self.button_data)

        await interaction.response.defer()

        try:
            await interaction.delete_original_response()
        except Exception as e:
            print(e)



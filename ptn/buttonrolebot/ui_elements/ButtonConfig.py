"""
A set of discord.ui elements for customising buttons added by BRB.

"""
# import libraries
import emoji
import traceback
import time

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

"""
Issues:
- prev button not working - why?
- confirm button needs to be reworked to basically be like the cancel button (delete the message)
- MasterConfirmButton needs to inherit old confirm button func, but add all buttons in the list to the original message
- final success page should be moved to masterconfirm response

"""

async def _update_preview(interaction, buttons: list, button_data: RoleButtonData):
    print(f'Called update_preview with {button_data}')
    try:
        original_interaction: discord.Interaction = button_data.preview_message
        view = View(timeout=None)
        new_button = NewButton(buttons, button_data)

        target_id = button_data.temp_id

        index_to_replace = None

        # we need to differentiate our current button in the list of buttons attached to the view
        # we then need to replace it with our updated button, insert it into the list, and add them all back
        print("⏳ Searching for current button in buttons list")
        for i, button in enumerate(buttons):
            if button.custom_id == target_id:
                print(f"Found button {button.custom_id}")
                index_to_replace = i
                break

        if index_to_replace is not None:
            print("Replacing existing button with updated button")
            buttons[index_to_replace] = new_button
        else:
            print("No existing button found, appending to list")
            buttons.append(new_button)

        for button in buttons:
            view.add_item(button)

        view.add_item(MasterCancelButton())
        view.add_item(MasterAddButton(buttons, button_data)) 

        await original_interaction.edit_original_response(view=view)

        return button

    except Exception as e:
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
            label=str(self.button_data.button_label),
            emoji=self.emoji_value,
            style=self.button_data.button_style,
            custom_id=self.button_data.temp_id
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
5. Confirm choices - OK button, back button, cancel button

"""

spamchannel = bot.get_channel(channel_botspam())

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
    elif index == 5:
        print("Assigning 5: ConfirmConfigView")
        view = ConfirmConfigView(buttons, button_data)
    return view


# function to increment index by one
def _increment_index(index, buttons, button_data: RoleButtonData):
    print("Called _increment_index")
    if index <= 5: # TODO: actual max index number here
        index += 1
        # generate new embed
        embed = button_config_embed(index, button_data)
        # assign new view
        view = _select_view_from_index(index, buttons, button_data)
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

            timestamp = int(time.time())

            # create new default button_data instance
            button_data_info_dict = {
                'message': self.button_data.message,
                'preview_message': self.button_data.preview_message,
                'temp_id': str(timestamp)
            }
            button_data = RoleButtonData(button_data_info_dict)
            print(button_data)

            print("⏳ Defining New Button...")
            new_button = NewButton(self.buttons, button_data)

            print("⏳ Appending to buttons list...")
            self.buttons.append(new_button)

            print("⏳ Adding list items to view...")
            for button in self.buttons:
                view.add_item(button)

            view.add_item(MasterCancelButton())
            view.add_item(MasterAddButton(self.buttons, self.button_data))

            print("▶ Updating message with view.")
            return await interaction.response.edit_message(view=view)

        except Exception as e:
            print(e)
            traceback.print_exc()
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(self.spamchannel, interaction, e)


class CancelButton(Button):
    def __init__(self, index):
        self.index = index
        super().__init__(
            label="✗",
            style=discord.ButtonStyle.danger,
            custom_id="generic_cancel_button",
            row=1 if self.index == 2 or self.index == 3 else 0
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✖ generic_cancel_button click")
        await interaction.response.defer()

        try:
            await interaction.message.delete() # TODO which of these actually works? whoops
        except Exception as e:
            print(e)

        try:
            await interaction.delete_original_response()
        except Exception as e:
            print(e)

class PrevButton(Button):
    def __init__(self, index, buttons, button_data: RoleButtonData):
        self.index = index
        self.buttons = buttons
        self.button_data = button_data
        super().__init__(
            label="◄",
            style=discord.ButtonStyle.secondary,
            custom_id="generic_previous_button",
            row=1 if self.index == 2 or self.index == 3 else 0
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
            row=1 if self.index == 2 or self.index == 3 else 0
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

class ConfirmButton(Button):
    def __init__(self, index, buttons, button_data: RoleButtonData):
        self.index = index
        self.buttons = buttons
        self.button_data = button_data
        super().__init__(
            label='✔',
            style=discord.ButtonStyle.success,
            custom_id="generic_confirm_button",
            row=1 if self.index == 2 or self.index == 3 else 0
        )

    async def callback(self, interaction: discord.Interaction):
        print("Received ✅ generic_confirm_button click")
        # increment index by 1
        embed, view = _increment_index(self.index, self.buttons, self.button_data)
        # update message
        await interaction.response.edit_message(embed=embed, view=view)


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
        self.add_item(CancelButton(self.index))
        self.add_item(self.button_enter_role_id)
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
        self.add_item(CancelButton(self.index))
        self.add_item(ConfirmButton(self.index, self.buttons, self.button_data))
        self.add_item(NextButton(self.index, self.buttons, self.button_data))

    pass

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
        self.add_item(CancelButton(self.index))
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
        self.add_item(CancelButton(self.index))
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
        self.add_item(CancelButton(self.index))
        self.add_item(self.label_emoji_button)
        self.add_item(NextButton(self.index, self.buttons, self.button_data))

    @discord.ui.button(
        label='Choose',
        custom_id='label_emoji_button',
        style=discord.ButtonStyle.primary,
        emoji='🏷',
        row=0
    )
    async def label_emoji_button(self, interaction: discord.Interaction, button):
        print("🔘 Received label_emoji_button click")

        await interaction.response.send_modal(EnterLabelEmojiModal(self.buttons, self.button_data))

"""
Page 6: Confirm
"""
class ConfirmConfigView(View):
    def __init__(self, buttons, button_data: RoleButtonData):
        self.buttons = buttons
        super().__init__(timeout=None)
        self.button_data = button_data
        self.message: discord.Message = self.button_data.message
        self.index = 5
        self.clear_items()
        self.add_item(PrevButton(self.index, self.buttons, self.button_data))
        self.add_item(CancelButton(self.index))
        self.add_item(self.final_submit_button)

    @discord.ui.button(
            label='✔ Create Button',
            style=discord.ButtonStyle.success,
            custom_id="final_submit_button",
            row=0
            )

    async def final_submit_button(self, interaction: discord.Interaction, button):
        print("Received ✅ final_submit_button click")
        try:
            # create the button!
            view = await _add_role_button_to_view(interaction, self.button_data)

            # edit it into the target message
            await self.message.edit(view=view)
            
            # increment index by 1
            final_index = self.index + 1
            embed = button_config_embed(final_index, self.button_data)
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


"""
Final page: success!
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

    @discord.ui.button(
        label='Add another',
        style=discord.ButtonStyle.primary,
        custom_id="add_another_button",
        emoji='➕',
        row=1
    )

    async def add_another_button(self, interaction: discord.Interaction, button):
        print("Received add_another_button click")
        try:
            # update our original message object to include our new view
            original_message: discord.Message = self.button_data.message
            print('Fetching updated message...')
            new_message: discord.Message = await original_message.channel.fetch_message(original_message.id)
            print(f'Fetched message as {new_message}')

            # create a fresh instance of button_data based on our updated message object
            print('create a fresh instance of button_data')
            info_dict = {"message": new_message}
            button_data = RoleButtonData(info_dict)
            print(button_data)

            # set embed back to original
            print('set embed back to original')
            embed = button_config_embed(0, button_data)
            # set view back to original
            print('set view back to original')
            view = _select_view_from_index(0, button_data)
            print('update message')
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            try:
                raise GenericError(e)
            except Exception as e:
                await on_generic_error(spamchannel, interaction, e)

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

        await _update_preview(interaction, self.buttons, self.button_data)

        embed, view = _increment_index(self.index, self.buttons, self.button_data)

        # edit our message to next in sequence
        print("Updating message with new embed and view...")
        await interaction.response.edit_message(embed=embed, view=view)



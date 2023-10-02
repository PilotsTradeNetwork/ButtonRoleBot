# ButtonRoleBot
A bot to provide users with roles based on interacting with buttons added to messages.

## Core features
- Send messages featuring rich Embeds defined by PTN Discord managers
- Add / remove / edit buttons on bot messages, with parameters defined by PTN Discord managers
- Use above buttons to grant/remove roles from users upon interaction
- Provide feedback to users who interact with above buttons
- Buttons must persist through bot restarts

## Commands
- `/send_embed`: Prepares to send a message to the current channel with a user-defined embed
- `Edit Embed`: Context Menu -> Message. Edits an existing embed in the target message.
- `Manage Role Buttons`: Context Menu -> Message. Used to add, remove, or edit buttons for that message.
- `Remove Buttons`: Context Menu -> Message. Quick command (with confirmation) to remove all buttons from target message.

## Architecture
- Discord.py 2.4+
 - `discord.ui.DynamicItem` requires version >2.4
 - `discord.ui.DynamicItem` allows persistent, user-created buttons without necessitating external database storage

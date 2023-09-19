# ButtonRoleBot
A bot to provide users with roles based on interacting with buttons added to messages.

## Core features
- Send messages featuring Embeds defined by PTN Discord managers
- Add buttons to above messages, with parameters defined by PTN Discord managers
- Use above buttons to grant/remove roles from users on interaction
- Provide feedback to users who interact with above buttons
- Buttons must persist through bot restarts

## Commands
- slash command to send an Embed to a channel
 - Modal pop-up to define content of Embed
- right-click (context command) to add button to message sent by ButtonRoleBot
 - Modal pop-up to define behaviour of button
 - Possible selectmenu to define role selection
- right-click (context command) to remove all buttons from a message sent by ButtonRoleBot

## Architecture
- Discord.py 2.4+
 - `discord.ui.DynamicItem` requires version >2.4
 - `discord.ui.DynamicItem` allows persistent, user-created buttons without necessitating external database storage

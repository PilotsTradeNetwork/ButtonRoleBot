"""
The Python script that starts the bot.

"""

# import libraries
import asyncio
import os
import logging

from discord.ext.prometheus import PrometheusCog

# import bot Cogs
from ptn.buttonrolebot.botcommands.AdminCommands import AdminCommands
from ptn.buttonrolebot.botcommands.ButtonRoleCommands import ButtonRoleCommands

# import bot object, token, production status
from ptn.buttonrolebot.constants import TOKEN, _production, DATA_DIR, log_handler, LOG_LEVEL
from discord.utils import setup_logging
from ptn.buttonrolebot.bot import bot

def run():
    asyncio.run(buttonrolebot())


async def buttonrolebot():
    async with bot:
        await bot.add_cog(AdminCommands(bot))
        await bot.add_cog(ButtonRoleCommands(bot))
        await bot.add_cog(PrometheusCog(bot))
        setup_logging(handler=log_handler, level=LOG_LEVEL)
        logging.info(f"Data dir is {DATA_DIR} from {os.path.join(os.getcwd(), 'ptn', 'buttonrolebot', DATA_DIR, '.env')}")
        logging.info(f'PTN buttonrolebot is connecting against production: {_production}.')
        await bot.start(TOKEN)


if __name__ == '__main__':
    """
    If running via `python ptn/buttonrolebot/application.py
    """
    run()

"""
Constants used throughout BRB.

Depends on: nothing
"""

# libraries
import ast
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


# Define whether the bot is in testing or live mode. Default is testing mode.
_production = ast.literal_eval(os.environ.get('PTN_BRB_SERVICE', 'False'))

# define paths
TESTING_DATA_PATH = os.path.join(os.getcwd(), 'ptn', 'buttonrolebot', 'data') # defines the path for use in a local testing environment
DATA_DIR = os.getenv('PTN_BRB_DATA_DIR', TESTING_DATA_PATH)


# Get the discord token from the local .env file. Deliberately not hosted in the repo or Discord takes the bot down
# because the keys are exposed. DO NOT HOST IN THE PUBLIC REPO.
# load_dotenv(os.path.join(DATA_DIR, '.env'))
load_dotenv(os.path.join(DATA_DIR, '.env'))


# define bot token
TOKEN = os.getenv('BRB_DISCORD_TOKEN_PROD') if _production else os.getenv('BRB_DISCORD_TOKEN_TESTING')


# bot = commands.Bot(command_prefix=commands.when_mentioned_or('🎢'), intents=discord.Intents.all()) # TODO: remove this if we get bot.py to work


# Production variables
PROD_DISCORD_GUILD = 800080948716503040 # PTN server ID
PROD_CHANNEL_BOTSPAM = 801258393205604372 # PTN bot-spam channel
PROD_CHANNEL_BOTDEV = 1153789139938988083 # PTN channel related to development for buttonrolebot
PROD_ROLE_COUNCIL = 800091021852803072 # PTN Council role
PROD_ROLE_MOD = 813814494563401780 # PTN Mod role


# Testing variables
TEST_DISCORD_GUILD = 818174236480897055 # PANTS server ID
TEST_CHANNEL_BOTSPAM = 1152273868073996298 # PANTS bot spam channel
TEST_CHANNEL_BOTDEV = 1153794231438168095 # PANTS channel related to development for buttonrolebot
TEST_ROLE_COUNCIL = 877586918228000819 # PANTS Council role
TEST_ROLE_MOD = 903292469049974845 # PANTS Mod role


# Embed colours
EMBED_COLOUR_ERROR = 0x800000           # dark red
EMBED_COLOUR_QU = 0x00d9ff              # que?
EMBED_COLOUR_OK = 0x80ff80              # we're good here thanks, how are you?


# define constants based on prod or test environment
def bot_guild():
  return PROD_DISCORD_GUILD if _production else TEST_DISCORD_GUILD

guild_obj = discord.Object(bot_guild())

def channel_botspam():
    return PROD_CHANNEL_BOTSPAM if _production else TEST_CHANNEL_BOTSPAM

def channel_botdev():
    return PROD_CHANNEL_BOTDEV if _production else TEST_CHANNEL_BOTDEV

def role_council():
    return PROD_ROLE_COUNCIL if _production else TEST_ROLE_COUNCIL

def role_mod():
    return PROD_ROLE_MOD if _production else TEST_ROLE_MOD


any_elevated_role = [role_council(), role_mod()]


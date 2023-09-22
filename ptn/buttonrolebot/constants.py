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
EMBED_COLOUR_PTN_DEFAULT = 42971     # used by various embeds throughout the server

EMOJI_DONE = '🟢'
EMOJI_NOT_DONE = '⭕'

HEX_COLOR_PATTERN = r'^0x[0-9A-Fa-f]{6}$'

BUTTON_CHOOSE_THUMBNAIL = "https://pilotstradenetwork.com/wp-content/uploads/2023/09/two_buttons_cropped.png"
BUTTON_SWEAT_THUMBNAIL = "https://pilotstradenetwork.com/wp-content/uploads/2023/09/two_buttons_sweating_guy.png"

HOORAY_GIFS = [
    "https://media.tenor.com/wPuTaxlyovsAAAAC/bluey-hooray.gif", # Bluey
    "https://media.tenor.com/v4FpeS4fxBUAAAAC/celebration-celebrate.gif", # keytar confetti party
    "https://media.tenor.com/t2BKH5zl5z4AAAAC/cookie-monster-sesame-street.gif", # cookie monster
    "https://media.tenor.com/t6pHmhd6VcoAAAAC/thumbs-up.gif" # thumbs up x a billion
]

STRESS_GIFS = [
    "https://media.tenor.com/BpWIVDqRNWYAAAAC/30rock-alec-baldwin.gif", # 30 rock broom toilet
    "https://media.tenor.com/9LnT9uU_IZoAAAAC/big-hero6-baymax.gif", # big hero 6
    "https://media.tenor.com/eZAJXNrFZd8AAAAd/hug-dan-levy.gif", # Schitt's Creek
    "https://media.tenor.com/xO6zr96a1Z4AAAAC/come-there-there.gif", # Dr Evil
    "https://media.tenor.com/IBinlCV2_koAAAAC/sssh-its-ok-you-are-loved-there-there.gif", # you are loved
    "https://media.tenor.com/diSWdrgqr_IAAAAd/there-there-there-there-human.gif", # there there human
    "https://media.tenor.com/nD5Qsz1adroAAAAd/there-30rock.gif", # 30 rock business card
    "https://media.tenor.com/CnTxN4UrdysAAAAC/boo-hug.gif", # Monsters Inc
    "https://media.tenor.com/uW0B9nSn4DsAAAAC/there-there-cats.gif" # dog and cat
]

AMAZING_GIFS = [
    "https://media.tenor.com/2cj5umkSaswAAAAd/ted-lasso-tedlassogifs.gif", # ted lasso
    "https://media.tenor.com/8qtOK6_iNRMAAAAC/proud-ron-swanson.gif", # ron is proud of you
    "https://media.tenor.com/OShgvZ8e50wAAAAC/kronk-mission.gif", # kronk accomplished
    "https://media.tenor.com/RdXkAIPupDcAAAAC/yes-sir-ana-kendrick.gif", # pitch perfect salute
    "https://media.tenor.com/VGuFz5LmvdcAAAAC/absolute-win-i-see-this-as-an-absolute-win.gif", # absolute win (no but srsly)
    "https://media.tenor.com/V9V2OMYWmMIAAAAC/oh-you-aint-seen-nothing-yet-branch.gif", # trolls ain't seen nuthin
    "https://media.tenor.com/K_YUkFYeDqUAAAAC/thor-marvel.gif", # that's what heroes do
    "https://media.tenor.com/ZCVrHrXgaoUAAAAC/treat-yo-self-treat-yourself.gif" # treat yo self
]

THERE_THERE = [
    "There, there.",
    "It's OK, it's over now.",
    "You did it! I'm so proud of you.",
    "You deserve some you time."
]

YOU_GO_GIRL = [
    "You're the best!",
    "You rock!",
    "Whoooo!",
    "Yeah!"
]

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


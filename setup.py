import io
import os
from pathlib import Path
from importlib import util

from setuptools import setup

NAMESPACE = 'ptn'
COMPONENT = 'buttonrolebot'

here = Path().absolute()

# Bunch of things to allow us to dynamically load the metadata file in order to read the version number.
# This is really overkill but it is better code than opening, streaming and parsing the file ourselves.

metadata_name = f'{NAMESPACE}.{COMPONENT}._metadata'
spec = util.spec_from_file_location(metadata_name, os.path.join(here, NAMESPACE, COMPONENT, '_metadata.py'))
metadata = util.module_from_spec(spec)
spec.loader.exec_module(metadata)

# load up the description field
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=f'{NAMESPACE}.{COMPONENT}',
    version=metadata.__version__,
    packages=[
        'ptn.buttonrolebot', # core
        'ptn.buttonrolebot.botcommands', # user interactions
        'ptn.buttonrolebot.modules' # various helper modules
        ],
    description='Pilots Trade Network Button Role Bot',
    long_description=long_description,
    author='Charles Tosh',
    url='',
    install_requires=[
        'DateTime==4.3',
        'discord==1.0.1',
        'discord.py>=2.3.0',
        'python-dotenv==0.15.0',
        'python-dateutil>=2.8.1',
    ],
    entry_points={
        'console_scripts': [
            'buttonrolebot=ptn.buttonrolebot.application:run',
        ],
    },
    license='None',
    keyword='PTN',
    project_urls={
        "Source": "https://github.com/PilotsTradeNetwork/ButtonRoleBot",
    },
    python_required='>=3.9',
)

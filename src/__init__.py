from discord.ext import commands
from opebot.util.init import init_intents

__version__ = '1.3.2'
__author__  = 'Erik Luttu'

bot = commands.Bot(command_prefix = '-', 
                   intents = init_intents(),
                   case_insensitive = True)

from . import _commands
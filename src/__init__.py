from discord.ext import commands
from ..util.init import init_intents

__title__   = "opebot"
__version__ = '1.5.4'
__author__  = 'Erik Luttu'

bot = commands.Bot(command_prefix = '-', 
                   intents = init_intents(),
                   case_insensitive = True)

from . import _commands
from discord.ext import commands
from ..util.init import init_intents

__version__ = '0.1.0'
__author__  = 'Erik Luttu'

bot = commands.Bot(command_prefix = 'o-', 
                   intents = init_intents(),
                   case_insensitive = True)

from . import _commands
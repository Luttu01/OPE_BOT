import os
from .src import bot

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
from discord.ext import commands
from discord.ext.commands import Context, CheckFailure

def in_same_voice_channel():
    def predicate(ctx: Context):
        if ctx.voice_client == None or not ctx.voice_client.is_connected():
            raise CheckFailure("The bot is not connected to any voice channel.")
        if ctx.author.voice == None or ctx.author.voice.channel == None:
            raise CheckFailure("You are not connected to any voice channel")
        if ctx.author.voice.channel != ctx.voice_client.channel:
            raise CheckFailure("You must be in the same channel as the bot.")
        return True
    return commands.check(predicate)
from discord.ext.commands import Context
from OPE_BOT.src.player import Player
from OPE_BOT.src.songmanager import SongManager
from OPE_BOT.src.botmanager import BotManager
from OPE_BOT.util.message import embed_msg_song

async def _play(ctx: Context, player: Player):
    ctx.voice_client.play(player)
    SongManager.current_player = player
    SongManager.song_curr_duration = 0
    if BotManager.last_message:
        BotManager.last_message.delete()
    BotManager.last_message = await ctx.send(embed=embed_msg_song(player.title))
    
def _now_playing() -> str:
    return SongManager.current_player.title
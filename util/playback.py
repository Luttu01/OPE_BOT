from discord.ext.commands import Context
from opebot.src.player import Player
from opebot.src.songmanager import SongManager
from opebot.src.botmanager import BotManager
from opebot.util.message import embed_msg_song

async def _play(ctx: Context, player: Player):
    ctx.voice_client.play(player)
    SongManager.current_player = player
    SongManager.song_curr_duration = 0
    if BotManager.last_message:
        await BotManager.last_message.delete()
    BotManager.last_message = await ctx.send(embed=embed_msg_song(player.title))
    
def _now_playing() -> str:
    return SongManager.current_player.title

def toggle_radio() -> bool:
    SongManager.radio_mode = not SongManager.radio_mode
    return SongManager.radio_mode
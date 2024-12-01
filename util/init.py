from discord import Intents

from opebot.config.paths import folder_path_cache

def init_intents() -> None:
    i = Intents.default()
    i.guilds = True
    i.voice_states = True
    i.message_content = True
    return i

def init_ytdl_options():
    format_options = {
    'outtmpl': folder_path_cache + r'\%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'verbose': True,
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'format': 'bestaudio',
    'extractaudio': True
    }
    return format_options

def init_ffmpeg():
    return {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    }
import os
import yt_dlp
import threading

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials as scc
from opebot.util.init import init_ytdl_options, init_ffmpeg

class BotManager:
    ytdl = yt_dlp.YoutubeDL(init_ytdl_options())
    ffmpeg_opts = init_ffmpeg()
    sp = Spotify(auth_manager=scc(client_id=os.getenv('SPOTIFY_CLIENT_ID'), 
                                  client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')))
    idle_timer: int = 0
    last_message: str = None
    
    MONDAY: int = 0
    DECEMBER: int = 12    

    __lock = threading.Lock()

    def __init__(self):
        pass

    @classmethod
    def on_step(cls):
        with cls.__lock:
            cls.idle_timer += 1
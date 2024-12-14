import discord
import asyncio
import json
import datetime
import os

from opebot.src.botmanager import BotManager
from opebot.config.paths import file_path_cache, folder_path_cache
from opebot.src.error import Error

class Player(discord.PCMVolumeTransformer):
    def __init__(self, original, url, title, duration, volume = 0.5):
        super().__init__(original, volume)
        self.original = original
        self.title    = title
        self.url      = url
        self.duration = duration
        self.volume   = volume

    @classmethod
    async def from_url(cls, url: str, query: str, *, spotify_url: str = None):
        print(1)
        cache = cls.check_url_in_cache(url)
        if cache:
            filename, title, volume, duration = cache
            if spotify_url:
                return cls(discord.FFmpegPCMAudio(filename), title=title, url=spotify_url, duration=duration, volume=volume)
            else:
                return cls(discord.FFmpegPCMAudio(filename), title=title, url=url, duration=duration, volume=volume)
        else:
            data = await asyncio.\
                         get_event_loop().\
                         run_in_executor(None, 
                                         lambda: BotManager.ytdl.extract_info(url, download=True))
            if data is None:
                return None
            if data.get('_type') == 'playlist':
                print("Playlist detected. Extracting first entry as a single video...")
                first_entry = data['entries'][0]
                url = first_entry.get('original_url')
                duration = first_entry.get('duration', None)
                title = first_entry.get('title', data.get('title'))
                filename = BotManager.ytdl.prepare_filename(first_entry)
            else:
                filename = BotManager.ytdl.prepare_filename(data)
                duration = data.get('duration', None)
                title = data.get('title')
            if duration >= 600:
                if filename.startswith(folder_path_cache) and os.path.isfile(filename): # Ensure safe path
                    os.remove(filename)
                return Error.DURATION_ERROR
            if spotify_url:
                await cls.update_json_cache(spotify_url, filename, title, duration, query)
                return cls(discord.FFmpegPCMAudio(filename), title=title, url=spotify_url, duration=duration)
            else:
                print(2)
                await cls.update_json_cache(url, filename, title, duration, query)
                return cls(discord.FFmpegPCMAudio(filename), title=title, url=url, duration=duration)

    @staticmethod
    def check_url_in_cache(url):
        try:
            with open(rf'{file_path_cache}', 'r') as r:
                cache = json.load(r)
        except (FileNotFoundError, json.JSONDecodeError):
            cache = {}
        if url in cache.keys():
            cache[url]['last_accessed'] = datetime.datetime.now().strftime("%Y-%m-%d")
            with open(rf'{file_path_cache}', "w") as w:
                json.dump(cache, w, indent=4)
            return (cache[url]['path'], cache[url]['title'], cache[url]['volume'], None) if not 'duration' in cache[url] else \
                   (cache[url]['path'], cache[url]['title'], cache[url]['volume'], cache[url]['duration'])
        return None
    
    @staticmethod
    async def update_json_cache(url, path, title, duration, query):
        print(3)
        with open(f'{file_path_cache}', 'r') as f:
            cache = json.load(f)

        def _new_cache_entry(path, title, last_accessed, duration, query):
            return {
                'path': path,
                'title': title,
                'last_accessed': last_accessed,
                'weight': 1,
                'volume': 0.5,
                'duration': duration,
                'query': query
            }

        cache[url] = _new_cache_entry(path, title, datetime.datetime.now().strftime("%Y-%m-%d"), duration, query)
        print(_new_cache_entry(path, title, datetime.datetime.now().strftime("%Y-%m-%d"), duration, query))
        with open(rf'{file_path_cache}', 'w') as f:
            json.dump(cache, f, indent=4)
import logging
import os
import googleapiclient.discovery as gdisc
from urllib.parse import urlparse

from ..util.res import get_cached_urls
from ..util.ext import clean_url
from ..src.botmanager import BotManager
from ..src.player import Player

async def get_player(_query: str):
    url = _query
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    try:
        if "spotify" in parsed.netloc:
            if base_url not in get_cached_urls():
                yt_url = get_youtube_link(url)
                return await Player.from_url(clean_url(yt_url), _query, spotify_url=base_url)
            return await Player.from_url(base_url, _query)
        
        if "youtube" in parsed.netloc or "youtu.be" in parsed.netloc:
            return await Player.from_url(clean_url(url), _query)
        return await Player.from_url(clean_url(url), _query)
    
    except Exception as e:
        print(e)
        return None

def get_youtube_link(spotify_url):
    track_info = BotManager.sp.track(spotify_url)
    track_name = track_info['name']
    artist_name = track_info['artists'][0]['name']
    logging.debug(f'Searching youtube with query: {track_name} {artist_name} audio')
    youtube_link = search_youtube(f"{track_name} {artist_name} audio")
    return youtube_link

def search_youtube(query: str):
    youtube = gdisc.build('youtube', 'v3', developerKey=os.getenv('YT_API_KEY'))
    
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=1
    ).execute()
    
    if search_response['items']:
        video_id = search_response['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    else:
        return "No video found for the given query."
    

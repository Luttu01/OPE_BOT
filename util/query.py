import logging
import os
import googleapiclient.discovery as gdisc
from urllib.parse import urlparse, parse_qs, urlunparse
from opebot.util.res import get_cached_urls
from opebot.src.botmanager import BotManager
from opebot.src.player import Player

async def get_player(url: str):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    if "spotify" in url:
        if base_url not in get_cached_urls():
            try:
                print(BotManager.sp.track(base_url))
                url = get_youtube_link(url)
                player = await Player.from_url(url, spotify_url=base_url)
            except Exception as e:
                print(e)
                return None
        else:
            player = await Player.from_url(base_url)
    elif "youtube" in url or "youtu.be" in url:
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            new_query = f"v={query_params['v'][0]}"
            cleaned_url = urlunparse(parsed_url._replace(query=new_query))
            print(cleaned_url)
            player = await Player.from_url(cleaned_url)
        else:
            player = await Player.from_url(url)
    else:
        player = await Player.from_url(url)

    return player

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
    

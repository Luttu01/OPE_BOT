import json

from ..config.paths import file_path_aliases, file_path_cache, file_path_tags
from ..src.songmanager import SongManager

def get_aliases():
    """Returns all aliases"""
    with open(f'{file_path_aliases}', 'r') as read_file:
        aliases = json.load(read_file)
        return list(aliases.values())

def get_alias_urls():
    with open(f'{file_path_aliases}', 'r') as read_file:
        aliases = json.load(read_file)
        return list(aliases.keys())

def get_aliases():
    with open(rf'{file_path_aliases}', 'r') as read_file:
        aliases = json.load(read_file)
        return list(aliases.values())
    
def get_url_from_alias(alias):
    with open(f'{file_path_aliases}', 'r') as read_file:
        aliases = json.load(read_file)
        for url, current_alias in aliases.items():
            if current_alias == alias:
                return url
        return False
    
def get_alias_from_url(url):
     with open(rf'{file_path_aliases}', 'r') as read_file:
        aliases = json.load(read_file)
        return aliases[url]
    
def get_query_from_title(pot_match: str) -> str | None:
    """Get corresponding url from title/query"""
    with open(f'{file_path_cache}', 'r') as read_file:
        cache = json.load(read_file)
        for url in cache:
            if cache[url]['title'] == pot_match:
                return url
            elif "query" in cache[url]:
                if cache[url]["query"] == pot_match:
                    return url
        return None
    
def get_titles():
    """Returns all titles"""
    with open(f'{file_path_cache}', 'r') as read_file:
        cache = json.load(read_file)
        titles = []
        for url in cache:
            titles.append(cache[url]['title'])
        return titles
    
def get_cached_urls():
    """Returns all urls in cache"""
    with open(rf'{file_path_cache}', 'r') as r:
        caches = json.load(r)
        return list(caches.keys())
    
def get_title_from_url(_url: str):
    with open(f'{file_path_cache}', 'r') as read_file:
        cache = json.load(read_file)
        for url in cache:
            if url == _url:
                return cache[url]['title']
        return False
    
def get_tags():
    with open(file_path_tags, 'r') as r:
        data = json.load(r)
        return data['tags']

def get_current_player_url():
    return SongManager.current_player.url

def get_current_player_duration():
    return SongManager.current_player.duration

def get_duration():
    return SongManager.song_curr_duration

def get_queries():
    with open(f'{file_path_cache}', 'r') as read_file:
        cache = json.load(read_file)
        queries = []
        for url in cache:
            if 'query' in cache[url]:
                queries.append(cache[url]['query'])
        return queries
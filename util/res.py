import json
from OPE_BOT.config.paths import file_path_aliases, file_path_cache

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
    
def get_query_from_title(title: str) -> str | None:
    """Get corresponding url from title"""
    with open(f'{file_path_cache}', 'r') as read_file:
        cache = json.load(read_file)
        for url in cache:
            if cache[url]['title'] == title:
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
        for url in cache.items():
            if url == _url:
                return cache[url]['title']
        return False
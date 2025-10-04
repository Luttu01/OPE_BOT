import json
import random
import datetime

from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from ..config.paths import file_path_aliases, file_path_cache, file_path_urlCounter, file_path_toRemove, file_path_tags
from ..util.res import get_url_from_alias, get_cached_urls
from ..src.error import Error
from ..util.res import get_tags
from ..src.botmanager import BotManager

def add_alias(url, new_name):
    try:
        with open(f'{file_path_aliases}', 'r') as read_file:
            aliases = json.load(read_file)
        if url in aliases.keys():
            return False
        with open(f'{file_path_aliases}', 'w') as write_file:
            aliases[url] = new_name
            json.dump(aliases, write_file, indent=4)
            return True
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(e)

def remove_alias(alias: str):
    try:
        with open(f'{file_path_aliases}', 'r') as read_file:
            aliases = json.load(read_file)
        url = get_url_from_alias(alias)
        if url:
            del aliases[url]
        else:
            return False
        with open(rf'{file_path_aliases}', 'w') as write_file:
            json.dump(aliases, write_file, indent=4)
            return True
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(e)

def get_random_cached_urls(n: int, mtag: str):
    """Extract n amount random urls, using inverse weighting"""
    with open(file_path_cache, 'r') as r:
        cache = json.load(r)
    cached_urls = get_cached_urls()
    urls = []
    if mtag:
        for url in cached_urls:
            if check_tag(cache[url], mtag):
                urls.append(url)
        if urls:
            cached_urls = urls
        else:
            return None
        
    random.shuffle(cached_urls)
    weights = [cache[url]['weight'] for url in cached_urls]
    selection_weights = [1 / (1 + weight) for weight in weights]
    total_weight = sum(selection_weights)
    normalized_weights = [w / total_weight for w in selection_weights]
    random_urls = random.choices(cached_urls, weights=normalized_weights, k=n)

    christmas_songs = []
    for url in random_urls:
        cache[url]['weight'] += 1
        if check_tag(cache[url], "jul"):
            christmas_songs.append(url)
    if datetime.datetime.now().month != BotManager.DECEMBER:
        random_urls = [url for url in random_urls if url not in christmas_songs]
    
    with open(file_path_cache, 'w') as w:
        json.dump(cache, w, indent=4)
    return list(set(random_urls))

def check_tag(cache_entry_attributes, mtag):
    cea = cache_entry_attributes
    if 'tag' in cea:
        return cea['tag'] == mtag
    else:
        return False
    
def add_tag(url: str, mtag: str):
    with open(file_path_cache, 'r') as r:
        cache = json.load(r)
    
    if 'tag' in cache[url]:
        return cache[url]['tag']
    else:
        cache[url]['tag'] = mtag

    with open(file_path_cache, 'w') as w:
        json.dump(cache, w, indent=4)
        return None
    
def update_url_counter(url, title):
    try:
        with open(file_path_urlCounter, 'r') as read_file:
            open_json = json.load(read_file)
        if url in open_json:
            open_json[url][0] += 1
        else:
            open_json[url] = [1, title]
        with open(file_path_urlCounter, 'w') as write_file:
            json.dump(open_json, write_file, indent=4)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(e)

def to_remove(new_tag):
    try:
        try:
            with open(file_path_toRemove, 'r') as r:
                data = json.load(r)
                remove_list = data.get('to_remove', [])
        except json.JSONDecodeError:
            data = {}
            remove_list = []
        remove_list.append(new_tag)
        with open(file_path_toRemove, 'w') as w:
            data['to_remove'] = remove_list
            json.dump(data, w, indent=4)
        return True
    except Exception:
        return False
    
def create_tag(new_tag):
    try:
        try:
            with open(file_path_tags, 'r') as r:
                data = json.load(r)
                tags = data.get('tags', [])
        except json.JSONDecodeError:
            tags = []         
        tags.append(new_tag)    
        with open(file_path_tags, 'w') as w:
            data['tags'] = tags
            json.dump(data, w, indent=4)   
        return True
    except Exception:
        return False

def extract_n_mtag(flags):
    n, mtag = None, None
    for flag in flags:
        if flag.isdigit():
            if n is not None:  
                return Error.FLAG_ERROR, Error.FLAG_ERROR
            n = int(flag)
        else:  
            if mtag is not None:  
                return Error.FLAG_ERROR, Error.FLAG_ERROR
            mtag = flag
    if n is None:
        n = 1

    return n, mtag

def extract_query_mtag(_query: tuple[str]):
    if _query[-1] in get_tags():
        mtag = _query[-1]
        query = ' '.join(_query[:-1])
    else:
        mtag = None
        query = ' '.join(_query)
    return query, mtag

def clean_url(url: str) -> str:
    parsed = urlparse(url)

    if "spotify" in parsed.netloc:
        cleaned = parsed._replace(query="")
    elif "youtube" in parsed.netloc or "youtu.be" in parsed.netloc:
        qs = parse_qsl(parsed.query)
        qs_clean = [(k, v) for k, v in qs if k == "v"]
        new_query = urlencode(qs_clean)
        cleaned = parsed._replace(query=new_query)
    else:
        cleaned = parsed._replace(query="")
    
    return urlunparse(cleaned)
import rapidfuzz
import json
import os

from opebot.config.paths import file_path_cache, file_path_toRemove, folder_path_cache
from opebot.util.res import get_aliases, get_query_from_title, get_titles
from opebot.util.validate import is_alias

def check_match(query: str) -> tuple[str, float] | tuple[None, None]:
    best_match, score = rapidfuzz.process.extractOne(query, 
                                                     get_aliases() + [title.lower() for title in get_titles()],
                                                     scorer=rapidfuzz.fuzz.WRatio
                                                     )[:2]
    if score >= 80:
        if is_alias(best_match):
            return best_match, score
        else:
            return get_query_from_title(best_match), score
    return None, None

def reset_weighting():
    with open(file_path_cache, 'r') as r:
        cache = json.load(r)
    
    for url in cache.keys():
        cache[url]['weight'] = 1

    with open(file_path_cache, 'w') as w:
        json.dump(cache, w, indent=4)

def remove_doomed_urls():
    try:
        with open(file_path_toRemove, 'r') as r:
            data = json.load(r)
            remove_list = data.get('to_remove', [])
    except json.JSONDecodeError:
        data = {}
        remove_list = []
    
    with open(file_path_cache, 'r') as r:
        cache = json.load(r)
        for url in remove_list:
            path: str = cache[url]['path']
            if path.startswith(folder_path_cache) and os.path.isfile(path):
                os.remove(path)
            del cache[url]
    with open(file_path_cache, 'w') as w:
        json.dump(cache, w, indent=4)    
    with open(file_path_toRemove, 'w') as w:
        data['to_remove'] = []
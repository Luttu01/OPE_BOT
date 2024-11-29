import json

from OPE_BOT.config.paths import file_path_aliases
from OPE_BOT.util.res import get_url_from_alias

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
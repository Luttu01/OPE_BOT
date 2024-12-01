import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

file_path_dotenv = os.path.join(parent_dir, "config", ".env")
file_path_logs   = os.path.join(parent_dir, 'logs', 'bot.log')
# file_path_cache  = os.path.join(parent_dir, 'res', 'cache.json')
file_path_cache = r'C:\\Users\\luttu\\Desktop\\python\\DIABETESBOT\\res\\cache.json'
# file_path_aliases  = os.path.join(parent_dir, 'res', 'aliases.json')
file_path_aliases = r'C:\\Users\\luttu\\Desktop\\python\\DIABETESBOT\res\aliases.json'
# file_path_tags  = os.path.join(parent_dir, 'res', 'tags.json')
file_path_tags = r'C:\\Users\\luttu\\Desktop\\python\\DIABETESBOT\res\tags.json'
# file_path_urlCounter  = os.path.join(parent_dir, 'res', 'url_counter.json')
file_path_urlCounter = r'C:\\Users\\luttu\\Desktop\\python\\DIABETESBOT\res\url_counter.json'
# file_path_playRequestCounter  = os.path.join(parent_dir, 'res', 'play_requests_counter.json')
file_path_playRequestCounter = r'C:\\Users\\luttu\\Desktop\\python\\DIABETESBOT\res\play_requests_counter.json'
# file_path_toRemove  = os.path.join(parent_dir, 'res', 'to_remove.json')
file_path_toRemove = r'C:\\Users\\luttu\\Desktop\\python\\DIABETESBOT\res\to_remove.json'

# folder_path_cache = os.path.join(parent_dir, "cache")
folder_path_cache = r"C:\Users\luttu\Desktop\python\DIABETESBOT\cache"
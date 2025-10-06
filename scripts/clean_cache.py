import os
import json
import dotenv

dotenv.load_dotenv()
file_path_cache = os.getenv('CACHE_PATH')

def main():
    with open(file_path_cache, "r") as f:
        cache: dict = json.load(f)
        for key in list(cache.keys()):
            if not os.path.exists(cache[key]['path']):
                del cache[key]
    with open(file_path_cache, "w") as f:
        json.dump(cache, f, indent=4)
    return 0

if __name__ == "__main__":
    main()
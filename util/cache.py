import rapidfuzz

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
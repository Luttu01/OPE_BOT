from OPE_BOT.util.res import get_aliases

def validate(arg):
    try:
        assert arg != None
    except AssertionError:
        return AssertionError 
    
def is_url(query):
    return "youtube" in query or \
           "soundcloud" in query or \
           "spotify" in query or \
           "youtu.be" in query

def is_playlist(query):
    return "album" in query or \
           "playlist" in query

def is_alias(alias: str) -> bool:
    return alias in get_aliases()
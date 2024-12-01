from opebot.util.res import get_aliases, get_tags, get_alias_urls, get_alias_from_url
from discord.ext.commands import Context
from .message import embed_msg_error

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

def is_mtag(mtag: str):
    return mtag in get_tags()

async def validate_move(ctx: Context, queue: list, from_position: int, to_position: int):
    if len(queue) == 0:
        await ctx.send(embed=embed_msg_error("The queue is currently empty."))
        return False
    if from_position < 1 or from_position > len(queue):
        await ctx.send(embed=embed_msg_error(f"Invalid `from_position`. Must be between 1 and {len(queue)}."))
        return False
    if to_position < 1 or to_position > len(queue):
        await ctx.send(embed=embed_msg_error(f"Invalid `to_position`. Must be between 1 and {len(queue)}."))
        return False
    if to_position > from_position:
        await ctx.send(embed=embed_msg_error("Can't move songs down the queue."))
        return False
    if from_position == to_position:
        await ctx.send(embed=embed_msg_error("Moving to the same position is redundant."))
        return False
    return True

async def validate_new_alias(ctx: Context, url: str, new_alias: str):
    if not is_url(url):
        await ctx.send(embed=embed_msg_error("Invalid url. Please make sure to send a valid youtube, spotify, or soundcloud link."))
        return False
    if is_alias(new_alias):
        await ctx.send(embed=embed_msg_error("That alias already exists."))
        return False
    if url in get_alias_urls():
        await ctx.send(embed=embed_msg_error(f"That song already has the alias: {get_alias_from_url(url)}"))
        return False
    return True
from __future__ import annotations
import datetime
from opebot.util.res import get_aliases, get_tags, get_alias_urls, get_alias_from_url
from opebot.util.message import embed_msg_error
from opebot.src.error import Error
from typing import Union
from discord.ext.commands import Context
from opebot.src.botmanager import BotManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from opebot.src.player import Player

def validate(arg):
    try:
        assert arg != None
        return True
    except AssertionError:
        return False 
    
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

async def validate_new_alias(ctx: Context, url: str, new_alias: str) -> bool:
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

async def validate_random(ctx: Context, 
                          n: Union[int, Error.FLAG_ERROR], 
                          mtag: Union[str, Error.FLAG_ERROR]) -> bool:
    if n == Error.FLAG_ERROR or mtag == Error.FLAG_ERROR:
        await ctx.send(embed=embed_msg_error("Improper usage of flags.\n"
                                             "For more help and details do:\n"
                                             "-help random"))
        return False
    else:
        if mtag:
            if not is_mtag(mtag):
                await ctx.send(embed=embed_msg_error("Not a valid tag."))
                return False 
            if mtag == "jul" and datetime.datetime.now().month != BotManager.DECEMBER:
                await ctx.send(embed=embed_msg_error("Christmas songs are only allowed during month of December."))
                return False
        return True

async def validate_player(ctx: Context, player: Player) -> bool:
    if player is None:
        await ctx.send(embed=embed_msg_error("Problem downloading the song, please try again."))
        return False
    elif player == Error.DURATION_ERROR:
        await ctx.send(embed=embed_msg_error("Songs over 10 minutes are not supported."))
        return False
    return True
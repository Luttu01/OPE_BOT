import logging
import random

from discord.ext.commands import Context
from discord.ext import tasks

from OPE_BOT.src import bot
from OPE_BOT.src.songmanager import SongManager
from OPE_BOT.src.botmanager import BotManager
from OPE_BOT.util.message import embed_msg, embed_msg_something_went_wrong, embed_msg_error
from OPE_BOT.util.validate import validate, is_url, is_playlist, is_alias
from OPE_BOT.util.cache import check_match
from OPE_BOT.util.query import get_player
from OPE_BOT.util.playback import _play, _now_playing
from OPE_BOT.util.res import get_alias_urls, get_alias_from_url, get_url_from_alias, get_aliases, get_title_from_url
from OPE_BOT.util.ext import add_alias, remove_alias

@bot.event
async def on_ready():
    #TODO:
    #clear_logs()
    #reset_weighting()
    #radio_mode(False)

    __song_manager = SongManager()
    __bot_manager = BotManager()

    print(f'Logged in as {bot.user.name}')

@tasks.loop(seconds=1)
async def tic(ctx: Context):
    if ctx.voice_client:
        if ctx.voice_client.is_playing():
            SongManager.increment_duration()
        elif not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            if SongManager.queue:
                next_song = SongManager.next_song()
                if next_song == None:
                    await ctx.send(embed=embed_msg_error("Skipping faulty song."))
                    return
                await _play(ctx, next_song)
            elif SongManager.radio_mode:
                if SongManager.radio_station:
                    pass
                    #TODO: play random of given tag
                #TODO: play random


@bot.command(name='join', help='Bot joins your voice channel.')
async def join(ctx: Context):
    if not ctx.message.author.voice:
        await ctx.send(embed=embed_msg("You are not connected to a voice channel."))
        return
    channel = ctx.message.author.voice.channel
    await channel.connect()
    if not tic.is_running():
        tic.start(ctx)

@bot.command(name='play', aliases=["p", "pl", "pla", "spela"], help="Plays given url or search")
async def play(ctx: Context, *_query, **flags):
    if validate(ctx) == AssertionError:
        await ctx.send(embed=embed_msg_something_went_wrong())
        return

    if not ctx.voice_client:
        await join(ctx)

    logging.debug(f"query is: {_query}")
    logging.debug(f"flags are: {flags}")

    query = ' '.join(_query)
    query_lower = query.lower()

    print(query)
    
    async with ctx.typing():
        if is_playlist(query):
            await ctx.send(embed=embed_msg_error("Playlists and albums are not supported."))
            return

        if not is_url(query) and not is_alias(query):
            pot_match, score = check_match(query_lower)
            if pot_match:
                SongManager.last_request = query
                query = pot_match
                if is_url(pot_match):
                    pot_match = get_title_from_url(pot_match)
                BotManager.last_message = await ctx.send(embed=embed_msg(f"Your query matched {pot_match!r} by {score:.2f}"))
        
        try:
            if query_lower in get_aliases():
                query = get_url_from_alias(query_lower)
            player = await get_player(query)
            print("after get player\n")
            if player is None:
                await ctx.send(embed=embed_msg("Problem downloading the song, please try again."))
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                SongManager.add_to_q(player)
                await ctx.send(embed=embed_msg(f"{player.title!r} added to queue, position {len(SongManager.queue)}"))
            else:
                await _play(ctx, player)
        except:
            #TODO: log errors
            pass

        #TODO: flags


@bot.command(name="skip", aliases=["s", "sk", "ski", "nästa"], help="Skip current song")
async def skip(ctx: Context):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await ctx.send(embed=embed_msg("No song is currently playing."))
        return
    
    # TODO: 
    # if not check_allowed_to_skip(ctx.author.id, get_current_player_url()):
    #     await ctx.send("You lack privilege to skip this song.")
    #     return

    ctx.voice_client.stop()
    await ctx.send(embed=embed_msg(f"Skipped the song: {_now_playing()}."))

@bot.command(name='leave', aliases=["lämna"], help='Bot clears queue and leaves channel')
async def leave(ctx: Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        SongManager.queue.clear()
        await voice_client.disconnect()
        tic.stop()

@bot.command(name='shuffle', aliases=["sh", "shu", "shuf", "shuff", "shuffl", "blanda"], help='Shuffle queue')
async def shuffle(ctx: Context):
    if len(SongManager.queue) > 1:

        random.shuffle(SongManager.queue)

        await ctx.send(embed=embed_msg("Queue has been shuffled."))
    else:
        await ctx.send(embed=embed_msg("Not enough songs in the queue to shuffle."))

@bot.command(name='remove', help='Remove first, or given position, from queue')
async def remove(ctx: Context, position: int = 1):
    queue = SongManager.queue
    if len(queue) > 0:
        if 1 <= position <= len(queue):
            removed_song = queue.pop(position - 1)
            await ctx.send(embed=embed_msg(removed_song.title, "Removed from queue"))
        else:
            await ctx.send(embed=embed_msg(f"Invalid position: {position}."))
    else:
        await ctx.send(embed=embed_msg("The queue is currently empty."))

@bot.command(name='queue', aliases=['q', "qu", "que", "queu", "kö"], help='Display queue')
async def show_queue(ctx: Context):
    queue = SongManager.queue
    if len(queue) == 0:
        await ctx.send("The queue is currently empty.")
        return

    message = ""
    for i, player in enumerate(queue, 1):
        message += f"**{i}**: {player.title}\n"

    await ctx.send(embed=embed_msg(message, "Queue"))

@bot.command(name='move', aliases=["m", "mo", "mov", "flytta"], help='Move a song in the queue to a new position')
async def move(ctx: Context, from_position: int, to_position: int = 1):
    queue = SongManager.queue
    if len(queue) == 0:
        await ctx.send(embed=embed_msg_error("The queue is currently empty."))
        return
    if from_position < 1 or from_position > len(queue):
        await ctx.send(embed=embed_msg_error(f"Invalid `from_position`. Must be between 1 and {len(queue)}."))
        return
    if to_position < 1 or to_position > len(queue):
        await ctx.send(embed=embed_msg_error(f"Invalid `to_position`. Must be between 1 and {len(queue)}."))
        return
    if to_position > from_position:
        await ctx.send(embed=embed_msg_error("Can't move songs down the queue."))
        return
    if from_position == to_position:
        await ctx.send(embed=embed_msg_error("Moving to the same position is redundant."))
        return
    from_index = from_position - 1
    to_index = to_position - 1
    song = queue.pop(from_index)
    queue.insert(to_index, song)
    SongManager.queue = queue
    await ctx.send(embed=embed_msg(f"Moved **{song.title}** to position {to_position}."))

@bot.command(name="alias", help="Sets given URL to given alias")
async def alias(ctx: Context, url: str, _new_alias: str):
    new_alias = _new_alias.lower()
    if url == 'np':
        if (np_url := SongManager.current_player.url):
            await alias(ctx, np_url, new_alias)
        else:
            await ctx.send(embed=embed_msg_error("Nothing valid is playing to add as an alias right now."))
        return
    if not is_url(url):
        await ctx.send(embed=embed_msg_error("Invalid url. Please make sure to send a valid youtube, spotify, or soundcloud link."))
        return
    if is_alias(new_alias):
        await ctx.send(embed=embed_msg_error("That alias already exists."))
        return
    if url in get_alias_urls():
        await ctx.send(embed=embed_msg_error(f"That song already has the alias: {get_alias_from_url(url)}"))
        return
    success = add_alias(url, new_alias)
    if success:
        await ctx.send(embed=embed_msg(f"Successfully added alias: {new_alias}"))

@bot.command(name="rmalias", help="remove given alias")
async def rmalias(ctx: Context, alias: str):
    if not is_alias(alias):
        await ctx.send(embed=embed_msg_error("Not an existing alias."))
        return
    success = remove_alias(alias)
    if success:
        await ctx.send(embed=embed_msg(f"Successfully removed alias: {alias}"))


from __future__ import annotations
from typing import TYPE_CHECKING

import asyncio
import datetime

from random import shuffle as _shuffle
from discord.ext import commands
from discord.ext import tasks

from ..src import bot
from ..src.songmanager import SongManager
from ..src.botmanager import BotManager
from ..src.decorator import in_same_voice_channel
from ..util.query import get_player
from ..util.cache import (check_match, reset_weighting, remove_doomed_urls,
                               get_songs_with_tag)
from ..util.message import embed_msg, embed_msg_something_went_wrong, embed_msg_error
from ..util.playback import _play, _now_playing, toggle_radio
from ..util.validate import (validate, is_url, is_playlist, 
                                  is_alias, is_mtag, validate_move, 
                                  validate_new_alias, validate_random, validate_player)
from ..util.res import (get_url_from_alias, get_aliases, get_title_from_url, 
                             get_current_player_url, get_tags, get_current_player_duration,
                             get_duration)
from ..util.ext import (add_alias, remove_alias, get_random_cached_urls, 
                             add_tag, to_remove, create_tag,
                             extract_n_mtag, extract_query_mtag)

if TYPE_CHECKING:
    from discord.ext.commands import Context

@bot.event
async def on_ready():
    # TODO:
    # clear_logs()
    remove_doomed_urls()
    if datetime.datetime.now().weekday() == BotManager.MONDAY:
        reset_weighting()

    __song_manager = SongManager()
    __bot_manager = BotManager()

    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_command_error(ctx: Context, error):
    print(f"Command error triggered: {error}")
    if isinstance(error, commands.CheckFailure):
        await ctx.send(embed=embed_msg_error(str(error)))
    elif isinstance(error, commands.CommandNotFound):
        msg = f"Command not found: {ctx.message.content}"
        if ctx.message.content == "-silence":
            msg += "\n Try -radio instead"
        await ctx.send(embed=embed_msg_error(msg))

@tasks.loop(seconds=1)
async def on_step(ctx: Context):
    if ctx.voice_client:
        if len(ctx.voice_client.channel.members) == 1:
            await leave(ctx)
            return
        if ctx.voice_client.is_playing():
            SongManager.increment_duration()
        elif not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            if SongManager.queue:
                next_song = SongManager.next_song()
                if next_song == None:
                    await ctx.send(embed=embed_msg_error("Skipping faulty song."))
                    return
                await _play(ctx, next_song)
            elif SongManager.radio_mode and not SongManager.processing_player:
                if SongManager.radio_station:
                    await play_random_song(ctx, SongManager.radio_station, random=True)
                else:
                    await play_random_song(ctx, random=True)

@bot.command(name='join', help='Bot joins your voice channel.')
async def join(ctx: Context):
    if not ctx.message.author.voice:
        await ctx.send(embed=embed_msg_error("You are not connected to a voice channel."))
        return
    if ctx.voice_client:
        await ctx.send(embed=embed_msg_error("Bot already connected to a voice client."))
    channel = ctx.message.author.voice.channel
    await channel.connect()
    if not on_step.is_running():
        on_step.start(ctx)

@bot.command(name='play', 
             aliases=["p", "pl", "pla", "spela"], 
             help=("Plays given url or search\n"
                   "You can add a tag (presuming it exists, otherwise you can create one using the -tag command) to your query to group it with other songs of the same tag\n"
                   "-play <your_query> <your_tag>\n"
                   "Use the tag with -random command to play one of those songs\n"
                   "-random <your_tag>"))
async def play(ctx: Context, *_query, **flags):
    try:
        if not validate(ctx):
            await ctx.send(embed=embed_msg_something_went_wrong())
            return
        
        SongManager.processing_player = True

        if not ctx.voice_client:
            await join(ctx)

        if "random" not in flags:
            SongManager.reset_history()

        query, mtag = extract_query_mtag(_query)
        print(query)
        query_lower = query.lower()

        async with ctx.typing():
            if is_playlist(query):
                return await ctx.send(embed=embed_msg_error("Playlists and albums are not supported."))
            if not is_url(query) and not is_alias(query) and "search" not in flags:
                pot_match, score = check_match(query_lower)
                if pot_match:
                    SongManager.last_request = query
                    query = pot_match
                    if is_url(pot_match):
                        pot_match = get_title_from_url(pot_match)
                    if score < 100:
                        await ctx.send(embed=embed_msg(f"Your query matched {pot_match!r} by {score:.2f}%\n"
                                                        "do -search if this is wrong."))
            try:
                for alias in (query, query_lower):
                    if alias in get_aliases():
                        query = get_url_from_alias(alias)
                        break
                player = await get_player(query)
                if not await validate_player(ctx, player):
                    return
                if "random" not in flags:
                    SongManager.last_player = player
                if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    SongManager.add_to_q(player)
                    await ctx.send(embed=embed_msg(f"{player.title}\n"
                                                   f"position {len(SongManager.queue)}",
                                                    "Added to queue"))
                else:
                    await _play(ctx, player)
            except:
                #TODO: log errors
                pass

            if mtag:
                if not is_mtag(mtag):
                    return await ctx.send(embed=embed_msg_error("Invalid tag."))
                existing_tag = add_tag(player.url, mtag)
                if existing_tag:
                    await ctx.send(embed=embed_msg_error(f"That song already has the tag: {existing_tag!r}"))
                else:
                    await ctx.send(embed=embed_msg(f"Successfully tagged your song with: {mtag!r}"))
    finally:
        SongManager.processing_player = False

@bot.command(name="skip", 
             aliases=["s", "sk", "ski", "nästa"], 
             help="Skip current song.")
@in_same_voice_channel()
async def skip(ctx: Context):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await ctx.send(embed=embed_msg("No song is currently playing."))
        return
    
    # TODO: 
    # if not check_allowed_to_skip(ctx.author.id, get_current_player_url()):
    #     await ctx.send("You lack privilege to skip this song.")
    #     return

    ctx.voice_client.stop()
    await ctx.send(embed=embed_msg(f"{_now_playing()}.", "Skipped song"))

@bot.command(name='leave', 
             aliases=["lämna"], 
             help='Bot clears queue and leaves channel.')
@in_same_voice_channel()
async def leave(ctx: Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        SongManager.queue.clear()
        SongManager.radio_mode = False
        await voice_client.disconnect()
        on_step.stop()

@bot.command(name='shuffle', 
             aliases=["sh", "shu", "shuf", "shuff", "shuffl", "blanda"], 
             help='Shuffle queue')
@in_same_voice_channel()
async def shuffle(ctx: Context):
    if len(SongManager.queue) > 1:
        _shuffle(SongManager.queue)
        await ctx.send(embed=embed_msg_error("Queue has been shuffled."))
    else:
        await ctx.send(embed=embed_msg_error("Not enough songs in the queue to shuffle."))

@bot.command(name='remove', 
             help='Remove first, or given position, from queue')
@in_same_voice_channel()
async def remove(ctx: Context, position: int = 1):
    queue = SongManager.queue
    if len(queue) > 0:
        if 1 <= position <= len(queue):
            removed_song = queue.pop(position - 1)
            await ctx.send(embed=embed_msg(removed_song.title, "Removed from queue"))
        else:
            await ctx.send(embed=embed_msg_error(f"Invalid position: {position}."))
    else:
        await ctx.send(embed=embed_msg_error("The queue is currently empty."))

@bot.command(name='queue', 
             aliases=['q', "qu", "que", "queu", "kö"], 
             help='Display queue.')
@in_same_voice_channel()
async def show_queue(ctx: Context):
    queue = SongManager.queue
    if len(queue) == 0:
        return await ctx.send(embed=embed_msg_error("The queue is currently empty."))
    message = ""
    for i, player in enumerate(queue, 1):
        message += f"**{i}**: {player.title}\n"
    await ctx.send(embed=embed_msg(message, "Queue"))

@bot.command(name='move', 
             aliases=["m", "mo", "mov", "flytta"], 
             help=('Move a song in the queue to a new position\n'
                   '-move 7 2\n'
                   "moves song from position 7 to 2\n"
                   "or leave out target position and it defaults to position 1\n"
                   "-move 7"))
@in_same_voice_channel()
async def move(ctx: Context, from_position: int, to_position: int = 1):
    queue = SongManager.queue
    if not await validate_move(ctx, queue, from_position, to_position):
        return 
    from_index = from_position - 1
    to_index = to_position - 1
    song = queue.pop(from_index)
    queue.insert(to_index, song)
    SongManager.queue = queue
    await ctx.send(embed=embed_msg(f"{song.title!r}\n To position {to_position}.",
                                    "Moved song."))

@bot.command(name="alias",
             help=(
                 "Sets given URL to given alias.\n"
                 "Example:\n"
                 "-alias <url> <your_alias>\n"
                 "You can then use this alias to query that song\n"
                 "-play <your_alias>"))
@in_same_voice_channel()
async def alias(ctx: Context, url: str, *_new_alias: str):
    new_alias = ' '.join(_new_alias).lower()
    if not await validate_new_alias(ctx, url, new_alias):
        return
    success = add_alias(url, new_alias)
    if success:
        await ctx.send(embed=embed_msg(f"Successfully added alias: {new_alias}"))

@bot.command(name="rmalias", 
             help=("remove given alias"
                   "-rmalias <your_alias>"))
@in_same_voice_channel()
async def rmalias(ctx: Context, alias: str):
    if not is_alias(alias):
        await ctx.send(embed=embed_msg_error("Not an existing alias."))
        return
    success = remove_alias(alias)
    if success:
        await ctx.send(embed=embed_msg(f"{alias}",
                                       "Removed alias."))

@bot.command(name="aliases", help="Show aliases.")
@in_same_voice_channel()
async def aliases(ctx: Context):
    _aliases = get_aliases()
    msg = ""
    for alias in _aliases:
        msg += f"{alias}\n"
    await ctx.send(embed=embed_msg(msg, "Aliases"))

@bot.command(name="random", 
             aliases=["r", "ra", "ran", "rand", "rando", "slumpa"], 
             help=("Play a random song.\n"
                   "Or you can queue an X amount of songs\n"
                   "-random 5\n"
                   "You can also specify a certain tag of songs\n"
                   "-random 5 <your_tag>"))
async def play_random_song(ctx: Context, *flags, **kwargs):
    if len(flags) > 2:
        return await ctx.send(embed=embed_msg_error("Too many flags\n"
                                                    "For more help and details do:\n"
                                                    "-help random"))
    n, mtag = extract_n_mtag(flags)
    if await validate_random(ctx, n, mtag, kwargs):
        random_urls = get_random_cached_urls(n, mtag)
        if random_urls:
            for url in random_urls:
                await play(ctx, url, random=True)
                await asyncio.sleep(.5) # Deload at large workload of requests
        else:
            return await ctx.send(embed=embed_msg_error("No songs with that tag."))
    
@bot.command(name="radio", 
             help=("Toggle radio mode.\n"
                   "If no songs are queued, play a random song."
                   "You can set a radio station to only play random songs with given tag."
                   "-radio <tag>"
                   "do -tags for available tags."))
async def radio(ctx: Context, station: str = ""):
    if station:
        if is_mtag(station):
            SongManager.radio_station = station
        else:
            return await ctx.send(embed=embed_msg_error("Not a valid radio station.\n"
                                                        "do -tags for valid options"))
    _radio = toggle_radio()
    if _radio:
        if not ctx.voice_client:
            await join(ctx)
        await ctx.send(embed=embed_msg("Radio has been turned on."))
    else:
        await ctx.send(embed=embed_msg("Radio has been turned off"))
        SongManager.radio_station = ""

@bot.command(name="trash", help="Skip and mark current song to be deleted at next boot.")
@in_same_voice_channel()
async def trash(ctx: Context):
    success = to_remove(get_current_player_url())
    if success:
        await ctx.send(embed=embed_msg("Successfully marked song to be deleted."))
        await skip(ctx)
    else:
        await ctx.send(embed=embed_msg_something_went_wrong())

@bot.command(name="newtag", 
             help=("Create a new music tag\n"
                    "-tag your_tag\n"
                    "then add it to a song in -play command\n"
                    "-play <your_query> <your_tag>\n"
                    "You can then use this tag in -random command to play songs with that tag\n"
                    "-random <your_tag>"))
@in_same_voice_channel()
async def new_tag(ctx: Context, new_tag: str):
    if new_tag in get_tags():
        await ctx.send(embed=embed_msg_error("That tag already exists"))
        return
    success = create_tag(new_tag)
    if success:
        await ctx.send(embed=embed_msg(f"Successfully created the tag: {new_tag!r}"))
        return
    else:
        await ctx.send(embed=embed_msg_something_went_wrong())
    
@bot.command(name="duration", 
             help="Show duration of current song.")
@in_same_voice_channel()
async def duration(ctx: Context):
    if not ctx.voice_client.is_playing():
        await ctx.send(embed=embed_msg_error("Nothing currently playing to display duration of."))
        return
    if not get_current_player_duration():
        await ctx.send(embed=embed_msg_error("No duration to display for this song."))
        return
    currently_at_minutes, currently_at_seconds = divmod(get_duration(), 60)
    player_dur_minutes, player_dur_seconds     = divmod(get_current_player_duration(), 60)
    await ctx.send(embed=embed_msg(f"{currently_at_minutes}:{currently_at_seconds:02d} / {player_dur_minutes}:{player_dur_seconds:02d}",
                                    "Duration"))

@bot.command(name="search",
            help="Do literal search if cache match was faulty.")
@in_same_voice_channel()
async def search(ctx: Context):
    if SongManager.last_request:
        await play(ctx, SongManager.last_request, search=True)
        if SongManager.queue:
           SongManager.queue.remove(SongManager.last_player)
        else:
            await skip(ctx)
        SongManager.reset_history()
    else:
        return await ctx.send(embed=embed_msg_error("No query to search."))
    
@bot.command(name="tags",
             help="Show existing tags\n"
                  "-tags"
                  "or count how many songs have given tag"
                  "-tags <tag>")
@in_same_voice_channel()
async def tags(ctx: Context, mtag: str = None):
    if not mtag:
        msg = ""
        for tag in get_tags():
            msg += f"{tag}\n"
        return await ctx.send(embed=embed_msg(msg, "Existing tags."))
    if mtag:
        if not is_mtag(mtag):
            return await ctx.send(embed=embed_msg_error("Not an existing tag."))
    quant = get_songs_with_tag(mtag, True)
    return await ctx.send(embed=embed_msg(f"There are {quant} songs with that tag."))

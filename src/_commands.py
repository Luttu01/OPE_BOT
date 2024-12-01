import logging
import asyncio

from random import shuffle as _shuffle
from discord.ext.commands import Context
from discord.ext import tasks

from opebot.src import bot
from opebot.src.songmanager import SongManager
from opebot.src.botmanager import BotManager
from opebot.util.query import get_player
from opebot.util.cache import check_match
from opebot.util.message import embed_msg, embed_msg_something_went_wrong, embed_msg_error
from opebot.util.playback import _play, _now_playing, toggle_radio
from opebot.util.validate import (validate, is_url, is_playlist, 
                                   is_alias, is_mtag, validate_move, 
                                   validate_new_alias)
from opebot.util.res import (get_url_from_alias, get_aliases, get_title_from_url, 
                              get_current_player_url, get_tags, get_current_player_duration,
                              get_duration)
from opebot.util.ext import (add_alias, remove_alias, get_random_cached_urls, 
                              add_tag, to_remove, create_tag)

@bot.event
async def on_ready():
    #TODO:
    #clear_logs()
    #reset_weighting()

    __song_manager = SongManager()
    __bot_manager = BotManager()

    print(f'Logged in as {bot.user.name}')

@tasks.loop(seconds=1)
async def tic(ctx: Context):
    if ctx.voice_client:
        if len(ctx.voice_client.channel.members) == 1:
            await leave()
            return
        #TODO: BotManager.on_step()
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
                    await play_random_song(ctx, mtag=SongManager.radio_station)
                else:
                    await play_random_song(ctx)

@bot.command(name='join', help='Bot joins your voice channel.')
async def join(ctx: Context):
    if not ctx.message.author.voice:
        await ctx.send(embed=embed_msg("You are not connected to a voice channel."))
        return
    channel = ctx.message.author.voice.channel
    await channel.connect()
    if not tic.is_running():
        tic.start(ctx)

@bot.command(name='play', 
             aliases=["p", "pl", "pla", "spela"], 
             help=("Plays given url or search\n"
                   "You can add a tag (presuming it exists, otherwise you can create one using the -tag command) to your query to group it with other songs of the same tag\n"
                   "-play your_query tag=your_tag\n"
                   "Use the tag with -random command to play one of those songs\n"
                   "-random your_tag"))
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

    async with ctx.typing():
        if is_playlist(query):
            await ctx.send(embed=embed_msg_error("Playlists and albums are not supported."))
            return

        if not is_url(query) and not is_alias(query):
            pot_match, score = check_match(query_lower)
            print(pot_match)
            if pot_match:
                SongManager.last_request = query
                query = pot_match
                if is_url(pot_match):
                    pot_match = get_title_from_url(pot_match)
                await ctx.send(embed=embed_msg(f"Your query matched {pot_match!r} by {score:.2f}"))
        
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

        if flags:
            if flags["tag"]:
                existing_tag = add_tag(player.url, flags["tag"])
                if existing_tag:
                    await ctx.send(embed=embed_msg_error(f"That song already has the tag: {existing_tag!r}"))
                else:
                    await ctx.send(embed=embed_msg(f"Successfully added the tag: {flags['tag']!r}"))

        # if 't' not in flags:
        #     update_url_counter(url, player.title)
        #     update_request_counter(ctx.author.name)

@bot.command(name="skip", 
             aliases=["s", "sk", "ski", "nästa"], 
             help="Skip current song.")
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

@bot.command(name='leave', 
             aliases=["lämna"], 
             help='Bot clears queue and leaves channel')
async def leave(ctx: Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        SongManager.queue.clear()
        await voice_client.disconnect()
        tic.stop()

@bot.command(name='shuffle', 
             aliases=["sh", "shu", "shuf", "shuff", "shuffl", "blanda"], 
             help='Shuffle queue')
async def shuffle(ctx: Context):
    if len(SongManager.queue) > 1:
        _shuffle(SongManager.queue)
        await ctx.send(embed=embed_msg("Queue has been shuffled."))
    else:
        await ctx.send(embed=embed_msg("Not enough songs in the queue to shuffle."))

@bot.command(name='remove', 
             help='Remove first, or given position, from queue')
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

@bot.command(name='queue', 
             aliases=['q', "qu", "que", "queu", "kö"], 
             help='Display queue')
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
                   "moves song in position 7 to 2\n"
                   "or leave out target position and it defaults to position 1\n"
                   "-move 7"))
async def move(ctx: Context, from_position: int, to_position: int = 1):
    queue = SongManager.queue
    if not await validate_move(ctx, queue, from_position, to_position):
        return 
    from_index = from_position - 1
    to_index = to_position - 1
    song = queue.pop(from_index)
    queue.insert(to_index, song)
    SongManager.queue = queue
    await ctx.send(embed=embed_msg(f"Moved **{song.title}** to position {to_position}."))

@bot.command(name="alias",
             help=(
                 "Sets given URL to given alias.\n"
                 "Example:\n"
                 "-alias url your_alias\n"
                 "You can then use this alias to query that song\n"
                 "-play your_alias")
                 )
async def alias(ctx: Context, url: str, *_new_alias: str):
    new_alias = ' '.join(_new_alias).lower()
    if not validate_new_alias(ctx, url, new_alias):
        return
    success = add_alias(url, new_alias)
    if success:
        await ctx.send(embed=embed_msg(f"Successfully added alias: {new_alias}"))

@bot.command(name="rmalias", 
             help=("remove given alias"
                   "-rmalias insert_alias"))
async def rmalias(ctx: Context, alias: str):
    if not is_alias(alias):
        await ctx.send(embed=embed_msg_error("Not an existing alias."))
        return
    success = remove_alias(alias)
    if success:
        await ctx.send(embed=embed_msg(f"Successfully removed alias: {alias}"))

@bot.command(name="aliases", help="Show aliases")
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
                   "-random 5 rap"))
async def play_random_song(ctx: Context, n: int = 1, mtag: str = ""):
    if mtag:
        if not is_mtag(mtag):
            return await ctx.send(embed=embed_msg_error("Not a valid tag."))
    random_urls = get_random_cached_urls(n, mtag)
    if random_urls:
        for url in random_urls:
            await play(ctx, url)
            await asyncio.sleep(1)
    else:
        return await ctx.send(embed=embed_msg_error("No songs with that tag."))
    
@bot.command(name="radio", 
             help=("Toggle radio mode.\n"
                    "If no songs are queued, play a random song."))
async def radio(ctx: Context, station: str = ""):
    if station:
        SongManager.radio_station = station
    _radio = toggle_radio()
    if _radio:
        await ctx.send(embed=embed_msg("Radio has been turned on."))
    else:
        await ctx.send(embed=embed_msg("Radio has been turned off"))
        SongManager.radio_station = ""

@bot.command(name="trash", help="Skip and mark current song to be deleted at next boot.")
async def trash(ctx: Context):
    success = to_remove(get_current_player_url())
    if success:
        await ctx.send(embed=embed_msg("Successfully marked song to be deleted."))
        await skip(ctx)
    else:
        await ctx.send(embed="Something went wrong.")

@bot.command(name="tag", 
             help=("Create a new music tag\n"
                    "-tag your_tag\n"
                    "then add it to a song in -play command\n"
                    "-play your_query your_tag\n"
                    "You can then use this tag in -random command to play songs with that tag\n"
                    "-random your_tag"))
async def tag(ctx: Context, new_tag: str):
    if new_tag in get_tags():
        await ctx.send(embed=embed_msg_error("That tag already exists"))
        return
    success = create_tag(new_tag)
    if success:
        await ctx.send(embed=embed_msg(f"Successfully created the tag: {new_tag!r}"))
        return
    else:
        await ctx.send(embed=embed_msg_something_went_wrong())
        return
    
@bot.command(name="duration", 
             help="Show how far through the current")
async def duration(ctx: Context):
    if not ctx.voice_client.is_playing():
        await ctx.send(embed=embed_msg_error("Nothing currently playing to display duration of."))
        return
    if not get_current_player_duration():
        await ctx.send(embed=embed_msg_error("No duration to display for this song."))
        return
    currently_at_minutes, currently_at_seconds = divmod(get_duration(), 60)
    player_dur_minutes, player_dur_seconds     = divmod(get_current_player_duration(), 60)
    await ctx.send(embed=embed_msg(f"{currently_at_minutes}:{currently_at_seconds} / {player_dur_minutes}:{player_dur_seconds}",
                             "Duration"))
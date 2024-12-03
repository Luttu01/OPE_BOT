from discord import Embed, Color

def embed_msg(content: str, title: str = "OPE BOT SAYS") -> Embed:
    msg = Embed(
        title=title,
        description=content,
        color=Color.blue()
    )
    return msg

def embed_msg_song(song_title: str, author: str = None) -> Embed:
    msg = Embed(
        title="Now playing",
        description=song_title,
        color=Color.blue()
    )
    if author:
        msg.add_field(name="Requested by:", value=f"{author}")
    return msg

def embed_msg_error(content: str, **fields) -> Embed:
    msg = Embed(
        title="Error",
        description=content,
        color=Color.red()
    )
    for name, value in fields.items():
        msg.add_field(name=name, value=value, inline=False)
    return msg

def embed_msg_something_went_wrong() -> Embed:
    msg = Embed(
        title="Error",
        description="Something went wrong, please try again.",
        color=Color.red()
    )
    return msg
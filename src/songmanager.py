from __future__ import annotations
from typing import TYPE_CHECKING

import threading

if TYPE_CHECKING:
    from ..src.player import Player

class SongManager:
    queue: list[Player]  = []
    current_player: Player = None
    radio_mode: bool = False
    radio_station: str = None
    last_request: str = None
    last_player: Player = None
    song_duration: int = 0
    song_curr_duration: int = 0
    song_is_paued: bool = False
    processing_player: bool = False

    __lock = threading.Lock()

    def __init__(self):
        pass

    @classmethod
    def add_to_q(cls, song: Player) -> None:
        with cls.__lock:
            cls.queue.append(song)

    @classmethod
    def next_song(cls):
        with cls.__lock:
            return cls.queue.pop(0)
        
    @classmethod
    def increment_duration(cls):
        cls.song_curr_duration += 1
    
    @classmethod
    def reset_history(cls):
        cls.last_player = None
        cls.last_request = ""
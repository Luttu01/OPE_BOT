from enum import Enum

class Error(Enum):
    FLAG_ERROR = "Faulty usage of flags."
    DURATION_ERROR = "Songs over 10 minutes are not supported."
from .exceptions import DebugException
from .logging import Logging
from .timer import Timer
from .tools import Tools


class DebugTools:
    timer = Timer
    logging = Logging
    tools = Tools
    exceptions = DebugException


DebugTools.logging.unmute()

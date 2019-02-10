import time

from .logging import Logging


class Timer:

    def __init__(self):
        self.current_time = time.time()

    def reset(self):
        self.current_time = time.time()

    def get_duration(self):
        current_time = self.current_time
        self.reset()
        return self.current_time - current_time

    def print_duration(self, purpose: str, indentation: int = 0, debug=True):
        duration = self.get_duration()
        if debug:
            Logging.print_debug("Took", duration, "seconds to", purpose, indentation=indentation)
        else:
            Logging.print_log("Took", duration, "seconds to", purpose, indentation=indentation)

SETTINGS = {
    "DEBUG": True,
    "LOG": True,
    "DEBUG_DEPTH": 100,
    "LOG_DEPTH": 100,
    "MISC": True
}


class Logging:
    muted = False

    @classmethod
    def mute(cls):
        cls.muted = True

    @classmethod
    def unmute(cls):
        cls.muted = False

    @classmethod
    def print_debug(cls, *content, indentation=0, show=SETTINGS["DEBUG"]):
        if show and SETTINGS["DEBUG_DEPTH"] >= indentation and cls.muted is False:
            print(" " * (indentation * 4), *content)
        else:
            pass

    @classmethod
    def print_log(cls, *content, indentation=0, show=SETTINGS["LOG"]):
        if show and SETTINGS["LOG_DEPTH"] >= indentation and cls.muted is False:
            print(" " * (indentation * 4), *content)
        else:
            pass

    @classmethod
    def print_misc(cls, *content, indentation=0, show=SETTINGS["MISC"]):
        if show and cls.muted is False:
            print(" " * (indentation * 4), *content)
        else:
            pass

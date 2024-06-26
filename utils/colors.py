import logging
from functools import partial


# Shamelessly stolen from blender
class bcolors:
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    HEADER = "\033[0;95m"
    WARNING = "\033[0;93m"
    FAIL = "\033[0;91m"
    OKRED = "\033[0;91m"
    OKGREEN = "\033[0;92m"
    OKYELLOW = "\033[0;93m"
    OKBLUE = "\033[0;94m"
    OKMAGENTA = "\033[0;95m"
    OKCYAN = "\033[0;96m"
    ORANGE = "\033[38;5;208m"


def modify_printed_string(att, *args, sep=" "):
    text = sep.join(args)
    return f"{att}{text}{bcolors.ENDC}"


red = partial(modify_printed_string, bcolors.OKRED, sep=" ")
green = partial(modify_printed_string, bcolors.OKGREEN, sep="")
yellow = partial(modify_printed_string, bcolors.OKYELLOW, sep=" ")
blue = partial(modify_printed_string, bcolors.OKBLUE, sep=" ")
magenta = partial(modify_printed_string, bcolors.OKMAGENTA, sep=" ")
cyan = partial(modify_printed_string, bcolors.OKCYAN, sep=" ")
orange = partial(modify_printed_string, bcolors.ORANGE, sep=" ")
bold = partial(modify_printed_string, bcolors.BOLD, sep=" ")
warning = partial(modify_printed_string, bcolors.WARNING, sep=" ")


def prettydict(d, indent=4, color=blue):
    space = max([0] + [len(str(x)) for x in d]) + 2
    print("")
    for key, value in d.items():
        print(color(" " * indent + str(key)), end="")
        if isinstance(value, dict):
            # prettydict(value, indent=len(" " * (space)), color=color)
            prettydict(value, indent=indent + 4, color=color)
        else:
            print(color(" " * (indent + space - len(str(key))) + str(value)))


class ColorFormatter(logging.Formatter):
    __format = "%(levelname)-8s| %(module)s::%(message)s"

    __FORMATS = {
        logging.DEBUG: orange(__format),
        logging.INFO: cyan(__format),
        logging.WARNING: warning(__format),
        logging.ERROR: red(__format),
        logging.CRITICAL: red(bold(__format)),
    }

    def format(self, record):
        log_fmt = self.__FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Shamelessly stolen from blender
class bcolors:
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    HEADER    = '\033[0;95m'
    WARNING   = '\033[0;93m'
    FAIL      = '\033[0;91m'
    OKRED     = '\033[0;91m'
    OKGREEN   = '\033[0;92m'
    OKYELLOW  = '\033[0;93m'
    OKBLUE    = '\033[0;94m'
    OKMAGENTA = '\033[0;95m'
    OKCYAN    = '\033[0;96m'
    ORANGE    = '\033[38;5;208m'

def modify_printed_string(att, *args, sep=' '):
    text = sep.join(args)
    return f"{att}{text}{bcolors.ENDC}"
    # return "%s%s%s"%(att,text,bcolors.ENDC)

def red(*args, sep=' '):
    return modify_printed_string(bcolors.OKRED, *args, sep=sep)

def green(*args, sep=' '):
    return modify_printed_string(bcolors.OKGREEN, *args, sep=sep)

def yellow(*args, sep=' '):
    return modify_printed_string(bcolors.OKYELLOW, *args, sep=sep)

def blue(*args, sep=' '):
    return modify_printed_string(bcolors.OKBLUE, *args, sep=sep)

def magenta(*args, sep=' '):
    return modify_printed_string(bcolors.OKMAGENTA, *args, sep=sep)

def cyan(*args, sep=' '):
    return modify_printed_string(bcolors.OKCYAN, *args, sep=sep)

def orange(*args, sep=' '):
    return modify_printed_string(bcolors.ORANGE, *args, sep=sep)

def bold(*args, sep=' '):
    return modify_printed_string(bcolors.BOLD, *args, sep=sep)

def warning(*args, sep=' '):
    return modify_printed_string(bcolors.WARNING, *args, sep=sep)

def prettydict(d, indent=4, color=blue):
    space = max([0]+[len(str(x)) for x in d])+2
    print('')
    for key, value in d.items():
        print(color(" "*indent + str(key)),end='')
        if isinstance(value, dict):
            prettydict(value, indent=len(" "*(space)), color=color)
        else:
            print(color(" "*(space-len(key)) + str(value)))


if __name__ == "__main__":
    test_string = 'test'
    print(red(test_string))
    print(green(test_string))
    print(yellow(test_string))
    print(blue(test_string))
    print(magenta(test_string))
    print(cyan(test_string))
    print(orange(test_string))
    print(bold(test_string))

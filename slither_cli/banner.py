"""ASCII art banner and small graphical bits used on the menu / game-over screens."""

# "SLITHER" rendered in a chunky box-drawing block font.
BANNER = [
    "███████╗██╗     ██╗████████╗██╗  ██╗███████╗██████╗ ",
    "██╔════╝██║     ██║╚══██╔══╝██║  ██║██╔════╝██╔══██╗",
    "███████╗██║     ██║   ██║   ███████║█████╗  ██████╔╝",
    "╚════██║██║     ██║   ██║   ██╔══██║██╔══╝  ██╔══██╗",
    "███████║███████╗██║   ██║   ██║  ██║███████╗██║  ██║",
    "╚══════╝╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
]

# A compact fallback banner for narrow terminals.
BANNER_SMALL = [
    "  ___ _    _ _   _              ",
    " / __| |  | | | | |_  ___ _ _   ",
    " \\__ \\ |__| | |_| ' \\/ -_) '_|  ",
    " |___/____|_|\\__|_||_\\___|_|    ",
]

# A little snake mascot for flavor.
SNAKE_ART = "  ~~~≈≈≈●   "

BANNER_WIDTH = max(len(line) for line in BANNER)
BANNER_SMALL_WIDTH = max(len(line) for line in BANNER_SMALL)

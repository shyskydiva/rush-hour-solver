"""Colors, sizes, and fonts for the Pink Lane look (from the style guide)."""
from pathlib import Path

import pygame

# --- Palette ---
ASPHALT = (13, 10, 18)       # window background
PANEL = (22, 18, 30)         # stat boxes and panels
RAISED = (31, 26, 43)        # buttons and cards
LINE = (50, 42, 69)          # board frame and speed lines
TEXT = (244, 238, 255)
MUTED = (167, 157, 191)
HOT_PINK = (255, 61, 139)    # only the player car and main buttons are pink
CYAN = (61, 224, 224)        # anything the solver does
VIOLET = (139, 116, 232)
TEAL = (47, 199, 199)
STEEL = (91, 127, 184)
GRAPHITE = (74, 67, 89)
SILVER = (183, 178, 198)
INDIGO = (92, 84, 168)       # two extra cool tones so big levels don't repeat colors
SEA = (38, 128, 140)

# Extra shades used in the screen designs
FAINT = (126, 117, 150)      # footer text, locked cards
SOFT = (221, 213, 240)       # body text on dark panels
STRIPE = (20, 16, 28)        # the big slanted background stripe
BOARD = (17, 14, 24)         # inside of the board frame
CELL_COLOR = (26, 21, 36)    # one empty square
ROW = (27, 22, 38)           # one row in the moves list
PINK_INK = (42, 6, 20)       # text on pink buttons
CYAN_INK = (5, 36, 36)       # text on cyan buttons
DEEP_PINK = (90, 16, 48)     # shadow under the title logo
HEADLIGHT = (255, 248, 224)
TAILLIGHT = (255, 77, 109)

# Every car except X gets one of these cool tones, so the pink car always pops.
CAR_COLORS = [TEAL, VIOLET, STEEL, GRAPHITE, SILVER, INDIGO, SEA]

# --- Sizes ---
WIDTH, HEIGHT = 960, 640
CELL = 64                     # one square on the board
GAP = 6                       # space between squares
STEP = CELL + GAP             # distance from one square to the next (70)
BOARD_PAD = 14                # space between the board's frame and the first square
BOARD_SIZE = BOARD_PAD * 2 + STEP * 6 - GAP   # 442

# --- Fonts ---
FONT_DIR = Path(__file__).parent / "fonts"
FONT_FILES = {
    "display": "Bungee-Regular.ttf",       # logo and big titles only
    "bold": "ChakraPetch-Bold.ttf",        # everything else
    "semibold": "ChakraPetch-SemiBold.ttf",
    "regular": "ChakraPetch-Regular.ttf",
}

_loaded_fonts = {}


def font(style, size):
    """Return a font like font("bold", 18). Fonts are loaded once and reused.

    If a font file is missing, a system font is used instead so the game
    still runs.
    """
    key = (style, size)
    if key not in _loaded_fonts:
        path = FONT_DIR / FONT_FILES[style]
        if path.exists():
            _loaded_fonts[key] = pygame.font.Font(path, size)
        else:
            _loaded_fonts[key] = pygame.font.SysFont("arial", size, bold=style != "regular")
    return _loaded_fonts[key]


def forget_fonts():
    """Drop the loaded fonts. Call this when Pygame shuts down, since they stop working then."""
    _loaded_fonts.clear()

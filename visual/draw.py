"""Small drawing helpers shared by every screen. Everything is rects and polygons."""
import math

import pygame

from visual import theme


def mix(color, other, amount):
    """Blend two colors. amount=0 gives `color`, amount=1 gives `other`."""
    return tuple(round(a + (b - a) * amount) for a, b in zip(color, other))


def lighter(color, amount=0.15):
    """A slightly brighter version of a color, for hover effects."""
    return mix(color, (255, 255, 255), amount)


# --- Shapes ---

def cut_corner_points(rect, cut):
    """The 6 corners of a box with its top-left and bottom-right corners clipped off."""
    x, y, w, h = rect
    return [(x + cut, y), (x + w, y), (x + w, y + h - cut),
            (x + w - cut, y + h), (x, y + h), (x, y + cut)]


def cut_corner(surface, color, rect, cut):
    """Draw a filled cut-corner box (used for buttons, panels and the board frame)."""
    if cut == 0:
        pygame.draw.rect(surface, color, rect)
    else:
        pygame.draw.polygon(surface, color, cut_corner_points(rect, cut))


def slanted_band(surface, color, left, width, top, height, offset=0):
    """Draw a tall stripe that leans like "/" (the skewed stripes in the design).

    `left` is where the stripe sits halfway down. It tilts 18 degrees.
    """
    lean = math.tan(math.radians(18))
    middle = top + height / 2
    x = left + offset
    top_shift = lean * (middle - top)
    bottom_shift = lean * (middle - top - height)
    pygame.draw.polygon(surface, color, [
        (x + top_shift, top), (x + width + top_shift, top),
        (x + width + bottom_shift, top + height), (x + bottom_shift, top + height),
    ])


def dashed_rect(surface, color, rect, width=2, dash=7, gap=5):
    """Draw a dashed outline around a rect."""
    x, y, w, h = rect
    edges = [((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)),
             ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))]
    for (x1, y1), (x2, y2) in edges:
        length = math.hypot(x2 - x1, y2 - y1)
        pos = 0
        while pos < length:
            end = min(pos + dash, length)
            start_point = (x1 + (x2 - x1) * pos / length, y1 + (y2 - y1) * pos / length)
            end_point = (x1 + (x2 - x1) * end / length, y1 + (y2 - y1) * end / length)
            pygame.draw.line(surface, color, start_point, end_point, width)
            pos = pos + dash + gap


def diamond(surface, color, center, size):
    """A square turned 45 degrees (the rating gems). `size` is the square's side."""
    cx, cy = center
    r = size * 0.707  # half the diagonal
    pygame.draw.polygon(surface, color, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)])


def play_arrows(surface, color, x, y, size, count=3):
    """The ▶▶▶ mark: `count` small triangles in a row."""
    for i in range(count):
        left = x + i * size * 0.75
        pygame.draw.polygon(surface, color, [(left, y), (left + size * 0.75, y + size / 2), (left, y + size)])


# --- Text ---

def render_text(words, font, color, spacing=0):
    """Turn text into an image. `spacing` adds extra pixels between letters."""
    if spacing == 0:
        return font.render(words, True, color)

    letters = [font.render(letter, True, color) for letter in words]
    width = sum(letter.get_width() for letter in letters) + spacing * (len(letters) - 1)
    image = pygame.Surface((max(width, 1), font.get_height()), pygame.SRCALPHA)
    x = 0
    for letter in letters:
        image.blit(letter, (x, 0))
        x = x + letter.get_width() + spacing
    return image


def text(surface, words, font, color, pos, spacing=0, anchor="topleft", shadow=None, shadow_offset=0):
    """Draw text and return the rect it covers.

    `anchor` says which point of the text sits at `pos`, like "center" or "topright".
    `shadow` draws a hard copy behind it, `shadow_offset` pixels down and right.
    """
    image = render_text(words, font, color, spacing)
    rect = image.get_rect(**{anchor: pos})
    if shadow is not None:
        surface.blit(render_text(words, font, shadow, spacing), rect.move(shadow_offset, shadow_offset))
    surface.blit(image, rect)
    return rect


def wrap(words, font, max_width):
    """Split a sentence into lines that each fit within max_width pixels."""
    lines = []
    line = ""
    for word in words.split():
        attempt = word if line == "" else line + " " + word
        if font.size(attempt)[0] <= max_width:
            line = attempt
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


# --- The car ---

def draw_car(surface, rect, color, horizontal, hero=False):
    """Draw a car seen from above, filling `rect`.

    The parts are drawn back to front: body, racing stripes (hero car only),
    windows, headlights, taillights. Horizontal cars face right; vertical cars
    face up.
    """
    x, y, w, h = rect
    length = w if horizontal else h      # along the car, back to front
    thick = h if horizontal else w       # across the car
    k = thick / theme.CELL               # parts are sized for a 64px-wide car
    glass = mix(color, theme.ASPHALT, 0.62)  # a dark window, 62% see-through

    def part(along, across, along_size, across_size, part_color, radius=2):
        """Draw one part. `along` is measured from the back of the car."""
        if horizontal:
            box = (x + along, y + across, along_size, across_size)
        else:
            # Front faces up, so the back of the car is at the bottom.
            box = (x + across, y + length - along - along_size, across_size, along_size)
        pygame.draw.rect(surface, part_color, pygame.Rect([round(n) for n in box]),
                         border_radius=round(radius * k))

    pygame.draw.rect(surface, color, pygame.Rect([round(n) for n in rect]), border_radius=round(14 * k))
    if hero:
        part(4 * k, thick / 2 - 9 * k, length - 8 * k, 4 * k, theme.TEXT, 1)
        part(4 * k, thick / 2 + 5 * k, length - 8 * k, 4 * k, theme.TEXT, 1)
    part(length * 0.14, 9 * k, length * 0.12, thick - 18 * k, glass, 6)   # rear window
    part(length * 0.58, 8 * k, length * 0.17, thick - 16 * k, glass, 8)   # windshield
    part(length - 7 * k, 8 * k, 4 * k, 12 * k, theme.HEADLIGHT)
    part(length - 7 * k, thick - 20 * k, 4 * k, 12 * k, theme.HEADLIGHT)
    part(3 * k, 8 * k, 3 * k, 12 * k, theme.TAILLIGHT)
    part(3 * k, thick - 20 * k, 3 * k, 12 * k, theme.TAILLIGHT)


# --- Buttons ---

BUTTON_STYLES = {
    # style name: (background, text color, font style)
    "pink": (theme.HOT_PINK, theme.PINK_INK, "bold"),
    "cyan": (theme.CYAN, theme.CYAN_INK, "bold"),
    "raised": (theme.RAISED, theme.TEXT, "semibold"),
    "chip": (theme.RAISED, theme.CYAN, "bold"),
}


class Button:
    """A clickable cut-corner button."""

    def __init__(self, rect, label, on_click, style="raised", size=16, cut=10,
                 number=None, accent=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.style = style
        self.size = size
        self.cut = cut
        self.number = number    # small "01" in front of the label (title menu)
        self.accent = accent    # color of a thin bar down the left edge

    def draw(self, surface):
        background, ink, weight = BUTTON_STYLES[self.style]
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            background = lighter(background)
        cut_corner(surface, background, self.rect, self.cut)
        if self.accent is not None:
            pygame.draw.rect(surface, self.accent, (self.rect.x, self.rect.y, 3, self.rect.h))

        label_font = theme.font(weight, self.size)
        if self.number is None:
            text(surface, self.label, label_font, ink, self.rect.center, spacing=3, anchor="center")
        else:
            # Left-aligned, with a small number in front: "01  PLAY"
            number_color = theme.CYAN if self.accent is not None else ink
            number_rect = text(surface, self.number, theme.font("bold", 13), number_color,
                               (self.rect.x + 20, self.rect.centery), anchor="midleft")
            text(surface, self.label, label_font, ink, (number_rect.right + 16, self.rect.centery),
                 spacing=3, anchor="midleft")

    def handle(self, event):
        """Run on_click if this event is a left click on the button. Returns True if it was."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.on_click()
            return True
        return False

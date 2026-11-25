"""The level select screen: one card per level, locked until you clear the one before."""
import pygame

from visual import draw, theme

CARD_TOP = 140
CARD_WIDTH = 272
CARD_HEIGHT = 330


def card_rect(index):
    return pygame.Rect(48 + index * (CARD_WIDTH + 24), CARD_TOP, CARD_WIDTH, CARD_HEIGHT)


def draw_lock(surface, color, x, y):
    """A small padlock icon, 22px tall."""
    pygame.draw.rect(surface, color, (x + 4, y + 10, 14, 11), 2)
    pygame.draw.arc(surface, color, (x + 7, y + 2, 8, 14), 0, 3.1416, 2)


class LevelsScreen:
    def __init__(self, app):
        self.app = app
        self.menu_button = draw.Button((theme.WIDTH - 48 - 130, 64, 130, 46), "MENU",
                                       app.show_title, size=15)

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.show_title()
            return
        if self.menu_button.handle(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index in range(len(self.app.levels)):
                if card_rect(index).collidepoint(event.pos) and self.app.is_unlocked(index):
                    self.app.play(index)
                    return

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(theme.ASPHALT)
        draw.slanted_band(surface, theme.STRIPE, theme.WIDTH - 240, 300, -40, 720)
        draw.slanted_band(surface, theme.HOT_PINK, theme.WIDTH - 14, 8, -40, 720)

        draw.text(surface, "PINK LANE", theme.font("bold", 14), theme.CYAN, (48, 30), spacing=4)
        draw.text(surface, "SELECT LEVEL", theme.font("display", 56), theme.TEXT, (48, 50),
                  shadow=theme.HOT_PINK, shadow_offset=4)
        self.menu_button.draw(surface)

        for index in range(len(self.app.levels)):
            self.draw_card(surface, index)

        footer = theme.font("semibold", 13)
        cleared = len(self.app.cleared)
        draw.text(surface, "CLEAR A LEVEL TO UNLOCK THE NEXT", footer, theme.FAINT, (48, 500), spacing=3)
        draw.text(surface, f"{cleared} / {len(self.app.levels)} CLEARED", footer, theme.FAINT,
                  (theme.WIDTH - 48, 500), spacing=3, anchor="topright")

    def draw_card(self, surface, index):
        rect = card_rect(index)
        name = self.app.levels[index][0].upper()
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        left = rect.x + 24
        bottom = rect.bottom - 24

        if index in self.app.cleared:
            # Cleared: dark card with a cyan bottom edge and the rating gems.
            result = self.app.cleared[index]
            pygame.draw.rect(surface, draw.lighter(theme.RAISED, 0.06) if hovered else theme.RAISED, rect)
            pygame.draw.rect(surface, theme.CYAN, (rect.x, rect.bottom - 4, rect.w, 4))
            label_color, number_color = theme.CYAN, theme.TEXT
            for gem in range(result["gems"]):
                draw.diamond(surface, theme.HOT_PINK, (left + 12 + gem * 26, bottom - 44), 16)
            draw.text(surface, f"CLEARED · {result['moves']} MOVES", theme.font("bold", 14), theme.CYAN,
                      (left, bottom), spacing=2, anchor="bottomleft")

        elif self.app.is_unlocked(index):
            # Next to play: the loud pink card.
            draw.cut_corner(surface, draw.lighter(theme.HOT_PINK, 0.1) if hovered else theme.HOT_PINK, rect, 16)
            label_color, number_color = theme.PINK_INK, theme.PINK_INK
            draw.text(surface, f"BEST · {self.app.best_moves(index)} MOVES", theme.font("semibold", 14),
                      theme.PINK_INK, (left, bottom - 32), spacing=2, anchor="bottomleft")
            play_rect = draw.text(surface, "PLAY", theme.font("bold", 20), theme.PINK_INK,
                                  (left, bottom), spacing=3, anchor="bottomleft")
            draw.play_arrows(surface, theme.PINK_INK, play_rect.right + 10, play_rect.centery - 7, 14, count=1)

        else:
            # Locked: flat and faded, with a hint about what unlocks it.
            pygame.draw.rect(surface, theme.PANEL, rect)
            label_color, number_color = theme.VIOLET, theme.FAINT
            previous = self.app.levels[index - 1][0].upper()
            draw_lock(surface, theme.FAINT, left, bottom - 22)
            draw.text(surface, f"CLEAR {previous} TO UNLOCK", theme.font("bold", 13), theme.FAINT,
                      (left + 30, bottom - 11), spacing=1, anchor="midleft")

        draw.text(surface, name, theme.font("bold", 15), label_color, (left, rect.y + 24), spacing=3)
        draw.text(surface, f"{index + 1:02}", theme.font("bold", 72), number_color, (left, rect.y + 40))

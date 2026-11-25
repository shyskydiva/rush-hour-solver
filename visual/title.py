"""The title screen: logo, PLAY and LEVELS."""
import math

import pygame

from visual import draw, theme


class TitleScreen:
    def __init__(self, app):
        self.app = app
        self.clock = 0  # seconds since the screen opened, for the stripe drift
        self.buttons = [
            draw.Button((56, 362, 330, 54), "PLAY", app.play_next, style="pink",
                        size=18, cut=12, number="01"),
            draw.Button((56, 426, 330, 50), "LEVELS", app.show_levels, style="raised",
                        size=17, cut=0, number="02", accent=theme.CYAN),
        ]

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.app.play_next()
            return
        for button in self.buttons:
            if button.handle(event):
                return

    def update(self, dt):
        self.clock = self.clock + dt

    def draw(self, surface):
        surface.fill(theme.ASPHALT)

        # Slanted stripes that drift slowly side to side so the menu never feels static.
        drift = math.sin(self.clock * 0.6) * 14
        draw.slanted_band(surface, theme.STRIPE, 470, 260, -60, 780, drift)
        draw.slanted_band(surface, theme.HOT_PINK, 760, 14, -60, 780, drift)
        draw.slanted_band(surface, theme.CYAN, 800, 4, -60, 780, drift)

        # Logo block
        draw.text(surface, "RUSH HOUR // SOLVER", theme.font("bold", 14), theme.CYAN, (56, 64), spacing=4)
        logo = theme.font("display", 104)
        draw.text(surface, "PINK", logo, theme.HOT_PINK, (56, 84), shadow=theme.DEEP_PINK, shadow_offset=6)
        draw.text(surface, "LANE", logo, theme.HOT_PINK, (56, 183), shadow=theme.DEEP_PINK, shadow_offset=6)
        draw.text(surface, "Clear the jam. Take the exit. Make it look easy.",
                  theme.font("regular", 17), theme.MUTED, (56, 314))

        for button in self.buttons:
            button.draw(surface)

        # Speed lines and the big pink car
        pygame.draw.rect(surface, theme.LINE, (440, 300, 120, 4))
        pygame.draw.rect(surface, theme.HOT_PINK, (470, 330, 80, 4))
        pygame.draw.rect(surface, theme.LINE, (430, 360, 110, 4))
        draw.draw_car(surface, (575, 274, 280, 112), theme.HOT_PINK, horizontal=True, hero=True)

        footer = theme.font("semibold", 13)
        draw.text(surface, "PRESS ENTER TO START", footer, theme.FAINT, (56, theme.HEIGHT - 34), spacing=3, anchor="bottomleft")
        draw.text(surface, "6×6 GRID · BFS SOLVER", footer, theme.FAINT, (theme.WIDTH - 56, theme.HEIGHT - 34),
                  spacing=3, anchor="bottomright")

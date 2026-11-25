"""Start Pink Lane. pygbag (the web version) also starts the game from this file.

The text version is text_game.py.
"""
import asyncio

# pygbag decides which libraries the web version needs by reading the imports in
# this file only, so Pygame has to be imported here even though visual/ uses it.
import pygame  # noqa: F401

from visual.app import App

if __name__ == "__main__":
    asyncio.run(App().run())

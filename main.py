"""Start Pink Lane. pygbag (the web version) also starts the game from this file.

The text version is text_game.py.
"""
import asyncio

from visual.app import App

if __name__ == "__main__":
    asyncio.run(App().run())

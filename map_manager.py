
import pygame
import os
from settings import TILE_SIZE

class MapManager:
    def __init__(self, folder="maps"):
        self.maps = {}
        self.current = None
        self.load(folder)

    def load(self, folder):
        for f in os.listdir(folder):
            if f.endswith(".py") and not f.startswith("__"):
                name = f[:-3]
                m = __import__(f"{folder}.{name}", fromlist=["MAP"])
                if hasattr(m, "MAP"):
                    self.maps[name] = m.MAP

    def use(self, name):
        self.current = self.maps.get(name)

    def draw(self, screen, camera):
        if not self.current:
            return
        for y,row in enumerate(self.current):
            for x,t in enumerate(row):
                if t:
                    pygame.draw.rect(
                        screen, (80,80,80),
                        (x*TILE_SIZE-camera.offset[0],
                         y*TILE_SIZE-camera.offset[1],
                         TILE_SIZE, TILE_SIZE)
                    )

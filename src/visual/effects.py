from src.underia import game
from src.resources import position
import pygame as pg

class Effect:
    def update(self, window) -> bool:
        return False

def pointed_curve(colour: tuple[int, int, int], pts: list[tuple[int, int]], width: int = 10, salpha: int = 255):
    displayer = game.get_game().displayer
    for i in range(len(pts) - 1):
        pg.draw.line(displayer.canvas, (colour[0], colour[1], colour[2], i * salpha // (len(pts) - 1)),
                     position.displayed_position(pts[i]), position.displayed_position(pts[i + 1]), width=width)

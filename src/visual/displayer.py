import pygame as pg
import copy
from src.visual import effects
from src.underia import game, weapons
from src.resources import position
from src import pygame_lights

class Displayer:
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900

    def __init__(self):
        self.canvas = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA)
        self.canvas.fill((255, 255, 255, 255))
        self.alpha_masks: list[tuple[int, int, int, int]] = []
        self.shake_x, self.shake_y = 0, 0
        self.effects: list[effects.Effect] = []
        self.font = pg.font.SysFont('Arial', 28)
        self.font_s = pg.font.SysFont('Arial', 18)
        self.night_darkness_color = (127, 127, 0)

    def update(self):
        window = pg.display.get_surface()
        for effect in self.effects:
            if not effect.update(self.canvas):
                self.effects.remove(effect)
        scale = min(window.get_width() / self.SCREEN_WIDTH, window.get_height() / self.SCREEN_HEIGHT)
        for alpha_mask in self.alpha_masks:
            self.canvas.fill(alpha_mask)
        self.alpha_masks.clear()
        blit_surface = pg.transform.scale(copy.copy(self.canvas), (int(self.SCREEN_WIDTH * scale), int(self.SCREEN_HEIGHT * scale)))
        rect = blit_surface.get_rect(center=window.get_rect().center)
        rect.x += self.shake_x
        rect.y += self.shake_y
        self.shake_x, self.shake_y = 0, 0
        window.blit(blit_surface, rect)
        self.canvas.fill((255, 255, 255, 255))

    def night_darkness(self):
        filter = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA)
        filter.fill(self.night_darkness_color)
        if game.get_game().day_time > 0.5 or game.get_game().day_time < 0.2:
            lv = game.get_game().player.get_light_level()
            px, py = position.displayed_position(game.get_game().player.obj.pos)
            if lv:
                filter.blit(pygame_lights.global_light(filter.get_size(), 50 + game.get_game().player.get_night_vision()), (0, 0))
                player = game.get_game().player
                light = pygame_lights.LIGHT(lv * 150, pygame_lights.pixel_shader(lv * 150, (255, 127, 0) if player.weapons[player.sel_weapon] is not weapons.WEAPONS['nights_edge'] else (127, 0, 127), 1, False))
                light.main([], filter, px, py)
        self.canvas.blit(filter, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        pg.display.update()

    def effect(self, effect_list):
        self.effects.extend(effect_list)

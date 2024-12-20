import copy
import os
import random

import pygame

from src import resources, visual, constants
from src.underia import player, entity, projectiles, weapons
import perlin_noise
import datetime

MUSICS = {
    'lantern': ['snowland1', 'snowland0', 'heaven1', 'heaven0', 'forest0', 'rainforest0', 'desert0'],
    'wild_east': ['desert1', 'desert0'],
    'waterfall': ['forest0', 'rainforest0', 'desert0'],
    'fields': ['forest1', 'rainforest1', 'snowland1', 'forest0'],
    'empty': ['hell0', 'hell1', 'forest1', 'rainforest1'],
    'null': [],
    'rude_buster': ['battle'],
    'worlds_revolving': ['battle'],
}

class Game:
    ITEM_SPLIT_MIN = 1
    ITEM_SPLIT_MAX = 2
    TIME_SPEED = .00004
    CHUNK_SIZE = 100

    def __init__(self):
        self.displayer = visual.Displayer()
        self.graphics = resources.Graphics()
        self.events = []
        self.player = player.Player()
        self.pressed_keys = []
        self.pressed_mouse = []
        self.entities: list[entity.Entities.Entity] = []
        self.projectiles: list[projectiles.Projectiles.Projectile] = []
        self.clock = resources.Clock()
        self.damage_texts: list[tuple[int, int, tuple[int, int]]] = []
        self.save = ''
        self.day_time = 0.3
        self.drop_items = []
        self.map: pygame.PixelArray | None = None
        self.chunk_pos = (0, 0)
        self.last_biome = ('forest', 0)
        self.stage = 0
        self.musics = {}
        self.channel = pygame.mixer.Channel(0)
        self.prepared_music = None
        self.cur_music = 'null'
        self.MUSICS = MUSICS
        self.noise = perlin_noise.PerlinNoise(1.2, datetime.datetime.now().microsecond)
        self.map_ns = {}
        self.m_min = 0
        self.m_max = 0

    def get_night_color(self, time_days: float):
        if len([1 for e in self.entities if type(e) is entity.Entities.AbyssEye]):
            return 255, 0, 0
        if 0.2 < time_days <= 0.3:
            r = int(255 * (time_days - 0.2) / 0.1)
            g = int(255 * (time_days - 0.2) / 0.1)
            b = int(255 * (time_days - 0.2) / 0.1)
        elif 0.3 < time_days <= 0.7:
            r = 255
            g = 255
            b = 255
        elif 0.7 < time_days <= 0.75:
            r = 255
            g = 255 - int(128 * (time_days - 0.7) / 0.05)
            b = 255 - int(255 * (time_days - 0.7) / 0.05)
        elif 0.75 < time_days <= 0.8:
            r = 255 - int(255 * (time_days - 0.75) / 0.05)
            g = 127 - int(127 * (time_days - 0.75) / 0.05)
            b = 0
        else:
            r = 0
            g = 0
            b = 0
        return r, g, b

    def load_graphics(self, directory, index=''):
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)):
                if file.endswith(".png"):
                    print('Loading', os.path.join(directory, file))
                    self.graphics.load_graphics(index + file.removesuffix(".png"), os.path.join(directory, file))
            else:
                self.load_graphics(os.path.join(directory, file), index + file + '_')

    def setup(self):
        self.map_ns = {}
        self.m_min = 0
        self.m_max = 0
        self.noise = perlin_noise.PerlinNoise(1.2, datetime.datetime.now().microsecond)
        for x in range(-200, 200):
            for y in range(-200, 200):
                self.get_biome((x, y))
        self.musics = {}
        self.cur_music = 'null'
        self.prepared_music = None
        self.MUSICS = MUSICS
        self.channel = pygame.mixer.Channel(0)
        self.load_graphics(resources.get_path('assets/graphics'))
        weapons.set_weapons()
        self.map = pygame.PixelArray(self.graphics['background_map'])
        for m in os.listdir(resources.get_path('assets/musics')):
            if m.endswith('.ogg'):
                self.musics[m.removesuffix('.ogg')] = pygame.mixer.Sound(resources.get_path('assets/musics/' + m))


    def on_update(self):
        pass

    def update_function(self, func):
        setattr(self, 'on_update', func)

    def get_biome(self, pos=None):
        if len([1 for e in self.entities if type(e) is entity.Entities.AbyssEye]):
            return 'heaven'
        if len([1 for e in self.entities if type(e) is entity.Entities.Jevil]):
            return 'inner'
        if pos is None:
            pos = self.chunk_pos
        if pos[0] ** 2 + pos[1] ** 2 < 1000:
            return 'forest'
        if pos in self.map_ns.keys():
            return self.map_ns[pos]
        lvs = ['hell', 'desert', 'forest', 'rainforest', 'snowland', 'heaven']
        val = self.noise([pos[0] / 100.0, pos[1] / 100.0])
        if val < self.m_min or val > self.m_max:
            self.map_ns = {}
        self.m_min = min(self.m_min, val)
        self.m_max = max(self.m_max, val)
        val = (val - self.m_min) / (self.m_max - self.m_min + 0.01)
        self.map_ns[pos] = lvs[int(val * (len(lvs)))]
        return self.map_ns[pos]
        """
        if pos is None:
            x, y = self.chunk_pos
        else:
            x, y = pos
        try:
            color = self.map[x, y] % 256 ** 3
        except IndexError:
            return 'forest'
        s = pygame.Surface((1, 1))
        if color == s.map_rgb((255, 127, 0, 0)):
            return 'desert'
        elif color == s.map_rgb((0, 255, 0, 0)):
            return 'forest'
        elif color == s.map_rgb((255, 41, 0, 0)):
            return 'hell'
        elif color == s.map_rgb((255, 255, 255, 0)):
            return 'snowland'
        elif color == s.map_rgb((0, 127, 0, 0)):
            return 'rainforest'
        elif color == s.map_rgb((127, 127, 127, 0)):
            return 'heaven'
        else:
            return 'forest'
        """

    def update(self):
        if (self.prepared_music is None and self.channel.get_busy() == 0) or \
                (self.cur_music is not None and (self.get_biome() + str(int(0.3 < self.day_time < 0.7))) not in
                 self.MUSICS[self.cur_music] and not len([1 for e in self.entities if e.IS_MENACE])) \
                or (self.cur_music is not None and len([1 for e in self.entities if e.IS_MENACE]) and
                    'battle' not in self.MUSICS[self.cur_music]):
            if len([1 for e in self.entities if e.IS_MENACE]):
                self.cur_music = None
                self.channel.stop()
                if len([1 for e in self.entities if type(e) is entity.Entities.Jevil]):
                    self.prepared_music = 'worlds_revolving'
                else:
                    self.prepared_music = 'rude_buster'
            else:
                self.cur_music = None
                self.channel.fadeout(8000)
                self.prepared_music = random.choice([k for k, v in self.MUSICS.items() \
                                                     if (self.get_biome() + str(int(0.3 < self.day_time < 0.7))) in v])
        if self.cur_music is None and self.prepared_music is not None and self.channel.get_busy() == 0:
            self.cur_music = self.prepared_music
            self.channel.play(self.musics[self.cur_music])
            self.prepared_music = None
        self.chunk_pos = (
        int(self.player.obj.pos[0]) // self.CHUNK_SIZE + 120, int(self.player.obj.pos[1]) // self.CHUNK_SIZE + 120)
        self.day_time += self.TIME_SPEED
        self.day_time %= 1.0
        self.on_update()
        self.clock.update()
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                raise resources.Interrupt()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise resources.Interrupt()
                else:
                    self.pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in self.pressed_keys:
                    self.pressed_keys.remove(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed_mouse.append(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in self.pressed_mouse:
                    self.pressed_mouse.remove(event.button)
        bg_size = int(120 / self.player.get_screen_scale())
        bg_ax = int(self.player.ax / self.player.get_screen_scale()) % bg_size
        bg_ay = int(self.player.ay / self.player.get_screen_scale()) % bg_size
        g = self.graphics.get_graphics('background_' + self.get_biome())
        lg, _ = self.last_biome
        lg = self.graphics.get_graphics('background_' + lg)
        if lg != g:
            self.last_biome = (self.last_biome[0], self.last_biome[1] + 1)
            if self.last_biome[1] >= 20:
                self.last_biome = (self.get_biome(), 0)
            lg = copy.copy(lg)
            lg.set_alpha(255 - 25 * self.last_biome[1])
        g = pygame.transform.scale(g, (bg_size, bg_size))
        if lg != g:
            lg = pygame.transform.scale(lg, (bg_size, bg_size))
        for i in range(-bg_size, self.displayer.SCREEN_WIDTH + bg_size, bg_size):
            for j in range(-bg_size, self.displayer.SCREEN_HEIGHT + bg_size, bg_size):
                if constants.DISPLAY_STYLE:
                    self.displayer.canvas.blit(g, (i - bg_ax, j - bg_ay))
                    if self.get_biome() != self.last_biome[0]:
                        self.displayer.canvas.blit(lg, (i - bg_ax, j - bg_ay))
                else:
                    cx, cy = resources.real_position((i - bg_ax + bg_size // 2, j - bg_ay + bg_size // 2))
                    cx = int(cx // self.CHUNK_SIZE) + 120
                    cy = int(cy // self.CHUNK_SIZE) + 120
                    bo = self.get_biome(pos=(cx, cy))
                    g.set_alpha(155 + self.last_biome[1] * 5 if self.last_biome[1] else 255)
                    ap = 255 - self.last_biome[1] * 5 if self.last_biome[1] else 155
                    lg = copy.copy(self.graphics.get_graphics('background_' + bo))
                    if bo != self.get_biome():
                        self.displayer.canvas.blit(g, (i - bg_ax, j - bg_ay))
                        lg.set_alpha(ap)
                    else:
                        lgg = copy.copy(self.graphics.get_graphics('background_' + self.last_biome[0]))
                        lgg = pygame.transform.scale(lgg, (bg_size, bg_size))
                        self.displayer.canvas.blit(lgg, (i - bg_ax, j - bg_ay))
                        lg.set_alpha(355 - ap)
                    lg = pygame.transform.scale(lg, (bg_size, bg_size))
                    self.displayer.canvas.blit(lg, (i - bg_ax, j - bg_ay))




        self.player.update()
        for monster in self.entities:
            monster.update()
            if monster.hp_sys.hp <= 0:
                self.entities.remove(monster)
                loots = monster.LOOT_TABLE()
                for item, amount in loots:
                    k = random.randint(self.ITEM_SPLIT_MIN, min(self.ITEM_SPLIT_MAX, amount))
                    for i in range(k):
                        self.drop_items.append(entity.Entities.DropItem((monster.obj.pos[0] + random.randint(-10, 10),
                                                                         monster.obj.pos[1] + random.randint(-10, 10)),
                                                                        item, amount // k + (i < amount % k)))
            for monster2 in self.entities:
                monster.obj.object_gravitational(monster2.obj)
                monster.obj.object_collision(monster2.obj,
                                             (monster2.img.get_width() + monster2.img.get_height()) // 4 + (
                                                         monster.img.get_width() + monster.img.get_height()) // 4)
        for drop_item in self.drop_items:
            drop_item.update()
            if drop_item.hp_sys.hp <= 0:
                self.drop_items.remove(drop_item)
        for proj in self.projectiles:
            proj.update()
            if proj.dead:
                self.projectiles.remove(proj)
        self.damage_texts = [(dmg, tick + 1, pos) for dmg, tick, pos in self.damage_texts if tick < 80]
        for dmg, tick, pos in self.damage_texts:
            f = self.displayer.font.render(str(dmg), True, (255, 0, 0))
            fr = f.get_rect(center=resources.displayed_position((pos[0], pos[1] + (80 - tick) ** 2 // 100)))
            self.displayer.canvas.blit(f, fr)
        self.displayer.night_darkness_color = self.get_night_color(self.day_time % 1.0)
        self.displayer.night_darkness()
        self.player.ui()
        menaces = [entity for entity in self.entities if entity.IS_MENACE]
        y = self.displayer.SCREEN_HEIGHT - 80
        x = self.displayer.SCREEN_WIDTH // 2
        for menace in menaces:
            pygame.draw.rect(self.displayer.canvas, (255, 0, 0), (x - 400, y - 30, 800, 60))
            pygame.draw.rect(self.displayer.canvas, (255, 127, 0),
                             (x - 400, y - 30, 800 * menace.hp_sys.displayed_hp / menace.hp_sys.max_hp, 60))
            pygame.draw.rect(self.displayer.canvas, (0, 255, 0),
                             (x - 400, y - 30, 800 * menace.hp_sys.hp / menace.hp_sys.max_hp, 60))
            pygame.draw.rect(self.displayer.canvas, (255, 255, 0), (x - 400, y - 30, 800, 60), width=5)
            f = self.displayer.font.render(menace.NAME + f"({int(menace.hp_sys.hp)}/{int(menace.hp_sys.max_hp)})", True,
                                           (0, 0, 0))
            fr = f.get_rect(center=(x, y))
            self.displayer.canvas.blit(f, fr)
            y -= 80
        self.displayer.update()
        return True

    def get_anchor(self):
        return self.player.obj.pos[0], self.player.obj.pos[1]
        # if not self.displayer.canvas.get_rect().collidepoint((self.player.obj.pos[0] - (self.entities[0].obj.pos[0] + self.player.obj.pos[0]) // 2 + self.displayer.SCREEN_WIDTH // 2, self.player.obj.pos[1] - (self.entities[0].obj.pos[1] + self.player.obj.pos[1]) // 2 + self.displayer.SCREEN_HEIGHT // 2)):
        # return self.player.obj.pos
        # return (self.entities[0].obj.pos[0] + self.player.obj.pos[0]) // 2, (self.entities[0].obj.pos[1] + self.player.obj.pos[1]) // 2

    def get_keys(self):
        return [event.key for event in self.events if event.type == pygame.KEYDOWN]

    def get_pressed_keys(self):
        return self.pressed_keys

    def get_mouse_press(self):
        return [event.button for event in self.events if event.type == pygame.MOUSEBUTTONDOWN]

    def get_pressed_mouse(self):
        return self.pressed_mouse

    def run(self):
        while self.update():
            pass


GAME: Game | None = None


def write_game(game: Game):
    global GAME
    GAME = game


def get_game() -> Game:
    global GAME
    if GAME is None:
        raise ValueError("Game not initialized")
    return GAME

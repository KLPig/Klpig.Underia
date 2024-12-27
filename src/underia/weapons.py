import math
import random

import pygame as pg

from src import constants
from src.physics import vector
from src.resources import position
from src.underia import game, projectiles, inventory, entity
from src.values import damages as dmg
from src.values import effects
from src.visual import effects as eff


class Weapon:
    def __init__(self, name, damages: dict[int, float], kb: float, img_index: str, speed: int, at_time: int,
                 auto_fire: bool = False):
        self.name = name
        self.damages = damages
        self.img_index = img_index
        self.img = pg.Surface((10, 10))
        self.d_img = pg.Surface((10, 10))
        self.timer = 0
        self.cool = 0
        self.knock_back = kb
        self.cd = speed
        self.at_time = at_time
        self.rot = 0
        self.x = 0
        self.y = 0
        self.display = False
        self.auto_fire = auto_fire
        self.key = 1
        self.keys = None
        self.combo = 0

    def re_init(self):
        pass

    def attack(self):
        self.timer = self.at_time + 1
        self.on_start_attack()

    def on_start_attack(self):
        pass

    def on_attack(self):
        self.display = True

    def forward(self, step: int):
        dx, dy = vector.rotation_coordinate(self.rot)
        self.x += dx * step
        self.y += dy * step

    def rotate(self, angle: int):
        self.set_rotation((self.rot + angle) % 360)

    def set_rotation(self, angle: int):
        self.img = game.get_game().graphics[self.img_index]
        self.d_img = pg.transform.rotate(pg.transform.scale_by(self.img, 1 / game.get_game().player.get_screen_scale()), 90 - angle)
        self.rot = angle

    def face_to(self, x: int, y: int):
        dx, dy = x - self.x, y - self.y
        self.set_rotation(vector.coordinate_rotation(dx, dy))

    def on_end_attack(self):
        self.display = False

    def on_idle(self):
        pass

    def update(self):
        if self.display:
            imr = self.d_img.get_rect(center=position.displayed_position(
                (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1])))
            game.get_game().displayer.canvas.blit(self.d_img, imr)
        if self.timer > 1:
            self.on_attack()
            self.combo += 1
            self.timer -= 1
            self.cool = 1
        elif self.timer == 1:
            self.on_end_attack()
            self.timer = 0
            self.cool = self.cd
            self.on_idle()
        else:
            self.on_idle()
        if not self.timer:
            if self.cool:
                self.cool -= 1
            else:
                if self.keys is None:
                    b = self.key in game.get_game().get_mouse_press() or (
                                self.auto_fire and self.key in game.get_game().get_pressed_mouse())
                else:
                    b = len([1 for k in self.keys if k in game.get_game().get_keys()]) or \
                        (self.auto_fire and len([1 for k in self.keys if k in game.get_game().get_pressed_keys()]))
                if b:
                    self.attack()
                else:
                    self.combo = -1


class SweepWeapon(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.rot_speed = rot_speed
        self.st_pos = st_pos
        self.double_sided = double_sided

    def on_start_attack(self):
        r = random.choice([-1, 1])
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r

    def on_attack(self):
        self.rotate(self.rot_speed)
        super().on_attack()
        self.damage()
        self.rotate(int(-(self.timer - self.at_time / 2)))

    def on_end_attack(self):
        super().on_end_attack()

    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() + (
                (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                    if not e.hp_sys.is_immune:
                        e.obj.apply_force(vector.Vector(r, self.knock_back * 120000 / e.obj.MASS))
                    e.hp_sys.enable_immume()

class RemoteWeapon(SweepWeapon):
    def update(self):
        mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        px, py = game.get_game().player.obj.pos
        self.x = (mx - px + self.x) // 2
        self.y = (my - py + self.y) // 2
        if not self.timer:
            self.face_to(mx - px, my - py)
        self.display = True
        super().update()

class Spear(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, forward_speed: int,
                 st_pos: int, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.st_pos = st_pos
        self.forward_speed = forward_speed
        self.pos = 0

    def on_start_attack(self):
        self.x = 0
        self.y = 0
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(px, py)
        self.forward(-self.st_pos)
        self.pos = -self.st_pos

    def on_attack(self):
        self.forward(self.timer * 2 - self.at_time)
        self.forward(self.forward_speed)
        self.pos += self.forward_speed
        super().on_attack()
        self.damage()

    def damage(self):
        self.rot %= 360
        rot_range = range(int(self.rot - 15), int(self.rot + 16))
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - game.get_game().player.obj.pos[0]
            py = dps[1] - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range:
                if vector.distance(px, py) < self.img.get_width() + self.pos + (
                (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                    if not e.hp_sys.is_immune:
                        e.obj.apply_force(vector.Vector(r, self.knock_back * 120000 / e.obj.MASS))
                    e.hp_sys.enable_immume()

class SwiftSword(Spear):
    def update(self):
        super().update()
        if not self.timer and not self.cool:
            if pg.K_q in game.get_game().get_keys() and game.get_game().player.mana >= 20:
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                px, py = game.get_game().player.obj.pos
                game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 3600))
                game.get_game().player.mana -= 20
                self.attack()


class ComplexWeapon(SweepWeapon):
    def __init__(self, name, damages_rot: dict[int, float], damages_spear: dict[int, float],
                 kb: float, img, speed: int, at_time_rot: int, at_time_spear: int,
                 rot_speed: int, st_pos_sweep: int, forward_speed: int, st_pos_spear: int,
                 auto_fire: bool = False, keys: list = [pg.K_w, pg.K_s, pg.K_a, pg.K_d]):
        super().__init__(name, damages_rot, kb, img, speed, at_time_rot, rot_speed, st_pos_sweep, auto_fire)
        self.forward_speed = forward_speed
        self.st_pos_spear = st_pos_spear
        self.spear = Spear(name, damages_spear, kb, img, speed, at_time_spear, forward_speed, st_pos_spear, auto_fire)
        self.spear.keys = keys
        self.key = 1

    def on_start_attack(self):
        super().on_start_attack()
        self.spear.on_start_attack()

    def update(self):
        self.spear.update()
        self.cool = self.spear.cool
        super().update()
        self.spear.cool = self.cool


class AutoSweepWeapon(SweepWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided, True)


class BloodySword(SweepWeapon):
    def on_attack(self):
        super().on_attack()
        if pg.K_q in game.get_game().get_keys():
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            px, py = game.get_game().player.obj.pos
            game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 600))


class SandSword(SweepWeapon):
    def on_attack(self):
        super().on_attack()
        if pg.K_q in game.get_game().get_keys():
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            px, py = game.get_game().player.obj.pos
            game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 900))


class Blade(AutoSweepWeapon):
    def on_start_attack(self):
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r

class LifeWoodenSword(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        px, py = game.get_game().player.obj.pos
        game.get_game().projectiles.append(projectiles.Projectiles.LifeWoodenSword(game.get_game().player.obj.pos,
                                                                                   vector.coordinate_rotation(mx - px, my - py)))

class BloodPike(Spear):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        px, py = game.get_game().player.obj.pos
        game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 480))

class PerseveranceSword(Blade):
    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                for t, d in self.damages.items():
                    e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                if not e.hp_sys.is_immune:
                    e.obj.apply_force(vector.Vector(r, self.knock_back * 120000 / e.obj.MASS))
                e.hp_sys.enable_immume()


class BlackHoleSword(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().player.obj.MASS = 10 ** 9

    def on_end_attack(self):
        super().on_end_attack()
        game.get_game().player.obj.MASS = 20

    def damage(self):
        super().damage()
        game.get_game().player.obj.FRICTION = 0


class MagicBlade(Blade):
    def on_start_attack(self):
        r = self.rot_speed // abs(self.rot_speed)
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r


class Volcano(Blade):
    def on_start_attack(self):
        for e in game.get_game().entities:
            px, py = e.obj.pos
            if vector.distance(px - game.get_game().player.obj.pos[0], py - game.get_game().player.obj.pos[1]) < 300:
                e.hp_sys.effect(effects.Burning(5, 15))

class JevilKnife(Blade):
    def on_attack(self):
        self.rotate(-int((self.timer - self.at_time / 2) * 10))
        super().on_attack()

class NightsEdge(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_start_attack(self):
        self.rots = []
        super().on_start_attack()
        if game.get_game().day_time > 0.75 or game.get_game().day_time < 0.2:
            self.at_time = 10
            self.rot_speed = 36
            spd = 1600
            self.damages = {dmg.DamageTypes.PHYSICAL: 380, dmg.DamageTypes.MAGICAL: 140}
            self.img_index = "items_weapons_nights_edge_night"
        else:
            self.at_time = 18
            self.rot_speed = 40
            spd = 4000
            self.damages = {dmg.DamageTypes.PHYSICAL: 200, dmg.DamageTypes.MAGICAL: 60}
            self.img_index = 'items_weapons_nights_edge'
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 100 * r)
        n = projectiles.Projectiles.NightsEdge((self.x + game.get_game().player.obj.pos[0] + vx * 200,
                                                self.y + game.get_game().player.obj.pos[1] + vy * 200),
                                               self.rot - r * 100)
        n.obj.apply_force(vector.Vector(self.rot - 100 * r, spd))
        n.set_rotation(self.rot)
        game.get_game().projectiles.append(n)
        self.lrot = self.rot

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -5))
        super().on_attack()
        for i in range(5):
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            r = self.lrot + (self.rot - self.lrot) * i // 4
            vx, vy = vector.rotation_coordinate(r)
            self.rots.append((vx, vy))
            if len(self.rots) > 19:
                self.rots.pop(0)
        for j in range(40):
            i = j / 10
            d = (130 - i * 23) / game.get_game().player.get_screen_scale()
            eff.pointed_curve((100 + int(i * 30), int(i * 25), 100 + int(i * 12)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1])
                               for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 30))
            self.lrot = self.rot


class SpiritualStabber(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -1))
        super().on_attack()
        for i in range(5):
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            r = self.lrot + (self.rot - self.lrot) * i // 4
            vx, vy = vector.rotation_coordinate(r)
            self.rots.append((vx, vy))
            if len(self.rots) > 20:
                self.rots.pop(0)
        for j in range(64):
            i = j / 10
            d = (200 - i * 23) / game.get_game().player.get_screen_scale()
            eff.pointed_curve((100 + int(i * 12), 200, 200),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1])
                               for vx, vy in self.rots[:-3]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot


class BalancedStabber(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -1))
        super().on_attack()
        for i in range(5):
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            r = self.lrot + (self.rot - self.lrot) * i // 4
            vx, vy = vector.rotation_coordinate(r)
            self.rots.append((vx, vy))
            if len(self.rots) > 20:
                self.rots.pop(0)
        for j in range(64):
            i = j / 10
            d = (200 - i * 23) / game.get_game().player.get_screen_scale()
            eff.pointed_curve((50 + int(i * 10), int(i * 30), 50 + int(i * 20)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1])
                               for vx, vy in self.rots[:-3]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot


class Excalibur(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_start_attack(self):
        self.rots = []
        super().on_start_attack()
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 180 * r)
        for ar in range(-30, 31, 10):
            n = projectiles.Projectiles.Excalibur((self.x + game.get_game().player.obj.pos[0] + vx * 200,
                                                   self.y + game.get_game().player.obj.pos[1] + vy * 200),
                                                  self.rot - r * 180 + ar)
            n.obj.apply_force(vector.Vector(self.rot - 180 * r + ar, 3000))
            n.set_rotation(self.rot)
            game.get_game().projectiles.append(n)

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -15))
        super().on_attack()
        for i in range(5):
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            r = self.lrot + (self.rot - self.lrot) * i // 4
            vx, vy = vector.rotation_coordinate(r)
            self.rots.append((vx, vy))
            if len(self.rots) > 19:
                self.rots.pop(0)

        for j in range(80):
            i = j / 10
            d = (260 - i * 23) / game.get_game().player.get_screen_scale()
            eff.pointed_curve((255, 200 + int(i * 5), 127 + int(i * 10)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1])
                               for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot


class TrueExcalibur(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_start_attack(self):
        self.rots = []
        super().on_start_attack()
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 180 * r)
        for ar in range(-80, 81, 8):
            n = projectiles.Projectiles.TrueExcalibur((self.x + game.get_game().player.obj.pos[0] + vx * 200,
                                                       self.y + game.get_game().player.obj.pos[1] + vy * 200),
                                                      self.rot - r * 180 + ar)
            n.obj.apply_force(vector.Vector(self.rot - 180 * r + ar, 2000))
            n.set_rotation(self.rot)
            game.get_game().projectiles.append(n)

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -15))
        super().on_attack()
        for i in range(5):
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            r = self.lrot + (self.rot - self.lrot) * i // 4
            vx, vy = vector.rotation_coordinate(r)
            self.rots.append((vx, vy))
            if len(self.rots) > 19:
                self.rots.pop(0)

        for j in range(80):
            i = j / 10
            d = (260 - i * 23) / game.get_game().player.get_screen_scale()
            eff.pointed_curve((255, 200 + int(i * 5), 127 + int(i * 10)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1])
                               for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot


class TrueNightsEdge(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_start_attack(self):
        self.rots = []
        super().on_start_attack()
        if game.get_game().day_time > 0.75 or game.get_game().day_time < 0.2:
            self.at_time = 32
            self.rot_speed = 60
            spd = 1600
            self.damages = {dmg.DamageTypes.PHYSICAL: 5280, dmg.DamageTypes.MAGICAL: 1240}
        else:
            self.at_time = 32
            self.rot_speed = 40
            spd = 4000
            self.damages = {dmg.DamageTypes.PHYSICAL: 3260, dmg.DamageTypes.MAGICAL: 880}
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 100 * r)
        n = projectiles.Projectiles.TrueNightsEdge((self.x + game.get_game().player.obj.pos[0] + vx * 200,
                                                    self.y + game.get_game().player.obj.pos[1] + vy * 200),
                                                   self.rot - r * 100)
        n.obj.apply_force(vector.Vector(self.rot - 100 * r, spd))
        n.set_rotation(self.rot)
        game.get_game().projectiles.append(n)
        self.lrot = self.rot

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -5))
        super().on_attack()
        for i in range(5):
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            r = self.lrot + (self.rot - self.lrot) * i // 4
            vx, vy = vector.rotation_coordinate(r)
            self.rots.append((vx, vy))
            if len(self.rots) > 19:
                self.rots.pop(0)
        for j in range(80):
            i = j / 10
            d = 260 - i * 23
            eff.pointed_curve((100 + int(i * 15), int(i * 12), 100 + int(i * 6)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1])
                               for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot

class TheBlade(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.ppos = [[] for _ in range(80)]
        self.wt = 0
        self.at_r = 0

    def on_start_attack(self):
        self.at_r = (self.at_r + 1) % 16
        self.wt = 0
        super().on_start_attack()

    def update(self):
        self.display = True
        for j in range(80):
            i = j / 10
            d = 260 - i * 23
            ax, ay = vector.rotation_coordinate(self.rot)
            self.ppos[j].append((ax * d + game.get_game().player.obj.pos[0] + self.x,
                                 ay * d + game.get_game().player.obj.pos[1] + self.y))
            if len(self.ppos[j]) > 6:
                self.ppos[j].pop(0)
            eff.pointed_curve((int(i * 25), 80 + int(i * 20), int(i * 25)), self.ppos[j], 3,
                              salpha=int(120 - i * 15))
        super().update()

    def on_idle(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        rot = (360 + rot % 360) % 360
        if rot > 270:
            rot = 180 - rot
        if rot < 90:
            rot = 180 - rot
        rot = 360 - rot
        self.set_rotation((self.rot + rot) // 2)
        self.x //= 2
        self.y //= 2
        super().on_idle()

    def on_attack(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        if self.at_r > 13:
            self.x //= 3
            self.y //= 3
            self.rotate(int(-(self.timer - self.at_time / 2) * -32))
        elif self.at_r % 4 < 2:
            self.x //= 2
            self.y //= 2
            self.rotate(int(-(self.timer - self.at_time / 2) * -16))
        else:
            self.x = (self.x + mx) // 2
            self.y = (self.y + my) // 2
        if 4 <= self.wt and self.at_r % 4 > 1 and self.at_r <= 13:
            if self.wt % 2 == 0:
                for _ in range(self.wt // 3 + 1):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.BladeBeamSmall((self.x + game.get_game().player.obj.pos[0],
                                                                self.y + game.get_game().player.obj.pos[1]),
                                                               random.randint(0, 360)))
        if self.wt == 4:
            rot = vector.coordinate_rotation(mx, my)
            if self.at_r == 13:
                for r in range(-30, 31, 15):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                            self.y + game.get_game().player.obj.pos[1]),
                                                           rot + r))
            elif self.at_r == 15:
                for r in range(-180, 181, 18):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                            self.y + game.get_game().player.obj.pos[1]),
                                                           rot + r))
            elif self.at_r > 13:
                pass
            elif self.at_r % 4 == 0:
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot))
            elif self.at_r % 4 == 1:
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot - 10))
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot))
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot + 10))
        self.wt += 1
        super().on_attack()

class LifeDevourer(Blade):
    def update(self):
        super().update()
        if not self.timer and not self.cool and pg.K_q in game.get_game().get_keys():
            super().attack()
            self.timer = 32
            for i in range(32):
                ax, ay = vector.rotation_coordinate(random.randint(0, 360))
                x, y = game.get_game().player.obj.pos[0] + ax * 1200, game.get_game().player.obj.pos[1] + ay * 1200
                pj = projectiles.Projectiles.LifeDevourer((x, y),
                                                          vector.coordinate_rotation(-ax, -ay) + random.randint(-5, 5))
                pj.DURATION = 16 + i // 2
                pj.WIDTH = 20
                game.get_game().projectiles.append(pj)

    def on_start_attack(self):
        super().on_start_attack()
        for i in range(random.randint(1, 3)):
            ax, ay = vector.rotation_coordinate(random.randint(0, 360))
            x, y = game.get_game().player.obj.pos[0] + ax * 1200, game.get_game().player.obj.pos[1] + ay * 1200
            pj = projectiles.Projectiles.LifeDevourer((x, y),
                                                      vector.coordinate_rotation(-ax, -ay) + random.randint(-2, 2))
            game.get_game().projectiles.append(pj)


class MagicSword(AutoSweepWeapon):
    def on_end_attack(self):
        super().on_end_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(projectiles.Projectiles.MagicSword(
            (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot))


class MagicWeapon(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.projectile = projectile
        self.spell_name = spell_name
        self.mana_cost = mana_cost

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(
            self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                            self.rot))
        game.get_game().player.mana -= self.mana_cost

class TargetDummy(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)
        self.dm = None

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.mana -= self.mana_cost

    def on_attack(self):
        if self.dm is None:
            self.dm = entity.Entities.Dummy((0, 0))
        self.dm.obj.pos = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        self.dm.update()
        if self.dm.obj not in game.get_game().p_obj:
            game.get_game().p_obj.append(self.dm.obj)

    def on_end_attack(self):
        if self.dm.obj in game.get_game().p_obj:
            game.get_game().p_obj.remove(self.dm.obj)

class Teleporter(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 teleport_range: int, mana_cost: int, auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectiles.Projectiles.Projectile, mana_cost, auto_fire, spell_name)
        self.teleport_range = teleport_range

    def on_start_attack(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        if vector.distance(mx, my) > self.teleport_range:
            self.timer = 0
            return
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        game.get_game().player.obj.pos = (game.get_game().player.obj.pos[0] + mx, game.get_game().player.obj.pos[1] + my)

class ChaosKiller(MagicWeapon):
    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        els = [e for e in game.get_game().entities if e.obj.IS_OBJECT]
        els.extend([e for e in game.get_game().entities if e.IS_MENACE])
        el = len(els)
        for e in els:
            e.hp_sys.damage(self.damages[dmg.DamageTypes.MAGICAL] * game.get_game().player.attack *
                            game.get_game().player.attacks[2] / el, dmg.DamageTypes.MAGICAL)

class EvilMagicWeapon(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, hp_cost: float,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)
        self.hp_cost = hp_cost

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost or game.get_game().player.hp_sys.hp <= self.hp_cost:
            self.timer = 0
            return
        game.get_game().player.hp_sys.hp -= self.hp_cost
        super().on_start_attack()

class Tornado(MagicWeapon):
    def on_start_attack(self):
        if game.get_game().player.mana >= self.mana_cost:
            game.get_game().player.mana -= self.mana_cost
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey),
                                                 1000000 / vector.distance(ex, ey) ** 2 * game.get_game().player.attack * game.get_game().player.attacks[2]))
        else:
            self.timer = 0

class SweepMagicWeapon(SweepWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 rot_speed: int, st_pos: int, double_sided: bool, mana_cost: int, auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided, auto_fire)
        self.spell_name = spell_name
        self.mana_cost = mana_cost

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        super().on_start_attack()

class MagicSet(Weapon):
    PRESET_KEY_SET = 'uiopgjklb'

    def __init__(self, name, img_index, element_feature, spell_name, style=0):
        super().__init__(name, {dmg.DamageTypes.MAGICAL: 32000}, 0, img_index, 1, 0, False)
        self.weapons = []
        self.element_feature = element_feature
        self.at_in: MagicWeapon | None = None
        self.spell_name = spell_name
        self.mana_cost = 10
        self.talent_cost = 0.2
        self.style = style
        self.sz = 0
        self.tick = 0
        self.sel = 0

    def update(self):
        self.tick += 1
        if self.style == 0:
            px, py = position.displayed_position(game.get_game().player.obj.pos)
            tk_wave = self.tick % 20 / 20
            tk_wk = math.cos(tk_wave * 2 * math.pi)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 220, 180),
                           (px, py - self.sz * 3 // 2 - 20), int(self.sz * (tk_wk * 0.3 + 1)))
            if random.randint(0, int(2000 - 1800 * tk_wave)) < self.sz:
                for _ in range(random.randint(1, 2 + int(math.sqrt(self.sz)))):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.LightsBeam(position.real_position((px, py - self.sz * 3 // 2 - 20)),
                                                           random.randint(0, 360)))
        elif self.style == 1:
            px, py = position.displayed_position(game.get_game().player.obj.pos)
            zq = int(4 + 56 / (math.sqrt(self.sz) + 1))
            tk_wave = self.tick % zq / zq
            tk_wk = math.cos(tk_wave * 2 * math.pi)
            for e in game.get_game().entities:
                if vector.distance(e.obj.pos[0] - game.get_game().player.obj.pos[0],
                                   e.obj.pos[1] - game.get_game().player.obj.pos[1]) < int((tk_wk + 1) * self.sz * 3):
                    e.hp_sys.damage(self.damages[dmg.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                    game.get_game().player.attacks[2], dmg.DamageTypes.MAGICAL)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255), (px, py),
                           int((tk_wk + 1) * self.sz * 3 / game.get_game().player.get_screen_scale()),
                           width=2)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255), (px, py),
                           int((-tk_wk + 1) * self.sz * 3 / game.get_game().player.get_screen_scale()),
                           width=2)
        super().update()
        self.weapons = [w for w in WEAPONS.values() if
                        self.element_feature(w) and w != self.name] #and
                        #w.name in game.get_game().player.inventory.items.keys()]
        self.sel = min(self.sel, len(self.weapons) - 1)
        if self.weapons[self.sel] is not self:
            self.weapons[self.sel].update()
        if self.at_in is not None:
            if not self.at_in.cool and not self.at_in.timer:
                self.at_in = None
            else:
                lv = [t for t in inventory.ITEMS[self.at_in.name.replace(' ', '_')].tags if t.name.startswith('magic_lv_')]
                lvs = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'xx': 8, 'xxv': 12, 'nulla': 50}
                sz = lvs[lv[0].value.removeprefix('LV.').lower()]
                self.sz = (self.sz * 49 + sz ** 2 * 3) // 50
        if self.at_in is None:
            self.sz *= 8
            self.sz //= 9
            for i, w in enumerate(self.weapons):
                if pg.key.key_code(self.PRESET_KEY_SET[i]) in game.get_game().pressed_keys or\
                        (self.sel == i and pg.mouse.get_pressed()[0]):
                    self.sel = i
                    self.at_in = w
                    w.re_init()
                    w.attack()
                    lv = [t for t in inventory.ITEMS[self.at_in.name.replace(' ', '_')].tags if t.name.startswith('magic_lv_')]
                    lvs = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'xx': 8, 'xxv': 12, 'nulla': 50}
                    sz = lvs[lv[0].value.removeprefix('LV.').lower()]
                    self.sz = (self.sz * 5 + sz ** 2 * 3) // 6
                    if sz == 12:
                        if game.get_game().player.mana > self.mana_cost:
                            game.get_game().player.mana -= self.mana_cost
                        else:
                            self.at_in = None
                            self.sz = 0
                        if game.get_game().player.talent > self.talent_cost:
                            game.get_game().player.talent -= self.talent_cost
                        else:
                            self.at_in = None
                            self.sz = 0


class ArcaneWeapon(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, talent_cost: float,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)
        self.talent_cost = talent_cost

    def on_start_attack(self):
        if game.get_game().player.talent < self.talent_cost:
            self.timer = 0
            return
        super().on_start_attack()
        if self.timer:
            game.get_game().player.talent -= self.talent_cost

class Domain(ArcaneWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, mana_cost: int,
                 talent_cost: float, domain_color: tuple[int, int, int], domain_size: int = 600,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectiles.Projectiles.Projectile, mana_cost,
                         talent_cost, auto_fire, spell_name)
        self.domain_color = domain_color
        self.domain_size = domain_size
        self.domain_open = False
        self.domain_tick = 0

    def on_start_attack(self):
        self.domain_open = not self.domain_open
        self.domain_tick = 0
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))

    def update(self):
        self.domain_tick += 1
        if self.domain_open:
            if game.get_game().player.mana < self.mana_cost or game.get_game().player.talent < self.talent_cost:
                self.domain_open = False
                self.domain_tick = 0
                return
            game.get_game().player.mana -= self.mana_cost
            game.get_game().player.talent -= self.talent_cost
            pg.draw.circle(game.get_game().displayer.canvas, self.domain_color,
                           position.displayed_position(game.get_game().player.obj.pos),
                           min(self.domain_size, self.domain_tick ** 2 * 8) / game.get_game().player.get_screen_scale(),
                           width=5)
            game.get_game().player.obj.FRICTION = 0
        elif self.domain_tick ** 2 * 8 <= self.domain_size:
            pg.draw.circle(game.get_game().displayer.canvas, self.domain_color,
                           position.displayed_position(game.get_game().player.obj.pos),
                           max(0, self.domain_size -self.domain_tick ** 2 * 8) / game.get_game().player.get_screen_scale(),
                           width=5)
        super().update()

class DomainWeapons(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), domain_name: str,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.domain_name = domain_name
        self.spell_name = spell_name
        self.mana_cost = 0
        self.projectile = projectile

    def on_start_attack(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        if vector.distance(mx, my) <= WEAPONS[self.domain_name].domain_size and \
            WEAPONS[self.domain_name].domain_open:
            self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            super().on_start_attack()
            game.get_game().player.hp_sys.heal(4)
        else:
            self.timer = 0
            return

    def update(self):
        super().update()
        WEAPONS[self.domain_name].update()

class WdCirculateClockwise(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey) + 90,
                                                 1000000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2]))

class WdCirculateAntiClockwise(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey) - 90,
                                                 1000000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2]))

class WdCirculateAttract(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey) + 180,
                                                 800000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2]))

class WdCirculateRepel(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey),
                                                 800000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2]))

class WdStrongWind(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                if vector.distance(ex, ey) < 100:
                    e.hp_sys.damage(self.damages[dmg.DamageTypes.ARCANE] * game.get_game().player.attack *
                                     game.get_game().player.attacks[2], dmg.DamageTypes.ARCANE)

class WdExtinct(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size:
                    continue
                e.hp_sys.damage(self.damages[dmg.DamageTypes.ARCANE] * game.get_game().player.attack *
                                 game.get_game().player.attacks[2], dmg.DamageTypes.ARCANE)

class LdSpawn(DomainWeapons):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), domain_name: str,
                 auto_fire: bool = False, spell_name = '', spawn_entity: type(entity.Entities.Entity) = entity.Entities.Entity):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, domain_name, auto_fire, spell_name)
        self.spawn_entity = spawn_entity

    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            if vector.distance(mx - game.get_game().player.obj.pos[0],
                               my - game.get_game().player.obj.pos[1]) <= WEAPONS[self.domain_name].domain_size and \
                    WEAPONS[self.domain_name].domain_open:
                self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
                m: entity.Entities.Entity = self.spawn_entity((mx, my))
                m.LOOT_TABLE = entity.LootTable([])
                game.get_game().entities.append(m)

class LdHeal(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            game.get_game().player.hp_sys.heal(10)

class ForbiddenCurseTime(ArcaneWeapon):
    def on_start_attack(self):
        if game.get_game().player.talent < self.talent_cost:
            self.timer = 0
            return
        game.get_game().player.talent -= self.talent_cost
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        fps = constants.FPS
        if fps == 40:
            fps = 10
        else:
            fps = 40
        constants.FPS = fps


class ToyKnife(MagicWeapon):
    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.mana -= self.mana_cost
        pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255),
                       position.displayed_position(game.get_game().player.obj.pos), 600, width=5)
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - game.get_game().player.obj.pos[1]) < 600:
                e.hp_sys.damage(self.damages[dmg.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                game.get_game().player.attacks[2], dmg.DamageTypes.MAGICAL)


class MidnightsWand(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False,
                 add_pos: int = 0):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire,
                         'Midnight Spell')
        self.add_pos = add_pos
        self.pts = []

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        if game.get_game().day_time > 0.75 or game.get_game().day_time < 0.2:
            self.at_time = 8
            k = 5
            self.damages = {dmg.DamageTypes.MAGICAL: 110}
        else:
            self.at_time = 6
            k = 3
            self.damages = {dmg.DamageTypes.MAGICAL: 80}
        player = game.get_game().player
        self.pts = [(player.obj.pos[0] + self.x, player.obj.pos[1] + self.y)]
        for i in range(k):
            self.x, self.y = random.randint(-self.add_pos, self.add_pos), random.randint(-self.add_pos, self.add_pos)
            self.face_to(*position.relative_position(
                position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            p = self.projectile(
                (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot)
            p.obj.apply_force(vector.Vector(self.rot, 1000))
            game.get_game().projectiles.append(p)
            self.pts.append((player.obj.pos[0] + self.x, player.obj.pos[1] + self.y))
        self.x, self.y = 0, 0
        game.get_game().player.mana -= self.mana_cost

    def on_attack(self):
        super().on_attack()
        eff.pointed_curve((127, 0, 127), self.pts, 5, salpha=255)


class Hematology(MagicWeapon):
    def __init__(self, name, img, speed: int, at_time: int, auto_fire: bool = False):
        super().__init__(name, {}, 0, img, speed, at_time, projectiles.Projectiles.Projectile,
                         30, auto_fire, 'Blood Regeneration')

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.hp_sys.heal(30)


class LifeWand(MagicWeapon):
    def __init__(self, name, img, speed: int, at_time: int, auto_fire: bool = False):
        super().__init__(name, {}, 0, img, speed, at_time, projectiles.Projectiles.Projectile,
                         0, auto_fire, 'Heal Prayer')

    def update(self):
        super().update()
        self.mana_cost = min(game.get_game().player.mana,
                             int(game.get_game().player.hp_sys.max_hp - game.get_game().player.hp_sys.hp) * 2)

    def on_start_attack(self):
        hp_lft = game.get_game().player.hp_sys.max_hp - game.get_game().player.hp_sys.hp
        mana_avail = game.get_game().player.mana
        game.get_game().player.mana -= min(mana_avail // 2, hp_lft) * 2
        game.get_game().player.hp_sys.heal(min(mana_avail // 2, hp_lft))

class AzureGuard(MagicWeapon):
    def update(self):
        super().update()
        aw = [v for n, v in game.get_game().player.hp_sys.shields if n == 'azure_guard']
        if len(aw):
            v = aw[0]
            pg.draw.circle(game.get_game().displayer.canvas, (int(255 - v * 2), int(255 - v * 2), 255),
                           position.displayed_position(game.get_game().player.obj.pos),
                           width=int(1 + v // 20), radius=240)

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        if len([v for n, v in game.get_game().player.hp_sys.shields if n == 'azure_guard']):
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        game.get_game().player.hp_sys.shields.append(('azure_guard', 100))

class EarthWall(MagicWeapon):
    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        e_w = 256
        for ar in [15, 18, 20, 30]:
            w = e_w / 2 / math.sin(math.radians(ar / 2))
            for r in range(0, 360, ar):
                ax, ay = vector.rotation_coordinate(r)
                game.get_game().entities.append(entity.Entities.HugeTree((self.x + game.get_game().player.obj.pos[0] + ax * w,
                                                                          self.y + game.get_game().player.obj.pos[1] + ay * w)))

class Bow(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, projectile_speed: int,
                 auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.spd = projectile_speed

    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        game.get_game().projectiles.append(
            projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                               self.y + game.get_game().player.obj.pos[1]),
                                                              self.rot, self.spd,
                                                              self.damages[dmg.DamageTypes.PIERCING]))


class DiscordStorm(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        for r in range(-30, 31, 15):
            game.get_game().projectiles.append(
                projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                   self.y + game.get_game().player.obj.pos[1]),
                                                                  self.rot + r, self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING]))


class DaedelusStormbow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        for i in range(3):
            x, y = mx + random.randint(-500, 500), -game.get_game().displayer.SCREEN_HEIGHT // 2 - 200
            p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x + game.get_game().player.obj.pos[0],
                                                                   y + game.get_game().player.obj.pos[1]),
                                                                  vector.coordinate_rotation(mx - x,
                                                                                             my - y) + random.randint(
                                                                      -1, 1), self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING])
            game.get_game().projectiles.append(p)
        self.face_to(mx, - 1200)


class TrueDaedalusStormbow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        for i in range(8):
            x, y = mx + random.randint(-800, 800), -game.get_game().displayer.SCREEN_HEIGHT // 2 - 200
            p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x + game.get_game().player.obj.pos[0],
                                                                   y + game.get_game().player.obj.pos[1]),
                                                                  vector.coordinate_rotation(mx - x,
                                                                                             my - y) + random.randint(
                                                                      -1, 1), self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING])
            game.get_game().projectiles.append(p)
        self.face_to(mx, - 1200)


class Gun(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < constants.ULTIMATE_AMMO_BONUS:
            game.get_game().player.ammo_bullet = (
            game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        game.get_game().projectiles.append(
            projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                      self.y + game.get_game().player.obj.pos[1]),
                                                                     self.rot, self.spd,
                                                                     self.damages[dmg.DamageTypes.PIERCING]))


class LazerGun(Gun):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < constants.ULTIMATE_AMMO_BONUS:
            game.get_game().player.ammo_bullet = (
            game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        wp: projectiles.Projectiles.Bullet = projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]
        ps = (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1])
        b = projectiles.Projectiles.Beam(ps, self.rot)
        b.LENGTH = (wp.SPEED + self.spd) // 1.5
        b.WIDTH = 30
        b.DURATION = 10
        b.DMG = self.damages[dmg.DamageTypes.PIERCING] + wp.DAMAGES
        b.COLOR = (255, 255, 150)
        b.DMG_TYPE = dmg.DamageTypes.PIERCING
        game.get_game().projectiles.append(b)


class MagmaAssaulter(Gun):
    def on_attack(self):
        super().on_attack()
        if pg.K_q in game.get_game().get_keys():
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            px, py = game.get_game().player.obj.pos
            game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), -800))


class Shadow(Gun):
    def on_start_attack(self):
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.x, self.y = mx, my
        self.face_to(0, 0)
        self.rotate(random.randint(-10, 10))
        self.forward(300)
        self.face_to(mx, my)
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < 1000:
            game.get_game().player.ammo_bullet = (
                game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        game.get_game().projectiles.append(
            projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                      self.y + game.get_game().player.obj.pos[1]),
                                                                     self.rot, self.spd,
                                                                     self.damages[dmg.DamageTypes.PIERCING]))


class Astigmatism(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, mana_cost: int,
                 auto_fire: bool = False, spell_name: str = ''):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.pre_beams = [projectiles.Projectiles.BeamLight((0, 0), 0) for _ in range(8)]
        self.using_beam = projectiles.Projectiles.Beam((0, 0), 0)
        self.spell_name = spell_name
        i = 0
        for b in self.pre_beams:
            b.COLOR = (i * 8, 255 - i * 8, i * 8)
            b.DAMAGE_AS = self.name
            b.WIDTH = 20
            b.FOLLOW_PLAYER = True
            b.DURATION = 100
            b.DMG = self.damages[dmg.DamageTypes.MAGICAL] // 4
            i += 1
        self.using_beam.COLOR = (100, 255, 0)
        self.using_beam.DAMAGE_AS = self.name
        self.using_beam.WIDTH = 240
        self.using_beam.DURATION = 100
        self.mana_cost = mana_cost

    def re_init(self):
        self.pre_beams = [projectiles.Projectiles.BeamLight((0, 0), 0) for _ in range(8)]
        self.using_beam = projectiles.Projectiles.Beam((0, 0), 0)

    def on_end_attack(self):
        self.on_attack()
        super().on_end_attack()

    def on_attack(self):
        super().on_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        self.display = True
        if self.combo < 30:
            rts = self.combo ** 3 // 10
            for b in self.pre_beams:
                b.tick = 50
                b.rot = self.rot + math.sin(math.radians(rts)) * (30 - self.combo)
                b.update()
                rts += 45
        else:
            self.using_beam.tick = 50
            self.using_beam.rot = self.rot
            self.using_beam.update()

    def on_start_attack(self):
        super().on_start_attack()
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        if self.combo >= 30:
            if game.get_game().player.mana < self.mana_cost:
                self.timer = 0
                return
            game.get_game().player.mana -= self.mana_cost


WEAPONS = {}


def set_weapons():
    global WEAPONS
    WEAPONS = {
        'null': SweepWeapon('null', {dmg.DamageTypes.PHYSICAL: 0}, 0,
                            'items_weapons_null', 0,
                            1, 40, 20),
        'wooden_sword': SweepWeapon('wooden sword', {dmg.DamageTypes.PHYSICAL: 8}, 0.1,
                                    'items_weapons_wooden_sword', 5,
                                    10, 9, 45),
        'copper_sword': SweepWeapon('copper sword', {dmg.DamageTypes.PHYSICAL: 12}, 0.3,
                                    'items_weapons_copper_sword', 8,
                                    15, 8, 60),
        'iron_sword': SweepWeapon('iron sword', {dmg.DamageTypes.PHYSICAL: 24}, 0.25,
                                  'items_weapons_iron_sword', 6,
                                  6, 18, 54),
        'iron_blade': Blade('iron blade', {dmg.DamageTypes.PHYSICAL: 16}, 0.15,
                            'items_weapons_iron_blade', 4,
                            16, 15, 120),
        'steel_sword': SweepWeapon('steel sword', {dmg.DamageTypes.PHYSICAL: 40}, 0.4,
                                   'items_weapons_steel_sword', 10,
                                   10, 16, 80),
        'platinum_sword': SweepWeapon('platinum sword', {dmg.DamageTypes.PHYSICAL: 64}, 0.6,
                                      'items_weapons_platinum_sword', 0,
                                      15, 16, 120),
        'platinum_blade': Blade('platinum blade', {dmg.DamageTypes.PHYSICAL: 32}, 0.1,
                                'items_weapons_platinum_blade', 10,
                                12, 30, 180),
        'life_wooden_sword': LifeWoodenSword('life wooden sword', {dmg.DamageTypes.PHYSICAL: 88}, 1.2,
                                             'items_weapons_life_wooden_sword', 1,
                                             5, 36, 110),
        'magic_sword': MagicSword('magic sword', {dmg.DamageTypes.PHYSICAL: 30}, 0.5,
                                  'items_weapons_magic_sword', 0,
                                  16, 12, 96),
        'magic_blade': MagicBlade('magic blade', {dmg.DamageTypes.PHYSICAL: 20}, 0.6,
                                  'items_weapons_magic_blade', 0,
                                  1, 30, 15),
        'bloody_sword': BloodySword('bloody sword', {dmg.DamageTypes.PHYSICAL: 96}, 0.2,
                                    'items_weapons_bloody_sword', 2,
                                    10, 20, 100, auto_fire=True),
        'volcano': Volcano('volcano', {dmg.DamageTypes.PHYSICAL: 120}, 0.5, 'items_weapons_volcano',
                           2, 18, 20, 200),
        'sand_sword': SandSword('sand_sword', {dmg.DamageTypes.PHYSICAL: 148}, 0.3,
                                'items_weapons_sand_sword', 0,
                                8, 30, 120, auto_fire=True),
        'nights_edge': NightsEdge('nights edge', {dmg.DamageTypes.PHYSICAL: 380, dmg.DamageTypes.MAGICAL: 140}, 0.6,
                                  'items_weapons_nights_edge',
                                  1, 18, 20, 100),
        'storm_swift_sword': SwiftSword('storm swift sword', {dmg.DamageTypes.PHYSICAL: 240}, 0.8,
                                               'items_weapons_storm_swift_sword',
                                               0, 3, 100, 180, auto_fire=True),
        'spiritual_stabber': SpiritualStabber('spiritual stabber', {dmg.DamageTypes.PHYSICAL: 685}, 0.5,
                                              'items_weapons_spiritual_stabber',
                                              2, 6, 40, 170),
        'palladium_sword': Blade('palladium sword', {dmg.DamageTypes.PHYSICAL: 450}, 0.2,
                                 'items_weapons_palladium_sword', 1, 5, 50, 120),
        'mithrill_sword': Blade('mithrill sword', {dmg.DamageTypes.PHYSICAL: 840}, 0.3,
                                'items_weapons_mithrill_sword', 1, 8, 30, 160),
        'titanium_sword': Blade('titanium sword', {dmg.DamageTypes.PHYSICAL: 1020}, 0.4,
                                'items_weapons_titanium_sword', 1, 10, 40, 200),
        'balanced_stabber': BalancedStabber('balanced stabber', {dmg.DamageTypes.PHYSICAL: 985}, 2,
                                            'items_weapons_balanced_stabber',
                                            1, 7, 50, 150),
        'excalibur': Excalibur('excalibur', {dmg.DamageTypes.PHYSICAL: 1250, dmg.DamageTypes.MAGICAL: 450}, 0.8,
                               'items_weapons_excalibur',
                               1, 6, 59, 180),
        'remote_sword': RemoteWeapon('remote sword', {dmg.DamageTypes.PHYSICAL: 1080}, 0.8,
                                      'items_weapons_remote_sword',
                                      1, 5, 72, 180, auto_fire=True),
        'true_excalibur': TrueExcalibur('true excalibur',
                                        {dmg.DamageTypes.PHYSICAL: 2020, dmg.DamageTypes.MAGICAL: 620}, 1,
                                        'items_weapons_true_excalibur',
                                        1, 4, 88, 180),
        'true_nights_edge': TrueNightsEdge('true nights edge',
                                           {dmg.DamageTypes.PHYSICAL: 5280, dmg.DamageTypes.MAGICAL: 1240}, 0.6,
                                           'items_weapons_true_nights_edge',
                                           1, 32, 60, 100),
        'perseverance_sword': PerseveranceSword('perseverance sword', {dmg.DamageTypes.PHYSICAL: 1500}, 2,
                                                'items_weapons_perseverance_sword',
                                                1, 6, 28, 90),
        'black_hole_sword': BlackHoleSword('black hole sword', {dmg.DamageTypes.PHYSICAL: 3200}, 0,
                                           'items_weapons_black_hole_sword',
                                           0, 6, 60, 90),
        'life_devourer': LifeDevourer('life devourer', {dmg.DamageTypes.PHYSICAL: 3200, dmg.DamageTypes.MAGICAL: 12800},
                                      0.8, 'items_weapons_life_devourer',
                                      1, 5, 70, 150),
        'jevil_knife': JevilKnife('jevil knife', {dmg.DamageTypes.PHYSICAL: 12800}, 0.5, 'items_weapons_jevil_knife',
                                  2, 20, 30, 120),
        'the_blade': TheBlade('the blade', {dmg.DamageTypes.PHYSICAL: 11400}, 7.2, 'items_weapons_the_blade',
                              4, 8, 60, 180),

        'spikeflower': Spear('spikeflower', {dmg.DamageTypes.PHYSICAL: 32}, 1.8, 'items_weapons_spikeflower',
                             1, 3, 30, 60, auto_fire=True),
        'spear': Spear('spear', {dmg.DamageTypes.PHYSICAL: 28}, 0.5, 'items_weapons_spear',
                       2, 6, 15, 60, auto_fire=True),
        'platinum_spear': Spear('platinum spear', {dmg.DamageTypes.PHYSICAL: 50}, 0.6, 'items_weapons_platinum_spear',
                                2, 4, 30, 80, auto_fire=True),
        'blood_pike': BloodPike('blood pike', {dmg.DamageTypes.PHYSICAL: 96}, 5.4, 'items_weapons_blood_pike',
                                1, 5, 50, 150, auto_fire=True),
        'firite_spear': Spear('firite spear', {dmg.DamageTypes.PHYSICAL: 150}, 0.7, 'items_weapons_firite_spear',
                              2, 10, 20, 100, auto_fire=True),
        'nights_pike': Spear('nights pike', {dmg.DamageTypes.PHYSICAL: 420}, 1.8, 'items_weapons_nights_pike',
                             2, 5, 60, 160, auto_fire=True),
        'energy_spear': ComplexWeapon('energy spear', {dmg.DamageTypes.PHYSICAL: 4500},
                                      {dmg.DamageTypes.PHYSICAL: 1800}, 2, 'items_weapons_energy_spear',
                                      2, 8, 6, 40, 120, 80, 250, auto_fire=True),

        'bow': Bow('bow', {dmg.DamageTypes.PIERCING: 6}, 0.1, 'items_weapons_bow',
                   3, 8, 10),
        'copper_bow': Bow('copper bow', {dmg.DamageTypes.PIERCING: 15}, 0.2, 'items_weapons_copper_bow',
                          4, 6, 18),
        'iron_bow': Bow('iron bow', {dmg.DamageTypes.PIERCING: 5}, 0.15, 'items_weapons_iron_bow',
                        3, 5, 40, auto_fire=True),
        'steel_bow': Bow('steel bow', {dmg.DamageTypes.PIERCING: 40}, 0.3, 'items_weapons_steel_bow',
                         9, 12, 70),
        'platinum_bow': Bow('platinum bow', {dmg.DamageTypes.PIERCING: 18}, 0.4, 'items_weapons_platinum_bow',
                            2, 6, 50, auto_fire=True),
        'bloody_bow': Bow('bloody bow', {dmg.DamageTypes.PIERCING: 80}, 0.5, 'items_weapons_bloody_bow',
                          5, 15, 120, auto_fire=True),
        'recurve_bow': Bow('recurve bow', {dmg.DamageTypes.PIERCING: 140}, 0.6, 'items_weapons_recurve_bow',
                           8, 2, 200, auto_fire=True),
        'spiritual_piercer': Bow('spiritual piercer', {dmg.DamageTypes.PIERCING: 580}, 0.5,
                                 'items_weapons_spiritual_piercer',
                                 1, 4, 650, auto_fire=True),
        'discord_storm': DiscordStorm('discord storm', {dmg.DamageTypes.PIERCING: 680}, 0.5,
                                      'items_weapons_discord_storm',
                                      1, 7, 200, auto_fire=True),
        'daedalus_stormbow': DaedelusStormbow('daedalus stormbow', {dmg.DamageTypes.PIERCING: 700}, 0.5,
                                              'items_weapons_daedalus_stormbow',
                                              0, 2, 500, auto_fire=True),
        'true_daedalus_stormbow': TrueDaedalusStormbow('true daedalus stormbow', {dmg.DamageTypes.PIERCING: 1600}, 0.5,
                                                       'items_weapons_true_daedalus_stormbow',
                                                       0, 3, 1000, auto_fire=True),

        'pistol': Gun('pistol', {dmg.DamageTypes.PIERCING: 28}, 0.1, 'items_weapons_pistol',
                      3, 15, 15),
        'rifle': Gun('rifle', {dmg.DamageTypes.PIERCING: 56}, 0.2, 'items_weapons_rifle',
                     10, 12, 20, auto_fire=True),
        'submachine_gun': Gun('submachine gun', {dmg.DamageTypes.PIERCING: 8}, 0.15, 'items_weapons_submachine_gun',
                              0, 2, 50, auto_fire=True),
        'magma_assaulter': MagmaAssaulter('magma assaulter', {dmg.DamageTypes.PIERCING: 60}, 0.5,
                                          'items_weapons_magma_assaulter',
                                          3, 5, 100, auto_fire=True),
        'shadow': Shadow('shadow', {dmg.DamageTypes.PIERCING: 56}, 0.5, 'items_weapons_shadow',
                         0, 1, 200, auto_fire=True),
        'palladium_gun': Gun('palladium gun', {dmg.DamageTypes.PIERCING: 440}, 0.2, 'items_weapons_palladium_gun',
                             1, 2, 300, auto_fire=True),
        'mithrill_gun': Gun('mithrill gun', {dmg.DamageTypes.PIERCING: 620}, 0.3, 'items_weapons_mithrill_gun',
                            1, 5, 800, auto_fire=True),
        'titanium_gun': Gun('titanium gun', {dmg.DamageTypes.PIERCING: 2200}, 0.4, 'items_weapons_titanium_gun',
                            3, 24, 1500, auto_fire=True),
        'true_shadow': Gun('true shadow', {dmg.DamageTypes.PIERCING: 35000}, 0.5, 'items_weapons_true_shadow',
                           5, 10, 5000, auto_fire=True),

        'lazer_gun': LazerGun('lazer gun', {dmg.DamageTypes.PIERCING: 18800}, 0.5, 'items_weapons_lazer_gun',
                              1, 2, 380, auto_fire=True),

        'glowing_splint': MagicWeapon('glowing splint', {dmg.DamageTypes.MAGICAL: 5}, 0.1,
                                      'items_weapons_glowing_splint', 6,
                                      10, projectiles.Projectiles.Glow, 4, spell_name='Glow Spawn'),
        'copper_wand': MagicWeapon('copper wand', {dmg.DamageTypes.MAGICAL: 32}, 0.2,
                                   'items_weapons_copper_wand', 8,
                                   8, projectiles.Projectiles.CopperWand, 5, spell_name='Copper Bomb'),
        'iron_wand': MagicWeapon('iron wand', {dmg.DamageTypes.MAGICAL: 36}, 0.1,
                                 'items_weapons_iron_wand', 2,
                                 6, projectiles.Projectiles.IronWand, 4, spell_name='Iron Bomb'),
        'cactus_wand': MagicWeapon('cactus wand', {dmg.DamageTypes.MAGICAL: 8}, 0.2,
                                    'items_weapons_cactus_wand', 2,
                                    10, projectiles.Projectiles.CactusWand, 18, spell_name='Cactus Spawning'),
        'watcher_wand': MagicWeapon('watcher wand', {dmg.DamageTypes.MAGICAL: 32}, 0.2,
                                    'items_weapons_watcher_wand', 8,
                                    2, projectiles.Projectiles.WatcherWand, 12, spell_name='Watch'),
        'platinum_wand': MagicWeapon('platinum wand', {dmg.DamageTypes.MAGICAL: 42}, 0.3,
                                     'items_weapons_platinum_wand', 2,
                                     5, projectiles.Projectiles.PlatinumWand, 5, True,
                                     'Energy Bomb'),
        'life_wooden_wand': MagicWeapon('life wooden wand', {dmg.DamageTypes.MAGICAL: 32}, 0.4,
                                        'items_weapons_life_wooden_wand', 1,
                                        4, projectiles.Projectiles.LifeWoodenWand, 18, True,
                                    'Earth\'s Lazer'),
        'burning_book': MagicWeapon('burning book', {dmg.DamageTypes.MAGICAL: 72}, 0.5,
                                    'items_weapons_burning_book', 5,
                                    10, projectiles.Projectiles.BurningBook, 9, True,
                                    'Flame'),
        'talent_book': MagicWeapon('talent book', {dmg.DamageTypes.MAGICAL: 24}, 0.7,
                                   'items_weapons_talent_book', 0,
                                   2, projectiles.Projectiles.TalentBook, 2, True,
                                   'Smart Ball'),
        'hematology': Hematology('hematology', 'items_weapons_hematology', 2, 3,
                                 True),
        'blood_wand': MagicWeapon('blood wand', {dmg.DamageTypes.MAGICAL: 75}, 0.1,
                                  'items_weapons_blood_wand', 4,
                                  12, projectiles.Projectiles.BloodWand, 8, True,
                                  'Blood Condense'),
        'fire_magic_sword': SweepMagicWeapon('fire magic sword', {dmg.DamageTypes.MAGICAL: 380}, 0.1,
                                              'items_weapons_fire_magic_sword', 1,
                                              4, 30, 60, False, 3, True,
                                             spell_name='Fire Sword'),
        'rock_wand': MagicWeapon('rock wand', {dmg.DamageTypes.MAGICAL: 65}, 0.6,
                                 'items_weapons_rock_wand', 0,
                                 4, projectiles.Projectiles.RockWand, 3, True,
                                 'Rock Storm'),
        'tornado': Tornado('tornado', {}, 0.1, 'items_weapons_tornado',
                           2, 18, projectiles.Projectiles.Projectile, 25, spell_name='Tornado'),
        'midnights_wand': MidnightsWand('midnights wand', {dmg.DamageTypes.MAGICAL: 110}, 0.3,
                                        'items_weapons_midnights_wand', 2,
                                        12, projectiles.Projectiles.MidnightsWand, 4, True,
                                        80),
        'spiritual_destroyer': MagicWeapon('spiritual destroyer', {dmg.DamageTypes.MAGICAL: 688}, 0.5,
                                           'items_weapons_spiritual_destroyer', 1,
                                           5, projectiles.Projectiles.SpiritualDestroyer, 6,
                                           True, 'Energy Destroy'),
        'blood_sacrifice': EvilMagicWeapon('blood sacrifice', {dmg.DamageTypes.MAGICAL: 456}, 0.5,
                                            'items_weapons_blood_sacrifice', 3,
                                            12, projectiles.Projectiles.BloodSacrifice, 20, 24, True,
                                            spell_name='Blood Sacrifice'),
        'blade_wand': MagicWeapon('blade wand', {dmg.DamageTypes.MAGICAL: 880}, 0.3,
                                  'items_weapons_blade_wand', 1,
                                  5, projectiles.Projectiles.WindBlade, 12, True,
                                  'Wind Blade'),
        'evil_book': MagicWeapon('evil book', {dmg.DamageTypes.MAGICAL: 1550}, 0.8,
                                 'items_weapons_evil_book', 1,
                                 4, projectiles.Projectiles.EvilBook, 15, True,
                                 'Evil Curse'),
        'curse_book': MagicWeapon('curse book', {dmg.DamageTypes.MAGICAL: 600}, 0.6,
                                  'items_weapons_curse_book', 20,
                                  10, projectiles.Projectiles.CurseBook, 40, True,
                                  'Dark Magic Circle'),
        'gravity_wand': MagicWeapon('gravity wand', {dmg.DamageTypes.MAGICAL: 800}, 0.8,
                                    'items_weapons_gravity_wand', 80,
                                    10, projectiles.Projectiles.GravityWand, 160, True,
                                    'Gravity'),
        'double_watcher_wand': MagicWeapon('double watcher wand', {dmg.DamageTypes.MAGICAL: 840}, 0.8,
                                            'items_weapons_double_watcher_wand', 1,
                                            4, projectiles.Projectiles.BeamPair, 12, True,
                                            'Double Watch'),
        'shield_wand': MagicWeapon('shield wand', {dmg.DamageTypes.MAGICAL: 240}, 0.8,
                                   'items_weapons_shield_wand', 80,
                                   10, projectiles.Projectiles.ShieldWand, 100, True,
                                   'Water Shield'),
        'forbidden_curse__spirit': ArcaneWeapon('forbidden curse  spirit', {dmg.DamageTypes.ARCANE: 4}, 0.8,
                                                'items_weapons_forbidden_curse__spirit', 30,
                                                10, projectiles.Projectiles.ForbiddenCurseSpirit, 40, 1.5, True,
                                                'Energy Magic Circle'),
        'forbidden_curse__evil': ArcaneWeapon('forbidden curse  evil', {dmg.DamageTypes.ARCANE: 23}, 0.8,
                                              'items_weapons_forbidden_curse__evil', 1,
                                              5, projectiles.Projectiles.ForbiddenCurseEvil, 10, 0.2, True,
                                              'Dark\'s Curse'),
        'forbidden_curse__time': ForbiddenCurseTime('forbidden curse  time', {}, 0.8,
                                                    'items_weapons_forbidden_curse__time', 10,
                                                    50, projectiles.Projectiles.Projectile, 300, 5, True,
                                                    'Time Adjust'),
        'prism': MagicWeapon('prism', {dmg.DamageTypes.MAGICAL: 8800}, 0.8,
                             'items_weapons_prism', 20,
                             5, projectiles.Projectiles.Beam, 54, True,
                             'Light Focus(Primarily)'),
        'prism_wand': MagicWeapon('prism wand', {dmg.DamageTypes.MAGICAL: 12500}, 0.8,
                                  'items_weapons_prism_wand', 2,
                                  5, projectiles.Projectiles.BeamLight, 24, True,
                                  'Light Focus(Secondarily)'),
        'light_purify': MagicWeapon('light purify', {dmg.DamageTypes.MAGICAL: 3600}, 0.8,
                                     'items_weapons_light_purify', 1,
                                     11, projectiles.Projectiles.LightPurify, 50, True,
                                     'Light Purify'),
        'astigmatism': Astigmatism('astigmatism', {dmg.DamageTypes.MAGICAL: 16000}, 0.1, 'items_weapons_astigmatism',
                                   0, 1, 8, True,
                                   'Energetic Light Focus'),
        'life_wand': LifeWand('life_wand', 'item_weapons_life_wand', 2, 8, True),

        'lights_bible': MagicSet('lights_bible', 'items_weapons_lights_bible',
                                 lambda w: (inventory.TAGS['magic_element_light'] in inventory.ITEMS[w.name.replace(' ', '_')].tags),
                                 'Pseudo Sun'),
        'energy_bible': MagicSet('energy_bible', 'items_weapons_energy_bible',
                                 lambda w: (inventory.TAGS['magic_element_energy'] in inventory.ITEMS[w.name.replace(' ', '_')].tags),
                                 'Energy Pulse', 1),
        'chaos_teleporter': Teleporter('chaos_teleporter', {}, 1, 'items_weapons_chaos_teleporter',
                                       1, 19, 1000, 300, False, 'Chaos Teleport'),
        'chaos_killer': ChaosKiller('chaos_killer', {dmg.DamageTypes.MAGICAL: 320000}, 1, 'items_weapons_chaos_killer',
                                     1, 9, projectiles.Projectiles.Projectile, 40, False, 'Chaos Kill'),
        'skyfire__meteor': MagicWeapon('skyfire__meteor', {dmg.DamageTypes.MAGICAL: 240000}, 1, 'items_weapons_skyfire__meteor',
                                       0, 1, projectiles.Projectiles.Meteor, 8, True, 'Skyfire Meteor'),
        'azure_guard': AzureGuard('azure_guard', {}, 1, 'items_weapons_azure_guard',
                                  1, 24, projectiles.Projectiles.Projectile, 300, False, 'Azure Guard'),

        'forbidden_curse__fire': ArcaneWeapon('forbidden curse  fire', {dmg.DamageTypes.ARCANE: 512}, 0.8,
                                               'items_weapons_forbidden_curse__fire', 111,
                                              89, projectiles.Projectiles.Seraph, 600, 4.5, True,
                                               'The Fire Seraph'),
        'storm': MagicWeapon('storm', {dmg.DamageTypes.MAGICAL: 60000}, 1, 'items_weapons_storm',
                             1, 9, projectiles.Projectiles.Storm, 120, True, 'Storm'),
        'earth_wall': EarthWall('earth_wall', {}, 1, 'items_weapons_earth_wall',
                                1, 12, projectiles.Projectiles.Projectile, 600, False, 'Earth Wall'),
        'lifebringer': MagicWeapon('lifebringer', {}, 1, 'items_weapons_lifebringer',
                                   20, 100, projectiles.Projectiles.LifeBringer, 500, True, 'Life Bringer'),
        'target_dummy': TargetDummy('target_dummy', {}, 1, 'items_weapons_target_dummy',
                                     0, 10, projectiles.Projectiles.Projectile, 15, True, 'Target Dummy'),
        'judgement_light': MagicWeapon('judgement light', {dmg.DamageTypes.MAGICAL: 20000}, 1, 'items_weapons_judgement_light',
                                       10, 220, projectiles.Projectiles.JudgementLight, 800, True, 'Judgement Light'),
        'dark_restrict': MagicWeapon('dark restrict', {}, 1, 'items_weapons_dark_restrict',
                                      1, 14, projectiles.Projectiles.DarkRestrict, 200, True, 'Dark Restrict'),

        'primal__winds_wand': MagicSet('primal  winds wand', 'items_weapons_primal__winds_wand',
                                       lambda w: w.name in [' circulates domain', ' wd circulate clockwise',
                                                            ' wd circulate anticlockwise', ' wd circulate attract',
                                                            ' wd circulate repel', ' wd strong wind', ' wd extinct'], 'Circulate\'s Domain',
                                          -1, ),

        '_circulates_domain': Domain(' circulates domain', {}, 1, 'items_weapons__circulates_domain',
                                     1, 19, 4, 0.02, (150, 250, 230),
                                     1200, True, 'Circulate\'s Domain'),
        '_wd_circulate_clockwise': WdCirculateClockwise(' wd circulate clockwise', {}, 1,
                                                        'items_weapons__wd_circulate_clockwise',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                        True, 'Circulate\'s Domain: Clockwise'),
        '_wd_circulate_anticlockwise': WdCirculateAntiClockwise(' wd circulate anticlockwise', {}, 1,
                                                              'items_weapons__wd_circulate_anticlockwise',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                              True, 'Circulate\'s Domain: Anticlockwise'),
        '_wd_circulate_attract': WdCirculateAttract(' wd circulate attract', {}, 1,
                                                    'items_weapons__wd_circulate_attract',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                    True, 'Circulate\'s Domain: Attract'),
        '_wd_circulate_repel': WdCirculateRepel(' wd circulate repel', {}, 1,
                                                 'items_weapons__wd_circulate_repel',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                 True, 'Circulate\'s Domain: Repel'),
        '_wd_strong_wind': WdStrongWind(' wd strong wind', {dmg.DamageTypes.ARCANE: 128}, 1, 'items_weapons__wd_strong_wind', 0, 1,
                                        projectiles.Projectiles.Projectile, '_circulates_domain', True,
                                        'Circulate\'s Domain: Strong Wind'),
        '_wd_extinct': WdExtinct(' wd extinct', {dmg.DamageTypes.ARCANE: 427}, 1, 'items_weapons__wd_extinct', 0, 1,
                                 projectiles.Projectiles.Projectile, '_circulates_domain', True,
                                 'Circulate\'s Domain: Extinct'),

        'primal__life_wand': MagicSet('primal  life wand', 'items_weapons_primal__life_wand',
                                      lambda w: w.name in [' life domain', ' ld summon tree', ' ld summon cactus',
                                                           ' ld summon coniferous tree', ' ld summon huge tree',
                                                           ' ld summon tree monster', ' ld summon bloodflower',
                                                           ' ld summon soulflower', ' ld heal'],
                                      'Life\'s Domain', style=-1),
        '_life_domain': Domain(' life domain', {}, 1, 'items_weapons__life_domain',
                               1, 19, 4, 0.02, (200, 255, 200),
                               1200, True, 'Life\'s Domain'),
        '_ld_summon_tree': LdSpawn(' ld summon tree', {}, 1, 'items_weapons__ld_summon_tree', 0, 2,
                                    entity.Entities.Tree, '_life_domain', True, 'Life\'s Domain: Tree',
                                   entity.Entities.Tree),
        '_ld_summon_cactus': LdSpawn(' ld summon cactus', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                     entity.Entities.Cactus, '_life_domain', True, 'Life\'s Domain: Cactus',
                                      entity.Entities.Cactus),
        '_ld_summon_coniferous_tree': LdSpawn(' ld summon coniferous tree', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                              entity.Entities.ConiferousTree, '_life_domain', True, 'Life\'s Domain: Coniferous Tree',
                                               entity.Entities.ConiferousTree),
        '_ld_summon_huge_tree': LdSpawn(' ld summon huge tree', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                        entity.Entities.HugeTree, '_life_domain', True, 'Life\'s Domain: Huge Tree',
                                         entity.Entities.HugeTree),
        '_ld_summon_tree_monster': LdSpawn(' ld summon tree monster', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                           entity.Entities.TreeMonster, '_life_domain', True, 'Life\'s Domain: Tree Monster',
                                            entity.Entities.TreeMonster),
        '_ld_summon_bloodflower': LdSpawn(' ld summon bloodflower', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                          entity.Entities.Bloodflower, '_life_domain', True, 'Life\'s Domain: Bloodflower',
                                           entity.Entities.Bloodflower),
        '_ld_summon_soulflower': LdSpawn(' ld summon soulflower', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                          entity.Entities.SoulFlower, '_life_domain', True, 'Life\'s Domain: Soulflower',
                                           entity.Entities.SoulFlower),
        '_ld_heal': LdHeal(' ld heal', {}, 1, 'items_weapons__ld_heal', 0, 1,
                            projectiles.Projectiles.Projectile, '_life_domain', True, 'Life\'s Domain: Heal'),

        'ballet_shoes': MagicWeapon('ballet shoes', {dmg.DamageTypes.MAGICAL: 3200}, 0.1,
                                    'items_weapons_ballet_shoes', 1,
                                    8, projectiles.Projectiles.BalletShoes, 20, True,
                                    'Water Bomb'),
        'tough_gloves': Bow('tough gloves', {dmg.DamageTypes.PIERCING: 7200}, 0.1, 'items_weapons_tough_glove',
                            3, 12, 5000, auto_fire=True),
        'burnt_pan': ComplexWeapon('burnt pan', {dmg.DamageTypes.PHYSICAL: 6000}, {dmg.DamageTypes.PHYSICAL: 6000}, 3,
                                   'items_weapons_burnt_pan', 2, 12, 6, 20, 120, 80, 300,
                                   True, [pg.K_q]),
        'toy_knife': ToyKnife('toy knife', {dmg.DamageTypes.MAGICAL: 1600}, 0.1,
                              'items_weapons_toy_knife', 0, 1, projectiles.Projectiles.Projectile,
                              3, True, 'Water Gather'),
        'worn_notebook': Blade('worn notebook', {dmg.DamageTypes.PHYSICAL: 10800}, 0.1,
                               'items_weapons_worn_notebook', 1, 3, 60, 120),
        'empty_gun': Gun('empty gun', {dmg.DamageTypes.PIERCING: 8400}, 0.1,
                         'items_weapons_empty_gun', 1, 4, 800, auto_fire=True),
    }


set_weapons()

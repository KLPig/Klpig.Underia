import pygame as pg
import random
from src.underia import game, projectiles
from src.physics import vector
from src.resources import position
from src.values import damages as dmg
from src.values import effects
from src.visual import effects as eff
from src import constants

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
        self.d_img = pg.transform.rotate(self.img, 90 - angle)
        self.rot = angle

    def face_to(self, x: int, y: int):
        dx, dy = x - self.x, y - self.y
        self.set_rotation(vector.coordinate_rotation(dx, dy))

    def on_end_attack(self):
        self.display = False

    def update(self):
        if self.display:
            imr = self.d_img.get_rect(center=position.displayed_position((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1])))
            game.get_game().displayer.canvas.blit(self.d_img, imr)
        if self.timer > 1:
            self.timer -= 1
            self.on_attack()
            self.cool = 1
        elif self.timer == 1:
            self.timer = 0
            self.cool = self.cd
            self.on_end_attack()
        elif self.cool:
            self.cool -= 1
        else:
            if 1 in game.get_game().get_mouse_press() or (self.auto_fire and 1 in game.get_game().get_pressed_mouse()):
                self.attack()

class SweepWeapon(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.rot_speed = rot_speed
        self.st_pos = st_pos
        self.double_sided = double_sided

    def on_start_attack(self):
        r = random.choice([-1, 1])
        px, py = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
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
            if r in rot_range or r + 360 in rot_range or (self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() + ((e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                    if not e.hp_sys.is_immune:
                        e.obj.apply_force(vector.Vector(r, self.knock_back * 120000 / e.obj.MASS))
                    e.hp_sys.enable_immume()

class Spear(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, forward_speed: int, st_pos: int, auto_fire: bool = False):
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
                if vector.distance(px, py) < self.img.get_width() + self.pos + ((e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                    if not e.hp_sys.is_immune:
                        e.obj.apply_force(vector.Vector(r, self.knock_back * 120000 / e.obj.MASS))
                    e.hp_sys.enable_immume()

class AutoSweepWeapon(SweepWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False):
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
        px, py = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r

class WillSword(Blade):
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
            if r in rot_range or r + 360 in rot_range or (self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
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
        px, py = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r

class Volcano(Blade):
    def on_start_attack(self):
        for e in game.get_game().entities:
            px, py = e.obj.pos
            if vector.distance(px - game.get_game().player.obj.pos[0], py - game.get_game().player.obj.pos[1]) < 300:
                e.hp_sys.effect(effects.Burning(5, 15))

class NightsEdge(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False):
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
        px, py = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 100 * r)
        n = projectiles.Projectiles.NightsEdge((self.x + game.get_game().player.obj.pos[0] + vx * 200, self.y + game.get_game().player.obj.pos[1] + vy * 200), self.rot - r * 100)
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
            d = 130 - i * 23
            eff.pointed_curve((100 + int(i * 30), int(i * 25), 100 + int(i * 12)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1]) for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 30))
            self.lrot = self.rot

class SpiritualStabber(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False):
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
            d = 200 - i * 23
            eff.pointed_curve((100 + int(i * 12), 200, 200),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1]) for vx, vy in self.rots[:-3]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot

class BalancedStabber(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False):
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
            d = 200 - i * 23
            eff.pointed_curve((50 + int(i * 10), int(i * 30), 50 + int(i * 20)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1]) for vx, vy in self.rots[:-3]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot

class Excalibur(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False):
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
            d = 260 - i * 23
            eff.pointed_curve((255, 200 + int(i * 5), 127 + int(i * 10)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1]) for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot

class TrueExcalibur(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False):
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
            d = 260 - i * 23
            eff.pointed_curve((255, 200 + int(i * 5), 127 + int(i * 10)),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1]) for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot

class TrueNightsEdge(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, rot_speed: int, st_pos: int, double_sided: bool = False):
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
        px, py = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 100 * r)
        n = projectiles.Projectiles.TrueNightsEdge((self.x + game.get_game().player.obj.pos[0] + vx * 200, self.y + game.get_game().player.obj.pos[1] + vy * 200), self.rot - r * 100)
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
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1]) for vx, vy in self.rots[:-2]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot


class MagicSword(AutoSweepWeapon):
    def on_end_attack(self):
        super().on_end_attack()
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(projectiles.Projectiles.MagicSword((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot))

class MagicWeapon(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.projectile = projectile
        self.mana_cost = mana_cost

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot))
        game.get_game().player.mana -= self.mana_cost

class ArcaneWeapon(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, talent_cost: float, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire)
        self.talent_cost = talent_cost

    def on_start_attack(self):
        if game.get_game().player.talent < self.talent_cost:
            self.timer = 0
            return
        game.get_game().player.talent -= self.talent_cost
        super().on_start_attack()

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
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        fps = constants.FPS
        if fps == 40:
            fps = 10
        else:
            fps = 40
        constants.FPS = fps

class MidnightsWand(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False, add_pos: int = 0):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire)
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
            self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            p = self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot)
            p.obj.apply_force(vector.Vector(self.rot, 1000))
            game.get_game().projectiles.append(p)
            self.pts.append((player.obj.pos[0] + self.x, player.obj.pos[1] + self.y))
        self.x, self.y = 0, 0
        game.get_game().player.mana -= self.mana_cost

    def on_attack(self):
        super().on_attack()
        eff.pointed_curve((127, 0, 127), self.pts, 5, salpha=255)

class Hematology(MagicWeapon):
    def __init__(self, name, img: pg.Surface, speed: int, at_time: int, auto_fire: bool = False):
        super().__init__(name, {}, 0, img, speed, at_time, projectiles.Projectiles.Projectile, 30, auto_fire)

    def on_start_attack(self):
        if game.get_game().player.mana < self.mana_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= self.mana_cost
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.hp_sys.heal(30)

class Bow(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img: pg.Surface, speed: int, at_time: int, projectile_speed: int, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.spd = projectile_speed

    def on_start_attack(self):
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < 1000:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        game.get_game().projectiles.append(projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                                              self.y + game.get_game().player.obj.pos[1]),
                                                                                             self.rot, self.spd, self.damages[dmg.DamageTypes.PIERCING]))

class DiscordStorm(Bow):
    def on_start_attack(self):
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < 1000:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        for r in range(-30, 31, 15):
            game.get_game().projectiles.append(projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                                                  self.y + game.get_game().player.obj.pos[1]),
                                                                                                 self.rot + r, self.spd, self.damages[dmg.DamageTypes.PIERCING]))

class DaedelusStormbow(Bow):
    def on_start_attack(self):
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < 1000:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        for i in range(3):
            x, y = mx + random.randint(-500, 500), -game.get_game().displayer.SCREEN_HEIGHT // 2 - 200
            p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x + game.get_game().player.obj.pos[0],
                                                                   y + game.get_game().player.obj.pos[1]),
                                                                  vector.coordinate_rotation(mx - x, my - y) + random.randint(-1, 1), self.spd, self.damages[dmg.DamageTypes.PIERCING])
            game.get_game().projectiles.append(p)
        self.face_to(mx, - 1200)

class TrueDaedalusStormbow(Bow):
    def on_start_attack(self):
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < 1000:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        for i in range(8):
            x, y = mx + random.randint(-800, 800), -game.get_game().displayer.SCREEN_HEIGHT // 2 - 200
            p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x + game.get_game().player.obj.pos[0],
                                                                   y + game.get_game().player.obj.pos[1]),
                                                                  vector.coordinate_rotation(mx - x, my - y) + random.randint(-1, 1), self.spd, self.damages[dmg.DamageTypes.PIERCING])
            game.get_game().projectiles.append(p)
        self.face_to(mx, - 1200)

class Gun(Bow):
    def on_start_attack(self):
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < 1000:
            game.get_game().player.ammo_bullet = (game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        game.get_game().projectiles.append(projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                                                     self.y + game.get_game().player.obj.pos[1]),
                                                                                                    self.rot, self.spd, self.damages[dmg.DamageTypes.PIERCING]))

class MagmaAssaulter(Gun):
    def on_attack(self):
        super().on_attack()
        if pg.K_q in game.get_game().get_keys():
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            px, py = game.get_game().player.obj.pos
            game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), -800))

class Shadow(Gun):
    def on_start_attack(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
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
        'platinum_sword':SweepWeapon('platinum sword', {dmg.DamageTypes.PHYSICAL: 64}, 0.6,
                                                       'items_weapons_platinum_sword', 0,
                                                       15, 16, 120),
        'platinum_blade': Blade('platinum blade', {dmg.DamageTypes.PHYSICAL: 20}, 0.1,
                                                    'items_weapons_platinum_blade', 10,
                                                    12, 30, 180),
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
        'nights_edge': NightsEdge('nights edge', {dmg.DamageTypes.PHYSICAL: 380, dmg.DamageTypes.MAGICAL: 140}, 0.6, 'items_weapons_nights_edge',
                                    1, 18, 20, 100),
        'spiritual_stabber': SpiritualStabber('spiritual stabber', {dmg.DamageTypes.PHYSICAL: 685}, 0.5, 'items_weapons_spiritual_stabber',
                                               2, 6, 40, 170),
        'palladium_sword': Blade('palladium sword', {dmg.DamageTypes.PHYSICAL: 450}, 0.2,
                                 'items_weapons_palladium_sword', 1, 5, 50, 120),
        'mithrill_sword': Blade('mithrill sword', {dmg.DamageTypes.PHYSICAL: 840}, 0.3,
                                    'items_weapons_mithrill_sword', 1, 8, 30, 160),
        'titanium_sword': Blade('titanium sword', {dmg.DamageTypes.PHYSICAL: 1020}, 0.4,
                                     'items_weapons_titanium_sword', 1, 10, 40, 200),
        'balanced_stabber': BalancedStabber('balanced stabber', {dmg.DamageTypes.PHYSICAL: 985}, 2, 'items_weapons_balanced_stabber',
                                              1, 7, 50, 150),
        'excalibur': Excalibur('excalibur', {dmg.DamageTypes.PHYSICAL: 1250, dmg.DamageTypes.MAGICAL: 450}, 0.8, 'items_weapons_excalibur',
                                1, 6, 59, 180),
        'true_excalibur': TrueExcalibur('true excalibur', {dmg.DamageTypes.PHYSICAL: 2020, dmg.DamageTypes.MAGICAL: 620}, 1, 'items_weapons_true_excalibur',
                                         1, 4, 88, 180),
        'true_nights_edge': TrueNightsEdge('true nights edge', {dmg.DamageTypes.PHYSICAL: 5280, dmg.DamageTypes.MAGICAL: 1240}, 0.6, 'items_weapons_true_nights_edge',
                                            1, 32, 60, 100),
        'will_sword': WillSword('will sword', {dmg.DamageTypes.PHYSICAL: 1500}, 2, 'items_weapons_will_sword',
                                1, 6, 28, 90),
        'black_hole_sword': BlackHoleSword('black hole sword', {dmg.DamageTypes.PHYSICAL: 3200}, 0, 'items_weapons_black_hole_sword',
                                        0, 6, 60, 90),

        'spear': Spear('spear', {dmg.DamageTypes.PHYSICAL: 28}, 0.5, 'items_weapons_spear',
                       2, 6, 15, 60, auto_fire=True),
        'platinum_spear': Spear('platinum spear', {dmg.DamageTypes.PHYSICAL: 50}, 0.6, 'items_weapons_platinum_spear',
                                2, 4, 30, 80, auto_fire=True),
        'firite_spear': Spear('firite spear', {dmg.DamageTypes.PHYSICAL: 150}, 0.7, 'items_weapons_firite_spear',
                              2, 10, 20, 100, auto_fire=True),
        'nights_pike': Spear('nights pike', {dmg.DamageTypes.PHYSICAL: 420}, 1.8, 'items_weapons_nights_pike',
                                   2, 5, 60, 160, auto_fire=True),

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
        'spiritual_piercer': Bow('spiritual piercer', {dmg.DamageTypes.PIERCING: 580}, 0.5, 'items_weapons_spiritual_piercer',
                                1, 4, 650, auto_fire=True),
        'discord_storm': DiscordStorm('discord storm', {dmg.DamageTypes.PIERCING: 680}, 0.5, 'items_weapons_discord_storm',
                                      1, 7, 200, auto_fire=True),
        'daedalus_stormbow': DaedelusStormbow('daedalus stormbow', {dmg.DamageTypes.PIERCING: 700}, 0.5, 'items_weapons_daedalus_stormbow',
                                              0, 2, 500, auto_fire=True),
        'true_daedalus_stormbow': TrueDaedalusStormbow('true daedalus stormbow', {dmg.DamageTypes.PIERCING: 1600}, 0.5, 'items_weapons_true_daedalus_stormbow',
                                                       0, 3, 1000, auto_fire=True),

        'pistol': Gun('pistol', {dmg.DamageTypes.PIERCING: 28}, 0.1, 'items_weapons_pistol',
                      3, 15, 15),
        'rifle': Gun('rifle', {dmg.DamageTypes.PIERCING: 56}, 0.2, 'items_weapons_rifle',
                     10, 12, 20, auto_fire=True),
        'submachine_gun': Gun('submachine gun', {dmg.DamageTypes.PIERCING: 8}, 0.15, 'items_weapons_submachine_gun',
                              0, 2, 50, auto_fire=True),
        'magma_assaulter': MagmaAssaulter('magma assaulter', {dmg.DamageTypes.PIERCING: 60}, 0.5, 'items_weapons_magma_assaulter',
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

        'glowing_splint': MagicWeapon('glowing splint', {dmg.DamageTypes.MAGICAL: 5}, 0.1,
                                                         'items_weapons_glowing_splint', 6,
                                                         10, projectiles.Projectiles.Glow, 4),
        'copper_wand': MagicWeapon('copper wand', {dmg.DamageTypes.MAGICAL: 32}, 0.2,
                                                       'items_weapons_copper_wand', 8,
                                                       8, projectiles.Projectiles.CopperWand, 5),
        'iron_wand': MagicWeapon('iron wand', {dmg.DamageTypes.MAGICAL: 36}, 0.1,
                                                      'items_weapons_iron_wand', 2,
                                                      6, projectiles.Projectiles.IronWand, 4),
        'platinum_wand': MagicWeapon('platinum wand', {dmg.DamageTypes.MAGICAL: 42}, 0.3,
                                                         'items_weapons_platinum_wand', 2,
                                                         5, projectiles.Projectiles.PlatinumWand, 5, True),
        'burning_book': MagicWeapon('burning book', {dmg.DamageTypes.MAGICAL: 72}, 0.5,
                                                         'items_weapons_burning_book', 5,
                                                         10, projectiles.Projectiles.BurningBook, 9, True),
        'talent_book': MagicWeapon('talent book', {dmg.DamageTypes.MAGICAL: 24}, 0.7,
                                                       'items_weapons_talent_book', 0,
                                                       2, projectiles.Projectiles.TalentBook, 2, True),
        'hematology': Hematology('hematology', 'items_weapons_hematology', 2, 3, True),
        'blood_wand': MagicWeapon('blood wand', {dmg.DamageTypes.MAGICAL: 75}, 0.1,
                                                       'items_weapons_blood_wand', 4,
                                                       12, projectiles.Projectiles.BloodWand, 8, True),
        'rock_wand': MagicWeapon('rock wand', {dmg.DamageTypes.MAGICAL: 65}, 0.6,
                                                      'items_weapons_rock_wand', 0,
                                                      4, projectiles.Projectiles.RockWand, 3, True),
        'midnights_wand': MidnightsWand('midnights wand', {dmg.DamageTypes.MAGICAL: 110}, 0.3,
                                                         'items_weapons_midnights_wand', 2,
                                        12, projectiles.Projectiles.MidnightsWand, 4, True, 80),
        'spiritual_destroyer': MagicWeapon('spiritual destroyer', {dmg.DamageTypes.MAGICAL: 688}, 0.5,
                                                         'items_weapons_spiritual_destroyer', 1,
                                                         5, projectiles.Projectiles.SpiritualDestroyer, 6, True),
        'evil_book': MagicWeapon('evil book', {dmg.DamageTypes.MAGICAL: 1550}, 0.8,
                                                       'items_weapons_evil_book', 1,
                                                       4, projectiles.Projectiles.EvilBook, 15, True),
        'curse_book': MagicWeapon('curse book', {dmg.DamageTypes.MAGICAL: 600}, 0.6,
                                                       'items_weapons_curse_book', 20,
                                                       10, projectiles.Projectiles.CurseBook, 40, True),
        'gravity_wand': MagicWeapon('gravity wand', {dmg.DamageTypes.MAGICAL: 800}, 0.8,
                                                         'items_weapons_gravity_wand', 80,
                                                         10, projectiles.Projectiles.GravityWand, 160, True),
        'shield_wand': MagicWeapon('shield wand', {dmg.DamageTypes.MAGICAL: 240}, 0.8,
                                                            'items_weapons_shield_wand', 80,
                                                            10, projectiles.Projectiles.ShieldWand, 100, auto_fire=True),
        'forbidden_curse__spirit': ArcaneWeapon('forbidden curse  spirit', {dmg.DamageTypes.ARCANE: 4}, 0.8,
                                                         'items_weapons_forbidden_curse__spirit', 30,
                                                         10, projectiles.Projectiles.ForbiddenCurseSpirit, 40, 1.5, True),
        'forbidden_curse__evil': ArcaneWeapon('forbidden curse  evil', {dmg.DamageTypes.ARCANE: 23}, 0.8,
                                                         'items_weapons_forbidden_curse__evil', 1,
                                                         5, projectiles.Projectiles.ForbiddenCurseEvil, 10, 0.2, True),
        'forbidden_curse__time': ForbiddenCurseTime('forbidden curse  time', {}, 0.8,
                                                         'items_weapons_forbidden_curse__time', 10,
                                                         50, projectiles.Projectiles.Projectile, 300, 5, True),
    }

set_weapons()

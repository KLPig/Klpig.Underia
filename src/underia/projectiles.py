from tkinter.constants import PROJECTING

from src.physics import mover, vector
from src.underia import game, weapons
from src.values import damages, effects
from src.resources import position
import math
import pygame as pg

class ProjectileMotion(mover.Mover):
    MASS = 20
    FRICTION = 0.98
    TOUCHING_DAMAGE = 10

    def __init__(self, pos, rotation, spd = 0):
        super().__init__(pos)
        self.rotation = rotation
        self.apply_force(vector.Vector(self.rotation, spd * 12))

    def on_update(self):
        self.apply_force(vector.Vector(self.rotation, 20))

class WeakProjectileMotion(ProjectileMotion):
    MASS = 10
    FRICTION = 0.9
    TOUCHING_DAMAGE = 5

    def __init__(self, pos, rotation):
        super().__init__(pos, rotation)
        self.apply_force(vector.Vector(self.rotation, 500))

    def on_update(self):
        pass


class Projectiles:

    class Projectile:
        NAME = 'Projectile'

        def get_closest_entity(self):
            closest_entity = None
            closest_distance = 1000000
            for entity in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - entity.obj.pos[0], self.obj.pos[1] - entity.obj.pos[1]) < closest_distance:
                    closest_entity = entity
                    closest_distance = vector.distance(self.obj.pos[0] - entity.obj.pos[0], self.obj.pos[1] - entity.obj.pos[1])
            if closest_entity is None:
                return None, 0
            return closest_entity, vector.coordinate_rotation(closest_entity.obj.pos[0] - self.obj.pos[0], closest_entity.obj.pos[1] - self.obj.pos[1])

        def __init__(self, pos, img = None, motion: type(ProjectileMotion) = ProjectileMotion):
            self.obj = motion(pos)
            self.img: pg.Surface | None = img
            self.d_img = self.img
            self.rot = 0
            self.dead = False

        def set_rotation(self, rot):
            self.rot = rot
            self.d_img = pg.transform.rotate(self.img, 90 - rot)

        def rotate(self, angle):
            self.set_rotation((self.rot + angle) % 360)

        def update(self):
            self.set_rotation(self.obj.velocity.get_net_rotation())
            displayer = game.get_game().displayer
            self.obj.update()
            imr = self.d_img.get_rect(center = position.displayed_position((self.obj.pos[0], self.obj.pos[1])))
            displayer.canvas.blit(self.d_img, imr)

    class MagicSword(Projectile):
        NAME = 'Magic Sword'

        def __init__(self, pos, rotation):
            self.img = game.get_game().graphics['projectiles_magic_sword']
            self.obj = ProjectileMotion(pos, rotation)
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.tick = 0
            self.dead = False

        def update(self):
            super().update()
            self.tick += 1
            if self.tick > 200:
                self.dead = True
            imr = self.d_img.get_rect(center = self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(center = entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['magic_sword'].damages[damages.DamageTypes.PHYSICAL] * 0.8 * game.get_game().player.attack * game.get_game().player.attacks[0], damages.DamageTypes.PHYSICAL)
                    self.dead = True
                    break

    class Glow(Projectile):
        NAME = 'Glow'

        def __init__(self, pos, rotation):
            self.obj = WeakProjectileMotion(pos, rotation)
            self.img = game.get_game().graphics['projectiles_glow']
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False

        def update(self):
            super().update()
            if self.obj.velocity.get_net_value() < 3:
                self.dead = True
            imr = self.d_img.get_rect(center = self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(center = entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['glowing_splint'].damages[damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL)
                    entity.hp_sys.effect(effects.Burning(5, weapons.WEAPONS['glowing_splint'].damages[damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[2] // 10 + 1))
                    self.dead = True
                    break

    class BurningBook(Projectile):
        NAME = 'Burning Book'

        def __init__(self, pos, rotation):
            self.obj = ProjectileMotion(pos, rotation)
            self.img = game.get_game().graphics['projectiles_glow']
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False
            self.tick = 0

        def update(self):
            _, target_rot = self.get_closest_entity()
            if target_rot - self.rot > 180:
                target_rot -= 360
            if target_rot - self.rot < -180:
                target_rot += 360
            self.obj.velocity.reset()
            self.obj.velocity.vectors[0].value *= math.cos(math.radians(.15 * (target_rot - self.obj.rotation)))
            self.obj.rotation = (self.obj.rotation + .15 * (target_rot - self.obj.rotation))
            self.tick += 1
            super().update()
            if self.tick > 100:
                self.dead = True
            imr = self.d_img.get_rect(center = self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(center = entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['burning_book'].damages[damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[2] * 0.5, damages.DamageTypes.MAGICAL)
                    entity.hp_sys.effect(effects.Burning(9, weapons.WEAPONS['burning_book'].damages[damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[2] // 10 + 1))
                    self.dead = True

    class TalentBook(Projectile):
        NAME = 'Talent Book'

        def __init__(self, pos, rotation):
            self.obj = ProjectileMotion(pos, rotation)
            self.img = game.get_game().graphics['projectiles_talent_book']
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False
            self.tick = 0

        def update(self):
            _, target_rot = self.get_closest_entity()
            if target_rot - self.rot > 180:
                target_rot -= 360
            if target_rot - self.rot < -180:
                target_rot += 360
            self.obj.velocity.reset()
            self.obj.velocity.vectors[0].value *= math.cos(math.radians(.92 * (target_rot - self.obj.rotation)))
            self.obj.rotation = (self.obj.rotation + .92 * (target_rot - self.obj.rotation))
            self.tick += 1
            super().update()
            if self.tick > 100:
                self.dead = True
            imr = self.d_img.get_rect(center = self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(center = entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['talent_book'].damages[damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL)
                    self.dead = True


    class CopperWand(Glow):
        DAMAGE_AS = 'copper_wand'
        IMG = 'projectiles_copper_wand'

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.img = game.get_game().graphics[self.IMG]

        def update(self):
            super().update()
            if self.obj.velocity.get_net_value() < 3:
                self.dead = True
            imr = self.d_img.get_rect(center = self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(center = entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS[self.DAMAGE_AS].damages[damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL)
                    self.dead = True
                    break

    class IronWand(CopperWand):
        DAMAGE_AS = 'iron_wand'

    class PlatinumWand(CopperWand):
        DAMAGE_AS = 'platinum_wand'
        IMG = 'projectiles_platinum_wand'

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.obj = ProjectileMotion(pos, rotation)
            self.obj.apply_force(vector.Vector(rotation, 100))
            self.tick = 0

        def update(self):
            self.tick += 1
            if self.tick > 100:
                self.dead = True
            super().update()

    class RockWand(PlatinumWand):
        DAMAGE_AS = 'rock_wand'
        IMG = 'projectiles_rock_wand'

    class NightsEdge(PlatinumWand):
        DAMAGE_AS = 'nights_edge'
        IMG = 'projectiles_nights_edge'

        def update(self):
            super().update()
            self.tick += 1
            if self.tick > 100:
                self.dead = True
            else:
                self.dead = False

    class BloodWand(PlatinumWand):
        DAMAGE_AS = 'blood_wand'
        IMG = 'projectiles_blood_wand'

    class Arrow(Projectile):
        NAME = 'Arrow'
        SPEED = 6
        DAMAGES = 7
        IMG = 'arrow'

        def __init__(self, pos, rotation, speed, damage):
            self.obj = ProjectileMotion(pos, rotation, speed + self.SPEED)
            self.dmg = damage + self.DAMAGES
            self.img = game.get_game().graphics['projectiles_' + self.IMG]
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False
            self.tick = 0
            self.obj.rotation = self.rot

        def update(self):
            ox, oy = self.obj.pos
            super().update()
            ax, ay = self.obj.pos
            self.tick += 1
            if self.tick > 300:
                self.dead = True
            if ox != ax:
                aax = -(ox - ax) / abs(ox - ax) * 10
            else:
                aax = 1
            if oy != ay:
                aay = -(oy - ay) / abs(oy - ay) * 10
            else:
                aay = 1
            for x in range(int(ox), int(ax) + 1, int(aax)):
                for y in range(int(oy), int(ay) + 1, int(aay)):
                    pos = (x, y)
                    imr = self.d_img.get_rect(center = pos)
                    for entity in game.get_game().entities:
                        if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(center = entity.obj.pos).collidepoint(x, y):
                            entity.hp_sys.damage(self.dmg * game.get_game().player.attack * game.get_game().player.attacks[1], damages.DamageTypes.PIERCING)
                            self.dead = True
                    if self.dead:
                        break
                if self.dead:
                    break

    class MagicArrow(Arrow):
        DAMAGES = 18
        SPEED = 5
        IMG = 'magic_arrow'

    class BloodArrow(Arrow):
        DAMAGES = 30
        SPEED = 12
        IMG = 'blood_arrow'

    class Bullet(Arrow):
        NAME = 'Bullet'
        DAMAGES = 12
        SPEED = 210
        IMG = 'bullet'

    class PlatinumBullet(Bullet):
        DAMAGES = 16
        IMG = 'platinum_bullet'

    class Plasma(Bullet):
        DAMAGES = 35
        SPEED = 120
        IMG = 'plasma'

    class RockBullet(Bullet):
        DAMAGES = 60
        SPEED = 20
        IMG = 'rock_bullet'


AMMOS = {
    'arrow': Projectiles.Arrow,
    'magic_arrow': Projectiles.MagicArrow,
    'blood_arrow': Projectiles.BloodArrow,
    'bullet': Projectiles.Bullet,
    'platinum_bullet': Projectiles.PlatinumBullet,
    'plasma': Projectiles.Plasma,
    'rock_bullet': Projectiles.RockBullet,
}

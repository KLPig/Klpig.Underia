import copy
import math

import pygame as pg

from src.physics import mover, vector
from src.resources import position
from src.underia import game, weapons
from src.values import damages, effects
from src.visual import effects as eff


class ProjectileMotion(mover.Mover):
    MASS = 20
    FRICTION = 0.98
    TOUCHING_DAMAGE = 10

    def __init__(self, pos, rotation, spd=0):
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
                if not entity.obj.IS_OBJECT:
                    continue
                if vector.distance(self.obj.pos[0] - entity.obj.pos[0],
                                   self.obj.pos[1] - entity.obj.pos[1]) - 1000 * entity.IS_MENACE < closest_distance:
                    closest_entity = entity
                    closest_distance = vector.distance(self.obj.pos[0] - entity.obj.pos[0],
                                                       self.obj.pos[1] - entity.obj.pos[1]) - 1000 * entity.IS_MENACE
            if closest_entity is None:
                return None, 0
            return closest_entity, vector.coordinate_rotation(closest_entity.obj.pos[0] - self.obj.pos[0],
                                                              closest_entity.obj.pos[1] - self.obj.pos[1])

        def __init__(self, pos, img=None, motion: type(ProjectileMotion) = ProjectileMotion):
            self.obj = motion(pos)
            self.img: pg.Surface | None = img
            self.d_img = self.img
            self.rot = 0
            self.dead = False

        def set_rotation(self, rot):
            self.rot = rot
            self.d_img = pg.transform.rotate(self.img, 90 - rot)
            self.d_img = pg.transform.scale_by(self.d_img, 1 / game.get_game().player.get_screen_scale())

        def rotate(self, angle):
            self.set_rotation((self.rot + angle) % 360)

        def update(self):
            displayer = game.get_game().displayer
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            self.set_rotation(self.obj.velocity.get_net_rotation())
            if p[1] > game.get_game().displayer.SCREEN_HEIGHT + 500:
                self.dead = True
            if p[0] < -500 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 500 or p[1] < -500 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 500:
                return
            self.obj.update()
            imr = self.d_img.get_rect(center=position.displayed_position((self.obj.pos[0], self.obj.pos[1])))
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
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['magic_sword'].damages[
                                             damages.DamageTypes.PHYSICAL] * 0.8 * game.get_game().player.attack *
                                         game.get_game().player.attacks[0],
                                         damages.DamageTypes.PHYSICAL)
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
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['glowing_splint'].damages[
                                             damages.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                         game.get_game().player.attacks[2],
                                         damages.DamageTypes.MAGICAL)
                    entity.hp_sys.effect(effects.Burning(5, weapons.WEAPONS['glowing_splint'].damages[
                        damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[
                                                             2] // 10 + 1))
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
            self.damage()

        def damage(self):
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['burning_book'].damages[
                                             damages.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                         game.get_game().player.attacks[2] * 0.5, damages.DamageTypes.MAGICAL,
                                         )
                    entity.hp_sys.effect(effects.Burning(9, weapons.WEAPONS['burning_book'].damages[
                        damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[
                                                             2] // 10 + 1))
                    self.dead = True

    class TalentBook(Projectile):
        NAME = 'Talent Book'
        IMG = 'projectiles_talent_book'
        DAMAGE_AS = 'talent_book'

        def __init__(self, pos, rotation):
            self.obj = ProjectileMotion(pos, rotation)
            self.img = game.get_game().graphics[self.IMG]
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
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS[self.DAMAGE_AS].damages[
                                             damages.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                         game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL)
                    self.dead = True

    class CopperWand(Glow):
        DAMAGE_AS = 'copper_wand'
        IMG = 'projectiles_copper_wand'
        DMG_TYPE = damages.DamageTypes.MAGICAL

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.img = game.get_game().graphics[self.IMG]

        def update(self):
            super().update()
            if self.obj.velocity.get_net_value() < 3:
                self.dead = True

        def damage(self):
            kb = weapons.WEAPONS[self.DAMAGE_AS].knock_backc
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(
                        weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                        game.get_game().player.attacks[2], self.DMG_TYPE)
                    self.dead = True
                    if not entity.hp_sys.is_immune:
                        r = vector.coordinate_rotation(entity.obj.pos[0] - self.obj.pos[0],
                                                       entity.obj.pos[1] - self.obj.pos[1])
                        entity.obj.apply_force(vector.Vector(r, kb * 120000 / entity.obj.MASS))
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

    class ForbiddenCurseEvil(RockWand):
        DAMAGE_AS = 'forbidden_curse__evil'
        IMG = 'projectiles_forbidden_curse__evil'
        DMG_TYPE = damages.DamageTypes.ARCANE

        def update(self):
            super().update()
            self.obj.apply_force(vector.Vector(self.obj.velocity.get_net_rotation(), 200))

    class BalletShoes(TalentBook):
        DAMAGE_AS = 'ballet_shoes'
        IMG = 'projectiles_ballet_shoes'

    class MagicCircle(Projectile):
        DAMAGE_AS = 'magic_circle'
        IMG = 'projectiles_magic_circle'
        ROT_SPEED = 2
        ALPHA = 127
        DURATION = 100
        AUTO_FOLLOW = True
        DMG_TYPE = damages.DamageTypes.MAGICAL

        def __init__(self, pos, rotation):
            self.obj = mover.Mover(pos)
            self.img = copy.copy(game.get_game().graphics[self.IMG])
            self.img.set_alpha(self.ALPHA)
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False
            self.tick = 0
            self.ttx = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))

        def update(self):
            mx, my = self.ttx
            if self.AUTO_FOLLOW:
                self.obj.pos = ((mx + self.obj.pos[0]) // 2, (my + self.obj.pos[1]) // 2)
            else:
                self.obj.pos = game.get_game().player.obj.pos
            self.tick += 1
            if self.tick > self.DURATION:
                self.dead = True
            displayer = game.get_game().displayer
            self.set_rotation(self.ROT_SPEED * self.tick)
            imr = self.d_img.get_rect(center=position.displayed_position((self.obj.pos[0], self.obj.pos[1])))
            displayer.canvas.blit(self.d_img, imr)
            for entity in game.get_game().entities:
                ex, ey = entity.obj.pos
                if vector.distance(self.obj.pos[0] - ex,
                                   self.obj.pos[1] - ey) < self.d_img.get_width() // 2 + entity.d_img.get_width() // 2:
                    entity.hp_sys.damage(
                        weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                        game.get_game().player.attacks[2], self.DMG_TYPE)

    class CactusWand(MagicCircle):
        DAMAGE_AS = 'cactus_wand'
        IMG = 'projectiles_cactus_wand'
        ROT_SPEED = 0.2
        ALPHA = 255
        DURATION = 200

    class CurseBook(MagicCircle):
        DAMAGE_AS = 'curse_book'
        IMG = 'projectiles_curse_book'

    class LightPurify(MagicCircle):
        DAMAGE_AS = 'light_purify'
        IMG = 'projectiles_light_purify'
        ROT_SPEED = 10
        ALPHA = 80

    class ShieldWand(MagicCircle):
        DAMAGE_AS = 'shield_wand'
        IMG = 'projectiles_shield_wand'
        DURATION = 200
        ROT_SPEED = 5
        AUTO_FOLLOW = False

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            game.get_game().player.hp_sys.effect(effects.Shield(10, 255))

    class ForbiddenCurseSpirit(MagicCircle):
        DAMAGE_AS = 'forbidden_curse__spirit'
        IMG = 'projectiles_forbidden_curse__spirit'
        DURATION = 240
        ALPHA = 80
        ROT_SPEED = 3
        AUTO_FOLLOW = True
        DMG_TYPE = damages.DamageTypes.ARCANE

    class GravityWand(MagicCircle):
        DAMAGE_AS = 'gravity_wand'
        IMG = 'projectiles_gravity_wand'
        DURATION = 40
        ROT_SPEED = 10
        ALPHA = 200
        AUTO_FOLLOW = False

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            game.get_game().player.hp_sys.effect(effects.Gravity(1, 255))

    class Beam(Projectile):
        WIDTH = 120
        LENGTH = 2000
        DAMAGE_AS = 'prism'
        DMG = None
        COLOR = (255, 255, 255)
        DMG_TYPE = damages.DamageTypes.MAGICAL
        DURATION = 30
        FOLLOW_PLAYER = True

        def __init__(self, pos, rotation):
            ax, ay = vector.rotation_coordinate(rotation)
            self.tar_reg = abs(ax - ay * (-1 if ((ax > 0) != (ay > 0)) else 1))
            self.lf = ax > 0
            self.lr = ay > 0
            self.slope = ax / ay
            self.tick = 0
            self.obj = ProjectileMotion(pos, rotation, 0)
            self.dead = False
            self.start_pos = None
            self.end_pos = None
            self.rot = rotation
            self.start_pos = pos[0] + ax * 100, pos[1] + ay * 100
            self.end_pos = self.start_pos[0] + ax * self.LENGTH, self.start_pos[1] + ay * self.LENGTH
            self.pos = pos
            self.pap = None

        def update(self):
            if self.pap is None:
                self.pap = self.pos[0] - game.get_game().player.obj.pos[0], self.pos[1] - game.get_game().player.obj.pos[1]
            ax, ay = vector.rotation_coordinate(self.rot)
            self.tar_reg = abs(ax - ay * (-1 if ((ax > 0) != (ay > 0)) else 1))
            self.lf = ax > 0
            self.lr = ay > 0
            self.slope = ax / ay
            if self.FOLLOW_PLAYER:
                self.pos = game.get_game().player.obj.pos[0] + self.pap[0], game.get_game().player.obj.pos[1] + self.pap[1]
            self.obj.pos = self.pos
            self.start_pos = self.pos[0] + ax * 50 + self.WIDTH / 2 * ax, self.pos[1] + ay * 50 + self.WIDTH / 2 * ay
            self.end_pos = self.start_pos[0] + ax * self.LENGTH, self.start_pos[1] + ay * self.LENGTH
            for entity in game.get_game().entities:
                ex = entity.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = entity.obj.pos[1] - game.get_game().player.obj.pos[1]
                if abs(self.slope * ey - ex) < self.WIDTH + (entity.d_img.get_width() + entity.d_img.get_height()) // 2 and \
                        ((ex > 0) == self.lf) and ((ey > 0) == self.lr) and vector.distance(ey, ex) < self.LENGTH:
                    entity.hp_sys.damage((weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] if self.DMG is None
                                          else self.DMG) * \
                                         game.get_game().player.attack * game.get_game().player.attacks[2],
                                         self.DMG_TYPE)
            if self.tick > self.DURATION:
                self.dead = True
            self.tick += 1
            size = min(self.WIDTH, int(self.tick ** 3) if self.tick < self.DURATION // 2 else \
                min(self.WIDTH, int((self.DURATION - self.tick) ** 3)))
            size = int(size / game.get_game().player.get_screen_scale())
            pg.draw.circle(game.get_game().displayer.canvas, self.COLOR, position.displayed_position(self.start_pos),
                           size // 2)
            pg.draw.line(game.get_game().displayer.canvas, self.COLOR, position.displayed_position(self.start_pos),
                         position.displayed_position(self.end_pos), size)

    class WatcherWand(Beam):
        WIDTH = 10
        LENGTH = 200
        DAMAGE_AS = 'watcher_wand'
        COLOR = (255, 0, 0)
        DURATION = 10

    class LifeWoodenWand(Beam):
        WIDTH = 20
        LENGTH = 1000
        DAMAGE_AS = 'life_wooden_wand'
        COLOR = (0, 80, 0)
        DURATION = 15

    class BeamLight(Beam):
        WIDTH = 100
        LENGTH = 1500
        DAMAGE_AS = 'prism_wand'
        COLOR = (200, 255, 200)
        DURATION = 20

    class LightsBeam(Beam):
        WIDTH = 30
        LENGTH = 1500
        DAMAGE_AS = 'lights_bible'
        COLOR = (255, 220, 180)
        DURATION = 15

    class LifeDevourer(Beam):
        WIDTH = 16
        LENGTH = 2000
        DAMAGE_AS = 'life_devourer'
        COLOR = (0, 80, 0)
        DURATION = 10
        FOLLOW_PLAYER = False

    class Excalibur(NightsEdge):
        DAMAGE_AS = 'excalibur'
        IMG = 'projectiles_excalibur'

    class TrueExcalibur(Excalibur):
        DAMAGE_AS = 'true_excalibur'

    class TrueNightsEdge(NightsEdge):
        DAMAGE_AS = 'true_nights_edge'
        IMG = 'projectiles_nights_edge'

        def update(self):
            super().update()
            self.tick += 1
            if self.tick > 100:
                self.dead = True
            else:
                self.dead = False
            self.img = pg.transform.scale_by(game.get_game().graphics['projectiles_nights_edge'],
                                             min(4.0, 0.3 * 1.15 ** self.tick))

    class BloodWand(PlatinumWand):
        DAMAGE_AS = 'blood_wand'
        IMG = 'projectiles_blood_wand'

    class MidnightsWand(BloodWand):
        DAMAGE_AS = 'midnights_wand'
        IMG = 'projectiles_midnights_wand'

    class SpiritualDestroyer(BloodWand):
        DAMAGE_AS = 'spiritual_destroyer'
        IMG = 'projectiles_spiritual_destroyer'

    class EvilBook(BloodWand):
        DAMAGE_AS = 'evil_book'
        IMG = 'projectiles_evil_book'

    class Arrow(Projectile):
        NAME = 'Arrow'
        SPEED = 6
        DAMAGES = 7
        IMG = 'arrow'
        AIMING = 0
        DELETE = True
        TAIL_SIZE = 0
        TAIL_WIDTH = 3
        TAIL_COLOR = (255, 255, 255)

        def __init__(self, pos, rotation, speed, damage):
            self.obj = ProjectileMotion(pos, rotation, speed + self.SPEED)
            self.dmg = damage + self.DAMAGES
            self.img = game.get_game().graphics['projectiles_' + self.IMG]
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(rotation)
            self.ps = [pos]

        def update(self):
            t, target_rot = self.get_closest_entity()
            self.rot %= 360
            target_rot %= 360
            if target_rot - self.rot > 180:
                target_rot -= 360
            if target_rot - self.rot < -180:
                target_rot += 360
            self.obj.velocity.reset()
            if self.AIMING:
                self.obj.velocity.vectors[0].value *= math.cos(
                    math.radians(self.AIMING * (target_rot - self.obj.rotation)))
                self.obj.rotation = (self.obj.rotation + self.AIMING * (target_rot - self.obj.rotation)) % 360
            ox, oy = self.obj.pos
            super().update()
            ax, ay = self.obj.pos
            if ox == ax and oy == ay:
                self.dead = True
                return
            if len(self.ps) > self.TAIL_SIZE:
                self.ps.pop(0)
            self.ps.append((ax, ay))
            if self.TAIL_SIZE:
                eff.pointed_curve(self.TAIL_COLOR, self.ps, self.TAIL_WIDTH, 255)
            self.tick += 1
            if self.tick > 300:
                self.dead = True
            if ox != ax:
                aax = -(ox - ax) / abs(ox - ax) * 50
            else:
                aax = 1
            if oy != ay:
                aay = -(oy - ay) / abs(oy - ay) * 50
            else:
                aay = 1
            cd = []
            for x in range(int(ox), int(ax) + 1, int(aax)):
                for y in range(int(oy), int(ay) + 1, int(aay)):
                    pos = (x, y)
                    imr = self.d_img.get_rect(center=pos)
                    for entity in game.get_game().entities:
                        if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                                center=entity.obj.pos).collidepoint(x, y) and entity not in cd:
                            entity.hp_sys.damage(
                                self.dmg * game.get_game().player.attack * game.get_game().player.attacks[1],
                                damages.DamageTypes.PIERCING)
                            if self.DELETE:
                                self.dead = True
                            else:
                                cd.append(entity)
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

    class ShadowBullet(Bullet):
        DAMAGES = 24
        SPEED = 100
        IMG = 'shadow_bullet'
        AIMING = 0.3

        def __init__(self, pos, rotation, speed, damage):
            super().__init__(pos, rotation, speed, damage)
            self.poss = [game.get_game().player.obj.pos]

        def update(self):
            self.poss.append(self.obj.pos)
            if len(self.poss) > 5:
                self.poss.pop(0)
            super().update()
            eff.pointed_curve((60, 0, 60), self.poss, 5, 255)

    class QuickArrow(Arrow):
        DAMAGES = 40
        SPEED = 200
        DELETE = False
        IMG = 'quick_arrow'

    class QuickBullet(Bullet):
        DAMAGES = 80
        SPEED = 500
        DELETE = False
        IMG = 'quick_bullet'
        TAIL_SIZE = 5
        TAIL_WIDTH = 5
        TAIL_COLOR = (255, 127, 0)


AMMOS = {
    'arrow': Projectiles.Arrow,
    'magic_arrow': Projectiles.MagicArrow,
    'blood_arrow': Projectiles.BloodArrow,
    'bullet': Projectiles.Bullet,
    'platinum_bullet': Projectiles.PlatinumBullet,
    'plasma': Projectiles.Plasma,
    'rock_bullet': Projectiles.RockBullet,
    'shadow_bullet': Projectiles.ShadowBullet,
    'quick_arrow': Projectiles.QuickArrow,
    'quick_bullet': Projectiles.QuickBullet,
}

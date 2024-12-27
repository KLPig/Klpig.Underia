import copy
import math
import random
import pygame as pg

from src.physics import mover, vector
from src.resources import position
from src.underia import game, weapons
from src.values import damages, effects, DamageTypes
from src.visual import effects as eff
from src.visual import particle_effects


class ProjectileMotion(mover.Mover):
    MASS = 20
    FRICTION = 0.98
    TOUCHING_DAMAGE = 10

    def __init__(self, pos, rotation=0, spd=0):
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
            if type(self) is Projectiles.Glow:
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
        WT = damages.DamageTypes.MAGICAL

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.img = game.get_game().graphics[self.IMG]

        def update(self):
            super().update()
            if self.obj.velocity.get_net_value() < 3:
                self.dead = True
            self.damage()

        def damage(self):
            kb = weapons.WEAPONS[self.DAMAGE_AS].knock_back
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    at_mt = {damages.DamageTypes.PHYSICAL: 0, damages.DamageTypes.PIERCING: 1,
                             damages.DamageTypes.ARCANE: 2, damages.DamageTypes.MAGICAL: 2}[self.WT]
                    entity.hp_sys.damage(
                        weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                        game.get_game().player.attacks[at_mt], self.DMG_TYPE)
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
        SPD = 100

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.obj = ProjectileMotion(pos, rotation, spd=self.SPD)
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

    class WindBlade(PlatinumWand):
        DAMAGE_AS = 'blade_wand'
        IMG = 'projectiles_wind_blade'
        WT = damages.DamageTypes.MAGICAL
        SPD = 320

    class NightsEdge(PlatinumWand):
        DAMAGE_AS = 'nights_edge'
        IMG = 'projectiles_nights_edge'
        WT = damages.DamageTypes.PHYSICAL

        def update(self):
            self.WT = damages.DamageTypes.PHYSICAL
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
            if self.tick < 5:
                self.img = copy.copy(game.get_game().graphics[self.IMG])
                self.img = pg.transform.scale_by(self.img, self.tick ** 2 / 25)
                self.img.set_alpha(self.ALPHA * self.tick ** 2 // 25)
                self.d_img = self.img
            elif self.tick > self.DURATION - 5:
                self.img = copy.copy(game.get_game().graphics[self.IMG])
                self.img = pg.transform.scale_by(self.img, (self.DURATION - self.tick) ** 2 / 25)
                self.img.set_alpha(self.ALPHA * (self.DURATION - self.tick) ** 2 // 25)
                self.d_img = self.img
            else:
                self.img = copy.copy(game.get_game().graphics[self.IMG])
                self.img.set_alpha(self.ALPHA)
                self.d_img = self.img
            if self.tick > self.DURATION:
                self.dead = True
            displayer = game.get_game().displayer
            self.set_rotation(self.ROT_SPEED * self.tick)
            imr = self.d_img.get_rect(center=position.displayed_position((self.obj.pos[0], self.obj.pos[1])))
            displayer.canvas.blit(self.d_img, imr)
            self.damage()

        def damage(self):
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

    class Storm(MagicCircle):
        DAMAGE_AS ='storm'
        IMG = 'projectiles_storm'
        ROT_SPEED = 28
        ALPHA = 127
        DURATION = 120
        AUTO_FOLLOW = True

        def update(self):
            super().update()
            self.obj.FRICTION = 0.5
            self.obj.MASS = 50000000
            for entity in game.get_game().entities:
                entity.obj.object_gravitational(self.obj)
                self.obj.object_gravitational(entity.obj)
            for p in game.get_game().projectiles:
                p.obj.object_gravitational(self.obj)
                self.obj.object_gravitational(p.obj)
            game.get_game().player.obj.object_gravitational(self.obj)
            self.obj.object_gravitational(game.get_game().player.obj)

    class LifeBringer(MagicCircle):
        DAMAGE_AS = 'lifebringer'
        IMG = 'projectiles_lifebringer'
        ROT_SPEED = 20
        ALPHA = 127
        DURATION = 120
        AUTO_FOLLOW = True

        def update(self):
            super().update()
            px, py = game.get_game().player.obj.pos
            if vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < self.img.get_width() // 2:
                game.get_game().player.hp_sys.heal(3)
                game.get_game().player.talent = min(game.get_game().player.talent + 0.25,
                                                    game.get_game().player.max_talent)
                game.get_game().player.mana = min(game.get_game().player.mana + 6, game.get_game().player.max_mana)


        def damage(self):
            pass

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

    class JudgementLight(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_judgement_light']
            self.d_img = self.img
            self.tx, self.ty = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.tick = 0
            self.te = []
            for e in game.get_game().entities:
                ex, ey = e.obj.pos
                if vector.distance(self.tx - ex, self.ty - ey) < 300:
                    self.te.append(e)
            self.tep = [e.obj.pos for e in self.te]

        def update(self):
            self.tick += 1
            for i in range(len(self.te)):
                self.te[i].obj.pos = self.tep[i]
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 200),
                           position.displayed_position((self.tx, self.ty)), 300 / game.get_game().player.get_screen_scale(),
                           2)
            if self.tick < 80:
                w = 1
            elif self.tick < 90:
                w = 1 + (self.tick - 80) ** 2 * 6
            elif self.tick < 210:
                w = 600
            elif self.tick < 220:
                w = 601 - (self.tick - 210) ** 2 * 6
            else:
                self.dead = True
                return
            w += int(math.sin(self.tick / 10) * 10)
            sf = pg.Surface((600, 2600), pg.SRCALPHA)
            sf.fill((0, 0, 0, 0))
            pg.draw.line(sf, (255, 255, 200),
                         (300, 300), (300, 2300), width=w)
            pg.draw.circle(sf, (255, 255, 200),
                           (300, 2300), w // 2)
            sf.set_alpha(100)
            sf = pg.transform.scale_by(sf, 1 / game.get_game().player.get_screen_scale())
            sfr = sf.get_rect(midbottom=position.displayed_position((self.tx,
                                                                     self.ty + 500 / game.get_game().player.get_screen_scale())))
            game.get_game().displayer.canvas.blit(sf, sfr)
            for e in game.get_game().entities:
                ex, ey = e.obj.pos
                if vector.distance(self.tx - ex, self.ty - ey) < w // 2:
                    e.hp_sys.damage(weapons.WEAPONS['judgement_light'].damages[damages.DamageTypes.MAGICAL] *
                                     game.get_game().player.attack * game.get_game().player.attacks[2],
                                     damages.DamageTypes.MAGICAL)

    class DarkRestrict(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.tick = 0
            self.img = game.get_game().graphics['entity_null']
            self.d_img = self.img
            self.tx, self.ty = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.obj.pos = self.tx, self.ty
            self.te = []
            for e in game.get_game().entities:
                ex, ey = e.obj.pos
                if vector.distance(self.tx - ex, self.ty - ey) < 800:
                    self.te.append(e)
            self.tep = [e.obj.pos for e in self.te]

        def update(self):
            self.tick += 1
            if self.tick < 10:
                w = self.tick ** 2 * 4
            elif self.tick < 70:
                w = 400
            elif self.tick < 80:
                w = 400 - (self.tick - 70) ** 2 * 4
            else:
                self.dead = True
                return
            pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0),
                           position.displayed_position((self.tx, self.ty)), w, 2)
            for i in range(len(self.te)):
                pg.draw.line(game.get_game().displayer.canvas, (0, 0, 0),
                             position.displayed_position(self.tep[i]),
                             position.displayed_position(self.te[i].obj.pos), 10)
                self.te[i].obj.pos = self.tep[i]


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
                                         game.get_game().player.attack * game.get_game().player.attacks[{DamageTypes.PHYSICAL: 0,
                                                                                                         DamageTypes.PIERCING: 1,
                                                                                                         DamageTypes.MAGICAL: 2,
                                                                                                         DamageTypes.ARCANE: 2}[self.DMG_TYPE]],
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

    class BladeBeam(Beam):
        WIDTH = 100
        LENGTH = 3200
        DAMAGE_AS = 'the_blade'
        COLOR = (0, 150, 50)
        DURATION = 12
        DMG_TYPE = damages.DamageTypes.PHYSICAL

    class BladeBeamSmall(BladeBeam):
        WIDTH = 30
        LENGTH = 3200
        DAMAGE_AS = 'the_blade'
        COLOR = (127, 255, 127)
        DURATION = 10
        DMG_TYPE = damages.DamageTypes.PHYSICAL

    class WatcherWand(Beam):
        WIDTH = 10
        LENGTH = 200
        DAMAGE_AS = 'watcher_wand'
        COLOR = (255, 0, 0)
        DURATION = 10

    class LifeWoodenSword(Beam):
        WIDTH = 30
        LENGTH = 150
        DAMAGE_AS = 'life_wooden_sword'
        COLOR = (0, 80, 0)
        DURATION = 5
        DMG_TYPE = damages.DamageTypes.PHYSICAL

    class LifeWoodenWand(Beam):
        WIDTH = 20
        LENGTH = 1000
        DAMAGE_AS = 'life_wooden_wand'
        COLOR = (0, 80, 0)
        DURATION = 15

    class BloodSacrifice(Beam):
        WIDTH = 40
        LENGTH = 1000
        DAMAGE_AS = 'blood_sacrifice'
        COLOR = (255, 0, 0)
        DURATION = 28

    class RedBeam(Beam):
        WIDTH = 40
        LENGTH = 1800
        DAMAGE_AS = 'double_watcher_wand'
        COLOR = (255, 100, 100)
        DURATION = 20

    class GreenBeam(Beam):
        WIDTH = 30
        LENGTH = 2400
        DAMAGE_AS = 'double_watcher_wand'
        COLOR = (100, 255, 100)
        DURATION = 20

    class BeamPair(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            r = Projectiles.RedBeam((pos[0] + random.randint(-300, 300), pos[1] + random.randint(-300, 300)),
                                    rotation)
            r.rot = vector.coordinate_rotation(mx - r.pos[0], my - r.pos[1])
            g = Projectiles.GreenBeam((pos[0] + random.randint(-300, 300), pos[1] + random.randint(-300, 300)),
                                      rotation)
            g.rot = vector.coordinate_rotation(mx - g.pos[0], my - g.pos[1])
            if random.randint(0, 1):
                game.get_game().projectiles.append(r)
                game.get_game().projectiles.append(g)
            else:
                game.get_game().projectiles.append(g)
                game.get_game().projectiles.append(r)
            self.dead = True

        def update(self):
            pass

    class Meteor(Projectile):
        DAMAGE_AS = 'skyfire__meteor'
        IMG = 'projectiles_meteor'
        DMG_TYPE = damages.DamageTypes.MAGICAL

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics[self.IMG]
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(rotation)
            self.ps = [pos]
            self.tpx, self.tpy = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.tpx += random.randint(-100, 100)
            self.tpy += random.randint(-100, 100)

        def update(self):
            self.tick += 1
            self.obj.pos = self.tpx, self.tpy - 4500 + 5 * self.tick ** 2
            self.ps.append(self.obj.pos)
            if len(self.ps) > 5:
                self.ps.pop(0)
            super().update()
            # eff.pointed_curve((255, 100, 150), self.ps, 50, 127)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position((self.tpx, self.tpy)),
                           radius=600 // game.get_game().player.get_screen_scale(), width=2)
            if self.tick >= 30:
                for e in game.get_game().entities:
                    if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 600:
                        e.hp_sys.damage(
                            weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                            game.get_game().player.attacks[{DamageTypes.PHYSICAL: 0,
                                                             DamageTypes.PIERCING: 1,
                                                             DamageTypes.MAGICAL: 2,
                                                             DamageTypes.ARCANE: 2}[self.DMG_TYPE]], self.DMG_TYPE)
                self.dead = True
                game.get_game().displayer.effect(particle_effects.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                                     r=40, t=15, sp=30, n=30))


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
        WT = damages.DamageTypes.PHYSICAL

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

    class Seraph(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = copy.copy(game.get_game().graphics['projectiles_seraph'])
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(0)

        def update(self):
            px, py = game.get_game().player.obj.pos
            self.obj.pos = (px, py - 1000)
            self.tick += 1
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.pos),
                           radius=2000 // game.get_game().player.get_screen_scale(), width=12)
            if self.tick < 10:
                self.img.set_alpha(self.tick * 10)
            elif self.tick < 90:
                if self.tick % 8 == 0:
                    game.get_game().displayer.effect(particle_effects.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                                         n=120, r=10, t=50, sp=40))
                    for e in game.get_game().entities:
                        if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 2000:
                            e.hp_sys.damage(
                                weapons.WEAPONS['forbidden_curse__fire'].damages[damages.DamageTypes.ARCANE] * game.get_game().player.attack *
                                game.get_game().player.attacks[2], damages.DamageTypes.ARCANE)
            elif self.tick < 100:
                self.img.set_alpha(100 - (self.tick - 90) * 10)
            else:
                self.dead = True
            super().update()


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

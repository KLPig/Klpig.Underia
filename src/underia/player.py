import math
import random

import pygame as pg

from src.physics import mover, vector
from src.resources import time, position, cursors
from src.underia import game, styles, inventory, weapons, entity, projectiles, player_profile
from src.values import hp_system, damages, effects
from src import constants


class PlayerObject(mover.Mover):
    MASS = 20
    FRICTION = 0.8
    SPEED = 20

    def on_update(self):
        keys = game.get_game().get_pressed_keys()
        if pg.K_w in keys:
            self.apply_force(vector.Vector(0, self.SPEED))
        elif pg.K_s in keys:
            self.apply_force(vector.Vector(180, self.SPEED))
        if pg.K_a in keys:
            self.apply_force(vector.Vector(270, self.SPEED))
        elif pg.K_d in keys:
            self.apply_force(vector.Vector(90, self.SPEED))


class Player:
    REGENERATION = 0.015
    MAGIC_REGEN = 0.04
    SIMULATE_DISTANCE = constants.SIMULATE_DISTANCE

    def __init__(self):
        self.obj = PlayerObject((400, 300))
        self.hp_sys = hp_system.HPSystem(200)
        self.ax, self.ay = 0, 0
        self.weapons = 4 * [weapons.WEAPONS['null']]
        self.sel_weapon = 0
        self.inventory = inventory.Inventory()
        self.accessories = 6 * ['null']
        self.sel_accessory = 0
        self.open_inventory = False
        self.attack = 0
        self.mana = 0
        self.max_mana = 30
        self.recipes = []
        self.sel_recipe = 0
        self.light_level = 0
        self.ammo = ('null', 0)
        self.ammo_bullet = ('null', 0)
        self.attacks = [1, 1, 1]
        self.in_ui = False
        self.touched_item = ''
        self.hp_sys(op='config', immune_time=10, true_drop_speed_max_value=1)
        self.talent = 0
        self.max_talent = 0
        self.strike = 0
        self.scale = 1.0
        self.profile = player_profile.PlayerProfile()
        self.ntcs = []

    def calculate_touching_defense(self):
        ACCESSORY_DEFENSE = {'shield': 7, 'green_ring': 18, 'orange_ring': -2, 'sheath': 16, 'quiver': 8,
                             'hat': 2, 'firite_helmet': 28, 'firite_cloak': 14, 'firite_pluvial': 6,
                             'windstorm_swordman_mark': 32, 'windstorm_assassin_mark': 17, 'windstorm_warlock_mark': 5,
                             'paladins_mark': 85, 'daedalus_mark': 55, 'palladium_glove': 90, 'mithrill_glove': 85,
                             'titanium_glove': 108, 'cowboy_hat': 120, 'cloudy_glasses': 188}
        defe = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DEFENSE.keys():
                defe += ACCESSORY_DEFENSE[self.accessories[i]]
        return defe

    def calculate_physical_defense(self):
        ACCESSORY_DEFENSE = {'shield': 12}
        defe = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DEFENSE.keys():
                defe += ACCESSORY_DEFENSE[self.accessories[i]]
        return defe

    def calculate_magical_defense(self):
        ACCESSORY_DEFENSE = {'blue_ring': 5, 'firite_helmet': 19, 'firite_cloak': 7, 'firite_pluvial': 12,
                             'windstorm_swordman_mark': 34, 'windstorm_assassin_mark': 18, 'windstorm_warlock_mark': 12,
                             'paladins_mark': 70, 'daedalus_mark': 45, 'palladium_glove': 65, 'mithrill_glove': 95,
                             'titanium_glove': 40, 'cowboy_hat': 150, 'cloudy_glasses': 128}
        defe = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DEFENSE.keys():
                defe += ACCESSORY_DEFENSE[self.accessories[i]]
        return defe

    def calculate_regeneration(self):
        ACCESSORY_REGEN = {'soul_bottle': 0.0075, 'blue_ring': -0.015, 'quiver': 0.0075, 'hat': 0.015,
                           'firite_helmet': .0225, 'firite_cloak': .0075, 'firite_pluvial': .0375,
                           'windstorm_swordman_mark': .045, 'windstorm_assassin_mark': .015,
                           'windstorm_warlock_mark': .09,
                           'paladins_mark': .075, 'daedalus_mark': .03, 'palladium_glove': .27, 'mithrill_glove': .045,
                           'titanium_glove': .15, 'necklace_of_life': .5, 'cowboy_hat': .16}
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.6:
            ACCESSORY_REGEN['terrified_necklace'] = -0.0075
        regen = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_REGEN.keys():
                regen += ACCESSORY_REGEN[self.accessories[i]]
        return regen

    def calculate_magic_regeneration(self):
        ACCESSORY_REGEN = {'natural_necklace': 0.06, 'magic_anklet': 0.06, 'blue_ring': 0.13, 'hat': 0.1, 'firite_pluvial': .12,
                           'windstorm_warlock_mark': .225,
                           'palladium_glove': .12, 'mithrill_glove': .6, 'titanium_glove': .48, 'necklace_of_life': 1}
        regen = 0.04
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_REGEN.keys():
                regen += ACCESSORY_REGEN[self.accessories[i]]
        regen *= 1.0 + int(self.profile.point_wisdom ** 1.5) / 300
        return regen

    def calculate_damage(self):
        ACCESSORY_DAMAGE = {'dangerous_necklace': 0.12, 'winds_necklace': -0.35, 'windstorm_swordman_mark': -.12,
                            'windstorm_assassin_mark': -.12, 'windstorm_warlock_mark': -.12, 'paladins_mark': -.15,
                            'daedalus_mark': -.15, 'palladium_glove': .25, 'mithrill_glove': .32,
                            'titanium_glove': .5, 'cowboy_hat': -.2, 'cloudy_glasses': -.2}
        dmg = 1.0 + int(self.profile.point_strength ** 1.5) / 300
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        if len([1 for e in self.hp_sys.effects if e.NAME == 'Faithless Curse']):
            dmg *= 0.2
        return dmg

    def calculate_speed(self):
        ACCESSORY_SPEED = {'magic_anklet': .2,
                            'orange_ring': 0.32, 'quiver': 0.15, 'firite_cloak': .45,
                           'winds_necklace': .5, 'wings': .8, 'honest_flyer': -.2, 'palladium_glove': .16,
                           'mithrill_glove': .8, 'titanium_glove': .2, 'cowboy_hat': .5, 'cloudy_glasses': .3}
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.6:
            ACCESSORY_SPEED['terrified_necklace'] = 0.4
        spd = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_SPEED.keys():
                spd += ACCESSORY_SPEED[self.accessories[i]]
        spd *= 1.0 + int(self.profile.point_agility ** 1.5) / 300
        return spd

    def calculate_melee_damage(self):
        ACCESSORY_DAMAGE = {'sheath': .18, 'firite_helmet': .3, 'windstorm_swordman_mark': .45, 'paladins_mark': .66,
                            'cloudy_glasses': 1.2}
        dmg = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        if self.profile.point_melee <= 0:
            dmg *= 0.91 ** abs(self.profile.point_melee)
        else:
            dmg *= 1 + self.profile.point_melee ** 1.5 * 2 / 100
        return dmg

    def calculate_ranged_damage(self):
        ACCESSORY_DAMAGE = {'quiver': .10, 'firite_cloak': .32, 'winds_necklace': .2, 'windstorm_assassin_mark': .56,
                            'daedalus_mark': .72, 'cowboy_hat': .9}
        dmg = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        if self.profile.point_ranged <= 0:
            dmg *= 0.91 ** abs(self.profile.point_ranged)
        else:
            dmg *= 1 + self.profile.point_ranged ** 1.5 * 2 / 100
        return dmg

    def calculate_magic_damage(self):
        ACCESSORY_DAMAGE = {'hat': .3, 'firite_pluvial': .44, 'windstorm_warlock_mark': .6}
        dmg = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        if self.profile.point_magic <= 0:
            dmg *= 0.91 ** abs(self.profile.point_magic)
        else:
            dmg *= 1 + self.profile.point_magic ** 1.5 * 2 / 100
        return dmg

    def calculate_air_resistance(self):
        ACCESSORY_AIR_RESISTANCE = {'wings': 0.4, 'honest_flyer': 0.2}
        air_res = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_AIR_RESISTANCE.keys():
                air_res *= ACCESSORY_AIR_RESISTANCE[self.accessories[i]]
        return air_res

    def get_max_screen_scale(self):
        ACCESSORY_SIZE = {'aimer': 1.5, 'winds_necklace': 1.1, 'cowboy_hat': 1.4}
        t = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_SIZE.keys():
                t *= ACCESSORY_SIZE[self.accessories[i]]
        t *= 1 + 0.01 * self.profile.point_agility
        return t

    def get_screen_scale(self):
        return self.scale

    def get_light_level(self):
        if len([1 for e in game.get_game().entities if type(e) is entity.Entities.AbyssEye]):
            return 0
        if len([1 for accessory in self.accessories if
                inventory.TAGS['light_source'] in inventory.ITEMS[accessory].tags]):
            b = 5
        else:
            b = 0
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['nights_edge']:
            b = max(0, b - 4)
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['true_nights_edge']:
            b = max(0, b - 4)
        return b

    def get_night_vision(self):
        if len([1 for accessory in self.accessories if
                inventory.TAGS['night_vision'] in inventory.ITEMS[accessory].tags]):
            b = 50
        else:
            b = 0
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['nights_edge']:
            b = max(0, b - 20)
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['true_nights_edge']:
            b = max(0, b - 10)
        return b

    def calculate_strike_chance(self):
        return 0.08

    def update(self):
        self.ntcs = []
        self.talent = min(self.talent + 0.005 + math.sqrt(self.max_talent) / 2000 + (self.max_talent - self.talent) / 1000, self.max_talent)
        self.hp_sys.pos = self.obj.pos
        self.attack = self.calculate_damage()
        self.strike = self.calculate_strike_chance()
        self.attacks = [self.calculate_melee_damage() * (1 + (random.random() < self.strike)),
                        self.calculate_ranged_damage() * (1 + (random.random() < self.strike)),
                        self.calculate_magic_damage() * (1 + (random.random() < self.strike))]
        if len([1 for eff in self.hp_sys.effects if eff.NAME == 'Mana Sickness']):
            self.attack *= 0.5
        self.obj.SPEED = self.calculate_speed() * 20
        self.obj.FRICTION = 1 - 0.2 * self.calculate_air_resistance()
        for w in weapons.WEAPONS.values():
            try:
                if w.domain_open:
                    self.ntcs.append(f'{w.name} is open.')
                    self.obj.FRICTION = 0
            except AttributeError:
                pass
        self.REGENERATION = 0.015 + self.calculate_regeneration()
        self.MAGIC_REGEN = self.calculate_magic_regeneration()
        self.hp_sys.defenses[damages.DamageTypes.TOUCHING] = self.calculate_touching_defense()
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = self.calculate_physical_defense()
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = self.calculate_magical_defense()
        if len([1 for eff in self.hp_sys.effects if eff.NAME in ['Shield', 'Justice Time']]):
            self.hp_sys.defenses[damages.DamageTypes.TOUCHING] += 1145114
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += 1145114
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 1145114
        if len([1 for eff in self.hp_sys.effects if eff.NAME in ['Shield']]):
            self.obj.FRICTION = 0
        if len([1 for eff in self.hp_sys.effects if eff.NAME in ['Justice Time']]):
            self.obj.SPEED *= 4
            self.attack *= 6
        if len([1 for eff in self.hp_sys.effects if eff.NAME == 'Gravity']):
            self.obj.apply_force(vector.Vector(180, 200))
        if pg.K_e in game.get_game().get_keys():
            self.open_inventory = not self.open_inventory

        tp_r = self.talent / self.max_talent if self.max_talent else 1
        if tp_r < .8:
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] *= tp_r * 1.25
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] *= tp_r * 1.25
            self.hp_sys.defenses[damages.DamageTypes.TOUCHING] *= tp_r * 1.25
            self.ntcs.append(f'Low Talent: Defense -{int(100 * (.8 - tp_r) * 1.25)}%')
        if tp_r < .5:
            self.attack *= tp_r * 2
            self.ntcs.append(f'Low Talent: Attack -{int(100 * (.5 - tp_r) * 2)}%')
        if tp_r < .4:
            self.obj.SPEED *= tp_r * 2.5
            self.ntcs.append(f'Low Talent: Speed -{int(100 * (.4 - tp_r) * 2.5)}%')
        if tp_r < .2:
            self.MAGIC_REGEN = 0
            self.REGENERATION = 0
            self.ntcs.append(f'Low Talent: Disable Regen.')
        self.hp_sys.heal(self.REGENERATION)
        self.mana = min(self.mana + self.MAGIC_REGEN, self.max_mana)
        displayer = game.get_game().displayer
        self.obj.update()
        self.ax, self.ay = game.get_game().get_anchor()
        pos = position.displayed_position(self.obj.pos)
        sf = self.profile.get_surface(*self.profile.get_color())
        sz = int(40 / self.get_screen_scale())
        sf = pg.transform.scale(sf, (sz, sz))
        displayer.canvas.blit(sf, (pos[0] - sz // 2, pos[1] - sz // 2))
        self.hp_sys.update()
        w = self.weapons[self.sel_weapon]
        if pg.K_EQUALS in game.get_game().get_pressed_keys():
            self.scale = min(self.scale + 0.05, self.get_max_screen_scale())
        if pg.K_MINUS in game.get_game().get_pressed_keys():
            self.scale = max(self.scale - 0.05, 0.8)
        if inventory.TAGS['magic_weapon'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
            if pg.K_y in game.get_game().get_keys():
                if 'windstorm_warlock_mark' in self.accessories:
                    if self.mana >= w.mana_cost * 20 and w.projectile is not projectiles.Projectiles.Projectile:
                        self.mana -= w.mana_cost * 20
                        for i in range(25):
                            x, y = self.obj.pos
                            x += random.randint(-200, 200)
                            y += random.randint(-200, 200)
                            mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                            pj = w.projectile((x, y), vector.coordinate_rotation(mx - x, my - y))
                            game.get_game().projectiles.append(pj)
        elif inventory.TAGS['bow'] in inventory.ITEMS[w.name.replace(' ', '_')].tags or inventory.TAGS['gun'] in \
                inventory.ITEMS[w.name.replace(' ', '_')].tags:
            if pg.K_y in game.get_game().get_keys():
                if 'windstorm_assassin_mark' in self.accessories:
                    if self.mana >= 60:
                        self.mana -= 60
                        mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                        self.obj.apply_force(
                            vector.Vector(vector.coordinate_rotation(mx - self.obj.pos[0], my - self.obj.pos[1]), 3000))
                elif 'daedalus_mark' in self.accessories:
                    if self.mana >= 60:
                        self.mana -= 60
                        if inventory.TAGS['bow'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
                            ammo = self.ammo[0]
                        else:
                            ammo = self.ammo_bullet[0]
                        ammo = projectiles.AMMOS[ammo]
                        mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                        for i in range(40):
                            x, y = mx + random.randint(-100 - i * 20,
                                                       100 + i * 20), my - game.get_game().displayer.SCREEN_HEIGHT // 2 - i * 12
                            pj = ammo((x, y), vector.coordinate_rotation(mx - x, my - y) + random.randint(-2, 2), 600,
                                      1200)
                            game.get_game().projectiles.append(pj)
                elif 'cowboy_hat' in self.accessories:
                    if self.mana >= 400:
                        self.mana -= 400
                        self.hp_sys.effect(effects.JusticeTime(2, 5))
        else:
            if pg.K_y in game.get_game().get_keys():
                if 'windstorm_swordman_mark' in self.accessories:
                    if not w.cool and self.mana >= 80:
                        self.mana -= 80
                        w.attack()
                        px, py = self.obj.pos
                        for e in game.get_game().entities:
                            ax = e.obj.pos[0] - px
                            ay = e.obj.pos[1] - py
                            if vector.distance(ax, ay) < 500:
                                e.hp_sys.damage(w.damages[damages.DamageTypes.PHYSICAL] * 3,
                                                damages.DamageTypes.PHYSICAL)
                                e.obj.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay), 4000))
                elif 'paladins_mark' in self.accessories:
                    if not w.cool and self.mana >= 40:
                        self.mana -= 40
                        w.attack()
                        w.timer = 30
                        px, py = self.obj.pos
                        for e in game.get_game().entities:
                            ax = e.obj.pos[0] - px
                            ay = e.obj.pos[1] - py
                            if vector.distance(ax, ay) < 500:
                                e.hp_sys.damage(w.damages[damages.DamageTypes.PHYSICAL] * 10,
                                                damages.DamageTypes.PHYSICAL)
                                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ax, ay), 15))
                elif 'cloudy_glasses' in self.accessories:
                    if self.mana >= 600:
                        self.mana -= 600
                        for e in game.get_game().entities:
                            if not e.obj.IS_OBJECT:
                                e.hp_sys.hp = 0
        if self.hp_sys.hp <= 1:
            self.hp_sys.hp = self.hp_sys.max_hp
            self.hp_sys.effects = []
            game.get_game().entities = []
            game.get_game().projectiles = []
            game.get_game().damage_texts = []
            self.obj.pos = (0, 0)

    def ui(self):
        self.in_ui = False
        self.touched_item = ''
        displayer = game.get_game().displayer
        displayer.SCREEN_WIDTH = displayer.canvas.get_width()
        displayer.SCREEN_HEIGHT = displayer.canvas.get_height()
        hp_l = min(300.0, self.hp_sys.max_hp // 2)
        mp_l = min(300.0, self.max_mana)
        tp_l = 8 * self.max_talent
        hp_p = self.hp_sys.hp / self.hp_sys.max_hp
        mp_p = self.mana / self.max_mana
        tp_p = self.talent / self.max_talent if self.max_talent else 0
        sd_p = min(1, sum([v for n, v in game.get_game().player.hp_sys.shields]) / game.get_game().player.hp_sys.max_hp)
        pg.draw.rect(displayer.canvas, (80, 0, 0), (10, 10, hp_l, 25))
        pg.draw.rect(displayer.canvas, (0, 0, 80), (10 + hp_l, 10, mp_l, 25))
        pg.draw.rect(displayer.canvas, (0, 80, 0), (10 + hp_l + mp_l, 10, tp_l, 25))
        pg.draw.rect(displayer.canvas, (255, 0, 0), (10, 10, hp_l * hp_p, 25))
        pg.draw.rect(displayer.canvas, (255, 255, 0), (10, 10, hp_l * sd_p, 25))
        pg.draw.rect(displayer.canvas, (0, 0, 255), (10 + hp_l + mp_l - mp_l * mp_p, 10, mp_l * mp_p, 25))
        pg.draw.rect(displayer.canvas, (0, 255, 0), (10 + hp_l + mp_l, 10, tp_l * tp_p, 25))
        pg.draw.rect(displayer.canvas, (255, 255, 255), (10, 10, hp_l + mp_l + tp_l, 25), width=2)
        for i in range(len(self.hp_sys.effects)):
            img = pg.transform.scale(game.get_game().graphics['effect_' + self.hp_sys.effects[i].IMG], (72, 72))
            imr = img.get_rect(
                topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(self.hp_sys.effects) + 80 * i, 10))
            displayer.canvas.blit(img, imr)
        for i in range(len(self.hp_sys.effects)):
            img = pg.transform.scale(game.get_game().graphics['effect_' + self.hp_sys.effects[i].IMG], (72, 72))
            imr = img.get_rect(
                topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(self.hp_sys.effects) + 80 * i, 10))
            if imr.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                f = displayer.font.render(f"{self.hp_sys.effects[i].NAME} ({self.hp_sys.effects[i].timer}s)", True,
                                          (255, 255, 255))
                fr = f.get_rect(topright=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                displayer.canvas.blit(f, fr)
        for _entity in game.get_game().entities:
            _entity.obj.touched_player = False
            _entity.obj.object_collision(self.obj, (_entity.img.get_width() + _entity.img.get_height()) // 4 + 50)
            if self.obj.object_collision(_entity.obj, (_entity.img.get_width() + _entity.img.get_height()) // 4 + 50):
                _entity.obj.touched_player = True
                if _entity.obj.TOUCHING_DAMAGE and not self.hp_sys.is_immune:
                    self.hp_sys.damage(_entity.obj.TOUCHING_DAMAGE, damages.DamageTypes.TOUCHING)
                    self.hp_sys.enable_immume()
            self.obj.object_gravitational(_entity.obj)
            _entity.obj.object_gravitational(self.obj)
        if pg.Rect(10, 10, 200 + self.max_mana, 25).collidepoint(
                game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            f = displayer.font.render(
                f"HP: {int(self.hp_sys.hp) + int(sum([v for n, v in game.get_game().player.hp_sys.shields]))}/{self.hp_sys.max_hp} MP: {int(self.mana)}/{self.max_mana}"
                f" TP: {int(self.talent)}/{int(self.max_talent)}",
                True, (255, 255, 255))
            displayer.canvas.blit(f, game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        if time.time_interval(game.get_game().clock.time, 0.1, 0.01):
            self.hp_sys.heal(self.REGENERATION)
        for i in range(len(self.weapons)):
            if i % len(self.weapons) == 0 and i:
                break
            styles.item_display(10 + i * 60, 80,
                                self.weapons[i % len(self.weapons)].name.replace(' ', '_'), str(i + 1),
                                '1', 0.75, selected=i == self.sel_weapon)
        for i in range(len(self.weapons)):
            if i % len(self.weapons) == 0 and i:
                break
            styles.item_mouse(10 + i * 60, 80,
                              self.weapons[i % len(self.weapons)].name.replace(' ', '_'), str(i),
                              '1', 0.75)
            rect = pg.Rect(10 + i * 60, 80, 60, 60)
            if rect.collidepoint(
                    game.get_game().displayer.reflect(*pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                self.sel_weapon = i % len(self.weapons)
        try:
            for i, ww in enumerate(self.weapons[self.sel_weapon].weapons):
                styles.item_display(10 + i * 60, 150, ww.name.replace(' ', '_'), self.weapons[self.sel_weapon].PRESET_KEY_SET[i], '1', 0.75)
            for i, ww in enumerate(self.weapons[self.sel_weapon].weapons):
                styles.item_mouse(10 + i * 60, 150, ww.name.replace(' ', '_'), str(i), '1', 0.75)
        except AttributeError:
            pass
        if self.open_inventory:
            for i in range(len(self.accessories)):
                styles.item_display(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90,
                                    self.accessories[i].replace(' ', '_'), str(i), '1', 1,
                                    selected=i == self.sel_accessory)
            l = game.get_game().displayer.SCREEN_WIDTH // 2 // 80
            for i in range(l):
                for j in range(l):
                    if i + j * l < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * l]
                        item = inventory.ITEMS[item]
                        styles.item_display(10 + i * 80, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 80,
                                            item.id, str(i + j * l + 1), str(amount), 1)
            for i in range(l):
                for j in range(l):
                    if i + j * l < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * l]
                        item = inventory.ITEMS[item]
                        styles.item_mouse(10 + i * 80, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 80, item.id,
                                          str(i + j * l + 1), str(amount), 1)
                        rect = pg.Rect(10 + i * 80, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 80, 80, 80)
                        if rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                            if pg.K_q in game.get_game().get_keys():
                                del self.inventory.items[item.id]
                        if rect.collidepoint(game.get_game().displayer.reflect(
                                *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                            if inventory.TAGS['accessory'] in item.tags:
                                self.inventory.remove_item(item)
                                if self.accessories[self.sel_accessory] != 'null':
                                    self.inventory.add_item(inventory.ITEMS[self.accessories[self.sel_accessory]])
                                self.accessories[self.sel_accessory] = item.id
                            elif inventory.TAGS['weapon'] in item.tags:
                                self.inventory.remove_item(item)
                                if self.weapons[self.sel_weapon].name != 'null':
                                    self.inventory.add_item(
                                        inventory.ITEMS[self.weapons[self.sel_weapon].name.replace(' ', '_')])
                                self.weapons[self.sel_weapon] = weapons.WEAPONS[item.id]
                            elif item.id == 'mana_crystal':
                                if self.max_mana < 120:
                                    self.max_mana += 15
                                    self.inventory.remove_item(item)
                            elif item.id == 'firy_plant':
                                if self.hp_sys.max_hp < 500:
                                    self.hp_sys.max_hp += 20
                                    self.inventory.remove_item(item)
                            elif item.id == 'spiritual_heart':
                                if self.hp_sys.max_hp >= 500 and self.max_mana >= 120:
                                    self.hp_sys.max_hp = 600
                                    self.max_mana = 300
                                    self.inventory.remove_item(item)
                                    game.get_game().stage = max(game.get_game().stage, 1)
                                    self.profile.add_point(1)
                            elif item.id == 'life_fruit':
                                if self.hp_sys.max_hp >= 600 and self.max_mana >= 300 and self.max_talent >= 10:
                                    self.hp_sys.max_hp = 1000
                                    self.max_mana = 800
                                    self.max_talent = 50
                                    self.inventory.remove_item(item)
                                    self.profile.add_point(2)
                            elif item.id == 'mystery_core':
                                if self.max_talent < 10:
                                    self.max_talent += 1
                                else:
                                    self.talent = min(self.talent + 5, self.max_talent)
                                self.inventory.remove_item(item)
                            elif inventory.TAGS['ammo_arrow'] in item.tags:
                                self.ammo = (item.id, self.inventory.items[item.id])
                                self.inventory.items[item.id] = 0
                                self.inventory.add_item(inventory.ITEMS[self.ammo[0]], self.ammo[1])
                            elif inventory.TAGS['ammo_bullet'] in item.tags:
                                self.ammo_bullet = (item.id, self.inventory.items[item.id])
                                self.inventory.items[item.id] = 0
                                self.inventory.add_item(inventory.ITEMS[self.ammo_bullet[0]], self.ammo_bullet[1])
                            elif item.id == 'suspicious_eye':
                                entity.entity_spawn(entity.Entities.TrueEye, 2000, 2000, 0, 1145, 100000)
                            elif item.id == 'fire_slime':
                                entity.entity_spawn(entity.Entities.MagmaKing, 2000, 2000, 0, 1145, 100000)
                            elif item.id == 'wind':
                                entity.spawn_sandstorm()
                            elif item.id == 'blood_substance':
                                entity.entity_spawn(entity.Entities.AbyssEye, 1600, 1600, 0, 1145, 100000)
                            elif item.id == 'mechanic_eye':
                                entity.entity_spawn(entity.Entities.FaithlessEye, 2000, 2000, 0, 1145, 100000)
                                entity.entity_spawn(entity.Entities.TruthlessEye, 2000, 2000, 0, 1145, 100000)
                            elif item.id == 'mechanic_worm':
                                entity.entity_spawn(entity.Entities.Destroyer, 4000, 4000, 0, 1145, 100000)
                            elif item.id == 'electric_unit':
                                entity.entity_spawn(entity.Entities.TheCPU, 2000, 2000, 0, 1145, 100000)
                            elif item.id == 'mechanic_spider':
                                entity.entity_spawn(entity.Entities.Greed, 2000, 2000, 0, 1145, 100000)
                            elif item.id == 'watch':
                                entity.entity_spawn(entity.Entities.EyeOfTime, 2000, 2000, 0, 1145, 100000)
                            elif item.id == 'metal_food':
                                entity.entity_spawn(entity.Entities.DevilPython, 2000, 2000, 0, 1145, 100000)
                            elif item.id == 'joker':
                                entity.entity_spawn(entity.Entities.Jevil, 2000, 2000, 0, 1145, 100000)

                            elif item.id == 'recipe_book':
                                rep = [r for r in inventory.RECIPES if r.is_related(self.inventory)]
                                window_opened = bool(len(rep))
                                sel = 0
                                window = pg.display.get_surface()
                                wx = window.get_width() // 2
                                wy = window.get_height() // 2
                                if not self.inventory.is_enough(inventory.ITEMS['tip0']):
                                    self.inventory.add_item(inventory.ITEMS['tip0'])
                                if not self.inventory.is_enough(inventory.ITEMS['tip1']):
                                    self.inventory.add_item(inventory.ITEMS['tip1'])
                                while window_opened:
                                    for event in pg.event.get():
                                        if event.type == pg.QUIT:
                                            window_opened = False
                                        if event.type == pg.KEYDOWN:
                                            if event.key == pg.K_ESCAPE:
                                                window_opened = False
                                            if event.key == pg.K_UP:
                                                sel = (sel - 1 + len(rep)) % len(rep)
                                            if event.key == pg.K_DOWN:
                                                sel = (sel + 1) % len(rep)
                                    pg.draw.rect(window, (255, 220, 200), (wx - 1200, wy - 800, 2400, 1600))
                                    pg.draw.rect(window, (255, 255, 255), (wx - 1200, wy - 800, 2400, 1600), 5)
                                    f = game.get_game().displayer.font.render(f"{sel + 1}/{len(rep)}", True, (0, 0, 0))
                                    fr = f.get_rect(center=(wx, wy + 750))
                                    window.blit(f, fr)
                                    cr = rep[sel]
                                    styles.item_display(wx - 1120, wy - 660, cr.result, '',
                                                        str(cr.crafted_amount), 4, _window=window)
                                    j = 0
                                    for it, qt in cr.material.items():
                                        styles.item_display(wx - 1120 + 160 * j, wy - 340, it, '', str(qt),
                                                            2, _window=window)
                                        j += 1
                                    styles.item_mouse(wx - 1120, wy - 660, cr.result, str(sel + 1),
                                                      str(cr.crafted_amount), 4, _window=window,
                                                      mp=pg.mouse.get_pos())
                                    j = 0
                                    for it, qt in cr.material.items():
                                        styles.item_mouse(wx - 1120 + 160 * j, wy - 340, it, str(j + 1), str(qt),
                                                          2, _window=window, mp=pg.mouse.get_pos())
                                        j += 1
                                    pg.display.update((wx - 1200, wy - 800, 2400, 1600))
                                game.get_game().pressed_keys = []
                                game.get_game().pressed_mouse = []
                            self.in_ui = True
            for i in range(len(self.accessories)):
                styles.item_mouse(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90,
                                  self.accessories[i].replace(' ', '_'), str(i), '1', 1)
                rect = pg.Rect(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90, 90, 90)
                if rect.collidepoint(game.get_game().displayer.reflect(
                        *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                    self.sel_accessory = i

            self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory)]
            if len(self.recipes):
                self.sel_recipe %= len(self.recipes)
                if pg.K_UP in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe - 1) % len(self.recipes)
                if pg.K_DOWN in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe + 1) % len(self.recipes)
                cur_recipe = self.recipes[self.sel_recipe]
                styles.item_display(game.get_game().displayer.SCREEN_WIDTH - 260,
                                    game.get_game().displayer.SCREEN_HEIGHT - 170,
                                    cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2)
                i = 0
                for item, amount in cur_recipe.material.items():
                    styles.item_display(
                        game.get_game().displayer.SCREEN_WIDTH - 20 - 80 * (1 + len(cur_recipe.material)) + 80 * i,
                        game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1)
                    i += 1
                if pg.Rect(game.get_game().displayer.SCREEN_WIDTH - 260, game.get_game().displayer.SCREEN_HEIGHT - 170,
                           160, 160).collidepoint(game.get_game().displayer.reflect(
                        *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                    rc = cur_recipe
                    cur_recipe.make(self.inventory)
                    self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory)]
                    res = [i for i, r in enumerate(self.recipes) if r is rc]
                    self.sel_recipe = res[0] if res else 0
                for i in range(-10, 10):
                    s = (self.sel_recipe + i + len(self.recipes)) % len(self.recipes)
                    cur_recipe = self.recipes[s]
                    styles.item_display(displayer.SCREEN_WIDTH - 90, displayer.SCREEN_HEIGHT // 2 + i * 80 - 40,
                                        cur_recipe.result, str(s + 1), str(cur_recipe.crafted_amount), 1)
                    i += 1
                cur_recipe = self.recipes[self.sel_recipe]
                styles.item_mouse(game.get_game().displayer.SCREEN_WIDTH - 260,
                                  game.get_game().displayer.SCREEN_HEIGHT - 170,
                                  cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2,
                                  anchor='right')
                i = 0
                for item, amount in cur_recipe.material.items():
                    styles.item_mouse(
                        game.get_game().displayer.SCREEN_WIDTH - 20 - 80 * (1 + len(cur_recipe.material)) + 80 * i,
                        game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1, anchor='right')
                    i += 1
                for i in range(-10, 10):
                    s = (self.sel_recipe + i + len(self.recipes)) % len(self.recipes)
                    cur_recipe = self.recipes[s]
                    styles.item_mouse(displayer.SCREEN_WIDTH - 90, displayer.SCREEN_HEIGHT // 2 + i * 80 - 40,
                                      cur_recipe.result, str(s + 1), str(cur_recipe.crafted_amount), 1, anchor='right')
                    r = pg.Rect(displayer.SCREEN_WIDTH - 90, displayer.SCREEN_HEIGHT // 2 + i * 80 - 40, 80, 80)
                    if r.collidepoint(game.get_game().displayer.reflect(
                            *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                        self.sel_recipe = s
            if pg.K_i in game.get_game().get_pressed_keys():
                ammo, amount = self.ammo
                styles.item_display(10, 10, ammo, '', str(amount), 2)
                styles.item_mouse(10, 10, ammo, '', str(amount), 2)
                ammo, amount = self.ammo_bullet
                styles.item_display(10, 170, ammo, '', str(amount), 2)
                styles.item_mouse(10, 170, ammo, '', str(amount), 2)
        else:
            t = (game.get_game().day_time % 1 * 24 * 60)
            for e in game.get_game().world_events:
                self.ntcs.append(f"Event: {e}")
            self.ntcs.append(f"{self.obj.pos[0] / 1000:.1f}, {self.obj.pos[1] / 1000:.1f}")
            self.ntcs.append(f"{int(t // 60)}:{'0' if int(t % 60) < 10 else ''}{int(t % 60)}")
            for i in range(len(self.ntcs)):
                t = game.get_game().displayer.font.render(self.ntcs[-i - 1], True, (255, 255, 255), (0, 0, 0))
                game.get_game().displayer.canvas.blit(t, (10, game.get_game().displayer.SCREEN_HEIGHT - 50 - i * 30))
        if len([1 for a in self.accessories if a == 'aimer']):
            for menace in [e for e in game.get_game().entities if e.IS_MENACE]:
                if type(menace) is entity.Entities.TheCPU:
                    continue
                px = menace.obj.pos[0] - self.obj.pos[0]
                py = menace.obj.pos[1] - self.obj.pos[1]
                dis = vector.distance(px, py)
                pg.draw.circle(displayer.canvas, (255, 0, 0), position.displayed_position(
                    (px * 300 // dis + self.obj.pos[0], py * 300 // dis + self.obj.pos[1])),
                               max(30, int(300 - dis // 30)) // 15)
        if pg.K_h in game.get_game().get_keys():
            potions = [inventory.ITEMS['butterscotch_pie'], inventory.ITEMS['crabapple'],
                       inventory.ITEMS['weak_healing_potion']]
            for p in potions:
                if p.id in self.inventory.items:
                    if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Potion Sickness']):
                        self.inventory.remove_item(p)
                        self.hp_sys.heal({'weak_healing_potion': 50, 'crabapple': 120, 'butterscotch_pie': 240}[p.id])
                        self.hp_sys.effect(effects.PotionSickness(60, 1))
                        game.get_game().play_sound('heal')
                        break
        if pg.K_m in game.get_game().get_keys():
            potions = [inventory.ITEMS['seatea'], inventory.ITEMS['weak_magic_potion']]
            for p in potions:
                if p.id in self.inventory.items:
                    if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Mana Sickness']):
                        self.inventory.remove_item(p)
                        self.mana = min(self.mana + {'weak_magic_potion': 80, 'seatea': 150}[p.id], self.max_mana)
                        self.hp_sys.effect(effects.ManaSickness(3, 1))
                        game.get_game().play_sound('mana')
                        break
        if self.touched_item != '':
            styles.item_display(displayer.SCREEN_WIDTH - 330, 10, self.touched_item, '', '', 4)
        if pg.K_1 in game.get_game().get_keys():
            self.sel_weapon = 0
        if pg.K_2 in game.get_game().get_keys():
            self.sel_weapon = 1
        if pg.K_3 in game.get_game().get_keys():
            self.sel_weapon = 2
        if pg.K_4 in game.get_game().get_keys():
            self.sel_weapon = 3
        if self.in_ui:
            pg.mouse.set_cursor(cursors.arrow_cursor_cursor)
        else:
            self.weapons[self.sel_weapon].update()
            w = self.weapons[self.sel_weapon]
            if inventory.TAGS['magic_weapon'] in inventory.ITEMS[w.name.replace(' ', '_')].tags or \
                    inventory.TAGS['bow'] in inventory.ITEMS[w.name.replace(' ', '_')].tags or \
                    inventory.TAGS['gun'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
                pg.mouse.set_cursor(cursors.target_cursor_cursor)
            else:
                pg.mouse.set_cursor(cursors.sword_cursor_cursor)

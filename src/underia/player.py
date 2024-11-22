from src.physics import mover, vector
from src.underia import game, styles, inventory, weapons, entity
from src.values import hp_system, damages, effects
from src.resources import time, position
import pygame as pg

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

    def __init__(self):
        self.obj = PlayerObject((400, 300))
        self.hp_sys = hp_system.HPSystem(200)
        self.hp_sys(op='config', immune_time=40, true_drop_speed_max_value=1)
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
        # self.hp_sys.defenses[damages.DamageTypes.TOUCHING] = 12
        # self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 3

    def calculate_touching_defense(self):
        ACCESSORY_DEFENSE = {'shield': 7, 'green_ring': 18, 'orange_ring': -2, 'sheath': 16, 'quiver': 8,
                             'hat': 2, 'firite_helmet': 28, 'firite_cloak': 14, 'firite_pluvial': 6}
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
        ACCESSORY_DEFENSE = {'blue_ring': 5, 'firite_helmet': 19, 'firite_cloak': 7, 'firite_pluvial': 12}
        defe = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DEFENSE.keys():
                defe += ACCESSORY_DEFENSE[self.accessories[i]]
        return defe

    def calculate_regeneration(self):
        ACCESSORY_REGEN = {'soul_bottle': 0.0075, 'blue_ring': -0.015, 'quiver': 0.0075, 'hat': 0.015,
                           'firite_helmet': .0225, 'firite_cloak': .0075, 'firite_pluvial': .0375}
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.6:
            ACCESSORY_REGEN['terrified_necklace'] = -0.0075
        regen = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_REGEN.keys():
                regen += ACCESSORY_REGEN[self.accessories[i]]
        return regen

    def calculate_magic_regeneration(self):
        ACCESSORY_REGEN = {'blue_ring': 0.13, 'hat': 0.1, 'firite_pluvial': .12}
        regen = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_REGEN.keys():
                regen += ACCESSORY_REGEN[self.accessories[i]]
        return regen

    def calculate_damage(self):
        ACCESSORY_DAMAGE = {'dangerous_necklace': 0.12, 'winds_necklace': -0.35}
        dmg = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        return dmg

    def calculate_speed(self):
        ACCESSORY_SPEED = {'orange_ring': 0.32, 'green_ring': -0.4, 'quiver': 0.15, 'firite_cloak': .45, 'winds_necklace': .5}
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.6:
            ACCESSORY_SPEED['terrified_necklace'] = 0.4
        spd = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_SPEED.keys():
                spd += ACCESSORY_SPEED[self.accessories[i]]
        return spd

    def calculate_melee_damage(self):
        ACCESSORY_DAMAGE = {'sheath': .18, 'firite_helmet': .3}
        dmg = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        return dmg

    def calculate_ranged_damage(self):
        ACCESSORY_DAMAGE = {'quiver': .10, 'firite_cloak': .32, 'winds_necklace': .2}
        dmg = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        return dmg

    def calculate_magic_damage(self):
        ACCESSORY_DAMAGE = {'hat': .3, 'firite_pluvial': .44}
        dmg = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_DAMAGE.keys():
                dmg += ACCESSORY_DAMAGE[self.accessories[i]]
        return dmg

    def get_light_level(self):
        if len([1 for accessory in self.accessories if inventory.TAGS['light_source'] in inventory.ITEMS[accessory].tags]):
            b = 5
        else:
            b = 0
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['nights_edge']:
            b = max(0, b - 4)
        return b

    def get_night_vision(self):
        if len([1 for accessory in self.accessories if inventory.TAGS['night_vision'] in inventory.ITEMS[accessory].tags]):
            b = 50
        else:
            b = 0
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['nights_edge']:
            b = max(0, b - 20)
        return b

    def update(self):
        self.hp_sys.pos = self.obj.pos
        self.attack = self.calculate_damage()
        self.attacks = [self.calculate_melee_damage(), self.calculate_ranged_damage(), self.calculate_magic_damage()]
        if len([1 for eff in self.hp_sys.effects if eff.NAME == 'Mana Sickness']):
            self.attack *= 0.5
        self.obj.SPEED = self.calculate_speed() * 20
        self.REGENERATION = 0.015 + self.calculate_regeneration()
        self.MAGIC_REGEN = 0.04 + self.calculate_magic_regeneration()
        self.hp_sys.defenses[damages.DamageTypes.TOUCHING] = self.calculate_touching_defense()
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = self.calculate_physical_defense()
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = self.calculate_magical_defense()
        if pg.K_e in game.get_game().get_keys():
            self.open_inventory = not self.open_inventory
        self.hp_sys.heal(self.REGENERATION)
        self.mana = min(self.mana + self.MAGIC_REGEN, self.max_mana)
        displayer = game.get_game().displayer
        self.obj.update()
        self.ax, self.ay = game.get_game().get_anchor()
        pg.draw.circle(displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.pos), 10)
        self.hp_sys.update()
        self.weapons[self.sel_weapon].update()

    def ui(self):
        displayer = game.get_game().displayer
        pg.draw.rect(displayer.canvas, (25, 25, 25), (10, 10, 200 + self.max_mana, 25))
        pg.draw.rect(displayer.canvas, (255, 0, 0), (10, 10, self.hp_sys.displayed_hp / self.hp_sys.max_hp * 200, 25))
        pg.draw.rect(displayer.canvas, (0, 255, 0), (10, 10, self.hp_sys.hp / self.hp_sys.max_hp * 200, 25))
        pg.draw.rect(displayer.canvas, (0, 0, 255), (210 + self.max_mana - self.mana, 10, self.mana, 25))
        pg.draw.rect(displayer.canvas, (255, 255, 255), (10, 10, 200 + self.max_mana, 25), width=2)
        for i in range(len(self.hp_sys.effects)):
            img = game.get_game().graphics['effect_' + self.hp_sys.effects[i].IMG]
            imr = img.get_rect(topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(self.hp_sys.effects) + 80 * i, 10))
            displayer.canvas.blit(img, imr)
        for i in range(len(self.hp_sys.effects)):
            img = game.get_game().graphics['effect_' + self.hp_sys.effects[i].IMG]
            imr = img.get_rect(topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(self.hp_sys.effects) + 80 * i, 10))
            if imr.collidepoint(pg.mouse.get_pos()):
                f = displayer.font.render(f"{self.hp_sys.effects[i].NAME} ({self.hp_sys.effects[i].timer}s)", True, (255, 255, 255))
                fr = f.get_rect(topright=pg.mouse.get_pos())
                displayer.canvas.blit(f, fr)
        for _entity in game.get_game().entities:
            _entity.obj.touched_player = False
            if self.hp_sys.is_immune:
                continue
            if self.obj.object_collide(_entity.obj):
                _entity.obj.touched_player = True
                if _entity.obj.TOUCHING_DAMAGE:
                    self.hp_sys.damage(_entity.obj.TOUCHING_DAMAGE, damages.DamageTypes.TOUCHING)
                    self.hp_sys.enable_immume()
        if pg.Rect(10, 10, 200 + self.max_mana, 25).collidepoint(pg.mouse.get_pos()):
            f = displayer.font.render(f"HP: {int(self.hp_sys.hp)}/{self.hp_sys.max_hp} MP: {int(self.mana)}/{self.max_mana}({self.obj.pos[0]:.1f}, {self.obj.pos[1]:.1f})", True, (255, 255, 255))
            displayer.canvas.blit(f, pg.mouse.get_pos())
        if time.time_interval(game.get_game().clock.time, 0.1, 0.01):
            self.hp_sys.heal(self.REGENERATION)
        for i in range(len(self.weapons)):
            if i % len(self.weapons) == 0 and i:
                break
            styles.item_display(10 + i * 60, 80, self.weapons[(self.sel_weapon + i) % len(self.weapons)].name.replace(' ', '_'), str(i), '1', 0.75, selected= not i)
        for i in range(len(self.weapons)):
            if i % len(self.weapons) == 0 and i:
                break
            styles.item_mouse(10 + i * 60, 80, self.weapons[(self.sel_weapon + i) % len(self.weapons)].name.replace(' ', '_'), str(i), '1', 0.75)
            rect = pg.Rect(10 + i * 60, 80, 60, 60)
            if rect.collidepoint(pg.mouse.get_pos()) and 1 in game.get_game().get_mouse_press():
                self.sel_weapon = (self.sel_weapon + i) % len(self.weapons)
        if self.open_inventory:
            for i in range(len(self.accessories)):
                styles.item_display(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90, self.accessories[i].replace(' ', '_'), str(i), '1', 1, selected=i == self.sel_accessory)
            for i in range(len(self.accessories)):
                styles.item_mouse(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90, self.accessories[i].replace(' ', '_'), str(i), '1', 1)
                rect = pg.Rect(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90, 90, 90)
                if rect.collidepoint(pg.mouse.get_pos()) and 1 in game.get_game().get_mouse_press():
                    self.sel_accessory = i
            l = game.get_game().displayer.SCREEN_WIDTH // 2 // 80
            for i in range(l):
                for j in range(l):
                    if i + j * l < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * l]
                        item = inventory.ITEMS[item]
                        styles.item_display(10 + i * 80, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 80, item.id, str(i + j * l + 1), str(amount), 1)
            for i in range(l):
                for j in range(l):
                    if i + j * l < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * l]
                        item = inventory.ITEMS[item]
                        styles.item_mouse(10 + i * 80, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 80, item.id, str(i + j * l + 1), str(amount), 1)
                        rect = pg.Rect(10 + i * 80, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 80, 80, 80)
                        if rect.collidepoint(pg.mouse.get_pos()):
                            if pg.K_q in game.get_game().get_keys():
                                del self.inventory.items[item.id]
                        if rect.collidepoint(pg.mouse.get_pos()) and 1 in game.get_game().get_mouse_press():
                            if inventory.TAGS['accessory'] in item.tags:
                                self.inventory.remove_item(item)
                                if self.accessories[self.sel_accessory] != 'null':
                                    self.inventory.add_item(inventory.ITEMS[self.accessories[self.sel_accessory]])
                                self.accessories[self.sel_accessory] = item.id
                            elif inventory.TAGS['weapon'] in item.tags:
                                self.inventory.remove_item(item)
                                if self.weapons[self.sel_weapon].name != 'null':
                                    self.inventory.add_item(inventory.ITEMS[self.weapons[self.sel_weapon].name.replace(' ', '_')])
                                self.weapons[self.sel_weapon] = weapons.WEAPONS[item.id]
                            elif inventory.TAGS['healing_potion'] in item.tags:
                                if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Potion Sickness']):
                                    self.inventory.remove_item(item)
                                    self.hp_sys.heal({'weak_healing_potion': 50, 'crabapple': 120}[item.id])
                                    self.hp_sys.effect(effects.PotionSickness(60, 1))
                            elif inventory.TAGS['magic_potion'] in item.tags:
                                if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Mana Sickness']):
                                    self.inventory.remove_item(item)
                                    self.mana = min(self.mana + {'weak_magic_potion': 80}[item.id], self.max_mana)
                                    self.hp_sys.effect(effects.ManaSickness(3, 1))
                            elif item.id == 'mana_crystal':
                                if self.max_mana < 120:
                                    self.max_mana += 15
                                    self.inventory.remove_item(item)
                            elif item.id == 'firy_plant':
                                if self.hp_sys.max_hp < 500:
                                    self.hp_sys.max_hp += 20
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
            self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory)]
            if len(self.recipes):
                self.sel_recipe %= len(self.recipes)
                if pg.K_UP in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe - 1) % len(self.recipes)
                if pg.K_DOWN in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe + 1) % len(self.recipes)
                cur_recipe = self.recipes[self.sel_recipe]
                styles.item_display(game.get_game().displayer.SCREEN_WIDTH - 250, game.get_game().displayer.SCREEN_HEIGHT - 170,
                                    cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2)
                i = 0
                for item, amount in cur_recipe.material.items():
                    styles.item_display(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * (1 + len(cur_recipe.material)) + 80 * i,
                                        game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1)
                    i += 1
                styles.item_mouse(game.get_game().displayer.SCREEN_WIDTH - 250, game.get_game().displayer.SCREEN_HEIGHT - 170,
                                  cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2, anchor='right')
                if pg.Rect(game.get_game().displayer.SCREEN_WIDTH - 250, game.get_game().displayer.SCREEN_HEIGHT - 170, 160, 160).collidepoint(pg.mouse.get_pos()) and 1 in game.get_game().get_mouse_press():
                    rc = cur_recipe
                    cur_recipe.make(self.inventory)
                    self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory)]
                    res = [i for i, r in enumerate(self.recipes) if r is rc]
                    self.sel_recipe = res[0] if res else 0
                i = 0
                for item, amount in cur_recipe.material.items():
                    styles.item_mouse(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * (1 + len(cur_recipe.material)) + 80 * i,
                                      game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1, anchor='right')
                    i += 1
            if pg.K_i in game.get_game().get_pressed_keys():
                ammo, amount = self.ammo
                styles.item_display(10, 10, ammo, '', str(amount), 2)
                styles.item_mouse(10, 10, ammo, '', str(amount), 2)
                ammo, amount = self.ammo_bullet
                styles.item_display(10, 170, ammo, '', str(amount), 2)
                styles.item_mouse(10, 170, ammo, '', str(amount), 2)
        else:
            t = (game.get_game().day_time % 1 * 24 * 60)
            f = displayer.font.render(f"{int(t // 60)}:{'0' if int(t % 60) < 10 else ''}{int(t % 60)}", (255, 255, 255), (0, 0, 0))
            fr = f.get_rect(bottomleft=(10, displayer.SCREEN_HEIGHT - 10))
            displayer.canvas.blit(f, fr)
            pg.draw.rect(displayer.canvas, (0, 0, 0), (displayer.SCREEN_WIDTH - 200, displayer.SCREEN_HEIGHT - 110, 100, 100))
            x, y = game.get_game().chunk_pos
            for i in range(x - 10, x + 10):
                for j in range(y - 10, y + 10):
                    if i < 0 or i >= game.get_game().map.shape[0] or j < 0 or j >= game.get_game().map.shape[1]:
                        continue
                    color = game.get_game().map[i, j]
                    pg.draw.rect(displayer.canvas, color, (displayer.SCREEN_WIDTH - 200 + (i - x + 10) * 5, displayer.SCREEN_HEIGHT - 110 + (j - y + 10) * 5, 5, 5))
        if len([1 for a in self.accessories if a == 'aimer']):
            for menace in [e for e in game.get_game().entities if e.IS_MENACE]:
                px = menace.obj.pos[0] - self.obj.pos[0]
                py = menace.obj.pos[1] - self.obj.pos[1]
                dis = vector.distance(px, py)
                pg.draw.circle(displayer.canvas, (255, 0, 0), position.displayed_position((px * 300 // dis + self.obj.pos[0], py * 300 // dis + self.obj.pos[1])), max(30, int(300 - dis // 30)) // 15)
        if pg.K_h in game.get_game().get_keys():
            potions = [inventory.ITEMS['crabapple'], inventory.ITEMS['weak_healing_potion']]
            for p in potions:
                if p.id in self.inventory.items:
                    if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Potion Sickness']):
                        self.inventory.remove_item(p)
                        self.hp_sys.heal({'weak_healing_potion': 50, 'crabapple': 120}[p.id])
                        self.hp_sys.effect(effects.PotionSickness(60, 1))
                        break
        if pg.K_m in game.get_game().get_keys():
            potions = [inventory.ITEMS['weak_magic_potion']]
            for p in potions:
                if p.id in self.inventory.items:
                    if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Mana Sickness']):
                        self.inventory.remove_item(p)
                        self.mana = min(self.mana + {'weak_magic_potion': 80}[p.id], self.max_mana)
                        self.hp_sys.effect(effects.ManaSickness(3, 1))
                        break
        if pg.K_1 in game.get_game().get_keys():
            self.sel_weapon = (self.sel_weapon + 1) % len(self.weapons)
        if pg.K_2 in game.get_game().get_keys():
            self.sel_weapon = (self.sel_weapon + 2) % len(self.weapons)
        if pg.K_3 in game.get_game().get_keys():
            self.sel_weapon = (self.sel_weapon + 3) % len(self.weapons)

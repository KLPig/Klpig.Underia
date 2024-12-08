from src import constants
from src.values import reduction, effects, damages
from src.underia import game

import random

class HPSystem:

    TRUE_DROP_SPEED_MAX_RATE = 0.1
    TRUE_DROP_SPEED_MAX_VALUE = 5

    IMMUNE = False
    IMMUNE_TIME = 2

    MINIMUM_DAMAGE = 1
    MAXIMUM_DAMAGE = constants.INFINITY

    DAMAGE_RANDOMIZE_RANGE = 0.12
    DAMAGE_TEXT_INTERVAL = 5

    def __init__(self, hp: float):
        self.resistances = reduction.Resistances()
        self.defenses = reduction.Defenses()
        self.resistances[damages.DamageTypes.ARCANE] = 379
        self.hp = hp
        self.displayed_hp = hp
        self.max_hp = hp
        self.is_immune = False
        self.effects: list[effects.Effect] = []
        self.pos = (0, 0)
        self.dmg_t = 0

    def __call__(self, *args, **kwargs):
        if 'op' in kwargs:
            if kwargs['op'] == 'config':
                avails = ['true_drop_speed_max_rate', 'true_drop_speed_max_value', 'immune_time',
                          'immune', 'minimum_damage','maximum_damage', 'damage_randomize_range',
                          'damage_text_interval']
                for k, v in kwargs.items():
                    if k in avails:
                        setattr(self, k.upper(), v)
        else:
            return self.hp

    def damage(self, damage: float, damage_type: int):
        if self.IMMUNE or self.is_immune:
            return
        dmg = damage * self.resistances[damage_type] - self.defenses[damage_type]
        dmg *= (1 - self.DAMAGE_RANDOMIZE_RANGE + 2 *
                self.DAMAGE_RANDOMIZE_RANGE * random.random())
        dmg = max(self.MINIMUM_DAMAGE, min(self.MAXIMUM_DAMAGE, dmg))
        print(damage, dmg)
        if not self.dmg_t:
            self.dmg_t = self.DAMAGE_TEXT_INTERVAL
            game.get_game().damage_texts.append((int(dmg), 0, (self.pos[0] + random.randint(-10, 10), self.pos[1] + random.randint(-10, 10))))
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0

    def enable_immume(self):
        self.is_immune = self.IMMUNE_TIME

    def update(self):
        if self.dmg_t:
            self.dmg_t -= 1
        for eff in self.effects:
            eff.on_update(self)
            if eff.timer <= 0:
                eff.on_end(self)
                self.effects.remove(eff)
        if self.is_immune:
            self.is_immune -= 1
            if self.is_immune <= 0:
                self.is_immune = False
        self.displayed_hp -= min(self.displayed_hp - self.hp, max(self.TRUE_DROP_SPEED_MAX_RATE * (self.displayed_hp - self.hp), self.TRUE_DROP_SPEED_MAX_VALUE))
        if self.displayed_hp < 0:
            self.displayed_hp = 0

    def effect(self, effect):
        effect.on_start(self)
        self.effects.append(effect)

    def heal(self, val):
        self.hp = min(self.max_hp, self.hp + val)
        self.displayed_hp = max(self.displayed_hp, self.hp)

class SubHPSystem(HPSystem):

    def __init__(self, hp_sys: HPSystem):
        super().__init__(hp_sys.hp)
        self.hp_sys = hp_sys

    def update(self):
        self.hp = self.hp_sys.hp
        self.displayed_hp = self.hp_sys.displayed_hp
        self.max_hp = self.hp_sys.max_hp
        self.is_immune = self.hp_sys.is_immune
        self.effects = self.hp_sys.effects

    def damage(self, damage: float, damage_type: int):
        super().damage(damage, damage_type)
        self.hp_sys.hp = self.hp
        self.hp_sys.displayed_hp = self.displayed_hp
        self.hp_sys.is_immune = self.is_immune
        self.hp_sys.effects = self.effects

from src.underia import weapons, projectiles, game
from src.values import damages


class Inventory:
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    VERY_RARE = 3
    EPIC = 4
    LEGENDARY = 5
    MYTHIC = 6
    SUPER_MYTHIC = 7
    GODLIKE = 8
    SUPER_GODLIKE = 9
    UNKNOWN = 114

    Rarity_Colors = [(255, 255, 255), (255, 255, 127), (150, 255, 127), (127, 255, 255), (255, 127, 127),
                     (255, 165, 64), (128, 64, 128), (255, 200, 255), (255, 127, 255), (255, 200, 255), (255, 255, 255)]
    Rarity_Names = ["Common", "Uncommon", "Rare", "Very Rare", "Epic", "Legendary", "Mythic", "Super Mythic", "Godlike",
                    "Super Godlike", "Unknown"]

    class Item:
        class Tag:
            def __init__(self, name: str, value: str):
                self.name = name
                self.value = value

            def get_all_items(self):
                return [item for item in ITEMS.values() if self.name in [tag.name for tag in item.tags]]

        def __init__(self, name, description, identifier: str, rarity: int = 0, tags: list[Tag] = []):
            self.name = name
            self.desc = description
            self.id = identifier
            self.rarity = rarity
            self.tags = tags
            self.inner_id = 0

        def __str__(self):
            return f"#{self.inner_id}: {self.name} - {self.desc}"

        def get_full_desc(self):
            d = self.desc
            if TAGS['major_accessory'] in self.tags:
                d = 'Can only be placed in the first slot.\n' + d
            if TAGS['wings'] in self.tags:
                d = 'Can only be placed in the second slot.\n' + d
            if TAGS['accessory'] in self.tags:
                d = 'Accessory\n' + d

            if TAGS['magic_weapon'] in self.tags:
                weapon: weapons.MagicWeapon = weapons.WEAPONS[self.id]
                d = f"{[t.value.upper() for t in self.tags if t.name.startswith('magic_element_')][0]} "\
                    f"{[t.value for t in self.tags if t.name.startswith('magic_lv_')][0]}: {weapon.spell_name}"
                d = f"{weapon.mana_cost} mana cost\n" + d
            if TAGS['arcane_weapon'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{weapon.talent_cost} talent cost\n" + d
                if weapon.mana_cost:
                    d = f"{weapon.mana_cost} mana cost\n" + d
            if TAGS['bow'] in self.tags or TAGS['gun'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{weapon.spd} projectile speed\n" + d
            if TAGS['weapon'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{round(100 / (weapon.at_time + weapon.cd), 1)}% speed\n" + d
                d = f"{weapon.knock_back} knockback\n" + d
                for dmg, val in weapon.damages.items():
                    _dmg = val * game.get_game().player.calculate_damage()
                    if TAGS['magic_weapon'] in self.tags:
                        _dmg *= game.get_game().player.calculate_magic_damage()
                    elif TAGS['bow'] in self.tags or TAGS['gun'] in self.tags:
                        _dmg *= game.get_game().player.calculate_ranged_damage()
                    else:
                        _dmg *= game.get_game().player.calculate_melee_damage()
                    d = f"{int(_dmg)} {damages.NAMES[dmg]} damage\n" + d
            elif TAGS['ammo'] in self.tags:
                ammo = projectiles.AMMOS[self.id]
                d = f"{ammo.DAMAGES} piercing damage\n" + d
            return d

    def __init__(self):
        self.items = {}

    def add_item(self, item: Item, number: int = 1):
        if item.id in self.items:
            self.items[item.id] += number
        else:
            self.items[item.id] = number
        self.sort()

    def remove_item(self, item: Item, number: int = 1):
        if item.id in self.items:
            self.items[item.id] -= number
            self.items = {k: v for k, v in self.items.items() if v > 0}
        else:
            pass

    def is_enough(self, item: Item, number: int = 1):
        if item.id in self.items:
            return self.items[item.id] >= number
        else:
            return False

    def get_all_items(self):
        return self.items.values()

    def get_item_by_name(self, name: str):
        return [item for item in self.items.values() if item.name == name][0]

    def get_item_by_id(self, item_id: int):
        return self.items[item_id]

    def get_item_by_tag(self, tag_name: str):
        return [item for item in self.items.values() if tag_name in [tag.name for tag in item.tags]]

    def get_item_by_rarity(self, rarity: int):
        return [item for item in self.items.values() if item.rarity == rarity]

    def get_item_by_rarity_name(self, rarity_name: str):
        return [item for item in self.items.values() if Inventory.Rarity_Names[item.rarity] == rarity_name]

    def get_item_by_rarity_color(self, rarity_color: tuple):
        return [item for item in self.items.values() if Inventory.Rarity_Colors[item.rarity] == rarity_color]

    def sort(self):
        self.items = {k: v for k, v in
                      sorted(self.items.items(), key=lambda item: ITEMS[item[0]].inner_id, reverse=True)}


TAGS = {
    'item': Inventory.Item.Tag('item', 'item'),
    'weapon': Inventory.Item.Tag('weapon', 'weapon'),
    'magic_weapon': Inventory.Item.Tag('magic_weapon', 'magic_weapon'),
    'arcane_weapon': Inventory.Item.Tag('arcane_weapon', 'arcane_weapon'),
    'accessory': Inventory.Item.Tag('accessory', 'accessory'),
    'major_accessory': Inventory.Item.Tag('major_accessory', 'major_accessory'),
    'wings': Inventory.Item.Tag('wings', 'wings'),
    'healing_potion': Inventory.Item.Tag('healing_potion', 'healing_potion'),
    'magic_potion': Inventory.Item.Tag('magic_potion', 'magic_potion'),
    'workstation': Inventory.Item.Tag('workstation', 'workstation'),
    'light_source': Inventory.Item.Tag('light_source', 'light_source'),
    'night_vision': Inventory.Item.Tag('night_vision', 'night_vision'),
    'bow': Inventory.Item.Tag('bow', 'bow'),
    'gun': Inventory.Item.Tag('gun', 'gun'),
    'lazer_gun': Inventory.Item.Tag('lazer_gun', 'lazer_gun'),
    'ammo': Inventory.Item.Tag('ammo', 'ammo'),
    'ammo_arrow': Inventory.Item.Tag('ammo_arrow', 'ammo_arrow'),
    'ammo_bullet': Inventory.Item.Tag('ammo_bullet', 'ammo_bullet'),

    'magic_element_fire': Inventory.Item.Tag('magic_element_fire', 'fire magic'),
    'magic_element_water': Inventory.Item.Tag('magic_element_water', 'water magic'),
    'magic_element_air': Inventory.Item.Tag('magic_element_air', 'air magic'),
    'magic_element_earth': Inventory.Item.Tag('magic_element_earth', 'earth magic'),
    'magic_element_light': Inventory.Item.Tag('magic_element_light', 'light magic'),
    'magic_element_dark': Inventory.Item.Tag('magic_element_dark', 'dark magic'),
    'magic_element_life': Inventory.Item.Tag('magic_element_life', 'life magic'),
    'magic_element_death': Inventory.Item.Tag('magic_element_death', 'death magic'),
    'magic_element_energy': Inventory.Item.Tag('magic_element_energy', 'energy magic'),
    'magic_element_time': Inventory.Item.Tag('magic_element_time', 'time magic'),
    'magic_element_space': Inventory.Item.Tag('magic_element_space', 'space magic'),

    'magic_lv_1': Inventory.Item.Tag('magic_lv_1', 'LV.I'),
    'magic_lv_2': Inventory.Item.Tag('magic_lv_2', 'LV.II'),
    'magic_lv_3': Inventory.Item.Tag('magic_lv_3', 'LV.III'),
    'magic_lv_4': Inventory.Item.Tag('magic_lv_4', 'LV.IV'),
    'magic_lv_5': Inventory.Item.Tag('magic_lv_5', 'LV.V'),
    'magic_lv_6': Inventory.Item.Tag('magic_lv_6', 'LV.VI'),
    'magic_lv_7': Inventory.Item.Tag('magic_lv_7', 'LV.VII'),
    'magic_lv_forbidden_curse': Inventory.Item.Tag('magic_lv_forbidden_curse', 'LV.XX'),
    'magic_lv_primal_magic': Inventory.Item.Tag('magic_lv_primal_magic', 'LV.NULLA'),
    'magic_lv_bible': Inventory.Item.Tag('magic_lv_bible', 'LV.XXV'),
}
items_dict: dict[str, Inventory.Item] = {
    'null': Inventory.Item('null', '', 'null', 0, [TAGS['item']]),

    'wood': Inventory.Item('Wood', '', 'wood', 0, [TAGS['item']]),
    'leaf': Inventory.Item('Leaf', '', 'leaf', 0, [TAGS['item']]),
    'copper': Inventory.Item('Copper', '', 'copper', 0, [TAGS['item']]),
    'copper_ingot': Inventory.Item('Copper Ingot', '', 'copper_ingot', 0, [TAGS['item']]),
    'iron': Inventory.Item('Iron', '', 'iron', 0, [TAGS['item']]),
    'iron_ingot': Inventory.Item('Iron Ingot', '', 'iron_ingot', 0, [TAGS['item']]),
    'steel': Inventory.Item('Steel', '', 'steel', 0, [TAGS['item']]),
    'steel_ingot': Inventory.Item('Steel Ingot', '', 'steel_ingot', 0, [TAGS['item']]),
    'cell_organization': Inventory.Item('Cell Organization', '', 'cell_organization', 1, [TAGS['item']]),
    'platinum': Inventory.Item('Platinum', '', 'platinum', 1, [TAGS['item']]),
    'platinum_ingot': Inventory.Item('Platinum Ingot', '', 'platinum_ingot', 1, [TAGS['item']]),
    'magic_stone': Inventory.Item('Magic Stone', '', 'magic_stone', 1, [TAGS['item']]),
    'blood_ingot': Inventory.Item('Blood Ingot', '', 'blood_ingot', 2, [TAGS['item']]),
    'firite_ingot': Inventory.Item('Firite Ingot', '', 'firite_ingot', 2, [TAGS['item']]),
    'mysterious_substance': Inventory.Item('Mysterious Substance', '', 'mysterious_substance', 2, [TAGS['item']]),
    'mysterious_ingot': Inventory.Item('Mysterious Ingot', '', 'mysterious_ingot', 2, [TAGS['item']]),
    'storm_core': Inventory.Item('Storm Core', '', 'storm_core', 2, [TAGS['item']]),
    'soul': Inventory.Item('Soul', 'Something left after death.', 'soul', 4, [TAGS['item']]),
    'evil_ingot': Inventory.Item('Evil Ingot', 'Endless evil.', 'evil_ingot', 5, [TAGS['item']]),
    'soul_of_flying': Inventory.Item('Soul of Flying', 'Soul of flying creatures.', 'soul_of_flying', 5,
                                     [TAGS['item']]),
    'palladium': Inventory.Item('Palladium', '', 'palladium', 5, [TAGS['item']]),
    'mithrill': Inventory.Item('Mithrill', '', 'mithrill', 5, [TAGS['item']]),
    'titanium': Inventory.Item('Titanium', '', 'titanium', 5, [TAGS['item']]),
    'palladium_ingot': Inventory.Item('Palladium Ingot', '', 'palladium_ingot', 5, [TAGS['item']]),
    'mithrill_ingot': Inventory.Item('Mithrill Ingot', '', 'mithrill_ingot', 5, [TAGS['item']]),
    'titanium_ingot': Inventory.Item('Titanium Ingot', '', 'titanium_ingot', 5, [TAGS['item']]),
    'saint_steel_ingot': Inventory.Item('Saint Steel Ingot', '', 'saint_steel_ingot', 6, [TAGS['item']]),
    'daedalus_ingot': Inventory.Item('Daedalus\' Ingot', '', 'daedalus_ingot', 6, [TAGS['item']]),
    'dark_ingot': Inventory.Item('Dark Ingot', '', 'dark_ingot', 6, [TAGS['item']]),
    'soul_of_integrity': Inventory.Item('Soul of Integrity', 'Power of the honest being.', 'soul_of_integrity', 6,
                                        [TAGS['item']]),
    'soul_of_bravery': Inventory.Item('Soul of Bravery', 'Power of fearless.', 'soul_of_bravery', 6, [TAGS['item']]),
    'soul_of_kindness': Inventory.Item('Soul of Kindness', 'Power of mercy.', 'soul_of_kindness', 6, [TAGS['item']]),
    'mystery_core': Inventory.Item('Mystery Core', 'Knowledge\n+1 max talent\n+5 talent', 'mystery_core', 7,
                                   [TAGS['item']]),
    'soul_of_perseverance': Inventory.Item('Soul of Perseverance', 'Power of hope.', 'soul_of_perseverance', 6,
                                           [TAGS['item']]),
    'soul_of_patience': Inventory.Item('Soul of Patience', 'Power of endurance.', 'soul_of_patience', 6,
                                       [TAGS['item']]),
    'soul_of_justice': Inventory.Item('Soul of Justice', 'Power of fairness.', 'soul_of_justice', 6, [TAGS['item']]),
    'soul_of_growth': Inventory.Item('Soul of Growth', 'The power to live.', 'soul_of_growth', 7, [TAGS['item']]),
    'photon': Inventory.Item('Photon', 'Light energy', 'photon', 7, [TAGS['item']]),
    'chlorophyte_ingot': Inventory.Item('Chlorophyte Ingot', '', 'chlorophyte_ingot', 7, [TAGS['item']]),

    'torch': Inventory.Item('Torch', 'Ignite the darkness.', 'torch', 0,
                            [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'night_visioner': Inventory.Item('Night Visioner', 'See in the dark.', 'night_visioner', 0,
                                     [TAGS['item'], TAGS['accessory'], TAGS['light_source'], TAGS['night_vision']]),

    'wooden_hammer': Inventory.Item('Wooden Hammer', '', 'wooden_hammer', 0, [TAGS['item'], TAGS['workstation']]),
    'furnace': Inventory.Item('Furnace', '', 'furnace', 0, [TAGS['item'], TAGS['workstation']]),
    'anvil': Inventory.Item('Anvil', '', 'anvil', 0, [TAGS['item'], TAGS['workstation']]),
    'mithrill_anvil': Inventory.Item('Mithrill Anvil', '', 'anvil', 4, [TAGS['item'], TAGS['workstation']]),
    'chlorophyll': Inventory.Item('Chlorophyll', 'Carry out photosynthesis.', 'chlorophyll', 7,
                                  [TAGS['item'], TAGS['workstation']]),

    'wooden_sword': Inventory.Item('Wooden Sword', '', 'wooden_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'copper_sword': Inventory.Item('Copper Sword', '', 'copper_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'iron_sword': Inventory.Item('Iron Sword', '', 'iron_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'iron_blade': Inventory.Item('Iron Blade', '', 'iron_blade', 0, [TAGS['item'], TAGS['weapon']]),
    'steel_sword': Inventory.Item('Steel Sword', '', 'steel_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'platinum_sword': Inventory.Item('Platinum Sword', '', 'platinum_sword', 1, [TAGS['item'], TAGS['weapon']]),
    'platinum_blade': Inventory.Item('Platinum Blade', '', 'platinum_blade', 1, [TAGS['item'], TAGS['weapon']]),
    'magic_sword': Inventory.Item('Magic Sword', '', 'magic_sword', 2, [TAGS['item'], TAGS['weapon']]),
    'magic_blade': Inventory.Item('Magic Blade', '', 'magic_blade', 2, [TAGS['item'], TAGS['weapon']]),
    'bloody_sword': Inventory.Item('Bloody Sword', 'When sweeping, press Q to sprint.', 'bloody_sword', 2,
                                   [TAGS['item'], TAGS['weapon']]),
    'volcano': Inventory.Item('Volcano', 'Gives target to fire.', 'volcano', 2, [TAGS['item'], TAGS['weapon']]),
    'sand_sword': Inventory.Item('Sand Sword', 'When sweeping, press Q to sprint.', 'sand_sword', 2,
                                 [TAGS['item'], TAGS['weapon']]),
    'nights_edge': Inventory.Item('Night\'s Edge', 'The sunset has gone, it now night...', 'nights_edge', 4,
                                  [TAGS['item'], TAGS['weapon']]),
    'spiritual_stabber': Inventory.Item('Spiritual Stabber', '\n\'Destroy the mark to enhance\'', 'spiritual_stabber',
                                        4, [TAGS['item'], TAGS['weapon']]),
    'palladium_sword': Inventory.Item('Palladium Sword', '', 'palladium_sword', 5, [TAGS['item'], TAGS['weapon']]),
    'mithrill_sword': Inventory.Item('Mithrill Sword', '', 'mithrill_sword', 5, [TAGS['item'], TAGS['weapon']]),
    'titanium_sword': Inventory.Item('Titanium Sword', '', 'titanium_sword', 5, [TAGS['item'], TAGS['weapon']]),
    'balanced_stabber': Inventory.Item('Balanced Stabber',
                                       'The power of the evil and the hallow are balanced.\n\n\'Make it under the hallow to enhance\'',
                                       'balanced_stabber', 5, [TAGS['item'], TAGS['weapon']]),
    'excalibur': Inventory.Item('Excalibur', 'The legendary sword of hallow.', 'excalibur', 6,
                                [TAGS['item'], TAGS['weapon']]),
    'true_excalibur': Inventory.Item('True Excalibur', 'Inviolable hallow.', 'true_excalibur', 7,
                                     [TAGS['item'], TAGS['weapon']]),
    'true_nights_edge': Inventory.Item('True Night\'s Edge', 'Inviolable dark.', 'true_nights_edge', 7,
                                       [TAGS['item'], TAGS['weapon']]),
    'perseverance_sword': Inventory.Item('Perseverance Sword', 'Ignore the distance.', 'perseverance_sword', 7,
                                         [TAGS['item'], TAGS['weapon']]),
    'black_hole_sword': Inventory.Item('The Black Hole Sword', 'Attracts enemies.', 'black_hole_sword', 7,
                                       [TAGS['item'], TAGS['weapon']]),
    'life_devourer': Inventory.Item('Life Devourer', 'Cuts lifeless lines.', 'life_devourer', 7,
                                    [TAGS['item'], TAGS['weapon']]),

    'spear': Inventory.Item('Spear', '', 'spear', 0, [TAGS['item'], TAGS['weapon']]),
    'platinum_spear': Inventory.Item('Platinum Spear', '', 'platinum_spear', 1, [TAGS['item'], TAGS['weapon']]),
    'firite_spear': Inventory.Item('Firite Spear', '', 'firite_spear', 2, [TAGS['item'], TAGS['weapon']]),
    'nights_pike': Inventory.Item('Night\'s Pike', 'The sunset has gone, it now night...', 'nights_pike', 4,
                                  [TAGS['item'], TAGS['weapon']]),
    'energy_spear': Inventory.Item('Energy Spear', 'Contained unparalleled energy.', 'energy_spear', 6,
                                   [TAGS['item'], TAGS['weapon']]),

    'bow': Inventory.Item('Bow', '', 'bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'copper_bow': Inventory.Item('Copper Bow', '', 'copper_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'iron_bow': Inventory.Item('Iron Bow', '', 'iron_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'steel_bow': Inventory.Item('Steel Bow', '', 'steel_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'platinum_bow': Inventory.Item('Platinum Bow', '', 'platinum_bow', 1, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'bloody_bow': Inventory.Item('Bloody Bow', '', 'bloody_bow', 2, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'recurve_bow': Inventory.Item('Recurve Bow', '', 'recurve_bow', 3, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'spiritual_piercer': Inventory.Item('Spiritual Piercer', '\n\'Destroy the mark to enhance\'', 'spiritual_piercer',
                                        4, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'discord_storm': Inventory.Item('Discord Storm',
                                    'Evil corrupted, all in chaos.\n\n\'Find that old god to enhance\'',
                                    'discord_storm', 5, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'daedalus_stormbow': Inventory.Item('Daedalus\' Stormbow', '', 'daedalus_stormbow', 6,
                                        [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'true_daedalus_stormbow': Inventory.Item('True Daedalus\' Stormbow', '', 'true_daedalus_stormbow', 7,
                                             [TAGS['item'], TAGS['weapon'], TAGS['bow']]),

    'pistol': Inventory.Item('pistol', '', 'pistol', 0, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rifle': Inventory.Item('rifle', '', 'rifle', 0, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'submachine_gun': Inventory.Item('Submachine Gun', '', 'submachine_gun', 2,
                                     [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'magma_assaulter': Inventory.Item('Magma Assaulter', 'When shooting, press Q to sprint back.', 'magma_assaulter', 2,
                                      [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'shadow': Inventory.Item('shadow', 'When there\'s light, there\'s dark.', 'shadow', 4,
                             [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'palladium_gun': Inventory.Item('Palladium Gun', '', 'palladium_gun', 5,
                                    [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'mithrill_gun': Inventory.Item('Mithrill Gun', '', 'mithrill_gun', 5, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'titanium_gun': Inventory.Item('Titanium Gun', '', 'titanium_gun', 5, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'true_shadow': Inventory.Item('True Shadow', 'Not the others, \'Pong! Nobody left.\'', 'true_shadow', 7,
                                  [TAGS['item'], TAGS['weapon'], TAGS['gun']]),

    'lazer_gun': Inventory.Item('Lazer Gun', '', 'lazer_gun', 7,
                                [TAGS['item'], TAGS['weapon'], TAGS['gun'], TAGS['lazer_gun']]),

    'arrow': Inventory.Item('Arrow', '', 'arrow', 0, [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'magic_arrow': Inventory.Item('Magic Arrow', '', 'magic_arrow', 1,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'blood_arrow': Inventory.Item('Blood Arrow', '', 'blood_arrow', 2,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'bullet': Inventory.Item('Bullet', '', 'bullet', 0, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'platinum_bullet': Inventory.Item('Platinum Bullet', '', 'platinum_bullet', 1,
                                      [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'plasma': Inventory.Item('Plasma', '', 'plasma', 2, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'rock_bullet': Inventory.Item('Rock Bullet', '', 'rock_bullet', 2,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'shadow_bullet': Inventory.Item('Shadow Bullet', '', 'shadow_bullet', 3,
                                    [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'quick_arrow': Inventory.Item('Quick Arrow', '', 'quick_arrow', 5,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'quick_bullet': Inventory.Item('Quick Bullet', '', 'quick_bullet', 5,
                                   [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),

    'glowing_splint': Inventory.Item('Glowing Splint', 'Shoots glows.', 'glowing_splint', 0,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                      TAGS['magic_element_fire'], TAGS['magic_lv_1']]),
    'copper_wand': Inventory.Item('Copper Wand', '', 'copper_wand', 0,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                   TAGS['magic_lv_1']]),
    'iron_wand': Inventory.Item('Iron Wand', '', 'iron_wand', 0,
                                [TAGS['item'],  TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                 TAGS['magic_lv_1']]),
    'cactus_wand': Inventory.Item('Cactus Wand', '', 'cactus_wand', 1,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_1']]),
    'watcher_wand': Inventory.Item('Watcher Wand', '', 'watcher_wand', 1,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                    TAGS['magic_lv_1']]),
    'platinum_wand': Inventory.Item('Platinum Wand', '', 'platinum_wand', 1,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                     TAGS['magic_element_energy'], TAGS['magic_lv_1']]),
    'life_wooden_wand': Inventory.Item('Life-Wooden Wand', '', 'life_wooden_wand', 2,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                         TAGS['magic_lv_1']]),
    'burning_book': Inventory.Item('Burning Book', 'Burns enemies.', 'burning_book', 2,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                     TAGS['magic_lv_2']]),
    'talent_book': Inventory.Item('Talent Book', '', 'talent_book', 2,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                   TAGS['magic_lv_2']]),
    'blood_wand': Inventory.Item('Blood Wand', '', 'blood_wand', 2,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_2']]),
    'hematology': Inventory.Item('Hematology', 'Recovers 30 HP.', 'hematology', 3,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_3']]),
    'fire_magic_sword': Inventory.Item('Fire Magic Sword', '', 'fire_magic_sword', 3,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                        TAGS['magic_lv_3']]),
    'rock_wand': Inventory.Item('Rock Wand', '', 'rock_wand', 3,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                 TAGS['magic_lv_3']]),
    'midnights_wand': Inventory.Item('Midnight\'s Wand', 'All darkness...', 'midnights_wand', 4,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                      TAGS['magic_lv_4']]),
    'spiritual_destroyer': Inventory.Item('Spiritual Destroyer', '\n\'Destroy the mark to enhance\'',
                                          'spiritual_destroyer', 4,
                                          [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                           TAGS['magic_element_energy'], TAGS['magic_lv_4']]),
    'evil_book': Inventory.Item('Evil Book', 'Full of corruption\n\n\'Change to enhance\'', 'evil_book', 5,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_death'],
                                  TAGS['magic_lv_4']]),
    'curse_book': Inventory.Item('Curse Book', 'Curse...', 'curse_book', 6,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                   TAGS['magic_lv_4']]),
    'shield_wand': Inventory.Item('Shield Wand', '+1145114 defense\n-100% speed', 'shield_wand', 6,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'],
                                    TAGS['magic_lv_4']]),
    'gravity_wand': Inventory.Item('Gravity Wand', 'Simulates gravity.', 'gravity_wand', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                     TAGS['magic_lv_4']]),
    'forbidden_curse__spirit': Inventory.Item('Forbidden Curse: Spirit', '', 'forbidden_curse__spirit', 7,
                                              [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                               TAGS['arcane_weapon'], TAGS['magic_element_energy'],
                                               TAGS['magic_lv_forbidden_curse']]),
    'forbidden_curse__evil': Inventory.Item('Forbidden Curse: Evil', '', 'forbidden_curse__evil', 7,
                                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                             TAGS['arcane_weapon'], TAGS['magic_element_death'],
                                              TAGS['magic_lv_forbidden_curse']]),
    'forbidden_curse__time': Inventory.Item('Forbidden Curse: Time', 'Adjust the rate of time.',
                                            'forbidden_curse__time', 7,
                                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                             TAGS['arcane_weapon'], TAGS['magic_element_time'],
                                              TAGS['magic_lv_forbidden_curse']]),
    'prism': Inventory.Item('Prism', 'Releases light beams.', 'prism', 6,
                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                             TAGS['magic_lv_4']]),
    'prism_wand': Inventory.Item('Prism Wand', 'Releases light beams.', 'prism_wand', 7,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                   TAGS['magic_element_light'], TAGS['magic_lv_5']]),
    'light_purify': Inventory.Item('Light Purify', '', 'light_purify', 7,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                     TAGS['magic_lv_5']]),
    'astigmatism': Inventory.Item('Astigmatism', 'Releases light beams.', 'astigmatism', 7,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                    TAGS['magic_lv_6']]),
    'life_wand': Inventory.Item('Life Wand', 'Heal you back to life.', 'life_wand', 7,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                 TAGS['magic_lv_6']]),

    'lights_bible': Inventory.Item('Light\'s Bible', 'Bright makes light', 'lights_bible', 7,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                  TAGS['magic_element_light'], TAGS['magic_lv_bible'], TAGS['workstation']]),
    'energy_bible': Inventory.Item('Energy\'s Bible', 'Energy makes light', 'energy_bible', 7,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                  TAGS['magic_element_energy'], TAGS['magic_lv_bible'], TAGS['workstation']]),

    'natural_necklace': Inventory.Item('Natural Necklace', '+4/sec mana regeneration', 'natural_necklace', 1,
                                       [TAGS['item'], TAGS['accessory']]),
    'shield': Inventory.Item('Simple Shield', '+7 touching defense\n+12 physic defense', 'shield', 1,
                             [TAGS['item'], TAGS['accessory']]),
    'soul_bottle': Inventory.Item('Soul Bottle', '+0.5/sec regeneration', 'soul_bottle', 1,
                                  [TAGS['item'], TAGS['accessory']]),
    'dangerous_necklace': Inventory.Item('Dangerous Necklace', '+12% damage', 'dangerous_necklace', 1,
                                         [TAGS['item'], TAGS['accessory']]),
    'terrified_necklace': Inventory.Item('Terrified Necklace', 'When hp < 60%:\n+40% speed\n-0.5/sec regeneration',
                                         'terrified_necklace', 1, [TAGS['item'], TAGS['accessory']]),
    'magic_anklet': Inventory.Item('Magic Anklet', '+4/sec mana rege\n+20% speed',
                                   'magic_anklet', 1, [TAGS['item'], TAGS['accessory']]),
    'sheath': Inventory.Item('Sheath', '+18% melee damage\n+16 touching defense\n+0.5/sec regeneration', 'sheath', 0,
                             [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'quiver': Inventory.Item('Quiver', '+10% ranged damage\n+15% speed\n+8 touching defense', 'quiver', 0,
                             [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'hat': Inventory.Item('Hat',
                          '+30% magical damage\n+6/sec mana regeneration\n+1/sec regeneration\n+2 touching defense',
                          'hat', 0, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'firite_helmet': Inventory.Item('Firite Helmet',
                                    'Enable night vision\n+30% melee damage\n+28 touching defense\n+19 magic defense\n+1.5/sec regeneration',
                                    'firite_helmet', 3,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'firite_cloak': Inventory.Item('Firite Cloak',
                                   'Enable night vision\n+32% ranged damage\n+14 touching defense\n+7 magic defense\n+0.5/sec regeneration\n+45% speed',
                                   'firite_cloak', 3,
                                   [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'firite_pluvial': Inventory.Item('Firite Pluvial',
                                     'Enable night vision\n+44% magical damage\n+6 touching defense\n+12 magic defense\n+2.5/sec regeneration\n+16/sec mana regeneration',
                                     'firite_pluvial', 3, [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                                           TAGS['major_accessory']]),
    'orange_ring': Inventory.Item('Orange Ring', 'Not afraid.\n+32% speed\n-2 touching defense', 'orange_ring', 3,
                                  [TAGS['item'], TAGS['accessory']]),
    'green_ring': Inventory.Item('Green Ring', 'Mercy.\n+18 touching defense\n-40% speed', 'green_ring', 3,
                                 [TAGS['item'], TAGS['accessory']]),
    'blue_ring': Inventory.Item('Blue Ring',
                                'Never lies.\n+8/sec mana regeneration\n+5 magic defense\n-1/sec regeneration',
                                'blue_ring', 3, [TAGS['item'], TAGS['accessory']]),
    'aimer': Inventory.Item('Aimer', 'Enables aiming to menaces.', 'aimer', 2,
                            [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'winds_necklace': Inventory.Item('Winds Necklace', '+50% speed.\n-35% damage.\n+20% ranged damage.',
                                     'winds_necklace', 2, [TAGS['item'], TAGS['accessory']]),
    'windstorm_swordman_mark': Inventory.Item('Windstorm Swordman\'s Mark',
                                              '+45% melee damage\n-12% damage\n+32 touching defense\n+34 magic defense\n+3/sec regeneration\nNight vision\nY: sweep the weapon and dealing 3 times the damage\n80 mana cost',
                                              'windstorm_swordman_mark', 4,
                                              [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                               TAGS['light_source'], TAGS['major_accessory']]),
    'windstorm_assassin_mark': Inventory.Item('Windstorm Assassin\'s Mark',
                                              '+56% ranged damage\n-12% damage\n+17 touching defense\n+18 magic defense\n+1/sec regeneration\nNight vision\nY: use the weapon and sprint\n60 mana cost',
                                              'windstorm_assassin_mark', 4,
                                              [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                               TAGS['light_source'], TAGS['major_accessory']]),
    'windstorm_warlock_mark': Inventory.Item('Windstorm Warlock\'s Mark',
                                             '+60% magical damage\n-12% damage\n+5 touching defense\n+12 magic defense\n+6/sec regeneration\n+15/sec mana regeneration\nNight vision\nY: use 20 times of the mana cost, summon 25 projectiles to the enemies',
                                             'windstorm_warlock_mark', 4,
                                             [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                              TAGS['light_source'], TAGS['major_accessory']]),
    'palladium_glove': Inventory.Item('Palladium Glove',
                                      '+25% damage\n+16% speed\n+18/sec regeneration\n+8/sec mana regeneration\n+90 touching defense\n+65 magic defense\nNight vision',
                                      'palladium_glove', 5,
                                      [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'mithrill_glove': Inventory.Item('Mithrill Glove',
                                     '+32% damage\n+80% speed\n+3/sec regeneration\n+40/sec mana regeneration\n85 touching defense\n+95 magic defense\nNight vision',
                                     'mithrill_glove', 5,
                                     [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'titanium_glove': Inventory.Item('Titanium Glove',
                                     '+50% damage\n+20% speed\n+10/sec regeneration\n+32/sec mana regeneration\n+108 touching defense\n+40 magic defense\nNight vision',
                                     'titanium_glove', 5,
                                     [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'paladins_mark': Inventory.Item('Paladin\'s Mark',
                                    '+66% melee damage\n-15% damage\n+85 touching defense\n+70 magic defense\n+5/sec regeneration\nNight vision\nY: deal hallow stab\n40 mana cost',
                                    'paladins_mark', 5,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['light_source'],
                                     TAGS['major_accessory']]),
    'daedalus_mark': Inventory.Item('Daedalus\'s Mark',
                                    '+72% ranged damage\n-15% damage\n+55 touching defense\n+45 magic defense\n+2/sec regeneration\nNight vision\nY: summon daedalus storm\n1200 piercing damage\n600 projectile speed\n60 mana cost',
                                    'daedalus_mark', 5,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['light_source'],
                                     TAGS['major_accessory']]),
    'necklace_of_life': Inventory.Item('Necklace of Life', '+30/sec regeneration\n+60/sec mana regeneration',
                                       'necklace_of_life', 7, [TAGS['item'], TAGS['accessory']]),
    'cowboy_hat': Inventory.Item('Cowboy Hat', '-20% damage\n+90% ranged damage\n+50% speed\n+10/sec '
                                               'regeneration\n+120 touching defense\n+150 magic defense\nNight '
                                               'vision\nY: +114514 defense\n+500% damage\n+300% speed\n400 mana '
                                               'cost', 'cowboy_hat', 7, [TAGS['item'], TAGS['accessory'],
                                                                         TAGS['night_vision'],
                                                                         TAGS['major_accessory']]),

    'wings': Inventory.Item('Wings', 'The perseverance to fly.\n-60% air resistance\n+80% speed', 'wings', 4,
                            [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'honest_flyer': Inventory.Item('Honest Flyer', 'The perseverance to fly.\n-80% air resistance\n-20% speed',
                                   'honest_flyer', 5, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),

    'weak_healing_potion': Inventory.Item('Weak Healing Potion', 'Recover 50 HP\nCausing potion sickness.',
                                          'weak_healing_potion', 0, [TAGS['item'], TAGS['healing_potion']]),
    'weak_magic_potion': Inventory.Item('Weak Magic Potion', 'Recover 60 MP\nCausing potion sickness.',
                                        'weak_magic_potion', 0, [TAGS['item'], TAGS['magic_potion']]),
    'crabapple': Inventory.Item('Crabapple', 'Heals 120 HP', 'crabapple', 2, [TAGS['item'], TAGS['healing_potion']]),
    'butterscotch_pie': Inventory.Item('Butterscotch Pie', 'Heals 240 HP', 'butterscotch_pie', 4,
                                       [TAGS['item'], TAGS['healing_potion']]),
    'seatea': Inventory.Item('Seatea', 'Recovers 150 MP', 'seatea', 4, [TAGS['item'], TAGS['magic_potion']]),

    'mana_crystal': Inventory.Item('Mana Crystal', '+15 maximum mana.', 'mana_crystal', 2, [TAGS['item']]),
    'firy_plant': Inventory.Item('Firy Plant', '+20 maximum hp', 'firy_plant', 3, [TAGS['item']]),
    'spiritual_heart': Inventory.Item('Spiritual Heart',
                                      '+100 maximum hp\n+180 maximum mana\nSomething perseverance happen.',
                                      'spiritual_heart', 4, [TAGS['item']]),
    'life_fruit': Inventory.Item('Life Fruit', '+400 maximum HP\n+500 maximum MP\n+40 maximum talent', 'life_fruit', 4,
                                 [TAGS['item'], TAGS['healing_potion']]),

    'ballet_shoes': Inventory.Item('Ballet Shoes', '', 'ballet_shoes', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'], TAGS['magic_lv_3']]),
    'tough_gloves': Inventory.Item('Tough Gloves', 'Shoots arrows by your hand.', 'tough_gloves', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'burnt_pan': Inventory.Item('Burnt Pan', 'Press Q to stab.', 'burnt_pan', 6, [TAGS['item'], TAGS['weapon']]),
    'toy_knife': Inventory.Item('Toy Knife', 'Deal damage to enemies in range.', 'toy_knife', 7,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'], TAGS['magic_lv_5']]),
    'worn_notebook': Inventory.Item('Worn Notebook', '', 'worn_notebook', 7, [TAGS['item'], TAGS['weapon']]),
    'empty_gun': Inventory.Item('Empty Gun', '', 'empty_gun', 7, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),

    'suspicious_eye': Inventory.Item('Suspicious Eye', 'Summon the true eye', 'suspicious_eye', 0, [TAGS['item']]),
    'fire_slime': Inventory.Item('Fire Slime', 'Summon the magma king', 'fire_slime', 0, [TAGS['item']]),
    'wind': Inventory.Item('Wind', 'Summon the sandstorm', 'wind', 0, [TAGS['item']]),
    'blood_substance': Inventory.Item('Blood Substance', 'Summon the Abyss Eye', 'blood_substance', 0, [TAGS['item']]),
    'mechanic_eye': Inventory.Item('Mechanic Eye', 'Summon the twin eyes', 'mechanic_eye', 0, [TAGS['item']]),
    'mechanic_worm': Inventory.Item('Mechanic Worm', 'Summon the destroyer', 'mechanic_worm', 0, [TAGS['item']]),
    'electric_unit': Inventory.Item('Electric Unit', 'Summon the CPU', 'electric_unit', 0, [TAGS['item']]),
    'mechanic_spider': Inventory.Item('Electric Spider', 'Summon the Greed', 'mechanic_spider', 0, [TAGS['item']]),
    'watch': Inventory.Item('Watch', 'Summon the eye of time', 'watch', 0, [TAGS['item']]),
    'metal_food': Inventory.Item('Metal Food', 'Summon the devil python', 'metal_food', 0, [TAGS['item']]),
    'joker': Inventory.Item('JOKER', 'Summon the Joker Evil', 'joker', 0, [TAGS['item']]),

    'invalid': Inventory.Item('Invalid Item', 'Invalid item', 'invalid', 0, []),
}


class Items:
    ITEMS = items_dict

    def __getitem__(self, item):
        try:
            return self.ITEMS[item]
        except KeyError:
            self.ITEMS[item] = Inventory.Item('Invalid Item', 'Invalid item: ' + item.replace('_', ' '), item, 0, [])
            return self.ITEMS[item]

    def values(self):
        return self.ITEMS.values()

    def keys(self):
        return self.ITEMS.keys()

    def items(self):
        return self.ITEMS.items()


ITEMS = Items()


class Recipe:
    def __init__(self, material: dict[str, int], result: str, crafted_amount: int = 1):
        self.material = material
        self.result = result
        self.crafted_amount = crafted_amount

    def make(self, inv: Inventory):
        for it, qt in self.material.items():
            if TAGS['workstation'] not in ITEMS[it].tags:
                inv.remove_item(ITEMS[it], qt)
        inv.add_item(ITEMS[self.result], self.crafted_amount)

    def is_valid(self, inv: Inventory):
        for it, qt in self.material.items():
            if not inv.is_enough(ITEMS[it], qt):
                return False
        return True

    def is_related(self, inv: Inventory):
        t = 0
        for it, qt in self.material.items():
            t += inv.is_enough(ITEMS[it], qt)
        return t >= len(self.material) // 2 and t


RECIPES = [
    Recipe({'wood': 15}, 'wooden_hammer'),
    Recipe({'wood': 35, 'wooden_hammer': 1}, 'wooden_sword'),
    Recipe({'wood': 40, 'copper': 1}, 'torch'),
    Recipe({'wood': 20, 'leaf': 8}, 'natural_necklace'),
    Recipe({'wood': 25, 'leaf': 1, 'wooden_hammer': 1}, 'glowing_splint'),
    Recipe({'wood': 55, 'wooden_hammer': 1}, 'bow'),
    Recipe({'wood': 1, 'wooden_hammer': 1}, 'arrow', 10),
    Recipe({'wood': 30, 'copper': 5, 'glowing_splint': 1, 'wooden_hammer': 1}, 'furnace'),
    Recipe({'copper': 3, 'furnace': 1}, 'copper_ingot'),
    Recipe({'copper_ingot': 8}, 'anvil'),
    Recipe({'copper_ingot': 12, 'wood': 10, 'anvil': 1}, 'copper_sword'),
    Recipe({'copper_ingot': 15, 'anvil': 1}, 'copper_wand'),
    Recipe({'copper_ingot': 22, 'anvil': 1}, 'copper_bow'),
    Recipe({'iron': 4}, 'iron_ingot'),
    Recipe({'iron_ingot': 15, 'wood': 10, 'anvil': 1}, 'iron_sword'),
    Recipe({'steel_ingot': 10, 'iron_ingot': 5, 'anvil': 1}, 'steel_sword'),
    Recipe({'iron_ingot': 12, 'steel_ingot': 6}, 'spear'),
    Recipe({'iron_ingot': 12, 'steel_ingot': 12, 'anvil': 1}, 'iron_blade'),
    Recipe({'iron_ingot': 15, 'anvil': 1}, 'iron_wand'),
    Recipe({'iron_ingot': 20, 'anvil': 1}, 'iron_bow'),
    Recipe({'iron_ingot': 25, 'steel_ingot': 2, 'anvil': 1}, 'pistol'),
    Recipe({'iron_ingot': 5, 'steel_ingot': 20, 'anvil': 1}, 'rifle'),
    Recipe({'steel_ingot': 24, 'iron_ingot': 6, 'anvil': 1}, 'steel_bow'),
    Recipe({'steel': 4}, 'steel_ingot'),
    Recipe({'steel_ingot': 1, 'iron_ingot': 1}, 'bullet', 50),
    Recipe({'steel': 10, 'anvil': 1}, 'shield'),
    Recipe({'cell_organization': 3}, 'soul_bottle'),
    Recipe({'cell_organization': 1}, 'weak_healing_potion', 10),
    Recipe({'cell_organization': 5, 'iron_ingot': 8}, 'terrified_necklace'),
    Recipe({'torch': 10, 'steel': 5, 'iron': 5, 'anvil': 1}, 'burning_book'),
    Recipe({'platinum': 3}, 'platinum_ingot'),
    Recipe({'platinum_ingot': 15, 'steel_ingot': 10, 'anvil': 1}, 'platinum_sword'),
    Recipe({'platinum_ingot': 21, 'iron_ingot': 8, 'anvil': 1}, 'platinum_blade'),
    Recipe({'platinum_ingot': 20, 'anvil': 1}, 'platinum_spear'),
    Recipe({'platinum_ingot': 15, 'magic_stone': 8, 'anvil': 1}, 'platinum_wand'),
    Recipe({'wood': 60, 'mana_crystal': 2, 'leaf': 10, 'anvil': 1}, 'life_wooden_wand'),
    Recipe({'platinum_ingot': 20, 'anvil': 1}, 'platinum_bow'),
    Recipe({'platinum_ingot': 30, 'magic_stone': 5, 'anvil': 1}, 'submachine_gun'),
    Recipe({'bullet': 100, 'platinum_ingot': 1, 'anvil': 1}, 'platinum_bullet', 100),
    Recipe({'magic_stone': 10}, 'mana_crystal'),
    Recipe({'magic_stone': 15, 'wood': 10, 'anvil': 1}, 'magic_arrow', 100),
    Recipe({'magic_stone': 25, 'platinum': 60}, 'talent_book'),
    Recipe({'magic_stone': 5, 'platinum_ingot': 6}, 'magic_anklet'),
    Recipe({'magic_stone': 1}, 'weak_magic_potion', 25),
    Recipe({'magic_blade': 2}, 'magic_sword'),
    Recipe({'magic_sword': 2}, 'magic_blade'),
    Recipe({'magic_stone': 40, 'anvil': 1}, 'night_visioner'),
    Recipe({'platinum_ingot': 3, 'magic_blade': 1}, 'sheath'),
    Recipe({'platinum_ingot': 3, 'magic_sword': 1}, 'sheath'),
    Recipe({'platinum_ingot': 3, 'magic_arrow': 100}, 'quiver'),
    Recipe({'platinum': 9, 'mana_crystal': 3}, 'hat'),
    Recipe({'platinum_ingot': 10, 'blood_ingot': 20, 'anvil': 1}, 'bloody_sword'),
    Recipe({'platinum_ingot': 6, 'blood_ingot': 24, 'anvil': 1}, 'bloody_bow'),
    Recipe({'platinum_ingot': 8, 'blood_ingot': 16, 'mana_crystal': 1, 'anvil': 1}, 'blood_wand'),
    Recipe({'blood_ingot': 5, 'platinum_ingot': 5, 'anvil': 1}, 'blood_arrow', 100),
    Recipe({'blood_ingot': 2, 'platinum_ingot': 1, 'anvil': 1}, 'plasma', 50),
    Recipe({'blood_ingot': 8, 'firite_ingot': 22, 'anvil': 1}, 'firite_spear'),
    Recipe({'blood_ingot': 5, 'firite_ingot': 30, 'anvil': 1}, 'magma_assaulter'),
    Recipe({'firite_ingot': 25, 'platinum': 20, 'anvil': 1}, 'volcano'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_helmet'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_cloak'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_pluvial'),
    Recipe({'platinum': 24, 'blood_ingot': 16, 'magic_stone': 10, 'firy_plant': 1, 'anvil': 1}, 'hematology'),
    Recipe({'platinum': 24, 'magic_stone': 6, 'firite_ingot': 8, 'firy_plant': 2, 'anvil': 1}, 'fire_magic_sword'),
    Recipe({'magic_stone': 10, 'firy_plant': 1}, 'crabapple', 5),
    Recipe({'mysterious_substance': 4, 'furnace': 1}, 'mysterious_ingot'),
    Recipe({'platinum_ingot': 30, 'mysterious_ingot': 5, 'anvil': 1}, 'winds_necklace'),
    Recipe({'mysterious_ingot': 12, 'anvil': 1}, 'recurve_bow'),
    Recipe({'mysterious_ingot': 10, 'blood_ingot': 8, 'anvil': 1}, 'sand_sword'),
    Recipe({'mysterious_ingot': 1, 'blood_ingot': 2, 'anvil': 1}, 'rock_bullet', 200),
    Recipe({'mysterious_ingot': 11, 'blood_ingot': 20, 'mana_crystal': 2}, 'rock_wand'),
    Recipe({'platinum_sword': 1, 'magic_sword': 1, 'bloody_sword': 1, 'volcano': 1, 'sand_sword': 1, 'storm_core': 1},
           'nights_edge'),
    Recipe({'platinum_ingot': 32, 'blood_ingot': 20, 'firite_ingot': 20, 'mysterious_ingot': 20, 'storm_core': 1},
           'nights_pike'),
    Recipe({'platinum_wand': 1, 'burning_book': 1, 'talent_book': 1, 'blood_wand': 1, 'rock_wand': 1, 'storm_core': 1},
           'midnights_wand'),
    Recipe({'platinum_bow': 1, 'submachine_gun': 1, 'bloody_bow': 1, 'magma_assaulter': 1, 'recurve_bow': 1,
            'storm_core': 1}, 'shadow'),
    Recipe({'platinum_ingot': 10, 'blood_ingot': 5, 'firite_ingot': 5, 'mysterious_ingot': 5, 'storm_core': 1},
           'shadow_bullet', 500),
    Recipe({'storm_core': 3}, 'windstorm_warlock_mark'),
    Recipe({'storm_core': 3}, 'windstorm_assassin_mark'),
    Recipe({'storm_core': 3}, 'windstorm_swordman_mark'),
    Recipe({'soul': 60, 'mithrill_anvil': 1}, 'spiritual_heart'),
    Recipe({'soul': 30, 'firy_plant': 5}, 'butterscotch_pie', 20),
    Recipe({'soul': 10, 'magic_stone': 5}, 'seatea', 20),
    Recipe({'palladium': 4}, 'palladium_ingot'),
    Recipe({'mithrill': 4}, 'mithrill_ingot'),
    Recipe({'titanium': 4}, 'titanium_ingot'),
    Recipe({'mithrill_ingot': 10}, 'mithrill_anvil'),
    Recipe({'palladium_ingot': 12, 'mithrill_anvil': 1}, 'palladium_sword'),
    Recipe({'mithrill_ingot': 12, 'mithrill_anvil': 1}, 'mithrill_sword'),
    Recipe({'titanium_ingot': 12, 'mithrill_anvil': 1}, 'titanium_sword'),
    Recipe({'palladium_ingot': 15, 'mithrill_anvil': 1}, 'palladium_gun'),
    Recipe({'mithrill_ingot': 15, 'mithrill_anvil': 1}, 'mithrill_gun'),
    Recipe({'titanium_ingot': 15, 'mithrill_anvil': 1}, 'titanium_gun'),
    Recipe({'palladium_ingot': 45, 'mithrill_anvil': 1}, 'palladium_glove'),
    Recipe({'mithrill_ingot': 45, 'mithrill_anvil': 1}, 'mithrill_glove'),
    Recipe({'titanium_ingot': 45, 'mithrill_anvil': 1}, 'titanium_glove'),
    Recipe({'spiritual_stabber': 1, 'evil_ingot': 20, 'soul': 120, 'mithrill_anvil': 1}, 'balanced_stabber'),
    Recipe({'spiritual_piercer': 1, 'evil_ingot': 20, 'soul': 120, 'mithrill_anvil': 1}, 'discord_storm'),
    Recipe({'spiritual_destroyer': 1, 'evil_ingot': 20, 'soul': 120, 'mithrill_anvil': 1}, 'evil_book'),
    Recipe({'soul_of_flying': 20, 'soul': 100, 'mithrill_anvil': 1}, 'wings'),
    Recipe({'palladium_ingot': 1, 'mithrill_ingot': 1, 'soul': 5, 'mithrill_anvil': 1}, 'saint_steel_ingot'),
    Recipe({'mithrill_ingot': 1, 'titanium_ingot': 1, 'soul': 5, 'mithrill_anvil': 1}, 'daedalus_ingot'),
    Recipe({'palladium_ingot': 1, 'titanium_ingot': 1, 'soul': 5, 'mithrill_anvil': 1}, 'dark_ingot'),
    Recipe({'balanced_stabber': 1, 'saint_steel_ingot': 8, 'mithrill_anvil': 1}, 'excalibur'),
    Recipe({'windstorm_swordman_mark': 1, 'saint_steel_ingot': 5, 'mithrill_anvil': 1}, 'paladins_mark'),
    Recipe({'discord_storm': 1, 'daedalus_ingot': 8, 'mithrill_anvil': 1}, 'daedalus_stormbow'),
    Recipe({'windstorm_assassin_mark': 1, 'daedalus_ingot': 5, 'mithrill_anvil': 1}, 'daedalus_mark'),
    Recipe({'evil_book': 1, 'dark_ingot': 8, 'mithrill_anvil': 1}, 'curse_book'),
    Recipe({'saint_steel_ingot': 6, 'soul_of_integrity': 20, 'mithrill_anvil': 1}, 'ballet_shoes'),
    Recipe({'palladium_ingot': 24, 'soul_of_integrity': 10, 'mithrill_anvil': 1}, 'gravity_wand'),
    Recipe({'wings': 1, 'soul_of_integrity': 10, 'mithrill_anvil': 1}, 'honest_flyer'),
    Recipe({'soul_of_integrity': 2, 'soul': 1, 'mithrill_anvil': 1}, 'quick_arrow', 200),
    Recipe({'daedalus_ingot': 6, 'soul_of_bravery': 20, 'mithrill_anvil': 1}, 'tough_gloves'),
    Recipe({'soul_of_bravery': 2, 'soul': 1, 'mithrill_anvil': 1}, 'quick_bullet', 200),
    Recipe({'mithrill_ingot': 24, 'soul_of_kindness': 10, 'mithrill_anvil': 1}, 'shield_wand'),
    Recipe({'mithrill_ingot': 20, 'soul_of_kindness': 24}, 'energy_spear'),
    Recipe({'dark_ingot': 6, 'soul_of_kindness': 20}, 'burnt_pan'),
    Recipe(
        {'excalibur': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10, 'mithrill_anvil': 1},
        'true_excalibur'),
    Recipe(
        {'nights_edge': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10, 'mithrill_anvil': 1},
        'true_nights_edge'),
    Recipe({'shadow': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10, 'mithrill_anvil': 1},
           'true_shadow'),
    Recipe({'soul_of_integrity': 2, 'soul_of_bravery': 1, 'soul_of_kindness': 1, 'mana_crystal': 1},
           'mystery_core'),
    Recipe({'mithrill_ingot': 30, 'mystery_core': 3, 'soul': 300}, 'forbidden_curse__spirit'),
    Recipe({'mithrill_ingot': 30, 'mystery_core': 3, 'evil_ingot': 100}, 'forbidden_curse__evil'),
    Recipe({'daedalus_stormbow': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10,
            'mithrill_anvil': 1},
           'true_daedalus_stormbow'),
    Recipe({'soul_of_perseverance': 15, 'saint_steel_ingot': 18}, 'perseverance_sword'),
    Recipe({'soul_of_perseverance': 32, 'saint_steel_ingot': 8}, 'black_hole_sword'),
    Recipe({'saint_steel_ingot': 18, 'soul_of_perseverance': 12}, 'worn_notebook'),
    Recipe({'mithrill_ingot': 30, 'mystery_core': 3, 'soul_of_patience': 10}, 'forbidden_curse__time'),
    Recipe({'dark_ingot': 18, 'soul_of_patience': 12}, 'toy_knife'),
    Recipe({'daedalus_ingot': 18, 'soul_of_justice': 12}, 'empty_gun'),
    Recipe({'chlorophyll': 1, 'weak_healing_potion': 1}, 'photon'),
    Recipe({'chlorophyll': 1, 'crabapple': 1}, 'photon', 2),
    Recipe({'chlorophyll': 1, 'butterscotch_pie': 1}, 'photon', 3),
    Recipe({'dark_ingot': 10, 'photon': 20}, 'prism'),
    Recipe({'chlorophyll': 1, 'photon': 5, 'soul_of_perseverance': 1, 'soul_of_patience': 1,
            'soul_of_justice': 1, 'soul_of_growth': 1}, 'chlorophyte_ingot', 3),
    Recipe({'chlorophyte_ingot': 16, 'soul_of_perseverance': 12, 'soul_of_patience': 3, 'soul_of_justice': 3},
           'life_devourer'),
    Recipe({'chlorophyte_ingot': 18, 'soul_of_justice': 12, 'soul_of_patience': 3, 'soul_of_perseverance': 3},
           'lazer_gun'),
    Recipe({'chlorophyte_ingot': 12, 'photon': 32, 'soul_of_patience': 10, 'soul_of_perseverance': 2,
            'soul_of_justice': 2}, 'prism_wand'),
    Recipe({'chlorophyte_ingot': 15, 'photon': 60, 'soul_of_patience': 10, 'soul_of_perseverance': 3,
            'soul_of_justice': 3}, 'astigmatism'),
    Recipe({'chlorophyte_ingot': 16}, 'necklace_of_life'),
    Recipe({'soul_of_growth': 32, 'chlorophyte_ingot': 1, 'butterscotch_pie': 1}, 'life_fruit'),
    Recipe({'soul_of_growth': 24, 'chlorophyte_ingot': 8}, 'life_wand'),
    Recipe({'chlorophyte_ingot': 5, 'soul_of_justice': 32}, 'cowboy_hat'),

    Recipe({'photon': 100, 'chlorophyll': 1}, 'lights_bible'),
    Recipe({'lights_bible': 1,' photon': 1}, 'light_purify'),
    Recipe({'soul': 20, 'chlorophyll': 1, 'soul_of_patience': 10}, 'energy_bible'),

    Recipe({'cell_organization': 10}, 'suspicious_eye'),
    Recipe({'cell_organization': 5, 'firite_ingot': 1}, 'fire_slime'),
    Recipe({'cell_organization': 5, 'mysterious_substance': 3}, 'wind'),
    Recipe({'cell_organization': 30, 'storm_core': 3}, 'blood_substance'),
    Recipe({'palladium_ingot': 1, 'mithrill_ingot': 1, 'titanium_ingot': 1, 'soul': 10}, 'mechanic_eye'),
    Recipe({'mithrill_ingot': 1, 'titanium_ingot': 1, 'palladium_ingot': 1, 'soul': 10}, 'mechanic_worm'),
    Recipe({'titanium_ingot': 1, 'palladium_ingot': 1, 'mithrill_ingot': 1, 'soul': 10}, 'electric_unit'),
    Recipe({'palladium_ingot': 2, 'soul_of_kindness': 1}, 'mechanic_spider'),
    Recipe({'mithrill_ingot': 2, 'soul_of_integrity': 1}, 'watch'),
    Recipe({'titanium_ingot': 2, 'soul_of_bravery': 1}, 'metal_food'),
    Recipe({'chlorophyte_ingot': 1, 'photon': 4}, 'joker'),

]


def setup():
    for i, item in enumerate(ITEMS.values()):
        item.inner_id = i


def get_item_by_id(item_id: int):
    return [item for item in ITEMS.values() if item.inner_id == item_id][0]


setup()

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

    Rarity_Colors = [(255, 255, 255), (255, 255, 127), (150, 255, 127), (127, 255, 255), (255, 127, 127), (255, 165, 64), (128, 64, 128), (255, 200, 255), (255, 127, 255), (255, 200, 255), (255, 255, 255)]
    Rarity_Names = ["Common", "Uncommon", "Rare", "Very Rare", "Epic", "Legendary", "Mythic", "Super Mythic", "Godlike", "Super Godlike", "Unknown"]

    class Item:
        class Tag:
            def __init__(self, name: str, value: str):
                self.name = name
                self.value = value

            def get_all_items(self):
                return [item for item in ITEMS.values() if self.name in [tag.name for tag in item.tags]]

        def __init__(self, name, description, identifier: str, rarity: int = 0, tags: list = []):
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
            if TAGS['magic_weapon'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
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

TAGS = {
    'item': Inventory.Item.Tag('item', 'item'),
    'weapon': Inventory.Item.Tag('weapon', 'weapon'),
    'magic_weapon': Inventory.Item.Tag('magic_weapon','magic_weapon'),
    'accessory': Inventory.Item.Tag('accessory', 'accessory'),
    'healing_potion': Inventory.Item.Tag('healing_potion', 'healing_potion'),
    'magic_potion': Inventory.Item.Tag('magic_potion','magic_potion'),
    'workstation': Inventory.Item.Tag('workstation', 'workstation'),
    'light_source': Inventory.Item.Tag('light_source', 'light_source'),
    'night_vision': Inventory.Item.Tag('night_vision', 'night_vision'),
    'bow': Inventory.Item.Tag('bow', 'bow'),
    'gun': Inventory.Item.Tag('gun', 'gun'),
    'ammo': Inventory.Item.Tag('ammo', 'ammo'),
    'ammo_arrow': Inventory.Item.Tag('ammo_arrow', 'ammo_arrow'),
    'ammo_bullet': Inventory.Item.Tag('ammo_bullet', 'ammo_bullet'),
}
ITEMS = {
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

    'torch': Inventory.Item('Torch', 'Ignite the darkness.', 'torch', 0, [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'night_visioner': Inventory.Item('Night Visioner', 'See in the dark.', 'night_visioner', 0, [TAGS['item'], TAGS['accessory'], TAGS['light_source'], TAGS['night_vision']]),

    'wooden_hammer': Inventory.Item('Wooden Hammer', '', 'wooden_hammer', 0, [TAGS['item'], TAGS['workstation']]),
    'furnace': Inventory.Item('Furnace', '', 'furnace', 0, [TAGS['item'], TAGS['workstation']]),
    'anvil': Inventory.Item('Anvil', '', 'anvil', 0, [TAGS['item'], TAGS['workstation']]),

    'wooden_sword': Inventory.Item('Wooden Sword', '', 'wooden_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'copper_sword': Inventory.Item('Copper Sword', '', 'copper_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'iron_sword': Inventory.Item('Iron Sword', '', 'iron_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'iron_blade': Inventory.Item('Iron Blade', '', 'iron_blade', 0, [TAGS['item'], TAGS['weapon']]),
    'steel_sword': Inventory.Item('Steel Sword', '','steel_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'platinum_sword': Inventory.Item('Platinum Sword', '', 'platinum_sword', 1, [TAGS['item'], TAGS['weapon']]),
    'platinum_blade': Inventory.Item('Platinum Blade', '', 'platinum_blade', 1, [TAGS['item'], TAGS['weapon']]),
    'magic_sword': Inventory.Item('Magic Sword', '','magic_sword', 2, [TAGS['item'], TAGS['weapon']]),
    'magic_blade': Inventory.Item('Magic Blade', '','magic_blade', 2, [TAGS['item'], TAGS['weapon']]),
    'bloody_sword': Inventory.Item('Bloody Sword', 'When sweeping, press Q to sprint.', 'bloody_sword', 2, [TAGS['item'], TAGS['weapon']]),
    'volcano': Inventory.Item('Volcano', 'Gives target to fire.', 'volcano', 2, [TAGS['item'], TAGS['weapon']]),

    'nights_edge': Inventory.Item('Nights Edge', 'Night....', 'nights_edge', 4, [TAGS['item'], TAGS['weapon']]),

    'bow': Inventory.Item('Bow', '', 'bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'copper_bow': Inventory.Item('Copper Bow', '', 'copper_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'iron_bow': Inventory.Item('Iron Bow', '', 'iron_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'steel_bow': Inventory.Item('Steel Bow', '', 'steel_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'platinum_bow': Inventory.Item('Platinum Bow', '', 'platinum_bow', 1, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'bloody_bow': Inventory.Item('Bloody Bow', '', 'bloody_bow', 2, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),

    'pistol': Inventory.Item('pistol', '', 'pistol', 0, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rifle': Inventory.Item('rifle', '', 'rifle', 0, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'submachine_gun': Inventory.Item('submachine_gun', '','submachine_gun', 2, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'magma_assaulter': Inventory.Item('magma_assaulter', 'When shooting, press Q to sprint back.','magma_assaulter', 2, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),

    'arrow': Inventory.Item('Arrow', '', 'arrow', 0, [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'magic_arrow': Inventory.Item('Magic Arrow', '', 'magic_arrow', 1, [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'blood_arrow': Inventory.Item('Blood Arrow', '', 'blood_arrow', 2, [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'bullet': Inventory.Item('Bullet', '', 'bullet', 0, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'platinum_bullet': Inventory.Item('Platinum Bullet', '', 'platinum_bullet', 1, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'plasma': Inventory.Item('Plasma', '', 'plasma', 2, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),

    'glowing_splint': Inventory.Item('Glowing Splint', 'Shoots glows.', 'glowing_splint', 0, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),
    'copper_wand': Inventory.Item('Copper Wand', '', 'copper_wand', 0, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),
    'iron_wand': Inventory.Item('Iron Wand', '', 'iron_wand', 0, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),
    'platinum_wand': Inventory.Item('Platinum Wand', '', 'platinum_wand', 1, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),
    'burning_book': Inventory.Item('Burning Book', 'Burns enemies.', 'burning_book', 2, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),
    'talent_book': Inventory.Item('Talent Book', '', 'talent_book', 2, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),
    'blood_wand': Inventory.Item('Blood Wand', '', 'blood_wand', 2, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),
    'hematology': Inventory.Item('Hematology', 'Recovers 30 HP.', 'hematology', 2, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon']]),

    'shield': Inventory.Item('Simple Shield', '+7 touching defense\n+12 physic defense', 'shield', 1, [TAGS['item'], TAGS['accessory']]),
    'soul_bottle': Inventory.Item('Soul Bottle', '+0.5/sec regeneration','soul_bottle', 1, [TAGS['item'], TAGS['accessory']]),
    'dangerous_necklace': Inventory.Item('Dangerous Necklace', '+12% damage', 'dangerous_necklace', 1, [TAGS['item'], TAGS['accessory']]),
    'terrified_necklace': Inventory.Item('Terrified Necklace', 'When hp < 60%:\n+40% speed\n-0.5/sec regeneration', 'terrified_necklace', 1, [TAGS['item'], TAGS['accessory']]),
    'sheath': Inventory.Item('Sheath', '+18% melee damage\n+16 touching defense\n+0.5/sec regeneration', 'sheath', 0, [TAGS['item'], TAGS['accessory']]),
    'quiver': Inventory.Item('Quiver', '+10% ranged damage\n+15% speed\n+8 touching defense', 'quiver', 0, [TAGS['item'], TAGS['accessory']]),
    'hat': Inventory.Item('Hat', '+30% magical damage\n+6/sec mana regeneration\n+1/sec regeneration\n+2 touching defense', 'hat', 0, [TAGS['item'], TAGS['accessory']]),
    'firite_helmet': Inventory.Item('Firite Helmet', 'Enable night vision\n+30% melee damage\n+28 touching defense\n+19 magic defense\n+1.5/sec regeneration', 'firite_helmet', 3, [TAGS['item'], TAGS['accessory'], TAGS['night_vision']]),
    'firite_cloak': Inventory.Item('Firite Cloak', 'Enable night vision\n+32% ranged damage\n+14 touching defense\n+7 magic defense\n+0.5/sec regeneration\n+45% speed', 'firite_cloak', 3, [TAGS['item'], TAGS['accessory'], TAGS['night_vision']]),
    'firite_pluvial': Inventory.Item('Firite Pluvial', 'Enable night vision\n+44% magical damage\n+6 touching defense\n+12 magic defense\n+2.5/sec regeneration\n+16/sec mana regeneration', 'firite_pluvial', 3, [TAGS['item'], TAGS['accessory'], TAGS['night_vision']]),
    'orange_ring': Inventory.Item('Orange Ring', 'Not afraid.\n+32% speed\n-2 touching defense', 'orange_ring', 3, [TAGS['item'], TAGS['accessory']]),
    'green_ring': Inventory.Item('Green Ring', 'Mercy.\n+18 touching defense\n-40% speed', 'green_ring', 3, [TAGS['item'], TAGS['accessory']]),
    'blue_ring': Inventory.Item('Blue Ring', 'Never lies.\n+8/sec mana regeneration\n+5 magic defense\n-1/sec regeneration', 'blue_ring', 3, [TAGS['item'], TAGS['accessory']]),
    'aimer': Inventory.Item('Aimer', 'Enables aiming to menaces.', 'aimer', 2, [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),

    'weak_healing_potion': Inventory.Item('Weak Healing Potion', 'Recover 50 HP\nCausing potion sickness.', 'weak_healing_potion', 0, [TAGS['item'], TAGS['healing_potion']]),
    'weak_magic_potion': Inventory.Item('Weak Magic Potion', 'Recover 60 MP\nCausing potion sickness.', 'weak_magic_potion', 0, [TAGS['item'], TAGS['magic_potion']]),

    'mana_crystal': Inventory.Item('Mana Crystal', '+15 maximum mana forever.', 'mana_crystal', 2, [TAGS['item']]),

    'suspicious_eye': Inventory.Item('Suspicious Eye', 'Summon the true eye', 'suspicious_eye', 0, [TAGS['item']]),
    'fire_slime': Inventory.Item('Fire Slime', 'Summon the magma king', 'fire_slime', 0, [TAGS['item']]),
}

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
    Recipe({'wood': 25, 'leaf': 5, 'wooden_hammer': 1}, 'glowing_splint'),
    Recipe({'wood': 55, 'wooden_hammer': 1}, 'bow'),
    Recipe({'wood': 1, 'wooden_hammer': 1}, 'arrow', 10),
    Recipe({'wood': 30, 'copper': 5, 'glowing_splint': 1, 'wooden_hammer': 1}, 'furnace'),
    Recipe({'copper': 6, 'furnace': 1}, 'copper_ingot'),
    Recipe({'copper_ingot': 15}, 'anvil'),
    Recipe({'copper_ingot': 12, 'wood': 10, 'anvil': 1}, 'copper_sword'),
    Recipe({'copper_ingot': 15, 'anvil': 1}, 'copper_wand'),
    Recipe({'copper_ingot': 22, 'anvil': 1}, 'copper_bow'),
    Recipe({'iron': 4}, 'iron_ingot'),
    Recipe({'iron_ingot': 15, 'wood': 10, 'anvil': 1}, 'iron_sword'),
    Recipe({'steel_ingot': 10, 'iron_ingot': 5, 'anvil': 1}, 'steel_sword'),
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
    Recipe({'platinum_ingot': 15, 'magic_stone': 8, 'anvil': 1}, 'platinum_wand'),
    Recipe({'platinum_ingot': 20, 'anvil': 1}, 'platinum_bow'),
    Recipe({'platinum_ingot': 30, 'magic_stone': 5, 'anvil': 1}, 'submachine_gun'),
    Recipe({'bullet': 100, 'platinum_ingot': 1, 'anvil': 1}, 'platinum_bullet', 100),
    Recipe({'magic_stone': 10}, 'mana_crystal'),
    Recipe({'magic_stone': 15, 'wood': 10, 'anvil': 1}, 'magic_arrow', 100),
    Recipe({'magic_stone': 25, 'platinum': 60}, 'talent_book'),
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
    Recipe({'platinum': 24, 'blood_ingot': 16, 'magic_stone': 10, 'anvil': 1}, 'hematology'),
    Recipe({'blood_ingot': 5, 'platinum_ingot': 5, 'anvil': 1}, 'blood_arrow', 100),
    Recipe({'blood_ingot': 2, 'platinum_ingot': 1, 'anvil': 1}, 'plasma', 50),
    Recipe({'blood_ingot': 5, 'firite_ingot': 30, 'anvil': 1}, 'magma_assaulter'),
    Recipe({'firite_ingot': 25, 'platinum': 20, 'anvil': 1}, 'volcano'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_helmet'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_cloak'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_pluvial'),

    Recipe({'cell_organization': 10}, 'suspicious_eye'),
    Recipe({'cell_organization': 5, 'firite_ingot': 1}, 'fire_slime'),

]

def setup():
    for i, item in enumerate(ITEMS.values()):
        item.inner_id = i

def get_item_by_id(item_id: int):
    return [item for item in ITEMS.values() if item.inner_id == item_id][0]

setup()

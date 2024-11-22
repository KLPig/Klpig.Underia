from src.physics import mover, vector
from src.underia import game, styles, inventory
from src.values import hp_system, damages
from src.resources import position
import pygame as pg
import random
import math

class Loots:
    def __call__(self):
        return []

class IndividualLoot(Loots):
    def __init__(self, item, chance, amount_min, amount_max):
        self.item = item
        self.chance = chance
        self.amount_min = amount_min
        self.amount_max = amount_max

    def __call__(self):
        if random.random() < self.chance:
            return [(self.item, random.randint(self.amount_min, self.amount_max))]
        else:
            return []

class SelectionLoot(Loots):
    def __init__(self, items: list[tuple[int, int, int]], selection_min, selection_max):
        self.items = items
        self.selection_min = selection_min
        self.selection_max = selection_max

    def __call__(self):
        selection_size = random.randint(self.selection_min, self.selection_max)
        return [(item, random.randint(rmin, rmax)) for item, rmin, rmax in random.choices(self.items, k=selection_size)]

class LootTable:
    def __init__(self, loot_list: list[Loots]):
        self.loot_list = loot_list

    def __call__(self):
        loot_items = []
        for loot in self.loot_list:
            loot_items.extend(loot())
        return loot_items

class MonsterAI(mover.Mover):
    MASS = 120
    FRICTION = 0.95
    TOUCHING_DAMAGE = 10

    def __init__(self, pos):
        super().__init__(pos)
        self.touched_player = False

    def on_update(self):
        pass

class TreeMonsterAI(MonsterAI):
    MASS = 200
    FRICTION = 0.8

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if vector.distance(px, py) < 500:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
        else:
            pass

class CactusAI(TreeMonsterAI):
    TOUCHING_DAMAGE = 30

class EyeAI(MonsterAI):
    MASS = 60
    FRICTION = 0.96
    TOUCHING_DAMAGE = 16

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0

    def on_update(self):
        self.timer = (self.timer + 1) % 240
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.touched_player:
            self.timer = -100
        if self.timer < 110:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 12))
        elif self.timer < 190:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 24))
        elif self.timer < 195:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 100))

class SlowMoverAI(MonsterAI):
    MASS = 200
    FRICTION = 0.8

    def __init__(self, pos):
        super().__init__(pos)
        self.idle_timer = 0
        self.idle_rotation = 0

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if vector.distance(px, py) < 500:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
        else:
            self.idle_timer += 1
            if self.idle_timer > random.randint(50, 200):
                self.idle_timer = 0
                self.idle_rotation = (self.idle_rotation + random.randint(-50, 50)) % 360
            self.apply_force(vector.Vector(self.idle_rotation, 100))

class MagmaCubeAI(SlowMoverAI):
    TOUCHING_DAMAGE = 32

class RuneRockAI(SlowMoverAI):
    MASS = 240
    FRICTION = 0.9
    TOUCHING_DAMAGE = 56

class BuildingAI(MonsterAI):
    MASS = 2000
    FRICTION = 0.5
    TOUCHING_DAMAGE = 0

class TrueEyeAI(MonsterAI):
    MASS = 300
    FRICTION = 0.97
    TOUCHING_DAMAGE = 45

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0

    def on_update(self):
        self.timer = (self.timer + 1) % 500
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.timer < 200:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 20))
        elif self.timer < 400:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 80))
        elif self.timer % 50 < 5:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 3000))

class StarAI(MonsterAI):
    FRICTION = 1
    MASS = 200

    def __init__(self, pos):
        super().__init__(pos)
        self.idle_timer = 0
        self.idle_rotation = 0

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if vector.distance(px, py) < 1200:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 40))
        else:
            self.idle_timer += 1
            if self.idle_timer > random.randint(50, 100):
                self.idle_timer = 0
                self.idle_rotation = (self.idle_rotation + random.randint(-50, 50)) % 360
            self.apply_force(vector.Vector(self.idle_rotation, 20))

class MagmaKingAI(MonsterAI):
    FRICTION = 0.9
    MASS = 360
    TOUCHING_DAMAGE = 65

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.state = 0

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.state == 0:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 450))
        elif self.state == 1:
            if self.timer % 40 < 5:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 5000))
        else:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), -200))
        if self.timer > random.randint(50, 200):
            self.state = (self.state + 1) % 3
            self.timer = 0
        self.timer += 1

class SandStormAI(MonsterAI):
    FRICTION = 1
    MASS = 50
    TOUCHING_DAMAGE = 180

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.d = 300
        self.tick = 0

    def on_update(self):
        self.rot = (self.rot + .5) % 360
        self.tick += 1
        self.d = 300 + abs(self.tick % 200 - 100) * 6
        self.pos = game.get_game().player.obj.pos
        ax, ay = vector.rotation_coordinate(self.rot)
        self.pos = (self.pos[0] + ax * self.d, self.pos[1] + ay * self.d)

class MagmaKingFireballAI(MonsterAI):
    FRICTION = 1
    MASS = 50
    TOUCHING_DAMAGE = 0

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0

    def on_update(self):
        self.apply_force(vector.Vector(self.rot, 20))

class Entities:

    class Tag(inventory.Inventory.Item.Tag):
        pass


    class DisplayModes:
        NO_IMAGE = 0
        DIRECTIONAL = 1
        BIDIRECTIONAL = 2
        NO_DIRECTION = 3

    class Entity:
        NAME = 'Entity'
        DISPLAY_MODE = 0
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False

        def __init__(self, pos, img = None, ai: type(MonsterAI) = MonsterAI, hp = 120, hp_sys: hp_system.HPSystem | None = None):
            self.obj: mover.Mover = ai(pos)
            if hp_sys is None:
                self.hp_sys = hp_system.HPSystem(hp)
            else:
                self.hp_sys = hp_sys
            self.img: pg.Surface | None = img
            self.d_img = self.img
            self.rot = 0
            self.touched_player = False

        def set_rotation(self, rot):
            self.rot = rot
            if self.DISPLAY_MODE == Entities.DisplayModes.DIRECTIONAL:
                self.d_img = pg.transform.rotate(self.img, rot)
            elif self.DISPLAY_MODE == Entities.DisplayModes.BIDIRECTIONAL:
                self.d_img = pg.transform.rotate(self.img, 90 if rot > 180 else 270)

        def is_suitable(self, biome: str):
            return True

        def rotate(self, angle):
            self.set_rotation((self.rot + angle) % 360)

        def update(self):
            self.hp_sys.pos = self.obj.pos
            displayer = game.get_game().displayer
            ax, ay = game.get_game().get_anchor()
            self.obj.update()
            self.hp_sys.update()
            if self.DISPLAY_MODE == Entities.DisplayModes.NO_IMAGE:
                pg.draw.circle(displayer.canvas, (0, 0, 255), position.displayed_position(self.obj.pos), 10)
                styles.hp_bar(self.hp_sys, position.displayed_position((self.obj.pos[0], self.obj.pos[1] - 10)), 60)
            else:
                r = self.d_img.get_rect()
                r.center = position.displayed_position(self.obj.pos)
                displayer.canvas.blit(self.d_img, r)
                styles.hp_bar(self.hp_sys, position.displayed_position((self.obj.pos[0], self.obj.pos[1] - self.d_img.get_height() // 2 - 10)), self.img.get_width() * 2)
                if r.collidepoint(pg.mouse.get_pos()):
                    f = displayer.font.render(f'{self.NAME}({int(self.hp_sys.hp)}/{self.hp_sys.max_hp})', True, (255, 255, 255), (0, 0, 0))
                    displayer.canvas.blit(f, pg.mouse.get_pos())

    class WormEntity:
        NAME = 'Entity'
        DISPLAY_MODE = 0
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False

        def __init__(self, pos, length, img_head = None, img_body = None, head_ai: type(MonsterAI) = MonsterAI, hp = 120):
            self.length = length
            self.hp_sys = hp_system.HPSystem(hp)
            self.body = [Entities.Entity(pos, img_head, head_ai, hp_sys=self.hp_sys)] + [Entities.Entity((pos[0] + i + 1, pos[1]), img_body, MonsterAI, hp_sys=self.hp_sys) for i in range(length - 1)]

        def update(self):
            self.body[0].update()
            for i in range(1, self.length):
                rot = (self.body[i].rot + self.body[i - 1].rot * 19) // 20
                self.body[i].obj.pos = self.body[i - 1].obj.pos
                self.body[i].rot = rot
                ax, ay = vector.rotation_coordinate(180 + rot)
                self.body[i].obj.pos = (self.body[i].obj.pos[0] + ax * 60, self.body[i].obj.pos[1] + ay * 60)
                self.body[i].update()

        def set_rotation(self, rot):
            self.body[0].set_rotation(rot)

        def rotate(self, rot):
            self.body[0].set_rotation(rot)



    class Test(Entity):
        NAME = 'Test'
        pass

    class Eye(Entity):
        NAME = 'Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            SelectionLoot([('iron', 10, 12), ('steel', 6, 8)], 1, 2),
            IndividualLoot('dangerous_necklace', 0.1, 1, 1),
            IndividualLoot('cell_organization', 0.8, 1, 3),
        ])

        def is_suitable(self, biome: str):
            return True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_eye'], EyeAI, 190)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -2
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 2

        def update(self):
            self.set_rotation((self.rot * 5 - self.obj.velocity.get_net_rotation()) // 6)
            super().update()

    class TrueEye(Entity):
        NAME = 'True Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('blood_ingot', 1, 20, 30),
            IndividualLoot('platinum', 1, 80, 90),
            SelectionLoot([('orange_ring', 1, 1), ('blue_ring', 1, 1), ('green_ring', 1, 1)], 1, 2),
            IndividualLoot('aimer', 0.2, 1, 1),
            ])
        IS_MENACE = True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_true_eye'], TrueEyeAI, 3800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -5
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 12
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 5

        def update(self):
            self.set_rotation((self.rot * 8 - self.obj.velocity.get_net_rotation()) // 9)
            super().update()

    class Tree(Entity):
        NAME = 'Tree'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25)
        ])

        def is_suitable(self, biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_tree'], BuildingAI, 10)
            self.hp_sys(op='config', maximum_damage=3)

    class TreeMonster(Entity):
        NAME = 'Tree Monster'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.5, 5, 12),
            IndividualLoot('leaf', 0.8, 1, 2),
            IndividualLoot('copper', 0.6, 15, 40),
        ])

        def is_suitable(self, biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_tree_monster'], TreeMonsterAI, 145)

    class Cactus(Entity):
        NAME = 'Cactus'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25),
            IndividualLoot('iron', 0.8, 20, 30),
            IndividualLoot('copper', 0.6, 15, 40),
        ])

        def is_suitable(self, biome: str):
            return biome in ['desert']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_cactus'], CactusAI, 345)

    class MagmaCube(Entity):
        NAME = 'Magma Cube'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('cell_organization', 0.9, 10, 15),
            IndividualLoot('platinum', 0.8, 20, 30),
            IndividualLoot('blood_ingot', 0.6, 5, 10),
            IndividualLoot('firite_ingot', 0.5, 8, 15),
        ])

        def is_suitable(self, biome: str):
            return biome in ['hell']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_magma_cube'], MagmaCubeAI, 960)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 10
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 8
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 15

    class DropItem(Entity):
        NAME = 'Drop Item'
        DISPLAY_MODE = 3

        def __init__(self, pos, item_id, item_amount):
            super().__init__(pos, game.get_game().graphics['items_' + item_id], BuildingAI, 1)
            self.amount = item_amount
            if self.img.get_width() < 64:
                self.img = pg.transform.scale(self.img, (64, 64))
                self.d_img = self.img
            self.NAME = item_id.replace('_','').title()
            self.item_id = item_id
            self.hp_sys(op='config', immune=True)

        def update(self):
            super().update()
            px, py = game.get_game().player.obj.pos
            if vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < 40:
                game.get_game().player.inventory.add_item(inventory.ITEMS[self.item_id], self.amount)
                self.hp_sys.hp = 0
            elif vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < 120:
                self.obj.apply_force(vector.Vector(vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1]), 24000))

    class Star(Entity):
        NAME = 'Star'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 0.7, 15, 55),
            IndividualLoot('magic_stone', 0.9, 12, 15),
            IndividualLoot('mana_crystal', 0.5, 1, 2)
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_star'], StarAI, 350)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -11

    class MagmaKingFireball(Entity):
        NAME = 'Magma King Fireball'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_fireball'], MagmaKingFireballAI, 5000)
            self.obj.rot = rot
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 40
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 20
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0], self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(40, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class SandStormAttack(MagmaKingFireball):

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0], self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(72, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class MagmaKing(Entity):
        NAME = 'Magma King'
        DISPLAY_MODE = 3
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('blood_ingot', 0.8, 5, 10),
            IndividualLoot('firite_ingot', 1, 30, 40),
            IndividualLoot('firy_plant', 1, 10, 20),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_magma_king'], MagmaKingAI, 7800)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 72
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 68
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 88

        def update(self):
            super().update()
            if self.obj.state == 2 and self.obj.timer % 10 == 1:
                player = game.get_game().player
                game.get_game().entities.append(Entities.MagmaKingFireball(self.obj.pos, vector.coordinate_rotation(player.obj.pos[0] - self.obj.pos[0], player.obj.pos[1] - self.obj.pos[1])))
            if self.obj.state == 1 and self.obj.timer % 40 == 20:
                player = game.get_game().player
                for k in range(-30, 31, 15):
                    fb = Entities.MagmaKingFireball(self.obj.pos, k + vector.coordinate_rotation(player.obj.pos[0] - self.obj.pos[0], player.obj.pos[1] - self.obj.pos[1]))
                    fb.obj.apply_force(vector.Vector(self.obj.velocity.get_net_rotation(), self.obj.velocity.get_net_value() // 50))
                    game.get_game().entities.append(fb)

    class SandStorm(Entity):
        NAME = 'Sandstorm'
        DISPLAY_MODE = 3
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('mysterious_ingot', 1, 15, 35),
            IndividualLoot('storm_core',  1, 2, 4),
            ])

        def __init__(self, pos, hp_sys, rot):
            super().__init__(pos, game.get_game().graphics['entity_sandstorm'], SandStormAI, hp_sys=hp_sys)
            self.obj.rot = rot
            self.tick = 0

        def update(self):
            super().update()
            self.tick += 1
            if self.tick % 6 == 1:
                px, py = game.get_game().player.obj.pos
                rot = vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1])
                self.set_rotation(rot)
                game.get_game().entities.append(Entities.SandStormAttack(self.obj.pos, self.rot))


    class RuneRock(Entity):
        NAME = 'Rune Rock'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('magic_stone', 0.3, 20, 30),
            IndividualLoot('mysterious_substance', 0.8, 10, 12),
        ])

        def is_suitable(self, biome: str):
            return biome in ['desert']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_rune_rock'], RuneRockAI, 1550)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 32

    class SwordInTheStone(Entity):
        NAME = 'Sword in the Stone'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            SelectionLoot([('magic_sword', 1, 1), ('magic_blade', 1, 1)], 1, 1)
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_sword_in_the_stone'], BuildingAI, 10000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 70

def entity_spawn(entity: type(Entities.Entity), to_player_min = 1500, to_player_max = 2500, number_factor = 0.5, target_number = 5, rate = 0.5):
    game_obj = game.get_game()
    if random.random() < max(0.0, (len([e for e in game_obj.entities if type(e) is entity]) - target_number) * number_factor / 10) - rate / 50 + 1:
        return
    player = game_obj.player
    dist = random.randint(to_player_min, to_player_max)
    r = random.random() * 2 * math.pi
    px, py = player.obj.pos[0] + dist * math.cos(r), player.obj.pos[1] + dist * math.sin(r)
    game_obj.entities.append(entity((px, py)))

def spawn_sandstorm():
    hp_sys = hp_system.HPSystem(12200)
    for i in range(4):
        e = Entities.SandStorm((0, 0), hp_sys, i * 90)
        e.IS_MENACE = i == 1
        game.get_game().entities.append(e)

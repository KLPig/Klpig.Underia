import copy

from src.physics import mover, vector
from src.underia import game, styles, inventory
from src.values import hp_system, damages, effects
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
    def __init__(self, items: list[tuple[str, int, int]], selection_min, selection_max):
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

class CloseBloodflowerAI(SlowMoverAI):
    MASS = 240
    TOUCHING_DAMAGE = 12

class BloodflowerAI(CloseBloodflowerAI):
    FRICTION = 0.97
    TOUCHING_DAMAGE = 22

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        self.timer += 1
        if self.timer > 100:
            self.timer = 0
        if vector.distance(px, py) < 800:
            if self.timer > 20:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
            if self.touched_player:
                self.timer = 0
        else:
            self.idle_timer += 1
            if self.idle_timer > random.randint(50, 200):
                self.idle_timer = 0
                self.idle_rotation = (self.idle_rotation + random.randint(-50, 50)) % 360
            self.apply_force(vector.Vector(self.idle_rotation, 100))

class SoulFlowerAI(BloodflowerAI):
    TOUCHING_DAMAGE = 68

class CellsAI(EyeAI):
    TOUCHING_DAMAGE = 89
    MASS = 720

    def on_update(self):
        self.timer = (self.timer + 1) % 240
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.touched_player:
            self.timer = -50
        if self.timer < 50:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 150))
        elif self.timer < 160:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 320))
        elif self.timer < 195:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 1500))

class MechanicEyeAI(CellsAI):
    MASS = 200
    TOUCHING_DAMAGE = 65

    def on_update(self):
        self.timer += 1
        if self.timer > 30:
            self.timer = 0
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.touched_player:
            self.timer = -20
        if self.timer < 0:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), -300))
        if vector.distance(px, py) > 1200:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
        if 0 <= self.timer < 10:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 800))

class RedWatcherAI(SlowMoverAI):
    FRICTION = 0.92
    MASS = 400
    TOUCHING_DAMAGE = 28

class RuneRockAI(SlowMoverAI):
    MASS = 240
    FRICTION = 0.9
    TOUCHING_DAMAGE = 56

class BuildingAI(MonsterAI):
    MASS = 2000
    FRICTION = 0.5
    TOUCHING_DAMAGE = 0

class AbyssEyeAI(BuildingAI):
    MASS = 6000
    FRICTION = 0.1
    TOUCHING_DAMAGE = 60

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
        self.d = 240
        self.tick = 0
        self.state = 0

    def on_update(self):
        if self.tick == 300:
            self.state = (self.state + 1) % 3
            self.tick = 0
        self.tick += 1
        if self.state == 0:
            self.rot = (self.rot + .5) % 360
            self.d = 240 + abs(self.tick % 200 - 100) * 6
        elif self.state == 1:
            self.rot = (self.rot + 6) % 360
            if self.d > 180:
                self.d -= 20
        else:
            self.rot = (self.rot + 13) % 360
            if self.d < 600:
                self.d += 20
        pos = game.get_game().player.obj.pos
        ax, ay = vector.rotation_coordinate(self.rot)
        px, py = pos[0] + ax * self.d, pos[1] + ay * self.d
        self.pos = ((self.pos[0] + px * 5) // 6, (self.pos[1] + py * 5) // 6)

class AbyssRuneAI(MonsterAI):
    FRICTION = 0.9
    MASS = 100
    TOUCHING_DAMAGE = 100

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.d = 240
        self.tick = 0
        self.state = 0
        self.ar = 6

    def on_update(self):
        self.rot = (self.rot + self.ar) % 360
        e = [e for e in game.get_game().entities if type(e) is Entities.AbyssEye]
        if not len(e):
            return
        self.pos = e[0].obj.pos
        ax, ay = vector.rotation_coordinate(self.rot)
        self.pos = (self.pos[0] + ax * self.d, self.pos[1] + ay * self.d)

class MagmaKingFireballAI(MonsterAI):
    FRICTION = 1
    MASS = 50
    TOUCHING_DAMAGE = 0
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0

    def on_update(self):
        self.apply_force(vector.Vector(self.rot, 20))

class AbyssRuneShootAI(MonsterAI):
    FRICTION = 1
    MASS = 5000
    TOUCHING_DAMAGE = 0
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0

    def on_update(self):
        self.apply_force(vector.Vector(self.rot, 2000))

class FaithlessEyeAI(MonsterAI):
    FRICTION = 0.9
    MASS = 800
    TOUCHING_DAMAGE = 100

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.tick = 0
        self.state = 0
        self.ax = -1000
        self.ay = 0
        self.phase = 1

    def on_update(self):
        if self.tick > 320:
            self.state = (self.state + 1) % 2
            self.tick = 0
        self.tick += 1
        px, py = game.get_game().player.obj.pos
        if self.state == 0:
            if self.tick % (100 - 20 * self.phase) < 30:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]), 4000 + self.phase * 2000))
        else:
            tar_x, tar_y = px + self.ax, py + self.ay
            self.apply_force(vector.Vector(vector.coordinate_rotation(tar_x - self.pos[0], tar_y - self.pos[1]), vector.distance(tar_x - self.pos[0], tar_y - self.pos[1]) * 5))
            self.rot = vector.coordinate_rotation(px - self.pos[0], py - self.pos[1])

class DestroyerAI(SlowMoverAI):
    MASS = 7200
    FRICTION = 0.9
    TOUCHING_DAMAGE = 220

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.tick > 200:
            self.state = (self.state + 1) % 2
            self.tick = 0
        self.tick += 1
        if self.state == 0:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 8000 + min(vector.distance(px, py) * 9, 22000)))
        else:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 45))

class TheCPUAI(SlowMoverAI):
    MASS = 10000
    FRICTION = 0.95
    TOUCHING_DAMAGE = 180

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.phase = 1

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.tick < 0:
            self.tick += 1
            return
        if self.tick > 100:
            self.state = (self.state + 1) % 2
            self.tick = 0
            if random.randint(0, 1):
                px *= -1
            if random.randint(0, 1):
                py *= -1
            if self.phase == 2 and random.randint(0, 1):
                t = px
                px = py
                py = t
            self.pos = (px + player.obj.pos[0], py + player.obj.pos[1])
        self.tick += 1
        if self.state == 0:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 15000))
        else:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 40))

class GreedAI(SlowMoverAI):
    MASS = 400
    FRICTION = 0.95
    TOUCHING_DAMAGE = 0
    TD = 220
    KB = 100

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.phase = 1
        self.rot = 0
        self.dp = pos

    def on_update(self):
        self.pos = self.dp
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        self.tick += 1
        if self.tick > 80:
            self.state = (self.state + 1) % 4
            if self.state == 3:
                self.rot = (self.rot + 180) % 360
            self.tick = 0
        if self.state == 0:
            self.TOUCHING_DAMAGE = self.TD
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 600))
        else:
            self.TOUCHING_DAMAGE = 0
            ax, ay = vector.rotation_coordinate(self.rot)
            px += ax * 320
            py += ay * 320
            self.pos = (self.pos[0] + px // 5, self.pos[1] + py // 5)
            self.velocity.clear()
            self.velocity.add(vector.Vector(0, self.KB))
            if self.state == 1:
                self.rot = (self.rot + 3) % 360
            elif self.state == 3:
                self.rot = (self.rot + 10) % 360
            else:
                pg.draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.pos),
                             position.displayed_position((self.pos[0] + px - 800 * ax, self.pos[1] + py - 800 * ay)), width=50)
        self.dp = self.pos

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
            self.show_bar = True
            if hp_sys is None:
                self.hp_sys = hp_system.HPSystem(hp)
            else:
                self.hp_sys = hp_system.SubHPSystem(hp_sys)
                self.show_bar = False
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
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) > game.get_game().player.SIMULATE_DISTANCE and not self.IS_MENACE:
                return
            displayer = game.get_game().displayer
            self.obj.update()
            self.hp_sys.update()
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if p[0] < -100 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 100 or p[1] < -100 or p[1] > game.get_game().displayer.SCREEN_HEIGHT + 100:
                return
            if self.DISPLAY_MODE == Entities.DisplayModes.NO_IMAGE:
                pg.draw.circle(displayer.canvas, (0, 0, 255), position.displayed_position(self.obj.pos), 10)
                if self.show_bar:
                    styles.hp_bar(self.hp_sys, position.displayed_position((self.obj.pos[0], self.obj.pos[1] - 10)), 60)
            else:
                r = self.d_img.get_rect()
                r.center = position.displayed_position(self.obj.pos)
                displayer.canvas.blit(self.d_img, r)
                if self.show_bar:
                    styles.hp_bar(self.hp_sys, position.displayed_position((self.obj.pos[0], self.obj.pos[1] - self.d_img.get_height() // 2 - 10)), self.img.get_width() * 2)
                if r.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                    f = displayer.font.render(f'{self.NAME}({int(self.hp_sys.hp)}/{self.hp_sys.max_hp})', True, (255, 255, 255), (0, 0, 0))
                    displayer.canvas.blit(f, game.get_game().displayer.reflect(*pg.mouse.get_pos()))

    class WormEntity:
        NAME = 'Entity'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False

        def __init__(self, pos, length, img_head = None, img_body = None, head_ai: type(MonsterAI) = MonsterAI, hp = 120, body_length = 60, body_touching_damage = 100):
            self.length = length
            self.body_length = body_length
            self.hp_sys = hp_system.HPSystem(hp)
            self.body = [Entities.Entity(pos, img_head, head_ai, hp_sys=self.hp_sys)] + [Entities.Entity((pos[0] + i + 1, pos[1]), img_body, MonsterAI, hp_sys=self.hp_sys) for i in range(length - 1)]
            self.obj = self.body[0].obj
            for i in range(1, self.length):
                game.get_game().entities.append(self.body[i])
                self.body[i].obj.TOUCHING_DAMAGE = body_touching_damage
                self.body[i].obj.IS_OBJECT = False
            self.d_img = self.body[0].d_img
            self.img = self.body[0].img
            self.rot = self.body[0].rot
            for b in self.body:
                b.DISPLAY_MODE = 1
                b.NAME = self.NAME

        def update(self):
            self.set_rotation(-self.body[0].obj.velocity.get_net_rotation())
            self.body[0].update()
            for i in range(1, self.length):
                ox, oy = self.body[i - 1].obj.pos
                nx, ny = self.body[i].obj.pos
                self.body[i].set_rotation(-vector.coordinate_rotation(ox - nx, oy - ny))
                ax, ay = vector.rotation_coordinate(vector.coordinate_rotation(ox - nx, oy - ny))
                tx, ty = ox - ax * self.body_length, oy - ay * self.body_length
                self.body[i].obj.pos = (tx, ty)
                # self.body[i].obj.apply_force(vector.Vector(vector.coordinate_rotation(tx - nx, ty - ny), vector.distance(tx - nx, ty - ny) * 8))

        def set_rotation(self, rot):
            self.body[0].set_rotation(rot)

        def rotate(self, rot):
            self.body[0].rotate(rot)

        def is_suitable(self, biome: str):
            return True



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

    class ClosedBloodflower(Entity):
        NAME = 'Closed Bloodflower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('copper', 0.9, 15, 25),
            IndividualLoot('cell_organization', 0.3, 2, 8),
            IndividualLoot('leaf', 0.5, 7, 12),
        ])

        def is_suitable(self, biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_closed_bloodflower'], CloseBloodflowerAI, 34)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 15
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 22
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 12

    class Bloodflower(Entity):
        NAME = 'Bloodflower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('steel', 0.9, 15, 25),
            IndividualLoot('cell_organization', 0.9, 12, 16),
            IndividualLoot('platinum', 0.3, 10, 20),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_bloodflower'], BloodflowerAI, 760)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = -18
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -32

    class RedWatcher(Entity):
        NAME = 'Red Watcher'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 0.9, 20, 40),
            IndividualLoot('magic_stone', 0.2, 5, 10),
            IndividualLoot('iron', 0.9, 15, 25),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_red_watcher'], RedWatcherAI, 800)
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 2.5
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 2.3
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 2.8

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
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 4
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 5

        def update(self):
            super().update()
            self.tick += 1
            if self.tick % (8 if self.obj.state == 0 else (5 if self.obj.state == 2 else 8000)) == 1:
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

    class AbyssRuneShoot(Entity):
        NAME = 'Abyss Rune'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_abyss_rune'], AbyssRuneShootAI, 50000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 200
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0], self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(68, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class TruthlessCurse(Entity):
        NAME = 'Truthless Curse'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_truthless_curse'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 2000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(80, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.TruthlessCurse(2, 30))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class FaithlessCurse(Entity):
        NAME = 'Faithless Curse'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_faithless_curse'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 2000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(80, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.FaithlessCurse(20, 1))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class Time(Entity):
        NAME = 'Time'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_time'], AbyssRuneShootAI, 5000000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 20000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(110, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class Lazer(Entity):
        NAME = 'Lazer'
        DISPLAY_MODE = 1

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_lazer'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 + rot)

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 2000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(188, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class AbyssRune(Entity):
        NAME = 'Abyss Rune'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 0.9, 1, 2),
        ])

        def __init__(self, pos, rot, dis, hp = 10000, ar=6):
            super().__init__(pos, game.get_game().graphics['entity_abyss_rune'], AbyssRuneAI, hp)
            self.obj.rot = rot
            self.obj.d = dis
            self.obj.ar = ar / 10

        def update(self):
            super().update()
            e = [e for e in game.get_game().entities if type(e) is Entities.AbyssEye]
            if not len(e):
                self.hp_sys.hp -= self.hp_sys.max_hp // 300


    class AbyssEye(Entity):
        NAME = 'Abyss Eye'
        DISPLAY_MODE = 3
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 1, 100, 200),
            SelectionLoot([('spiritual_stabber', 1, 1), ('spiritual_piercer', 1, 1), ('spiritual_destroyer', 1, 1)], 1, 2)
        ])

        def is_suitable(self, biome: str):
            return biome in ['heaven']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_abyss_eye'], AbyssEyeAI, 38600)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 20
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 23
            self.tick = 0
            self.state = 0
            self.rounds = 0
            for i in range(5):
                for r in range(0, 361, [60, 40, 30, 20, 15, 10][i]):
                    game.get_game().entities.append(Entities.AbyssRune((0, 0), r, i * 300 + 300, 15000 - i * i * 500, int((-1.15) ** i * 3)))
            for r in range(0, 361, 5):
                game.get_game().entities.append(Entities.AbyssRune((0, 0), r, 1800, 10000000, 12))

        def update(self):
            super().update()
            game.get_game().day_time = 0
            self.tick += 1
            if self.tick > random.randint(200, 400):
                self.tick = 0
                self.state = (self.state + 1) % 3
                if not self.state:
                    self.rounds += 1
            if self.state == 0:
                if self.tick % 10 == 1:
                    game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, self.tick * 2))
            elif self.state == 1:
                if self.tick % 10 == 1:
                    game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, random.randint(0, 360)))
            else:
                if self.tick % 10 == 1:
                    if self.rounds < 5:
                        k = [180, 120, 90, 72, 60][self.rounds]
                    else:
                        k = 45
                    for r in range(0, 360, k):
                        game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, self.tick + r))

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

    class EvilMark(Entity):
        NAME = 'Evil Mark'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 0.9, 6, 7),
            IndividualLoot('evil_ingot', 1, 10, 12),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_evil_mark'], BuildingAI, 4800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 400
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 500
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 800


    class SoulFlower(Entity):
        NAME = 'soul flower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('mana_crystal', 0.9, 15, 25),
            IndividualLoot('seatea', 0.9, 12, 16),
            IndividualLoot('evil_ingot', 0.6, 1, 3),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_soul_flower'], SoulFlowerAI, 12600)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 80
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60

    class Cells(Entity):
        NAME = 'Cells'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_flying', 0.9, 5, 12),
            IndividualLoot('evil_ingot', 0.9, 2, 5),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_cells'], CellsAI, 28500)

    class MechanicEye(Entity):
        NAME = 'Mechanic Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.9, 5, 8),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_mechanic_eye'], MechanicEyeAI, 4800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 150
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 180

        def update(self):
            super().update()
            self.set_rotation((self.rot * 4 - self.obj.velocity.get_net_rotation()) // 5)

    class FaithlessEye(Entity):
        NAME = 'Faithless Eye'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_integrity', 1, 10, 22),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_faithless_eye'], FaithlessEyeAI, 124000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 350
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 370
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 380
            self.phase = 1

        def update(self):
            if self.phase == 1 and (self.hp_sys.hp < self.hp_sys.max_hp // 2 or not \
                    bool(len([1 for e in game.get_game().entities if type(e) is Entities.TruthlessEye]))):
                self.phase = 2
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_faithless_eye_phase2']
            super().update()
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation((self.rot - self.obj.rot) // 2)
                if self.obj.tick % 50 == 1:
                    px, py = game.get_game().player.obj.pos
                    k = 1
                    if self.obj.phase == 2:
                        k = 3
                    for r in range(-k * 15, k * 15 + 1, 15):
                        game.get_game().entities.append(Entities.FaithlessCurse(self.obj.pos, vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1]) + r))

    class TruthlessEye(Entity):
        NAME = 'Truthless Eye'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_integrity', 1, 10, 22),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_truthless_eye'], FaithlessEyeAI, 138000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 350
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 370
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 380
            self.obj.ax = 900
            self.obj.ay = -400
            self.obj.state = 1
            self.phase = 1

        def update(self):
            if self.phase == 1 and (self.hp_sys.hp < self.hp_sys.max_hp // 2 or not \
                    bool(len([1 for e in game.get_game().entities if type(e) is Entities.FaithlessEye]))):
                self.phase = 2
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_faithless_eye_phase2']
            super().update()
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation((self.rot - self.obj.rot) // 2)
                if self.obj.tick % 60 == 0:
                    px, py = game.get_game().player.obj.pos
                    k = 0
                    if self.obj.phase == 2:
                        k = 5
                    for r in range(-k * 20, k * 20 + 1, 20):
                        game.get_game().entities.append(Entities.TruthlessCurse(self.obj.pos, vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1]) + r))

    class Destroyer(WormEntity):
        NAME = 'Destroyer'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_courage', 1, 10, 22),
        ])

        def __init__(self, pos):
            super().__init__(pos, 54, game.get_game().graphics['entity_destroyer_head'], game.get_game().graphics['entity_destroyer_body'], DestroyerAI, 1920000, body_length=90)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 800
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 850
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 120

        def update(self):
            super().update()
            for b in self.body:
                if random.randint(0, 1000) == 0:
                    rot = vector.coordinate_rotation(game.get_game().player.obj.pos[0] - b.obj.pos[0], game.get_game().player.obj.pos[1] - b.obj.pos[1])
                    l = Entities.Lazer(b.obj.pos, rot)
                    l.obj.apply_force(vector.Vector(rot, 3000))
                    game.get_game().entities.append(l)

    class TheCPU(Entity):
        NAME = 'The CPU'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_kindness', 1, 10, 22),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_the_cpu'], TheCPUAI, 985000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 80
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 100
            self.show_bar = False

        def update(self):
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.obj.phase == 1:
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_the_cpu_phase2']
                self.set_rotation(self.rot)
                self.obj.tick = -200
            px, py = game.get_game().player.obj.pos
            aax, aay = self.obj.pos[0] - game.get_game().player.obj.pos[0], self.obj.pos[1] - game.get_game().player.obj.pos[1]
            displayer = game.get_game().displayer
            r = self.d_img.get_rect()
            self.d_img.set_alpha(255 - int(240 * self.hp_sys.hp // self.hp_sys.max_hp))
            r.center = position.displayed_position((px - aax, py + aay))
            displayer.canvas.blit(self.d_img, r)
            r.center = position.displayed_position((px + aax, py - aay))
            displayer.canvas.blit(self.d_img, r)
            r.center = position.displayed_position((px - aax, py - aay))
            displayer.canvas.blit(self.d_img, r)
            if self.obj.phase == 2:
                r.center = position.displayed_position((px + aay, py + aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px - aay, py - aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px + aay, py - aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px - aay, py + aax))
                displayer.canvas.blit(self.d_img, r)
            self.d_img.set_alpha(255)
            super().update()

    class Greed(Entity):
        NAME = 'Greed'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('saint_steel_ingot', 1, 5, 8),
            IndividualLoot('soul_of_will', 1, 10, 22),
        ])

        def __init__(self, pos, d = False):
            super().__init__(pos, game.get_game().graphics['entity_greed'], GreedAI, 4000000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 300
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 400
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 1600
            self.d = d
            self.phase = 1
            if self.d:
                self.LOOT_TABLE = LootTable([])

        def update(self):
            super().update()
            if self.hp_sys.hp <= self.hp_sys.max_hp * (1 - self.phase * 0.2) and not self.d:
                self.phase += 1
                for i in range(4 * self.phase - 1):
                    d = Entities.Greed(self.obj.pos, True)
                    d.IS_MENACE = False
                    d.hp_sys.hp = 50000 + 20000 * self.phase
                    d.hp_sys.max_hp = d.hp_sys.hp
                    d.img = pg.transform.scale_by(d.img, 0.2 + 0.1 * self.phase)
                    d.obj.state = i
                    d.obj.TD = 60
                    d.obj.KB = 40
                    d.rot = random.randint(0, 360)
                    game.get_game().entities.append(d)
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation(-vector.coordinate_rotation(game.get_game().player.obj.pos[0] - self.obj.pos[0], game.get_game().player.obj.pos[1] - self.obj.pos[1]))

    class EyeOfTime(Entity):
        NAME = 'Eye of Time'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 2, 3), ('mithrill', 2, 3), ('titanium', 2, 3)], 1, 3),
            IndividualLoot('soul_of_patience', 1, 1, 2),
        ])

        def __init__(self, pos, d: int = False, _hp_sys = None, idx: float = 0):
            _p = pos
            _p = (game.get_game().player.obj.pos[0] + random.randint(-5000, 5000), game.get_game().player.obj.pos[1] + random.randint(-5000, 5000))
            if not d:
                hp_sys = hp_system.HPSystem(4400000)
                for i in range(9):
                    game.get_game().entities.append(Entities.EyeOfTime(pos, True, hp_sys, i + 1))
                super().__init__(_p, game.get_game().graphics['entity_eye_of_time'], BuildingAI, hp_sys=hp_sys)
            else:
                super().__init__(_p, game.get_game().graphics['entity_eye_of_time'], BuildingAI, hp_sys=_hp_sys)
                self.IS_MENACE = False
            self.img = copy.copy(self.img)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 300
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 500
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 600
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 1000
            self.tick = 20 * idx
            self.state = 0
            self.obj.IS_OBJECT = True
            self.obj.TOUCHING_DAMAGE = 100
            self.me = 1
            self.phase = 1
            self.d = d

        def update(self):
            self.tick += 1
            if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * 0.5:
                self.phase = 2
                self.me = 2
                if not self.d:
                    for f in range(20):
                        et = Entities.EyeOfTime(self.obj.pos, 114, self.hp_sys, 1)
                        et.tick = (self.tick + 20 * f + 10) % 100
                        game.get_game().entities.append(et)
            if self.tick > 200 // self.me:
                self.state = (self.state + 1) % 1
                self.tick = 0
                self.obj.pos = (game.get_game().player.obj.pos[0] + random.randint(-500, 500),
                                game.get_game().player.obj.pos[1] + random.randint(-500, 500))
                self.obj.velocity.clear()
                self.obj.velocity.add(vector.Vector(random.randint(0, 360), 5))
                self.set_rotation(random.randint(-50, 50))
            if self.tick < 20:
                self.img.set_alpha(self.tick * 12 + 15)
            elif self.tick > 200 // self.me - 20:
                self.img.set_alpha(255 - (self.tick - 200 // self.me + 20) * 12)
            if self.tick % 20 == 0 and 20 <= self.tick <= 20 + 20 * self.me:
                t = Entities.Time(self.obj.pos,
                                  vector.coordinate_rotation(game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                             game.get_game().player.obj.pos[1] - self.obj.pos[1]))
                t.obj.apply_force(vector.Vector(vector.coordinate_rotation(game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                                           game.get_game().player.obj.pos[1] - self.obj.pos[1]), 1000))
                game.get_game().entities.append(t)
            self.set_rotation(self.rot)
            super().update()


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
    hp_sys = hp_system.HPSystem(15200)
    for i in range(2):
        e = Entities.SandStorm((0, 0), hp_sys, i * 180)
        e.IS_MENACE = i == 1
        game.get_game().entities.append(e)

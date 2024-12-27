import os
import pickle

import pygame as pg

from src import resources, visual, physics, saves_chooser, underia

pg.init()

_, file = saves_chooser.choose_save()
try:
    if os.path.exists(resources.get_save_path(file)):
        game = pickle.load(open(resources.get_save_path(file), "rb"))
        game.chunk_pos = (0, 0)
        game.player.obj = underia.PlayerObject((0, 0))
        game.displayer = visual.Displayer()
        game.graphics = resources.Graphics()
        game.clock = resources.Clock()
        game.pressed_keys = []
        game.pressed_mouse = []
        game.drop_items = []
        game.last_biome = ('forest', 0)
        game.player.hp_sys.dmg_t = 0
        game.player.scale = 1.0
        try:
            game.player.talent
        except AttributeError:
            game.player.talent = 0
            game.player.max_talent = 0
        try:
            game.player.profile
        except AttributeError:
            game.player.profile = underia.PlayerProfile()
        try:
            game.player.profile.stage
        except AttributeError:
            game.player.profile.stage = 0
        if not game.player.profile.stage:
            game.player.profile.add_point(0)
    else:
        game = underia.Game()
except Exception as e:
    raise e

pg.display.set_caption('Underia')
game.save = file
underia.write_game(game)

game.setup()
game.map = pg.PixelArray(game.graphics['background_map'])
underia.set_weapons()
game.player.weapons = 4 * [underia.WEAPONS['null']]
game.player.sel_weapon = 0
game.player.inventory.sort()
game.player.inventory.items['recipe_book'] = 1
game.player.hp_sys(op='config', immune_time=10, true_drop_speed_max_value=1)
game.player.hp_sys.shields = []

@game.update_function
def update():
    bm = 'blood moon' in game.world_events
    for entity in game.entities:
        if entity.IS_MENACE:
            continue
        d = physics.distance(entity.obj.pos[0] - game.player.obj.pos[0], entity.obj.pos[1] - game.player.obj.pos[1])
        if d > 8000 or (d > 1200 and not entity.is_suitable(game.get_biome())):
            game.entities.remove(entity)
    for entity in game.drop_items:
        d = physics.distance(entity.obj.pos[0] - game.player.obj.pos[0], entity.obj.pos[1] - game.player.obj.pos[1])
        if d > 2000:
            game.drop_items.remove(entity)
    if game.get_biome() == 'forest':
        underia.entity_spawn(underia.Entities.Tree, target_number=40, to_player_max=5000, to_player_min=800, rate=5)
        underia.entity_spawn(underia.Entities.TreeMonster, target_number=10, to_player_max=5000, to_player_min=800,
                             rate=5)
        underia.entity_spawn(underia.Entities.ClosedBloodflower, target_number=22, to_player_max=5000,
                             to_player_min=800, rate=1)
        if game.stage > 0:
            underia.entity_spawn(underia.Entities.SoulFlower, target_number=42 + bm * 36, to_player_max=5000, to_player_min=800,
                                 rate=1)
    elif game.get_biome() == 'rainforest':
        underia.entity_spawn(underia.Entities.Tree, target_number=10, to_player_max=5000, to_player_min=1000, rate=5)
        underia.entity_spawn(underia.Entities.HugeTree, target_number=40, to_player_max=5000, to_player_min=1000,
                             rate=1)
        underia.entity_spawn(underia.Entities.TreeMonster, target_number=10, to_player_max=5000, to_player_min=1000,
                             rate=5)
        underia.entity_spawn(underia.Entities.ClosedBloodflower, target_number=35, to_player_max=5000,
                             to_player_min=800, rate=1)
        if game.stage > 0:
            underia.entity_spawn(underia.Entities.SoulFlower, target_number=45 + bm * 40, to_player_max=5000, to_player_min=800,
                                 rate=1)
            underia.entity_spawn(underia.Entities.Leaf, target_number=50, to_player_max=5000, to_player_min=1000,
                                 rate=2)
    elif game.get_biome() == 'desert':
        underia.entity_spawn(underia.Entities.Cactus, target_number=15, to_player_max=5000, to_player_min=1000, rate=5)
        if game.player.hp_sys.max_hp >= 500:
            underia.entity_spawn(underia.Entities.RuneRock, target_number=12, to_player_max=2000, to_player_min=1000,
                                 rate=0.8)
    elif game.get_biome() == 'hell':
        underia.entity_spawn(underia.Entities.MagmaCube, target_number=12, to_player_max=2000, to_player_min=1000,
                             rate=0.8)
    elif game.get_biome() == 'heaven':
        if game.stage > 0:
            underia.entity_spawn(underia.Entities.Cells, target_number=6, to_player_max=2000, to_player_min=1500,
                                 rate=0.8)
    elif game.get_biome() == 'snowland':
        underia.entity_spawn(underia.Entities.ConiferousTree, target_number=15, to_player_max=5000, to_player_min=1000, rate=5)
        if game.stage > 0:
            underia.entity_spawn(underia.Entities.SnowDrake, target_number=12, to_player_max=5000, to_player_min=1000,
                                 rate=.9)
            underia.entity_spawn(underia.Entities.IceCap, target_number=15, to_player_max=5000, to_player_min=1000,
                                 rate=.2)
    underia.entity_spawn(underia.Entities.SwordInTheStone, target_number=1, to_player_max=5000, to_player_min=4000,
                         rate=50, number_factor=2)
    if game.stage > 0:
        underia.entity_spawn(underia.Entities.EvilMark, target_number=3, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=1.9)
    if game.day_time > 0.75 or game.day_time < 0.2:
        underia.entity_spawn(underia.Entities.Eye, target_number=4 + bm * 12, to_player_max=2000, to_player_min=1500,
                             rate=0.4 + bm * 0.8)
        underia.entity_spawn(underia.Entities.Bloodflower, target_number=5 + bm * 24, to_player_max=2000, to_player_min=1500,
                             rate=0.5 + bm * 1.2)
        underia.entity_spawn(underia.Entities.RedWatcher, target_number=2 + bm * 17, to_player_max=2000, to_player_min=1800,
                             rate=0.2 + bm * 0.7)
        if game.stage > 0:
            underia.entity_spawn(underia.Entities.MechanicEye, target_number=1 + bm * 8, to_player_max=2000, to_player_min=1500,
                                 rate=0.2 + bm * 0.9)

            underia.entity_spawn(underia.Entities.Destroyer, target_number=1, to_player_max=6000, to_player_min=5000,
                                 rate=0.001 + bm * 0.06, number_factor=1.5)
            underia.entity_spawn(underia.Entities.TheCPU, target_number=1, to_player_max=6000, to_player_min=5000,
                                 rate=0.001 + bm * 0.06, number_factor=1.5)
            underia.entity_spawn(underia.Entities.TruthlessEye, target_number=1, to_player_max=6000, to_player_min=5000,
                                 rate=0.0005 + bm * 0.03, number_factor=1.5)
            underia.entity_spawn(underia.Entities.FaithlessEye, target_number=1, to_player_max=6000, to_player_min=5000,
                                 rate=0.0005 + bm * 0.03, number_factor=1.5)

        else:
            underia.entity_spawn(underia.Entities.TrueEye, target_number=1, to_player_max=6000, to_player_min=5000,
                                 rate=0.1 + bm * 0.2, number_factor=1.5)

    underia.entity_spawn(underia.Entities.Star, target_number=12 + bm * 10, to_player_max=2000, to_player_min=1500, rate=0.7)


try:
    game.run()



except Exception as err:
    def try_delete_attribute(obj, attr):
        delattr(obj, attr)


    try_delete_attribute(game, "displayer")
    try_delete_attribute(game, "graphics")
    try_delete_attribute(game, "clock")
    try_delete_attribute(game, "on_update")
    try_delete_attribute(game, "drop_items")
    try_delete_attribute(game, "map")
    try_delete_attribute(game, "musics")
    try_delete_attribute(game, "channel")
    try_delete_attribute(game, 'sounds')
    game.events = []
    game.projectiles = []
    game.entities = []
    for w in game.player.weapons:
        game.player.inventory.add_item(underia.ITEMS[w.name.replace(" ", "_")])
    game.player.weapons = []
    with open(resources.get_save_path(game.save), 'wb') as w:
        w.write(pickle.dumps(game))
    pg.quit()
    if type(err) is not resources.Interrupt:
        raise resources.UnderiaError(f"An error occurred while running the game:\n{err}") from err

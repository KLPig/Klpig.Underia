from src import underia, saves_chooser, resources, visual
import pygame as pg
import pickle
import os

from src.physics import distance

pg.init()

_, file = saves_chooser.choose_save()
if os.path.exists(resources.get_path(file)):
    game = pickle.load(open(resources.get_path(file), "rb"))
    game.displayer = visual.Displayer()
    game.graphics = resources.Graphics()
    game.clock = resources.Clock()
    game.pressed_keys = []
    game.pressed_mouse = []
    game.drop_items = []
    game.last_biome = ('forest', 0)
else:
    game = underia.Game()
game.player.inventory.add_item(underia.ITEMS['nights_edge'])
game.save = file
underia.write_game(game)


game.setup()
game.map = pg.PixelArray(game.graphics['background_map'])
underia.set_weapons()
game.player.weapons = 4 * [underia.WEAPONS['null']]
#for i in underia.WEAPONS.keys():
    #game.player.inventory.add_item(underia.ITEMS[i])
game.player.sel_weapon = 0


@game.update_function
def update():
    for entity in game.entities:
        d = distance(entity.obj.pos[0] - game.player.obj.pos[0], entity.obj.pos[1] - game.player.obj.pos[1])
        if d > 8000 or (d > 1200 and not entity.is_suitable(game.get_biome())):
            game.entities.remove(entity)
    #underia.entity_spawn(underia.Entities.Eye)
    if game.get_biome() == 'forest':
        underia.entity_spawn(underia.Entities.Tree, target_number=40, to_player_max=5000, to_player_min=800, rate=50)
        underia.entity_spawn(underia.Entities.TreeMonster, target_number=16, to_player_max=5000, to_player_min=800, rate=50)
    elif game.get_biome() == 'rainforest':
        underia.entity_spawn(underia.Entities.Tree, target_number=20, to_player_max=5000, to_player_min=1000, rate=50)
        underia.entity_spawn(underia.Entities.TreeMonster, target_number=28, to_player_max=5000, to_player_min=1000, rate=50)
    elif game.get_biome() == 'desert':
        underia.entity_spawn(underia.Entities.Cactus, target_number=15, to_player_max=5000, to_player_min=1000, rate=50)
    elif game.get_biome() == 'hell':
        underia.entity_spawn(underia.Entities.MagmaCube, target_number=12, to_player_max=2000, to_player_min=1000, rate=0.8)
    underia.entity_spawn(underia.Entities.SwordInTheStone, target_number=1, to_player_max=5000, to_player_min=4000, rate=50, number_factor=2)
    if game.day_time > 0.75 or game.day_time < 0.2:
        underia.entity_spawn(underia.Entities.Eye, target_number=10, to_player_max=2000, to_player_min=1500, rate=0.5)
    underia.entity_spawn(underia.Entities.Star, target_number=5, to_player_max=2000, to_player_min=1500, rate=0.3)
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
    game.events = []
    game.projectiles = []
    game.entities = []
    for w in game.player.weapons:
        game.player.inventory.add_item(underia.ITEMS[w.name.replace(" ", "_")])
    game.player.weapons = []
    open(file, "wb").write(pickle.dumps(game))
    pg.quit()
    raise err
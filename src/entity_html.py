import pygame as pg

from src import underia, values

pg.init()
pg.display.set_mode((800, 600))

recipes = underia.RECIPES
game = underia.Game()
underia.write_game(game)
game.setup()

f = "<!DOCTYPE html><html><head>\n<title>Underia Entities</title>\n" \
    "<link rel='stylesheet' type='text/css' href='styles.css'>\n" \
    "<meta charset='UTF-8'></head><body>"

f += "<h1>Underia Entities</h1>"

f += "<table>"
img_str = ("<td><div class='item %s drop' id='%s-%s' onclick='location.href=\"./items.html#%s-main\"'"
           "> <img src='assets/graphics/items/%s.png'/> <p class='amount'>%s</p> </div></td>")

entity_str = "<div class='entity' id='%s'><img src='assets/graphics/entity/%s.png'/> <p class='amount'>%s</p></div>"

ets = [
    'Tree', 'TreeMonster', 'HugeTree', 'ClosedBloodflower', 'Eye', 'Bloodflower', 'RedWatcher', 'Star',
    'SwordInTheStone',
    'Cactus', 'TrueEye', 'MagmaCube', 'MagmaKing', 'RuneRock', 'SandStorm', 'AbyssEye', 'EvilMark', 'SoulFlower',
    'MechanicEye', 'Cells', 'FaithlessEye', 'TruthlessEye', 'Destroyer', 'TheCPU', 'Greed', 'EyeOfTime', 'DevilPython',
    'Leaf'
]

# ets = dir(underia.Entities)

print(ets)

for entity in ets:
    try:
        e: underia.Entities.Entity = getattr(underia.Entities, entity)((0, 0))
    except TypeError:
        continue
    try:
        f += "<tr><td>%s</td>\n" % (entity_str % (entity, e.NAME.lower().replace(' ', '_'),
                                                  e.NAME + '<br>' + str(e.hp_sys.max_hp) + ' HP<br>' +
                                                  (f'{e.obj.TOUCHING_DAMAGE} AT ' if e.obj.TOUCHING_DAMAGE else ' ') +
                                                  f'{int(e.hp_sys.defenses[values.DamageTypes.PHYSICAL] +
                                                         e.hp_sys.defenses[values.DamageTypes.PIERCING] +
                                                         e.hp_sys.defenses[values.DamageTypes.MAGICAL]) // 3} DF<br>' +
                                                  'AI: ' + type(e.obj).__name__))
        for item in e.LOOT_TABLE.get_all_items():
            t = underia.text(underia.ITEMS[item].name)
            f += img_str % ('regular', item, 'regular', item, item, f'{underia.ITEMS[item].name} {t}')
        f += "</tr>\n"
    except AttributeError:
        pass
f += "</table></body></html>"

with open("../docs/entities.html", "w") as ff:
    ff.write(f)
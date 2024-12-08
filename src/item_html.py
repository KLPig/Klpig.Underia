from src import underia
import pygame as pg

pg.init()
pg.display.set_mode((800, 600))

recipes = underia.RECIPES
game = underia.Game()
underia.write_game(game)
game.setup()

f = "<!DOCTYPE html><html><head>\n<title>Underia Items</title>\n"\
     "<link rel='stylesheet' type='text/css' href='styles.css'>\n"\
    "<meta charset='UTF-8'></head><body>"

f += "<h1>Underia Recipes</h1>"

f += "<table>"
img_str = "<div class='item %s' id='%s-%s'> <img src='../src/assets/graphics/items/%s.png'/></div>"
item_str = "<h2 style='color: rgb%s'>%s</h2><p class='desc' style='color: rgb%s'>%s</p>"


for _, item in underia.ITEMS.items():
    f += f"<tr onclick='location.href=\"./recipes.html#{item.id}-main\"'>\n"
    f += "<td>" + img_str % ('main', item.id, 'main', item.id) + "</td>\n"
    c = underia.Inventory.Rarity_Colors[item.rarity]
    c = (c[0] // 2, c[1] // 2, c[2] // 2)
    t = underia.text(item.name)
    if t is None:
        t = ''
    f += "<td>" + item_str % (c, f'(#{item.inner_id}){item.name} {t}', c, item.get_full_desc().replace('\n', '<br/>')) + "</td>\n"

f += "</table></body></html>"

with open("../doc/items.html", "w") as ff:
    ff.write(f)


from src import underia
import pygame as pg

pg.init()
pg.display.set_mode((800, 600))

recipes = underia.RECIPES
game = underia.Game()
underia.write_game(game)
game.setup()

f = "<!DOCTYPE html><html><head>\n<title>Underia Recipes</title>\n"\
     "<link rel='stylesheet' type='text/css' href='styles.css'>\n"\
     "<meta charset='UTF-8'></head><body>"

f += "<h1>Underia Recipes</h1>"

f += "<table>"
img_str = ("<div class='item %s' id='%s-%s' onclick='location.href=\"./items.html#%s-main\"'"
           "> <img src='../src/assets/graphics/items/%s.png'/> <p class='amount'>%s</p> </div>")


for recipe in recipes:
    t = underia.text(underia.ITEMS[recipe.result].name)
    f += "<tr><td>%s</td>\n" % (img_str % ('main', recipe.result, 'main', recipe.result, recipe.result,
                                           f'{underia.ITEMS[recipe.result].name} {t}*{recipe.crafted_amount}'))
    j = 0
    for item, amount in recipe.material.items():
        t = underia.text(underia.ITEMS[item].name)
        f += "<td>%s</td>\n" % (img_str % ('regular', item, 'regular', item, item,
                                           f'{underia.ITEMS[item].name} {t}*{amount}'))
        j += 1
    f += "</tr>\n"
f += "</table></body></html>"

with open("../doc/recipes.html", "w") as ff:
    ff.write(f)


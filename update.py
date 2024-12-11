import os

os.chdir("src/assets/graphics/items")
import src.assets.graphics.items.convert_weapon as convert_weapon
os.chdir("../../..")
import src.item_html as item_html
import src.recipe_html as recipe_html
import src.entity_html as entity_html

print(f"Done. Modules {convert_weapon, item_html, recipe_html, entity_html} updated.")

print('Copying assets to docs/assets')
path = os.path.dirname(__file__)
os.system(f'cp -r {os.path.join(path, 'src/assets')} {os.path.join(path, './ docs / assets')}')
print('Done.')

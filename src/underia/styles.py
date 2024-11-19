import pygame as pg
from src.values import hp_system
from src.underia import game, inventory
import copy


def hp_bar(hp: hp_system.HPSystem, midtop: tuple, size: float):
    displayer = game.get_game().displayer
    width = int(size * 0.8)
    height = int(size * 0.1)
    rect = pg.Rect(midtop[0] - width // 2, midtop[1] - height - size // 3, width, height)
    hp_rate = hp.hp / hp.max_hp
    hp_dis_rate = hp.displayed_hp / hp.max_hp
    hp_rate = max(0.0, min(1.0, hp_rate))
    if hp_dis_rate >= 1.0:
        return
    hp_dis_rate = max(0.0, min(1.0, hp_dis_rate))
    color = (255 - hp_rate * 255, hp_rate * 255, 0)
    color_dis = (255 - hp_dis_rate * 255, hp_dis_rate * 255, 0)
    pg.draw.rect(displayer.canvas, color_dis, (rect.left, rect.top, int(width * hp_dis_rate), height))
    pg.draw.rect(displayer.canvas, color, (rect.left, rect.top, int(width * hp_rate), height))
    pg.draw.rect(displayer.canvas, (0, 0, 0), rect, 2)

def text(txt: str) -> str:
    return txt

def item_mouse(x, y, name, no, amount, scale, anchor='left'):
    if name == 'null':
        return
    window = game.get_game().displayer.canvas
    r = (x, y, 80 * scale, 80 * scale)
    if pg.Rect(r).collidepoint(pg.mouse.get_pos()):
        desc_split = inventory.ITEMS[name].get_full_desc().split('\n')
        l = len(desc_split) + 1
        t = game.get_game().displayer.font.render(text(f"(#{inventory.ITEMS[name].inner_id})" + f"{inventory.ITEMS[name].name}{'(' + amount + ')' if amount not in ['1', ''] else ''}"), True,
                               inventory.Inventory.Rarity_Colors[inventory.ITEMS[name].rarity], (0, 0, 0))
        if pg.mouse.get_pos()[1] > 36 * l:
            p_y = 0
        else:
            p_y = 36 * l - pg.mouse.get_pos()[1] + 36
        if anchor == 'left':
            tr = t.get_rect(bottomleft=(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - 36 * l + p_y))
        else:
            tr = t.get_rect(bottomright=(pg.mouse.get_pos()[0] - 80 * scale, pg.mouse.get_pos()[1] - 36 * l + p_y))
        window.blit(t, tr)

        for j in range(l - 1):
            t = game.get_game().displayer.font.render(text(desc_split[j]), True,
                                   (255, 255, 255), (0, 0, 0))
            if anchor == 'left':
                tr = t.get_rect(bottomleft=(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - 36 * (l - j - 1) + p_y))
            else:
                tr = t.get_rect(bottomright=(
                pg.mouse.get_pos()[0] - 80 * scale, pg.mouse.get_pos()[1] - 36 * (l - j - 1) + p_y))
            window.blit(t, tr)

def item_display(x, y, name, no, amount, scale, selected=False):
    window = game.get_game().displayer.canvas
    r = (x, y, 80 * scale, 80 * scale)
    if pg.Rect(r).collidepoint(pg.mouse.get_pos()):
        pg.draw.rect(window, (160, 160, 160), r)
    else:
        pg.draw.rect(window, (127, 127, 127), r)
    pg.draw.rect(window, (0, 0, 0), r, 3)
    im = game.get_game().graphics['items_' + name]
    im = copy.copy(pg.transform.scale(im, (64 * scale, 64 * scale)))
    imr = im.get_rect(center=(x + 40 * scale, y + 40 * scale))
    window.blit(im, imr)
    if amount not in ['1', '']:
        t = game.get_game().displayer.font_s.render(amount, True, (0, 0, 0))
        tr = t.get_rect(topleft=(x + 10, y + 5))
        window.blit(t, tr)
    t = game.get_game().displayer.font_s.render(no.split('/')[0], True, (0, 0, 0))
    tr = t.get_rect(topright=(x + 80 * scale - 10, y + 5))
    window.blit(t, tr)
    if selected:
        pg.draw.rect(window, (255, 255, 0), (x, y, 80 * scale, 80 * scale), 6)
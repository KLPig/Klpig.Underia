import copy
import math
import os
import pygame as pg
from src.resources import path

n = 0

selects = []

for i in range(1, 10):
    if os.path.exists(path.get_save_path(f".save{i}.pkl")):
        selects.append(f"Save {i}")
    else:
        selects.append(f"Save {i} (empty)")

anchor = 0
cmds = []
cb = 0
bios = [pg.image.load(path.get_path(f'assets/graphics/background/{b}.png')) for b in ['forest', 'rainforest', 'snowland', 'heaven',
                                                                                      'inner', 'hell', 'desert']]
bios = [pg.transform.scale(b, (100, 100)) for b in bios]

def choose_save():
    global n, selects, anchor, cmds, cb
    pg.init()
    clk = pg.time.Clock()
    pg.display.set_caption("Underia")
    screen = pg.display.set_mode((1600, 900), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF | pg.FULLSCREEN | pg.SCALED)
    font = pg.font.SysFont('dtm-mono', 48)
    tick = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return cmds, None
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    return cmds, None
                elif event.key == pg.K_UP:
                    n = (n - 1) % len(selects)
                    anchor = n
                elif event.key == pg.K_DOWN:
                    n = (n + 1) % len(selects)
                    anchor = n
                elif event.key == pg.K_RETURN:
                    return cmds, f".save{n + 1}.pkl"
                elif event.key == pg.K_BACKSPACE:
                    if os.path.exists(path.get_save_path(f".save{n + 1}.pkl")):
                        os.remove(path.get_save_path(f".save{n + 1}.pkl"))
                        selects[n] = f"Save {n + 1} (empty)"
        screen.fill((0, 0, 0))
        cs = bios[cb]
        ncx = bios[(cb + 1) % 7]
        if tick > 300:
            ncx = copy.copy(ncx)
            ncx.set_alpha((tick - 300) * 255 // 200)
        for x in range(-100, screen.get_width() + 100, 100):
            for y in range(-100, screen.get_height() + 100, 100):
                screen.blit(cs, (x + tick % 100, y))
                if tick > 300:
                    screen.blit(ncx, (x + tick % 100, y))
        if tick >= 500:
            tick = 0
            cb = (cb + 1) % 7
        tick += 1
        ot = pg.transform.rotate(font.render(f"Underia", True, (255, 255, 255), (0, 0, 0)),
                                  math.cos(tick / 250 * math.pi) * 24)
        otr = ot.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(ot, otr)
        sn = selects[n]
        st = font.render(sn, True, (255, 255, 0), (0, 0, 0))
        str = st.get_rect(center=(screen.get_width() // 2, 500))
        screen.blit(st, str)
        pg.display.flip()
        clk.tick(60)

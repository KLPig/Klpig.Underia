import os

import pygame as pg

from src.resources import path

n = 1

selects = []

for i in range(1, 10):
    if os.path.exists(path.get_save_path(f".save{i}.pkl")):
        selects.append(f"Save {i}")
    else:
        selects.append(f"Save {i} (empty)")

anchor = 0
cmds = []


def choose_save():
    global n, selects, anchor, cmds
    pg.init()
    pg.display.set_caption("Save Chooser")
    screen = pg.display.set_mode((1600, 900), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF | pg.FULLSCREEN | pg.SCALED)
    font = pg.font.Font(None, 30)
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
                        os.remove(path.get_save_path(f".save{n}.pkl"))
                        selects[n] = f"Save {n + 1} (empty)"
        screen.fill((0, 0, 0))
        for i, select in enumerate(selects):
            if i == n:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)
            text = font.render(select, True, (0, 0, 0))
            rect = pg.Rect(100, 50 + i * 50 - anchor * 50, 200, 50)
            text_rect = text.get_rect(center=rect.center)
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, (0, 0, 0), rect, 2)
            screen.blit(text, text_rect)
        pg.display.flip()

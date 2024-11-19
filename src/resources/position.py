from src.underia import game

def absolute_position(pos):
    ax, ay = game.get_game().get_anchor()
    return pos[0] + ax, pos[1] + ay


def relative_position(pos):
    ax, ay = game.get_game().get_anchor()
    return pos[0] - ax, pos[1] - ay

def displayed_position(pos):
    ax, ay = game.get_game().get_anchor()
    dis = game.get_game().displayer
    return pos[0] - ax + dis.SCREEN_WIDTH // 2, pos[1] - ay + dis.SCREEN_HEIGHT // 2

def real_position(pos):
    ax, ay = game.get_game().get_anchor()
    dis = game.get_game().displayer
    return pos[0] + ax - dis.SCREEN_WIDTH // 2, pos[1] + ay - dis.SCREEN_HEIGHT // 2


import numpy as np
import pygame as pg
import sys, random
from collections import defaultdict



CELL = 48 # Cell width TODO: Makes dependent on map_size but still global...
WHITE, GREY, BLACK = (240, 240, 240),  (200, 200, 200), (20, 20, 20)
YELLOW, RED, GREEN = (200, 200, 0), (200, 0, 0), (0, 200, 0)
COLORS = [BLACK, YELLOW, GREEN]  # empty, wall, goal
a = lambda x, y: np.array((y, x))
t = lambda x: tuple(x)
DIRS = [a(1, 0), a(0, -1), a(-1, 0), a(0, 1), # Right, Up, Left, Down
        a(1, -1), a(-1, -1), a(-1, 1), a(1, 1)] #Right-up, Left-up, Left-down, Right-down 

flip_tup = lambda arr: (arr[0], arr[1])

random.seed(0)
W, H, pct = 10, 5, 0.4

pg.display.set_caption('A*')
screen = pg.display.set_mode([W * CELL, H * CELL])

def solve():
    shortest_path = AStar()
    if shortest_path:
        draw_path(shortest_path)

def get_neighbors(n):
    # @params: tuple of node (y, x)
    # @returns: list of neighboring tuples
    n = np.array(n)
    # x, y = tuple(neighbor)
    # grid[x, y]

    neighbors = [n + d for d in DIRS]
    filtered = list(filter(lambda neighbor: neighbor[1] >= 0 \
                        and neighbor[0] >= 0 and neighbor[1] < W and neighbor[0] < H and grid[neighbor[0], neighbor[1]] == 0, neighbors))

    return filtered
    

def AStar():
    # https://en.wikipedia.org/wiki/A*_search_algorithm
    # h = lambda n: np.abs(goal - n).sum()
    h = lambda n: np.abs(goal - n).max()
    

    # open_set = {t(source) : h(source)}  # from set to dic that maps to f_score
    open_set = {t(source)}
    came_from = {}

    g_score = defaultdict(lambda: sys.maxsize)
    g_score[t(source)] = 0

    f_score = defaultdict(lambda: sys.maxsize)  # g_score[n] + h(n)
    f_score[t(source)] = h(source)

    while len(open_set) != 0:
        current = min(open_set, key=f_score.get)  # minimal f_score of elements in open_set
        # current = min(open_set, key=open_set.get)
        # current = min(f_score.items(), key=lambda x: x[1])
        if current == t(goal):
            return reconstruct_path(came_from, current)

        open_set.discard(current)
        for neighbor in get_neighbors(current):
            # d(current,neighbor) = 1, is the weight of the edge from current to neighbor
            # tentative_gScore is the distance from start to the neighbor through current
            tentative_gscore = g_score[current] + 1  # gScore[current] + d(current, neighbor)
            if tentative_gscore < g_score[t(neighbor)]:
            # This path to neighbor is better than any previous one. Record it!
                came_from[t(neighbor)] = current
                g_score[t(neighbor)] = tentative_gscore
                f_score[t(neighbor)] = tentative_gscore + h(neighbor)
                if not t(neighbor) in open_set:
                    open_set.add(t(neighbor))

    # Open set is empty, but never reached goal 
    return None

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from.keys():
        current = came_from[t(current)]
        total_path.append(t(current))
    return total_path



def reset():
    grid = np.empty((H, W), dtype=int)
    for x in range(W):
        for y in range(H):
            grid[y, x] = int(random.random() < pct)

    source = random.randint(0, H-1), random.randint(0, W-1)
    goal = random.randint(0, H-1), random.randint(0, W-1)
    source = np.array(source)
    goal = np.array(goal)

    grid[tuple(source)] = 0
    grid[tuple(goal)] = 0

    return grid, source, goal

def render():
    draw_rect = lambda x, y, c: pg.draw.rect(screen, c, pg.Rect(x*CELL, y*CELL, CELL, CELL), 0)
    screen.fill(BLACK)
    walls = np.nonzero(grid)

    for y, x in zip(*walls):
        draw_rect(x, y, YELLOW)

    y, x = source
    draw_rect(x, y, RED)
    y, x = goal
    draw_rect(x, y, GREEN)

    
    pg.display.flip()

def draw_path(path):
    draw_rect = lambda x, y, c: pg.draw.rect(screen, c, pg.Rect(x*CELL, y*CELL, CELL, CELL), 0)
    for y, x in path:
        draw_rect(x, y, RED)
    pg.display.flip()


def process_input():
    event = pg.event.wait()
    if event.type == pg.QUIT:
        pg.display.quit()
        pg.quit()
        sys.exit()

    elif event.type == pg.KEYDOWN:
        if event.key == pg.K_ESCAPE:
            pg.display.quit()
            pg.quit()
            sys.exit()

        if event.key == pg.K_r:
            global grid, source, goal
            grid, source, goal = reset()
            render()
        if event.key == pg.K_SPACE:
            space()
            



grid, source, goal = reset()
render()
# AStar()
space = lambda: solve()



while True:
    process_input()




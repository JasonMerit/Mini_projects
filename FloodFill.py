from treelib import Tree
import random
import pygame as pg
# random.seed(0)

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
SIZE = 10

# Visualize the maze
pg.init()
SCREEN_SIZE = 500
CELL = SCREEN_SIZE // SIZE
BLACK, GREEN, TEAL = (20, 20, 20), (20, 120, 20), (20, 70, 20)

# Screens
screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

fill_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
fill_screen.fill(BLACK)

maze_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
maze_screen.set_colorkey((0, 0, 0))


player_screen = pg.Surface((CELL, CELL))
pg.draw.circle(player_screen, GREEN, (CELL//2, CELL//2), CELL//4)
player_screen.set_colorkey((0, 0, 0))

pg.display.set_caption("Flood Fill")
clock = pg.time.Clock()

class Maze:
    

    def __init__(self):
        self.grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        self.tree = Tree()

        self.create_maze()

    def create_maze(self):
        for i in range(SIZE+1): # First draw all walls then remove walls between nodes in Maze
            pg.draw.line(maze_screen, GREEN, (0, i * CELL), (SCREEN_SIZE, i * CELL), 2)
            pg.draw.line(maze_screen, GREEN, (i * CELL, 0), (i * CELL, SCREEN_SIZE), 2)
        self.tree.create_node("0,0", "0,0")
        self.expand(0, 0)
        self.draw_maze(self.tree.get_node("0,0"))


    def expand(self, x, y):
        self.grid[y][x] = 1
        random.shuffle(DIRECTIONS)
        for dir in DIRECTIONS:
            nx = x + dir[0]
            ny = y + dir[1]
            if nx < 0 or nx >= len(self.grid[0]) or ny < 0 or ny >= SIZE:  # out of bounds
                continue
            if self.grid[ny][nx] == 1:  # already expanded
                continue
            
            # Create edge between (x, y) and (nx, ny)
            self.tree.create_node(f"{nx},{ny}", f"{nx},{ny}", parent=f"{x},{y}")

            self.expand(nx, ny)

    def draw_maze(self, node):
        if node.is_leaf():
            return
        for child in self.tree.children(node.tag):
            # draw line between node and child
            x1, y1 = int(node.tag[0]), int(node.tag[2])
            x2, y2 = int(child.tag[0]), int(child.tag[2])

            if x1 == x2: # horizontal wall
                y = max(y1, y2)
                pg.draw.line(maze_screen, (0, 0, 0), (x1 * CELL, y * CELL), (x1 * CELL + CELL, y * CELL), 2)
            else: # vertical wall
                x = max(x1, x2)
                pg.draw.line(maze_screen, (0, 0, 0), (x * CELL, y1 * CELL), (x * CELL, y1 * CELL + CELL), 2)
            self.draw_maze(child)
    
    # for player traversal
    def connected(self, a, b):
        node1 = self.tree.get_node(a)
        node2 = self.tree.get_node(b)
        if self.tree.parent(node1.tag) == node2 or self.tree.parent(node2.tag) == node1:
            return True

# Flood fill
def flood_fill_rec(x, y):
    if (x, y) in inside:
        return
    step(x, y)
    if x < SIZE-1 and maze.connected(f"{x},{y}", f"{x+1},{y}"):
        flood_fill_rec(x+1, y)
    if x > 0 and maze.connected(f"{x},{y}", f"{x-1},{y}"):
        flood_fill_rec(x-1, y)
    if y < SIZE-1 and maze.connected(f"{x},{y}", f"{x},{y+1}"):
        flood_fill_rec(x, y+1)
    if y > 0 and maze.connected(f"{x},{y}", f"{x},{y-1}"):
        flood_fill_rec(x, y-1)

from queue import Queue
def flood_fill_queue(x, y):
    Q = Queue()
    Q.put((x, y))
    while not Q.empty():
        n = Q.get()
        x, y = n
        if n in inside:
            continue
        
        step(x, y)

        if x < SIZE-1 and maze.connected(f"{x},{y}", f"{x+1},{y}"):
            Q.put((x+1, y))
        if x > 0 and maze.connected(f"{x},{y}", f"{x-1},{y}"):
            Q.put((x-1, y))
        if y < SIZE-1 and maze.connected(f"{x},{y}", f"{x},{y+1}"):
            Q.put((x, y+1))
        if y > 0 and maze.connected(f"{x},{y}", f"{x},{y-1}"):
            Q.put((x, y-1))
  
def step(x, y):
    inside.add((x, y))
    fill_screen.fill(TEAL, (x*CELL, y*CELL, CELL, CELL))
    screen.blit(fill_screen, (0, 0))
    screen.blit(maze_screen, (0, 0))
    pg.display.update()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()

    clock.tick(20)

def restart():
    maze = Maze()
    px, py = 0, 0
    inside = set((px, py))  # set of (x, y) that have been visited
    fill_screen.fill(BLACK)
    fill_screen.fill(TEAL, (px*CELL, py*CELL, CELL, CELL))
    screen.blit(fill_screen, (0, 0))
    screen.blit(maze_screen, (0, 0))
    screen.blit(player_screen, (px*CELL, py*CELL))
    pg.display.update()
    
    return maze, inside, px, py

maze, inside, px, py = restart()
# flood_fill_rec(px, py)
# flood_fill_queue(px, py)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif event.key == pg.K_r:
                maze, inside, px, py = restart()
            
            if event.key == pg.K_UP:
                if py > 0 and maze.connected(f"{px},{py}", f"{px},{py-1}"):
                    py -= 1
            elif event.key == pg.K_DOWN:
                if py < SIZE-1 and maze.connected(f"{px},{py}", f"{px},{py+1}"):
                    py += 1
            elif event.key == pg.K_LEFT:
                if px > 0 and maze.connected(f"{px},{py}", f"{px-1},{py}"):
                    px -= 1
            elif event.key == pg.K_RIGHT:
                if px < SIZE-1 and maze.connected(f"{px},{py}", f"{px+1},{py}"):
                    px += 1

            # Update position
            if (px, py) not in inside:
                fill_screen.fill(TEAL, (px*CELL, py*CELL, CELL, CELL))
            inside.add((px, py))
            screen.blit(fill_screen, (0, 0))
            screen.blit(maze_screen, (0, 0))
            screen.blit(player_screen, (px*CELL, py*CELL))
            pg.display.update()
    
    clock.tick(60)

"""
MAZE GENERATION using list and saving edges in tree. Note tree guarantees no cycles.
BUG:
    - Double A* cheats! But it seems to predict which is the correct path: Seed: 24769 / size: 20
      SOLUTION: Bad indenting. Did not check if maze.connected(B, neighbor), lol. 
"""
from treelib import Tree
import random
import pygame as pg
from queue import Queue
# random.seed(1)
PLAYER = False

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
SCREEN_SIZE = 640
SIZE = 20
GOAL = SIZE * SIZE - 1
FPS = 300

# Visualize the maze
pg.init()
CELL = SCREEN_SIZE // SIZE
BLACK, GREEN, TEAL = (20, 20, 20), (20, 120, 20), (20, 70, 20)
BLUE, RED = (40, 40, 170), (170, 40, 40)

# Screens
screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

fill_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
fill_screen.fill(BLACK)

maze_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
maze_screen.set_colorkey((0, 0, 0))

heat_map = [[1 for _ in range(SIZE)] for _ in range(SIZE)]
max_heat, min_heat = 1, 0
heat_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
heat_screen.set_colorkey((0, 0, 0))

player_screen = pg.Surface((CELL, CELL))
pg.draw.circle(player_screen, GREEN, (CELL//2, CELL//2), CELL//4)
player_screen.set_colorkey((0, 0, 0))


pg.display.set_caption("Maze")
clock = pg.time.Clock()

DIRS = [-SIZE, SIZE, -1, 1] # up, down, left, right
class Maze:
    def __init__(self, start, goal):
        self.grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        self.tree = Tree()
        self.create_maze()
        # self.create_maze(random.randrange(0, SIZE), random.randrange(0, SIZE))
        gx, gy = goal % SIZE, goal // SIZE
        pg.draw.rect(fill_screen, GREEN, (gx*CELL, gy*CELL, CELL, CELL))

    def create_maze(self, root=SIZE * SIZE // 2):
        self.tree.create_node(root, root) # root node (tag, identifier)
        rx, ry = root % SIZE, root // SIZE
        self.grid[ry][rx] = 1
        queue = []
        queue.append((rx, ry))
        while len(queue) > 0:
            x, y = queue.pop(random.randrange(len(queue)))
            index = y * SIZE + x

            directions = DIRECTIONS.copy()
            random.shuffle(directions)
            for dir in directions:
                nx = x + dir[0]
                ny = y + dir[1]
                if nx < 0 or nx >= SIZE or ny < 0 or ny >= SIZE:
                    continue
                if self.grid[ny][nx] == 1:
                    continue
                nindex = ny * SIZE + nx
                # if self.tree.contains(nindex):  # quicker?
                #     continue

                # Create edge between (x, y) and (nx, ny)
                self.tree.create_node(nindex, nindex, parent=index)
                
                self.grid[ny][nx] = 1
                queue.append((nx, ny))


        for i in range(SIZE+1): # First draw all walls then remove walls between nodes in Maze
            pg.draw.line(maze_screen, GREEN, (0, i * CELL), (SCREEN_SIZE, i * CELL), 2)
            pg.draw.line(maze_screen, GREEN, (i * CELL, 0), (i * CELL, SCREEN_SIZE), 2)

        self.draw_maze(self.tree.get_node(root))

        for i in range(SIZE+1):            
            for j in range(SIZE+1): # Draw poles at every corner
                pg.draw.circle(maze_screen, GREEN, (i*CELL, j*CELL), 2)

    def draw_maze(self, node):
        k = 0
        if node.is_leaf():
            return
        x1, y1 = node.tag % SIZE, node.tag // SIZE
        for child in self.tree.children(node.tag):
            # draw line between node and child
            x2, y2 = child.tag % SIZE, child.tag // SIZE

            if x1 == x2: # horizontal wall
                y = max(y1, y2)
                a = (x1 * CELL + k, y * CELL)
                b = (x1 * CELL + CELL, y * CELL)
            else: # vertical wall
                x = max(x1, x2)
                a = (x * CELL, y1 * CELL + k)
                b = (x * CELL, y1 * CELL + CELL)
            pg.draw.line(maze_screen, (0, 0, 0), a, b, 2)
            self.draw_maze(child)
        
    def connected(self, a, b):
        node1 = self.tree.get_node(a)
        node2 = self.tree.get_node(b)
        return self.tree.parent(a) == node2 or self.tree.parent(b) == node1

def flood_fill(start):
    Q = Queue()
    Q.put(start)
    while not Q.empty():
        index = Q.get()
        if index == GOAL:
            return True
        x, y = index % SIZE, index // SIZE
        
        step(x, y)

        if x < SIZE-1 and maze.connected(index, index+1) and (x+1, y) not in inside:
            Q.put(index+1)
        if x > 0 and maze.connected(index, index-1) and (x-1, y) not in inside:
            Q.put(index-1)
        if y < SIZE-1 and maze.connected(index, index+SIZE) and (x, y+1) not in inside:
            Q.put(index+SIZE)
        if y > 0 and maze.connected(index, index-SIZE) and (x, y-1) not in inside:
            Q.put(index-SIZE)

# import default dict
from collections import defaultdict
def A_star(start, goal):
    open_set = set()
    open_set.add(start)
    came_from = {}
    g_score = defaultdict(lambda: float("inf"))
    g_score[start] = 0
    f_score = defaultdict(lambda: float("inf"))
    f_score[start] = heuristic(start, goal)

    while len(open_set) > 0:
        current = min(open_set, key=lambda x: f_score[x])
        if current == goal:
            reconstruct_path(came_from, current)
            return True
        step(current % SIZE, current // SIZE)

        open_set.remove(current)
        for dir in DIRS:
            neighbor = current + dir
            if neighbor < 0 or neighbor >= SIZE * SIZE:
                continue
            if maze.connected(current, neighbor):
                tentative_g_score = g_score[current] + 1  # Redundant, since all positions are visited only once
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.add(neighbor)


def heuristic(index, goal):  # manhattan distance 
    x, y = index % SIZE, index // SIZE
    gx, gy = goal % SIZE, goal // SIZE
    return abs(x - gx) + abs(y - gy)

def reconstruct_path(came_from, current, reverse=False):
    if reverse:
        # determine path, reverse it, then draw it
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        for index in path:
            x, y = index % SIZE, index // SIZE
            step(x, y, GREEN)
    else:
        while current in came_from:
            current = came_from[current]  # root has no came_from so terminates there
            x, y = current % SIZE, current // SIZE
            step(x, y, GREEN)

# Flip between two agents initially seeking the goal and star respectively
def A_star_double(start, goal):
    open_set_A = set([start])
    open_set_B = set([goal])
    came_from_A = {}
    came_from_B = {}
    g_score_A = defaultdict(lambda: float("inf"))
    g_score_A[start] = 0
    g_score_B = defaultdict(lambda: float("inf"))
    g_score_B[goal] = 0
    f_score_A = defaultdict(lambda: float("inf"))
    f_score_A[start] = heuristic(start, goal)
    f_score_B = defaultdict(lambda: float("inf"))
    f_score_B[goal] = heuristic(goal, start)

    # while len(open_set) > 0:
    while True:
        A = min(open_set_A, key=lambda x: f_score_A[x])
        step(A % SIZE, A // SIZE)

        open_set_A.remove(A)
        for dir in DIRS:
            neighbor = A + dir
            if neighbor < 0 or neighbor >= SIZE * SIZE:
                continue
            if maze.connected(A, neighbor):
                tentative_g_score = g_score_A[A] + 1
                if tentative_g_score < g_score_A[neighbor]:
                    came_from_A[neighbor] = A
                    g_score_A[neighbor] = tentative_g_score
                    f_score_A[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in open_set_A:
                        open_set_A.add(neighbor)
            
                if neighbor in open_set_B:
                    step(neighbor % SIZE, neighbor // SIZE, RED)
                    increment_heat_map(neighbor)
                    reconstruct_path(came_from_B, neighbor, True)
                    reconstruct_path(came_from_A, neighbor)
                    return True
            
        B = min(open_set_B, key=lambda x: f_score_B[x])
        step(B % SIZE, B // SIZE)

        open_set_B.remove(B)
        for dir in DIRS:
            neighbor = B + dir
            if neighbor < 0 or neighbor >= SIZE * SIZE:
                continue
            if maze.connected(B, neighbor):
                tentative_g_score = g_score_B[B] + 1
                if tentative_g_score < g_score_B[neighbor]:
                    came_from_B[neighbor] = B
                    g_score_B[neighbor] = tentative_g_score
                    f_score_B[neighbor] = tentative_g_score + heuristic(neighbor, start)
                    if neighbor not in open_set_B:
                        open_set_B.add(neighbor)
            
                if neighbor in open_set_A:
                    step(neighbor % SIZE, neighbor // SIZE, RED)
                    increment_heat_map(neighbor)
                    reconstruct_path(came_from_B, neighbor, True)
                    reconstruct_path(came_from_A, neighbor)
                    return True

def increment_heat_map(index):
    global min_heat, max_heat
    x, y = index % SIZE, index // SIZE
    if heat_map[index % SIZE][index // SIZE] == min_heat:
        min_heat += 1
    heat_map[index % SIZE][index // SIZE] += 1
    max_heat = max(max_heat, heat_map[y][x])


  
def step(x, y, color=TEAL):
    inside.add((x, y))
    fill_screen.fill(color, (x*CELL, y*CELL, CELL, CELL))
    update_screen()
    process_input()
    clock.tick(FPS)

def process_input():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()

def update_screen(pos=None):
    screen.blit(fill_screen, (0, 0))
    # min-max normalize heat_map
    # show_heat_map()
    
    screen.blit(maze_screen, (0, 0))
    if pos:
        screen.blit(player_screen, (pos[0]*CELL, pos[1]*CELL))
    pg.display.update()

def show_heat_map():
    heat_screen.fill(BLACK)
    process_input()
    for y in range(SIZE):
        for x, r in enumerate(heat_map[y]):
            red = (r - min_heat) / (max_heat - min_heat)
            heat_screen.fill((red, 0, 0), (x*CELL, y*CELL, CELL, CELL))
    screen.blit(heat_screen, (0, 0))

def restart(seed=0):
    if seed:
        random.seed(seed)
    px, py = 0, 0
    fill_screen.fill(BLACK)
    maze = Maze(0, GOAL)
    inside = set((px, py))  # set of (x, y) that have been visited
    fill_screen.fill(TEAL, (px*CELL, py*CELL, CELL, CELL))
    update_screen((px, py))
    
    return maze, inside, px, py


if not PLAYER:
    seed = 0
    while True:
        seed = random.randrange(100000)
        # seed = 48063
        maze, inside, px, py = restart(seed)
        # print(f"{seed = }")
        # flood_fill(0)
        # A_star(0, GOAL)
        # maze, inside, px, py = restart(seed)
        A_star_double(0, GOAL)
else:
    maze, inside, px, py = restart()
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
                    if py > 0 and maze.connected(py * SIZE + px, (py - 1) * SIZE + px):
                        py -= 1
                elif event.key == pg.K_DOWN:
                    if py < SIZE-1 and maze.connected(py * SIZE + px, (py + 1) * SIZE + px):
                        py += 1
                elif event.key == pg.K_LEFT:
                    if px > 0 and maze.connected(py * SIZE + px, py * SIZE + px - 1):
                        px -= 1
                elif event.key == pg.K_RIGHT:
                    if px < SIZE-1 and maze.connected(py * SIZE + px, py * SIZE + px + 1):
                        px += 1

                # Update position
                if (px, py) not in inside:
                    fill_screen.fill(TEAL, (px*CELL, py*CELL, CELL, CELL))
                inside.add((px, py))
                update_screen((px, py))
                pg.display.update()
        
        clock.tick(60)

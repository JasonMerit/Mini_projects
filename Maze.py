"""
MAZE GENERATION using list and saving edges in tree. Note tree guarantees no cycles.
BUG:
    - Double A* cheats! But it seems to predict which is the correct path: Seed: 24769 / size: 20
      SOLUTION: Bad indenting. Did not check if maze.connected(B, neighbor), lol. 
"""
import random
import pygame as pg
from queue import Queue
import networkx as nx
# random.seed(1)
from Maze_config import *

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
CELL = SCREEN_SIZE // SIZE
BLACK, GREEN, TEAL = (20, 20, 20), (20, 120, 20), (20, 70, 20)
BLUE, RED = (40, 40, 170), (170, 40, 40)

pg.init()
clock = pg.time.Clock()

class Display:
    """Draws all information from Maze to the screen
    - screen - main screen
    - fill_screen - that path traveled thus far
    - maze_screen - constant layout of maze
    - player_screen - player circle
    - heat_screen - heat map
    """
    
    def __init__(self, graph):
        self.graph = graph
        
        # Screens
        self.screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pg.display.set_caption("Maze")

        self.fill_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
        self.fill_screen.fill(BLACK)
        pg.draw.rect(self.fill_screen, TEAL, (START[0]*CELL, START[1]*CELL, CELL, CELL))
        pg.draw.rect(self.fill_screen, GREEN, (GOAL[0]*CELL, GOAL[1]*CELL, CELL, CELL))

        self.maze_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
        self.maze_screen.set_colorkey((0, 0, 0))

        # heat_map = [[1 for _ in range(SIZE)] for _ in range(SIZE)]
        # max_heat, min_heat = 1, 0
        self.heat_screen = pg.Surface((SCREEN_SIZE, SCREEN_SIZE))
        self.heat_screen.set_colorkey((0, 0, 0))

        self.player_screen = pg.Surface((CELL, CELL))
        pg.draw.circle(self.player_screen, GREEN, (CELL//2, CELL//2), CELL//4)
        self.player_screen.set_colorkey((0, 0, 0))

        # Draw the graph into appropriate screens
        for i in range(SIZE+1): # First draw all walls then remove walls between nodes in Maze
            pg.draw.line(self.maze_screen, GREEN, (0, i * CELL), (SCREEN_SIZE, i * CELL), 2)
            pg.draw.line(self.maze_screen, GREEN, (i * CELL, 0), (i * CELL, SCREEN_SIZE), 2)
        
        k = 0
        for edge in graph.edges():
            (x1, y1), (x2, y2) = edge
            if x1 == x2: # horizontal wall
                y = max(y1, y2)
                a = (x1 * CELL + k, y * CELL)
                b = (x1 * CELL + CELL, y * CELL)
            else: # vertical wall
                x = max(x1, x2)
                a = (x * CELL, y1 * CELL + k)
                b = (x * CELL, y1 * CELL + CELL)
            pg.draw.line(self.maze_screen, (0, 0, 0), a, b, 2)

        for i in range(SIZE+1):            
            for j in range(SIZE+1): # Draw poles at every corner
                pg.draw.circle(self.maze_screen, GREEN, (i*CELL, j*CELL), 2) 
        
        self.update_screen(START)

    def update_screen(self, pos=None):
        self.screen.blit(self.fill_screen, (0, 0))
        # min-max normalize heat_map
        # show_heat_map()
        
        self.screen.blit(self.maze_screen, (0, 0))
        if pos:
            self.screen.blit(self.player_screen, (pos[0]*CELL, pos[1]*CELL))
        pg.display.update()
        

    

DIRS = [-SIZE, SIZE, -1, 1] # up, down, left, right
class Maze:
    """Handles maze generation and intereaction.
    Uses Display class to draw the maze."""
    def __init__(self):
        self.graph = self.create_maze(START)
        self.display = Display(self.graph)
    
    def create_maze(self, start):
        grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        x, y = start
        grid[y][x] = 1

        graph = nx.Graph()
        graph.add_node((x, y))

        stack = [(x, y)]
        max_x, max_y = x, y
        while stack:
            x, y = stack.pop()
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            unvisited = []
            for dir in DIRECTIONS:
                xp = x + dir[0]
                yp = y + dir[1]
                if 0 <= xp < SIZE and 0 <= yp < SIZE and not grid[yp][xp]:
                    unvisited.append((xp, yp))
            
            if unvisited:
                stack.append((x, y))
                xp, yp = unvisited.pop(random.randrange(len(unvisited)))
                
                graph.add_edge((x, y), (xp, yp))
                grid[yp][xp] = 1
                stack.append((xp, yp))
        
        return graph

    def step(self, pos, color=TEAL):
        inside.add(pos)
        self.display.fill_screen.fill(color, (pos[0]*CELL, pos[1]*CELL, CELL, CELL))
        self.display.update_screen()
        process_input()
        clock.tick(FPS)
    
    def player_step(self, pos):
        self.display.fill_screen.fill(TEAL, (pos[0]*CELL, pos[1]*CELL, CELL, CELL))
        self.display.update_screen(pos)
        process_input()
        clock.tick(FPS)

    def connected(self, a, b):
        return self.graph.has_edge(a, b)

def flood_fill(start):
    Q = Queue()
    Q.put(start)
    while not Q.empty():
        pos = Q.get()
        # if pos == GOAL:
        #     return True
        
        maze.step(pos)

        x, y = pos
        
        if y > 0 and maze.connected((x, y), (x, y-1)) and not (x, y-1) in inside: # and inside
            Q.put((x, y-1))
        if y < SIZE-1 and maze.connected((x, y), (x, y+1)) and not (x, y+1) in inside:
            Q.put((x, y+1))
        if x > 0 and maze.connected((x, y), (x-1, y)) and not (x-1, y) in inside:
            Q.put((x-1, y))
        if x < SIZE-1 and maze.connected((x, y), (x+1, y)) and not (x+1, y) in inside:
            Q.put((x+1, y))


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
        maze.step(current)

        open_set.remove(current)
        for dir in DIRECTIONS:
            neighbor = (current[0] + dir[0], current[1] + dir[1])
            if 0 <= neighbor[0] < SIZE and 0 <= neighbor[1] < SIZE and maze.connected(current, neighbor):
                tentative_g_score = g_score[current] + 1  # Redundant, since all positions are visited only once
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.add(neighbor)


def heuristic(pos, goal):  # manhattan distance 
    (x, y), (gx, gy) = pos, goal
    return abs(x - gx) + abs(y - gy)

def reconstruct_path(came_from, current, reverse=False):
    # Draw a path 
    if not reverse:
        while current in came_from:
            current = came_from[current]  # root has no came_from so terminates there
            maze.step(current, GREEN)
    else:
        path = [current]  # determine path, reverse it, then draw it
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        for current in path:
            maze.step(current, GREEN)
       

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
        maze.step(A)

        open_set_A.remove(A)

        for dir in DIRECTIONS:
            neighbor = (A[0] + dir[0], A[1] + dir[1])
            if 0 <= neighbor[0] < SIZE and 0 <= neighbor[1] < SIZE and maze.connected(A, neighbor):
                tentative_g_score = g_score_A[A] + 1
                if tentative_g_score < g_score_A[neighbor]:
                    came_from_A[neighbor] = A
                    g_score_A[neighbor] = tentative_g_score
                    f_score_A[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in open_set_A:
                        open_set_A.add(neighbor)
            
                if neighbor in open_set_B:
                    maze.step(neighbor, RED)
                    increment_heat_map(neighbor)
                    reconstruct_path(came_from_B, neighbor, True)
                    reconstruct_path(came_from_A, neighbor)
                    return True
            
        B = min(open_set_B, key=lambda x: f_score_B[x])
        maze.step(B)

        open_set_B.remove(B)
        for dir in DIRECTIONS:
            neighbor = (B[0] + dir[0], B[1] + dir[1])
            if 0 <= neighbor[0] < SIZE and 0 <= neighbor[1] < SIZE and maze.connected(B, neighbor):
                tentative_g_score = g_score_B[B] + 1
                if tentative_g_score < g_score_B[neighbor]:
                    came_from_B[neighbor] = B
                    g_score_B[neighbor] = tentative_g_score
                    f_score_B[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in open_set_B:
                        open_set_B.add(neighbor)
            
                if neighbor in open_set_A:
                    maze.step(neighbor, RED)
                    increment_heat_map(neighbor)
                    reconstruct_path(came_from_B, neighbor, True)
                    reconstruct_path(came_from_A, neighbor)
                    return True

def increment_heat_map(index):
    return 
    global min_heat, max_heat
    x, y = index % SIZE, index // SIZE
    if heat_map[index % SIZE][index // SIZE] == min_heat:
        min_heat += 1
    heat_map[index % SIZE][index // SIZE] += 1
    max_heat = max(max_heat, heat_map[y][x])


  
def process_input():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()

def pause():
    while True:
        process_input()
        clock.tick(60)

# def show_heat_map():
#     heat_screen.fill(BLACK)
#     process_input()
#     for y in range(SIZE):
#         for x, r in enumerate(heat_map[y]):
#             red = (r - min_heat) / (max_heat - min_heat)
#             heat_screen.fill((red, 0, 0), (x*CELL, y*CELL, CELL, CELL))
#     screen.blit(heat_screen, (0, 0))

def restart(seed=0):
    if seed:
        random.seed(seed)
    maze = Maze()
    inside = set(START)  # set of (x, y) that have been visited
    
    return maze, inside, START

if not PLAYER:
    seed = 0
    while True:
        seed = random.randrange(100000)
        # seed = 48063
        maze, inside, (px, py) = restart(seed)
        # print(f"{seed = }")
        # flood_fill(START)
        # A_star(START, GOAL)
        # maze, inside = restart(seed)
        A_star_double(START, GOAL)
else:
    maze, inside, (px, py) = restart()
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
                    maze, inside, (px, py) = restart()
                
                if event.key == pg.K_UP:
                    if py > 0 and maze.connected((px, py), (px, py-1)):
                        py -= 1
                elif event.key == pg.K_DOWN:
                    if py < SIZE-1 and maze.connected((px, py), (px, py+1)):
                        py += 1
                elif event.key == pg.K_LEFT:
                    if px > 0 and maze.connected((px, py), (px-1, py)):
                        px -= 1
                elif event.key == pg.K_RIGHT:
                    if px < SIZE-1 and maze.connected((px, py), (px+1, py)):
                        px += 1


                if (px, py) == GOAL:
                    maze, inside, (px, py) = restart()
                    continue
                # Update position
                if (px, py) not in inside:
                    maze.player_step((px, py))
                inside.add((px, py))
        
        clock.tick(60)

"""
https://weblog.jamisbuck.org/archives.html
MAZE GENERATION using list and saving edges in tree. Note tree guarantees no cycles.
BUG:
    - Double A* cheats! But it seems to predict which is the correct path: Seed: 24769 / size: 20
      SOLUTION: Bad indenting. Did not check if maze.connected(B, neighbor), lol. 
"""
import random
import pygame as pg
from queue import Queue
import networkx as nx
from Maze_config import *
import csv

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right

CELL = SCREEN_SIZE // SIZE
WIDTH = 1
BLACK, GREEN, TEAL = (20, 20, 20), (20, 120, 20), (20, 70, 20)
BLUE, RED = (40, 40, 170), (170, 40, 40)

pg.init()
clock = pg.time.Clock()

screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pg.display.set_caption("Maze")

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
            pg.draw.line(self.maze_screen, GREEN, (0, i * CELL), (SCREEN_SIZE, i * CELL), WIDTH)
            pg.draw.line(self.maze_screen, GREEN, (i * CELL, 0), (i * CELL, SCREEN_SIZE), WIDTH)
        
        k = 0
        for edge in graph.edges:
            (x1, y1), (x2, y2) = edge
            if x1 == x2: # horizontal wall
                y = max(y1, y2)
                a = (x1 * CELL + k, y * CELL)
                b = (x1 * CELL + CELL, y * CELL)
            else: # vertical wall
                x = max(x1, x2)
                a = (x * CELL, y1 * CELL + k)
                b = (x * CELL, y1 * CELL + CELL)
            pg.draw.line(self.maze_screen, (0, 0, 0), a, b, WIDTH)

        for i in range(SIZE+1):            
            for j in range(SIZE+1): # Draw poles at every corner
                pg.draw.circle(self.maze_screen, GREEN, (i*CELL, j*CELL), WIDTH) 
        
        self.update_screen(START)

    def update_screen(self, pos=None):
        self.screen.blit(self.fill_screen, (0, 0))
        # min-max normalize heat_map
        # show_heat_map()
        
        self.screen.blit(self.maze_screen, (0, 0))
        if pos:
            self.screen.blit(self.player_screen, (pos[0]*CELL, pos[1]*CELL))
        pg.display.update()
    
    def draw_path(self, path):
        x, y = path[0]
        for xp, yp in path[1:]:
            a = ((x + 0.5) * CELL, (y + 0.5) * CELL)
            b = ((xp + 0.5) * CELL, (yp + 0.5) * CELL)
            pg.draw.line(self.fill_screen, RED, a, b, CELL // 4)
            x, y = xp, yp
            self.update_screen()
            process_input()
            clock.tick(FPS)
        self.update_screen()
        

    

DIRS = [-SIZE, SIZE, -1, 1] # up, down, left, right
class Maze:
    """Handles maze generation and intereaction.
    Uses Display class to draw the maze."""
    def __init__(self):
        self.graph = self._create_maze(MAZE_GENERATOR)
        self.display = Display(self.graph) if DISPLAY else None
    
    def _create_maze(self, generator):
        if generator == 0:
            return self._stack()
        elif generator == 1:
            return self._eller()
        elif generator == 2:
            return self._wilson()
        elif generator == 3:
            return self._kruskal()
        elif generator == 4:
            return self._prim()
        elif generator == 5:
            return self._hunt_and_kill()
        else:
            raise ValueError(f"Unknown generator: {generator}")

    def _stack(self):
        grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        x, y = 0, 0
        grid[y][x] = 1

        graph = nx.Graph()
        graph.add_node((x, y))

        stack = [(x, y)]
        while stack:
            x, y = stack.pop()

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

    def _eller(self):
        graph = nx.Graph()  # edges are added horizontally at 2) + 6) and vertically at 3)

        # 1. Initialize the cells of the first row to each exist in their own set.
        # grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]  # Contains info about sets
        # grid[0] = list(range(SIZE)) # initally all unique
        counter = SIZE
        row = list(range(SIZE))
        # 5. Repeat until the last row is reached.
        for y in range(SIZE-1):

            # 2. Now, randomly join adjacent cells, but only if they are not in the same set.
            for x in range(SIZE-1):
                if row[x] != row[x + 1] and random.random() < 0.5:
                    row[x + 1] = row[x]
                    graph.add_edge((x, y), (x+1, y))

            # 3. For each set, randomly create vertical connections downward to the next row.
            # 4. Flesh out the next row by putting any remaining cells into their own sets.
            next_row = [0 for _ in range(SIZE)]
            for x in range(SIZE):
                if random.random() < 0.5:
                    next_row[x] = row[x]
                    graph.add_edge((x, y), (x, y+1))
                else:
                    next_row[x] = counter
                    counter += 1
            
            # 3.1. Ensure that each set has at least one downward connection.
            unexpanded = set(row) - set(next_row)
            for u in unexpanded:
                positions = [i for i, x in enumerate(row) if x == u]
                pos = random.choice(positions)
                next_row[pos] = u
                graph.add_edge((pos, y), (pos, y+1))
        
            row = next_row

        # return grid

        # 6. For the last row, join all adjacent cells that do not share a set, and omit the vertical connections, and you’re done!
        # y += 1
        for x in range(SIZE-1):
            if row[x] != row[x + 1]:
                # grid[y][x + 1] = grid[y][x]
                graph.add_edge((x, y), (x+1, y))

        return graph

    def _kruskal(self):
        grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        sets = [set([(x, y)]) for x in range(SIZE) for y in range(SIZE)]
        coords = [(x, y) for x in range(SIZE) for y in range(SIZE)]
        random.shuffle(coords)
    

    def _wilson(self):
        graph = nx.Graph()
        maze = set()
        cells = [(x, y) for x in range(SIZE) for y in range(SIZE)]

        cell = cells.pop(0)
        maze.add(cell)

        while cells:
            # Choose arbitrary cell to start path from
            cell = cells.pop(0)
            if cell in maze:
                continue

            path = self._random_walk(cell, maze)
            maze.update(path)
            
            last = path.pop(0)
            for p in path:
                graph.add_edge(last, p)
                last = p

        return graph

    def _random_walk(self, cell, maze):
        path = [cell]
        while True:
            dir = random.choice(DIRECTIONS)
            xp = cell[0] + dir[0]
            yp = cell[1] + dir[1]
            if xp < 0 or xp >= SIZE or yp < 0 or yp >= SIZE:
                continue
            if (xp, yp) in maze:  # Path entered maze
                path.append((xp, yp))
                return path
            if (xp, yp) in path:  # No loops!
                index = path.index((xp, yp))
                path = path[:index+1]
                cell = path[-1]
                continue
            path.append((xp, yp))
            cell = (xp, yp)

    def _prim(self):
        graph = nx.Graph()
        maze = set()
        cells = [(x, y) for x in range(SIZE) for y in range(SIZE)]
        grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]

        cell = cells.pop(0)
        maze.add(cell)
        grid[cell[1]][cell[0]] = 1

        stack = set(self._get_neighbors(cell, grid))
        while stack:
            cell = random.choice(stack)
            # If only one of the cells that the wall divides is visited
            num_visited = 0
            for neighbor in self._get_neighbors(cell, grid):
                if grid[neighbor[1]][neighbor[0]]:
                    num_visited += 1
    
    def _get_neighbors(self, cell, grid):
        walls = []
        for dir in DIRECTIONS:
            xp = cell[0] + dir[0]
            yp = cell[1] + dir[1]
            if xp < 0 or xp >= SIZE or yp < 0 or yp >= SIZE or grid[yp][xp]:
                continue
            walls.append((cell, (xp, yp)))
        return walls
    
    def _hunt_and_kill(self):
        graph = nx.Graph()
        grid = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        # unexhausted = [(x, y) for x in range(SIZE) for y in range(SIZE)]
        # free_cells = set((x, y) for x in range(SIZE) for y in range(SIZE))

        # 1. Choose a starting location.
        pos = (0, 0)
        grid[pos[1]][pos[0]] = 1
        
        # 4. Repeat steps 2-3 until all locations have been visited. (Hunt can't find any unvisited cells)
        while True:
            # 2. Perform a random walk, carving passages to unvisited neighbors, until it is unable to move.
            while True:
                directions = DIRECTIONS.copy()
                random.shuffle(directions)
                for dir in directions:
                    xp = pos[0] + dir[0]
                    yp = pos[1] + dir[1]
                    if xp < 0 or xp >= SIZE or yp < 0 or yp >= SIZE or grid[yp][xp]:
                        continue

                    graph.add_edge(pos, (xp, yp))
                    grid[yp][xp] = 1
                    pos = (xp, yp)
                    break
                else:  # directions exhausted
                    break

            # 3. Hunt for unvisited cell with visited neighbor.
            pos, visited = self._hunt(None, grid)
            if pos is None:
                return graph
            grid[pos[1]][pos[0]] = 1
            graph.add_edge(pos, visited)
    
    # def _rando_walk(self, pos, grid, graph):
        

    def _hunt(self, free_cells, grid):
        for x in range(SIZE):
            for y in range(SIZE):
                if grid[y][x]:
                    continue

                for dir in DIRECTIONS:
                    xp = x + dir[0]
                    yp = y + dir[1]
                    if not self.in_bounds(xp, yp) or not grid[yp][xp]:
                        continue

                    return (x, y), (xp, yp)
        return None, None

    def in_bounds(self, x, y):
        return 0 < x < SIZE and 0 < y < SIZE
    
    def step(self, pos, color=TEAL):
        inside.add(pos)
        if DISPLAY:
            self.display.fill_screen.fill(color, (pos[0]*CELL, pos[1]*CELL, CELL, CELL))
            self.display.update_screen()
        process_input()
        clock.tick(FPS)
    
    def player_step(self, pos):
        if DISPLAY:
            self.display.fill_screen.fill(TEAL, (pos[0]*CELL, pos[1]*CELL, CELL, CELL))
            self.display.update_screen(pos)
        process_input()
        clock.tick(FPS)

    def connected(self, a, b):
        # return random.random() < 0.5
        return a in self.graph[b]
        return self.graph.has_edge(a, b)

    def draw_path(self, path):
        self.display.draw_path(path)

        

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
    count = 0
    open_set = set()
    open_set.add(start)
    came_from = {}
    g_score = defaultdict(lambda: float("inf"))
    g_score[start] = 0
    f_score = defaultdict(lambda: float("inf"))
    f_score[start] = heuristic(start, goal)

    while len(open_set) > 0:
        count += 1
        current = min(open_set, key=lambda x: f_score[x])
        if current == goal:
            if DISPLAY:
                reconstruct_path(came_from, current)
            return count
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
    # Determine path, then draw it
    path = [current]
    while current in came_from:
        current = came_from[current]  # start has no came_from so terminates there
        path.append(current)

    if reverse:
        path.reverse()

    maze.draw_path(path)
       

# Flip between two agents initially seeking the goal and star respectively
def A_star_double(start, goal):
    count = 0
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
        count += 1
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
                    if not DISPLAY:
                        return count
                    maze.step(neighbor, RED)
                    # increment_heat_map(neighbor)
                    reconstruct_path(came_from_B, neighbor, True)
                    reconstruct_path(came_from_A, neighbor)
                    return count
        count += 1
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
                    if not DISPLAY:
                        return count
                    maze.step(neighbor, RED)
                    increment_heat_map(neighbor)
                    reconstruct_path(came_from_B, neighbor, True)
                    reconstruct_path(came_from_A, neighbor)
                    return count

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


            if event.key == pg.K_SPACE:
                return "yikes"
            if event.key == pg.K_p:

                while True:
                    event = pg.event.wait()
                    if event.type == pg.QUIT:
                        pg.quit()
                        exit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            pg.quit()
                            exit()
                    if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                        break

def pause():
    while True:
        if process_input():
            print("unpause")
            return
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

single_steps_avg = 0
double_steps_avg = 0
iteration = 1
table = []
if not PLAYER:
    while True:
        # seed a random number
        seed = random.randrange(10e100)
        # seed = 48063
        maze, inside, (px, py) = restart(seed)
        if SOLVER == 0:
            flood_fill(START)
        elif SOLVER == 1:
            A_star(START, GOAL)
            maze, inside, (px, py) = restart(seed)
        elif SOLVER == 2:
            single_result = A_star(START, GOAL)
            single_steps_avg += 1/iteration * (single_result - single_steps_avg)

            maze, inside, (px, py) = restart(seed)
            double_result = A_star_double(START, GOAL)
            double_steps_avg += 1/iteration * (double_result - double_steps_avg)

            print(iteration, round(single_steps_avg, 2), round(double_steps_avg, 2))
            iteration += 1
            table.append([seed, single_result, double_result])
            with open("Maze_out.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(table)
else:
    # seed = 48063
    maze, inside, (px, py) = restart()
    # maze.draw_path(PATH)
    # pause()
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
                # if (px, py) not in inside:
                maze.player_step((px, py))
                inside.add((px, py))
        
        clock.tick(60)

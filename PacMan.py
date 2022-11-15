""" GridWorld environment for RL
    Run this script for human play

    Common bugs
    - "list index out of range" => random.randint(a, b) is inclusive so replace b with b-1. 
    - Forgetting to remove prior element in grid

    TODO
    - Curriculum friendly structure for training
"""

from logging import exception
from gym import spaces
import numpy as np
import pygame as pg
import sys, random, math
from collections import defaultdict

CELL = 25  # Cell width
WHITE, GREY, BLACK = (200, 200, 200), (190, 190, 190), (20, 20, 20)
YELLOW, RED, GREEN = (200, 200, 0), (200, 0, 0), (0, 150, 0)
BLUE = (0, 0, 200)
RED, PINK, LIGHT_BLUE, ORANGE = (255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)
COLORS = [RED, PINK, LIGHT_BLUE, ORANGE] # Blinky, Pinky, Inky, Clyde

MOVE = [pg.K_d, pg.K_w,  # RIGHT, UP,
        pg.K_a, pg.K_s]  # LEFT, DOWN
RIGHT, UP, LEFT, DOWN = range(len(MOVE))


# NUM_ENTITIES = 3
# WALL, AGENT, GOAL = range(NUM_ENTITIES)

pg.init()
pg.display.set_caption('GridWorld')
pg.font.init()

walls = np.array([[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                 [0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
                 [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                 [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                 [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
                 [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                 [0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
                 [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                 [0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                 [0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]])

seeds = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
				[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
				[0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
				[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
				[0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0],
				[0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0],
				[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
				[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
				[0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
				[0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
				[0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0],
				[0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0],
				[0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
				[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
				[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

class Vec2D():
    """Helper class for flipping coordinates and basic arithmetic.
    pygame draws by v=(x, y) and numpy indexes by p=(y, x)."""

    def __init__(self, x, y=0):
        if type(x) != tuple:
            self.x, self.y = x, y
        else:
            self.x, self.y = x[0], x[1]

    @property
    def v(self):
        return self.x, self.y

    @property
    def p(self):
        return int(self.y), int(self.x)

    @property
    def sum(self):
        return self.x + self.y

    def __repr__(self):
        return f'Vec2D({self.x}, {self.y})'

    def __add__(self, o):
        return Vec2D(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        return Vec2D(self.x - o.x, self.y - o.y)

    def __mul__(self, k):
        return Vec2D(k * self.x, k * self.y)

    def __rmul__(self, k):
        return self.__mul__(self, k)

    def __floordiv__(self, k):
        return Vec2D(self.x // k, self.y // k)

    def __ceil__(self):
        return Vec2D(math.ceil(self.x), math.ceil(self.y))

    def __abs__(self):
        return Vec2D(abs(self.x), abs(self.y))

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y

    def __iter__(self):
        for i in [self.x, self.y]:
            yield i

    def __hash__(self):
        return hash((self.x, self.y))


class Display():
    """Handles all rendering"""

    def __init__(self, start, ghost_starts):
        self.H, self.W = walls.shape
        self.screen = pg.display.set_mode([self.W * CELL, self.H * CELL])
        self.font = pg.font.Font(None, 12)

        # Mouths
        turn = lambda x: (x[1], -x[0])
        self.big_mouth = [[(11.5,-11.5), (-2,0), (11.5,11.5)]]
        for _ in range(3):
            self.big_mouth.append([turn(x) for x in self.big_mouth[-1]])

        self.mid_mouth = [[(11.5,-8), (-2,0), (11.5,8)]]
        for _ in range(3):
            self.mid_mouth.append([turn(x) for x in self.mid_mouth[-1]])

        self.small_mouth = [[(11.5,-5), (-2,0), (11.5,5)]]
        for _ in range(3):
            self.small_mouth.append([turn(x) for x in self.small_mouth[-1]])

        self.reset(start, ghost_starts)
        self.pos = start
        self.ghost_starts = ghost_starts

    def update(self, pos, facing, frame, ghosts):
        # PacMan
        pg.draw.circle(self.screen, BLACK, self.rect.center, 12)
        self.rect.center = pos.v
        self._draw_pacman(self.rect.center, facing, frame)

        # Ghosts
        for i, ghost in enumerate(ghosts):
            color = COLORS[i]
            pg.draw.circle(self.screen, color, ghost.pos.v, 12)

        pg.display.flip()
        # pg.display.update(self.rect)

    
    def reset(self, start, ghost_starts):
        for x in range(self.W):
            for y in range(self.H):
                pos = Vec2D(x, y)

                color = BLUE if walls[pos.p] else BLACK
                self._draw_rect(pos, color)
                # self._draw_text(pos.v, pos)

                if seeds[pos.p]:
                    self._draw_circle(pos, CELL >> 3, WHITE)

        # PacMan
        self.rect = self._draw_pacman(start.v, 1, 0)
        pg.display.flip()

    def draw_path(self):
        for p in self.path:
            self._draw_circle(p, CELL >> 3)  # x >> 3 = x / 8
    
    def _draw_rect(self, pos, color):
        pos = pos * CELL# + Vec2D(1, 1)
        rect = pg.Rect(pos.v, (CELL, CELL))
        # rect = pg.Rect(pos.v, (CELL - 2, CELL - 2))
        pg.draw.rect(self.screen, color, rect, 0)
        return rect

    def _draw_circle(self, pos, r, color):
        center = (pos + Vec2D(0.5, 0.5)) * CELL
        return pg.draw.circle(self.screen, color, center.v, r)
    
    def _draw_pacman(self, pos, facing, frame):
        # center = pos + Vec2D(0.5, 0.5) * (CELL>>1)
        rect = pg.draw.circle(self.screen, YELLOW, pos, 12)

        # Mouth
        mouth = self.big_mouth
        if frame > 9:
            mouth = self.mid_mouth
        if frame > 17:
            mouth = self.small_mouth
        corners = mouth[facing]
        points = [(Vec2D(pos) + Vec2D(c)).v for c in corners]
        pg.draw.polygon(self.screen, BLACK, points)

        return rect

    def _draw_text(self, text, pos):
        center = (pos + Vec2D(0.5, 0.5)) * CELL
        text = self.font.render(str(text), True, WHITE)
        text_rect = text.get_rect(center=center.v)
        self.screen.blit(text, text_rect)

class Ghost():
    # https://dev.to/code2bits/pac-man-patterns--ghost-movement-strategy-pattern-1k1a


    def __init__(self):
        self._is_collide = lambda vec: walls[(self.unit + vec).p]  # Collision
    
    def reset(self, unit):
        self.unit = unit
        self.pos = unit2pix(unit)

offset = math.ceil(CELL / 2)
unit2pix = lambda unit: unit * CELL + Vec2D(offset, offset)  # Mao from unit up to pixels


class PacMan():
    """PacMan environment following OpenAI functionality"""

    def test(self):

        print(self.unit)

    def __init__(self, seed=None, space_fun=None):
        """
        Keyword arguments:
        seed      -- int seed for grid generation and action sampling.
        space_fun -- function to execute. Used for debugging. 
        """
        if seed != None:
            random.seed(seed)
        self.space_fun = space_fun if space_fun else lambda: None


        self.DIRS = [Vec2D(1, 0), Vec2D(0, -1),  # RIGHT, UP
                     Vec2D(-1, 0), Vec2D(0, 1)]  # LEFT, DOWN

        self.action_space = spaces.Discrete(len(self.DIRS))
        self._is_collide = lambda vec: walls[(self.unit + vec).p]  # Collision

        self.num_seeds = seeds.sum()
        self.ghosts = [Ghost()]
        [ghost.reset(Vec2D(10, 9)) for ghost in self.ghosts]
        
        
    def reset(self):	
        """Reset class properties"""
        self.done = False

        self.score = 0
        self.frame = CELL
        self.unit = Vec2D(4, 9)
        assert(not walls[self.unit.p]), f'Starting in wall {self.unit}'
        self.vel = Vec2D(0, 0)
        self.last_action = -1
        self.pos = unit2pix(self.unit) # Start position (cealing)
        # self.observation_space = spaces.Box(0, 1, shape=walls.shape, dtype=int)
        self.display = Display(self.pos, [unit2pix(Vec2D(10, 10))])

    def move(self):
        """ vel is changed in step() and used here
        check for collision frame, then wrapping and reset accordingly"""
        if self.vel == Vec2D(0, 0): 
            return
        
        # Collision frame
        if self.frame == CELL:  
            
            # Wrapping
            if (self.unit + self.vel).x < 0:  
                self.unit.x = len(walls[0])
                self.pos.x = self.unit.x * CELL + 13
            elif (self.unit + self.vel).x > len(walls[0])-1:
                self.unit.x = -1
                self.pos.x = -13

            # Collision check
            elif self._is_collide(self.vel):
                self.vel = Vec2D(0, 0)  # Stand still and return
                return
            
            self.frame = 0  		# Reset frame count and displace unit
            self.unit += self.vel

            if seeds[self.unit.p]:  # Seed munching
                self.score += 1
                seeds[self.unit.p] = 0
                if self.score == self.num_seeds:
                    print("WON")

        # Count frame and displace actors
        self.frame += 1
        self.pos += self.vel
        self.display.update(self.pos, self.last_action, self.frame, self.ghosts)


    def step(self, action):
        """Take action and return new state grid, reward and done"""
        err_msg = f"{action!r} ({type(action)}) invalid"
        assert self.action_space.contains(action), err_msg

        # Can't move opposite and avoid redundant updating
        if self.last_action in [action]: # (action + 2) % len(MOVE)
            return

        direction = self.DIRS[action]
        if self._is_collide(direction):
            return 

        self.vel = direction
        self.last_action = action


    def close(self, total=False):
        """Quit pygame and script if total is flagged true."""
        pg.display.quit()
        pg.quit()
        if total: sys.exit()

    def _get_neighbors(self, n, grid):
        """ Return neigboring reachable Vec2D list of nodes to node Vec2D n"""
        neighbors = [n + d for d in self.DIRS]
        filtered = list(filter(lambda neighbor: not self._is_collide(neighbor, grid), neighbors))
        return filtered

    def _AStar(self, grid, start, goal):
        """AStar to quickly solve grid. 'n' refers to a node in the maze.  
            @returns: Vec2D list of shortest path or None if unsolvable
        """
        h = lambda n: max(abs(goal - n))  # Heuristic function "bird flight with diagonal movement
        # h = lambda n: abs(goal - n).sum  # Cartesian movement (proper planning)

        open_set = {start}  # Unvisited nodes
        came_from = {}  # Path tracking

        g_score = defaultdict(lambda: sys.maxsize)  # Cost of reaching n from start
        g_score[start] = 0

        f_score = defaultdict(lambda: sys.maxsize)  # g_score[n] + h(n)
        f_score[start] = h(start)

        while open_set:
            current = min(open_set, key=f_score.get)  # minimal f_score of n in open_set, i.e. best guess
            if current == goal:
                return self._reconstruct_path(came_from, current)  # Shortest path

            open_set.discard(current)
            for neighbor in self._get_neighbors(current, grid):
                tentative_gscore = g_score[current] + 1  # gScore[current] + d(current, neighbor) (d = 1)
                if tentative_gscore < g_score[neighbor]:
                    # This path to neighbor is better than any previous one. Record it!
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_gscore
                    f_score[neighbor] = tentative_gscore + h(neighbor)
                    if not neighbor in open_set:
                        open_set.add(neighbor)
        return None

    def _reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return total_path

    

    # def visit(self, action, pos): # ValueIteration helper function
    #     """Return tuple new pos and float reward from taking int action at tuple pos (x, y)"""
    #     err_msg = f"{action!r} ({type(action)}) invalid"
    #     assert self.action_space.contains(action), err_msg
    #     pos = Vec2D(pos)

    #     reward = self.step_penalty
    #     new_pos = pos + self.DIRS[action]

    #     if not self._is_collide(new_pos, self.grid):
    #         pos = new_pos
    #         if self.grid[GOAL][new_pos.p]:
    #             reward = self.win_reward

        return pos.p, reward

    def process_input(self):
        """Process user input quit/restart/step/space"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close(True)

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.close(True)

                if event.key == pg.K_r:
                    return self.reset()

                # if event.key in MOVE:
                #     return self.step(MOVE.index(event.key))

                if event.key == pg.K_SPACE:
                    try:
                        self.space_fun(self)
                    except:
                        self.space_fun()  # For external functions
        self.keyPressed()
        				
    def keyPressed(self):
        if self.frame != CELL:
            return 
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            self.step(RIGHT)
        elif keys[pg.K_w]:
            self.step(UP)
        elif keys[pg.K_a]:
            self.step(LEFT)
        elif keys[pg.K_s]:
            self.step(DOWN)

clock = pg.time.Clock()
fps = 120
if __name__ == "__main__":
    env = PacMan(seed=9, space_fun=PacMan.test)
    env.reset()
    while True:
        clock.tick(fps)
        env.move()
        obs = env.process_input()

        # if type(obs) == tuple:  # step return
        #     s, r, done = obs
        #     if done:
        #         s = env.reset(False)
        # elif type(obs) == np.ndarray:  # reset return
        #     grid = obs

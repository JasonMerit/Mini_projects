""" GridWorld environment for RL
    Run this script for human play

    Common bugs
    - "list index out of range" => random.randint(a, b) is inclusive so replace b with b-1. 
    - Forgetting to remove prior element in grid
    - Forgetting to reset grid


    TODO
    - Curriculum friendly structure for training
    - Add passive action

    SUGGESTIONS
    - Use link cut tree if we are adding/removing walls of grid https://github.com/tyilo/link_cut_tree/blob/master/link_cut_tree.py


"""

from logging import exception
from gym import spaces
import numpy as np
import pygame as pg
import sys, random
from collections import defaultdict

CELL = 48  # Cell width TODO: Makes dependent on map_size but still global...
WHITE, GREY, BLACK = (200, 200, 200), (190, 190, 190), (20, 20, 20)
YELLOW, RED, GREEN = (150, 150, 0), (200, 0, 0), (0, 150, 0)
COLORS = [YELLOW, GREY, GREEN]  # wall, agent, goal

MOVE = [pg.K_d, pg.K_w, pg.K_a, pg.K_s,  # RIGHT, UP, LEFT, DOWN
        pg.K_e, pg.K_q, pg.K_z, pg.K_c]  # RIGHT-UP, LEFT-UP, LEFT-DOWN, RIGHT-DOWN
NUM_ENTITIES = 3
WALL, AGENT, GOAL = range(NUM_ENTITIES)

pg.init()
pg.display.set_caption('GridWorld')
pg.font.init()

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

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
        return self.y, self.x

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

    def __init__(self, grid, start, goal, max_steps, points=None):
        self.grid = grid
        self.H, self.W = grid[WALL].shape
        self.points = points
        self.screen = pg.display.set_mode([self.W * CELL, self.H * CELL])
        self.font = pg.font.Font(None, 25)
        self.disp_reset(start, goal)

        self.max_steps = max_steps
        self.step = -1  # -1, because we want to display before first step (flash logic)

    def update(self, pos, before=None):
        if before:
            self.grid[AGENT][before.p] = 0 
            rect = self._draw_rect(before, BLACK)  # Draw prior object (assume never leaving goal)
            pg.display.update(rect)
            if self.points and before in self.points:  # Draw points
                rect = self._draw_circle(before, CELL >> 3)
                pg.display.update(rect)

        self.grid[AGENT][pos.p] = 1  
        rect = self._draw_circle(pos, CELL >> 2)  # x >> 2 = x / 4     # Draw agent

        # Game over
        self.step += 1
        if pos == self.goal:
            self.flash(GREEN)
            self.step = -1
        elif self.step == self.max_steps:
            self.flash(RED)
            self.step = -1
            # pg.display.quit()
            # del self
        
        pg.display.update(rect)

    def disp_reset(self, start, goal): #TODO set agent to start position on given env.
        self.goal = goal
        self.screen.fill(GREY)
        
        for x in range(self.W):
            for y in range(self.H):
                pos = Vec2D(x, y)
                color = YELLOW if self.grid[WALL][pos.p] else BLACK
                self._draw_rect(pos, color)
        
        self._draw_rect(goal, GREEN)          
        if self.points:
            self.draw_points()
        self._draw_circle(start, CELL >> 2)  

        pg.display.flip()

    def draw_policy(self, actions):
        pass

    def draw_points(self):
        for p in self.points:
            self._draw_circle(p, CELL >> 3)  # x >> 3 = x / 8
    
    def _get_color(self, pos):  # Note used currently
        for i in range(NUM_ENTITIES):
            if self.grid[i][pos.p]:
                return COLORS[i]
        return BLACK

    def _draw_rect(self, pos, color):
        pos = pos * CELL + Vec2D(1, 1)
        rect = pg.Rect(pos.v, (CELL - 2, CELL - 2))
        pg.draw.rect(self.screen, color, rect, 0)
        return rect

    def _draw_circle(self, pos, r):
        center = (pos + Vec2D(0.5, 0.5)) * CELL
        return pg.draw.circle(self.screen, GREY, center.v, r)


    def flash(self, color=GREEN):
        self.screen.fill(color)
        pg.display.flip()
        pg.time.wait(50)
        # self.disp_reset(self.start, self.goal)
    
    
    # ---- Value iteration ----
    def update_values(self, V):
        """Remove game elements and impose nparray V over grid"""
        assert self.grid[0].shape == V.shape, f"Array dimensions don't match (grid) \
                                            {self.grid.shape} != {V.shape} (V)"
        V = np.round(V, 2)  # Remove decimals up to 2 points
        # normalize V to [0, 1]
        # V_norm = (V - V.min()) / (V.max() - V.min())
        V_norm = V
        for x in range(self.W):
            for y in range(self.H):
                if self.grid[WALL][y, x]:
                    continue
                pos = Vec2D(x, y)
                if self.grid[GOAL][y, x]:
                    self._draw_rect(pos, GREEN)
                    continue
                if self.grid[AGENT][y, x]:
                    self._draw_circle(pos, CELL >> 2)
                    continue
                text = self.font.render(str(V[pos.p]), True, WHITE)
                try:
                    color = [x + V_norm[pos.p] * (y - x) for x, y in zip(BLACK, GREEN)]  # Color gradient
                except:
                    color = BLACK
                self._draw_rect(pos, color)
                self._draw_text(text, pos)

        pg.display.flip()

    def _draw_text(self, text, pos):
        center = (pos + Vec2D(0.5, 0.5)) * CELL
        text_rect = text.get_rect(center=center.v)
        self.screen.blit(text, text_rect)


class GridWorld():
    """Gridworld environment following OpenAI functionality

    Helper class Vec2D alleviates syntax strain from numpy indexing by (y, x),
    while pygame instances rects for drawing by (x, y). All rendering is performed
    in helper class Display. 

    Methods:
    reset()         -- Reset all class properties to initial values and generate new grid.
    step(action)    -- Take action in environment and return new grid, reward and done.
    sample()        -- Return a random action. Equivalent to action_space.sample(), but returns non-termination actions.
    close()         -- Quit pygame and if this script is main, terminates script.
    process_input() -- Process input using pygame.

    Important variables:
    grid         -- 3d nparray of hot encoded map with nominal values {0:Wall, 1:Agent, 2:Goal), e.g. grid[WALL][2, 1] = 1 if wall. 
    done         -- bool flag of game termination state.
    action_space -- Discrete of {0:Right, 1:Right-Up, 2:Up, 3:Left-Up, 4:Left, 5:Left-Down, 6:Down, 7:Right-Down}.
    pos          -- Vec2D of current position of agent.
    goal         -- Vec2D of goal position.
    """

    def test(self):
        pass

    def __init__(self, map=(5, 10, 5, 10), wall_pct=0.7, rewards=(0.0, 1.0), 
                seed=None, non_diag=False, max_steps=4, space_fun=None):
        """
        Keyword arguments:
        map_size  -- int tuple of (min_x, max_x, min_y, max_y) constraining map size.
        wall_pct  -- float of wall density in grid.
        resetter  -- int of {0:Grid, 1:Start, 2:Goal, 3:Start and Goal} of how to reset environment.
        rewards   -- float tuple (step_penality, win_reward) rewards given after step.
        seed      -- int seed for grid generation and action sampling.
        space_fun -- function to execute. Used for debugging. 
        """
        assert(wall_pct >= 0 and wall_pct < 1), "wall_pct must be between 0 and 1"

        self.map_size = map
        self.wall_pct = wall_pct
        self.max_steps = max_steps

        self.level = 0 # change difficult externally
        self.difficulty = 0# change map size and wall density
        self.display = None

        if seed != None:
            random.seed(seed)
        self.space_fun = space_fun if space_fun else lambda: None

        self.DIRS = [Vec2D(1, 0), Vec2D(0, -1),  # RIGHT, UP
                     Vec2D(-1, 0), Vec2D(0, 1)]  # LEFT, DOWN
        if not non_diag:
            self.DIRS += [Vec2D(1, -1), Vec2D(-1,-1),  # RIGHT-UP, LEFT-UP
                          Vec2D(-1, 1), Vec2D(1 , 1)]  # LEFT-DOWN, RIGHT-DOWN

        self.action_space = spaces.Discrete(len(self.DIRS)) # observation_space defined in reset()
        self.step_penalty, self.win_reward = rewards
        self.reach = None  # Tiles that reach goal - for resetting
        self.last_pos = None  # Last position of agent - for rendering
        self.step_count = 0  # Number of steps taken

        # Define reset function

        self.reset_grid()

    def level_up(self):
        # clasp level around 0 - 2 (exlude 3 as we don't want to resize the map)
        level = self.level + 1
        self.level = max(min(level, 4), 0)
    
    def level_down(self):
        level = self.level - 1
        self.level = max(min(level, 4), 0)
    
    def set_level(self, level):
        self.level = max(min(level, 4), 0)

    def reset(self):
        self.step_count = 0
        self.last_pos = None
        
        if self.level == 0: # Reset to original map (fetus)
            self.grid[AGENT][self.pos.p] = 0
            self.pos = self.start
            self.grid[AGENT][self.start.p] = 1

            return self.grid
            
        if self.level == 1: # reset start (baby) - too easy? Sure, but learn to walk first
            self.grid[AGENT][self.pos.p] = 0
            self.pos = self._random_tile(self.grid[WALL]+self.grid[GOAL], self.reach)[0]
            self.start = self.pos
            self.grid[AGENT][self.pos.p] = 1

            return self.grid
        
        if self.level == 2: # reset goal (toddler) 
            self.grid[GOAL][self.goal.p] = 0
            self.goal = self._random_tile(self.grid[WALL]+self.grid[AGENT], self.reach)[0]
            self.grid[GOAL][self.goal.p] = 1

            return self.grid


        if self.level == 3:  # reset start/goal (teen)
            
            self.grid[AGENT][self.pos.p] = 0
            self.grid[GOAL][self.goal.p] = 0

            while True:  # Create grid
                start, goal = self._random_tile(self.grid[WALL], n=2)
                if reach := self._dfs_reaches(self.grid[WALL], start, goal):
                    break

            self.reach = reach
            self.pos, self.goal = start, goal
            self.start = self.pos
            self.grid[AGENT][self.pos.p] = 1
            self.grid[GOAL][self.goal.p] = 1

            return self.grid

        if self.level == 4:
            return self.reset_grid()

        
        # if self.level == 4: # reset grid (adult)
        #     self.difficulty += 1
        #     add = self.difficulty // 100
        #     W = self.W + add  # every 100 steps, increase width by 1
        #     H = self.H + add  # every 100 steps, increase height by 1

        #     wall_pct = self.wall_pct * sigmoid(self.difficulty/1000)  

        #     self.last_pos = None
        #     self.grid, start, goal, self.reach = self._generate_grid(wall_pct)
        #     self.observation_space = spaces.Box(0, 1, shape=self.grid.shape, dtype=int)
        #     self.start = start
        #     self.pos = start
        #     self.goal = goal

        #     return self.grid


    def reset_grid(self):
        """Generate new grid 0"""
        self.last_pos = None
        self.grid, start, goal, self.reach = self._generate_grid(self.wall_pct)
        self.observation_space = spaces.Box(0, 1, shape=self.grid.shape, dtype=int)
        self.start = start
        self.pos = start
        self.goal = goal

        return self.grid

    def reset_to(self, grid):
        """Set environment to ndarray grid"""
        self.grid = self._one_hot_encode(grid)
        self.H, self.W = grid.shape
        self.map_size = (self.W, self.W, self.H, self.H)  # For genarating new grids
        self.observation_space = spaces.Box(0, 1, shape=self.grid.shape, dtype=int)
        self.pos = Vec2D(tuple(*np.argwhere(self.grid[AGENT].T)))
        self.start = self.pos
        self.goal = Vec2D(tuple(*np.argwhere(self.grid[GOAL].T)))
        self.reach = self._dfs_reaches(self.grid[WALL], self.pos, self.goal)

        return self.grid

    """Environment functions"""
    def step(self, action):
        """Take action and return new state grid, reward and done 
        Mutate pos, grid."""
        # Let terminate = done to reset env after failure
        err_msg = f"{action!r} ({type(action)}) invalid"
        assert self.action_space.contains(action), err_msg

        self.step_count += 1
        reward = self.step_penalty  # Default reward
        new_pos = self.pos + self.DIRS[action]

        terminate = self._is_collide(new_pos, self.grid[WALL])
        done = False
        if not terminate:
            if self.grid[GOAL][new_pos.p]:
                terminate = True
                done = True
                reward = self.win_reward

            # Update grid
            self.grid[AGENT][self.pos.p] = 0
            self.grid[AGENT][new_pos.p] = 1

            self.last_pos = self.pos  # For rendering
            self.pos = new_pos

        if self.step_count > self.max_steps:
            done = True # give up

        return self.grid, reward, done

    def sample(self):
        """Return random action in action_space"""
        # if legal_only:
        legal_actions = list(filter(lambda dir: not self._is_collide(self.pos + dir, self.grid[WALL]), self.DIRS))
        action = random.choice(legal_actions)
        return self.DIRS.index(action)
        # return random.randint(0, len(self.DIRS)-1)

    def render(self):
        """Render grid to pygame display. User should call this after reset and step."""
        if self.last_pos is None or self.display is None:
            self.display = Display(self.grid, self.pos, self.goal, self.max_steps, self.reach)
        else:
            self.display.update(self.pos, self.last_pos)
    
    def close_display(self):
        """Close pygame display"""
        self.display = None
        pg.display.quit()

    def close(self, total=False):
        """Quit pygame and script if total is flagged true."""
        pg.display.quit()
        pg.quit()
        if total: sys.exit()

    """Helper functions"""
    def _generate_grid(self, wall_pct=0.5):
        """
        Generate 100 grids sprinkled by wall_pct argument density.
        Raise error after 100 iterations of unsolvable grids,
        otherwise returns nparray grid and starting position tuple
        """

        while True:
            min_x, max_x, min_y, max_y = self.map_size
            self.W = random.randint(min_x, max_x)
            self.H = random.randint(min_y, max_y)

            grid = np.zeros((NUM_ENTITIES, self.H, self.W), dtype=int)

            # Sprinkle in walls 
            grid[WALL] = np.random.binomial(1, wall_pct, size=(self.H, self.W))
            if grid[WALL].sum() > self.W * self.H - 2:  # Avoid infinite loop
                continue

            start, goal = self._random_tile(grid[WALL], n=2)
            grid[AGENT][start.p] = 1
            grid[GOAL][goal.p] = 1

            if reach := self._dfs_reaches(grid[WALL], start, goal):
                return grid, start, goal, reach

        raise RuntimeError("Failed to create map after 100 tries! Your map"
                           "size is probably too small")

    def _random_tile(self, obstacles, stack=[], n=1):
        """Return random unique Vec2D tile"""
        if stack:
            assert(len(stack) >= n)

        def rand(): return np.random.choice(stack) if stack else Vec2D(random.randint(0, self.W-1), random.randint(0, self.H-1))
        rs = set()
        while len(rs) != n:
            r = rand()
            if not obstacles[r.p]:
                rs.add(r)
            
        return list(rs)
    
    def _one_hot_encode(self, grid):
        """One hot encode ndarray grid"""
        shape = (grid.max(),) + grid.shape
        hot = np.zeros(shape)

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i, j]:  # Skip zeroes
                    hot[grid[i, j]-1, i, j] = 1
        return hot

    def _get_neighbors(self, n, walls):
        """ Return neigboring reachable Vec2D list of nodes to node Vec2D n"""
        neighbors = [n + d for d in self.DIRS]
        filtered = list(filter(lambda neighbor: not self._is_collide(neighbor, walls), neighbors))
        return filtered

    def _dfs_reaches(self, walls, start, goal):
        """Return list of points that reach goal"""
        solvable = False
        stack = [start]
        visited = set()
        reach = []
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                reach.append(node)
                stack += self._get_neighbors(node, walls)
                if node == goal:
                    solvable = True
        if solvable:
            return reach

    def _is_collide(self, pos, walls):
        """Returns if new_pos Vec2D is out of bounds of nparray grid or colliding with wall"""
        return pos.x < 0 or pos.x >= self.W or pos.y < 0 or pos.y >= self.H or walls[pos.p]



    """ Value iteration functions """
    def visit(self, action, pos):
        """Return tuple new pos and float reward from taking int action at tuple pos (x, y)"""
        err_msg = f"{action!r} ({type(action)}) invalid"
        assert self.action_space.contains(action), err_msg
        pos = Vec2D(pos)

        reward = self.step_penalty
        new_pos = pos + self.DIRS[action]

        if not self._is_collide(new_pos, self.grid[WALL]):
            pos = new_pos
            if self.grid[GOAL][new_pos.p]:
                reward = self.win_reward

        return pos.p, reward

    def display_values(self, V):
        self.display.update_values(V)

    def set_pos(self, x, y):
        self.grid[AGENT][self.pos.p] = 0
        self.pos = Vec2D(x, y)
        self.grid[AGENT][self.pos.p] = 1

    """ Junk functions not relevant anymore"""
    def _AStar(self, grid, start, goal):
        """AStar to quickly solve grid. 'n' refers to a node in the maze.  
            @returns: Vec2D list of shortest path or None if unsolvable
        """
        # TODO extend to find all paths to goal
        h = lambda n: max(abs(goal - n))  # Heuristic function "bird flight with diagonal movement
        # h = lambda n: abs(goal - n).sum  # Cartesian movement (proper planning) - both are appropiate for this problem

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
    
    def process_input(self):
        """Process user input quit/restart/step/space"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close(True)

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.close(True)

                if event.key == pg.K_r:
                    if pg.key.get_pressed()[pg.K_LCTRL]:
                        obs = self.reset_grid()
                        env.render()
                        return obs
                    obs = self.reset()
                    env.render()
                    return obs

                if event.key in MOVE:
                    if (action := MOVE.index(event.key)) < len(self.DIRS):
                        obs = self.step(action)
                        env.render()
                        return obs

                if event.key == pg.K_SPACE:
                    try:
                        self.space_fun(self)
                    except:
                        self.space_fun()  # For external functions
                
def test(env):
    clock = pg.time.Clock()
    env.rendering = False
    for _ in range(10):
        env.process_input()
        env.reset()
        # clock.tick(60)
    env.rendering = True




if __name__ == "__main__":
    clock = pg.time.Clock()
    clock.tick(30)
    env = GridWorld(wall_pct=0.4, map=(7, 7, 7, 7), non_diag=False, max_steps = 10, space_fun=GridWorld.test)
    env.render()
    env.set_level(3)
    # test(env)
    while True:
        clock.tick(30)
        obs = env.process_input()  # step is called here
        if type(obs) == tuple:  # step return
            s, r, done = obs
            if done:
                s = env.reset()
                env.render()

# First initililize env
# then reset()
# then s, r, done =  step(action)
# if done, s = reset()

 
# env.set_level(x)
# 0) Reset to original map
# 1) Random start
# 2) Random goal
# 3) Random start and goal
# 4) Random start, goal and walls
# 5) Random everything, including map size
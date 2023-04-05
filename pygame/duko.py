# cd C:\Users\Jason\Documents\Mini_projects\pygame
# python duko.py
"""
TODO:
- Create proper starting configuration
- Press 1-2-3-4-5 for choosing dimension size (4, 6, 8, 10, 12)
- Change pos = (x, y) to pos = (r, c) in Duko and Display
- Aestetics
    - Fix tile offset
    - Add outline to font (write a congrats surface)
    - Cursor outline
    - Shadowed locks on fixed tiles upon press
    - Thomas shadows (buggy for higher dims)

"""

import sys, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
from pygame import gfxdraw
import numpy as np
import random, time

class Display():

    WHITE, BLACK, GREY = (244, 244, 244), (22, 22, 22), (52, 52, 52)
    RED, GREEN, BLUE = (200, 20, 20), (100, 200, 20), (255, 100, 0)
    ORANGE, YELLOW, PURPLE = (0, 156, 255), (255, 255, 0), (128, 0, 255)
    COLORS = [GREY, ORANGE, BLUE]
    SHADES = [None, (0, 130, 220), (220, 50, 0)]

    pg.font.init()
    font_big = pg.font.SysFont("calibri", 50, True)
    font_med = pg.font.SysFont("calibri", 30, True)

    

    def __init__(self, grid, is_player):
        self.dim = len(grid)
        self.SIZE = 480 # divisible by 4, 6, 8, 10, 12
        self.size = self.SIZE // self.dim
        self.is_player = is_player

        self.screen = pg.display.set_mode((self.SIZE, self.SIZE))
        pg.display.set_caption("Duko")

        self.screen_grid = pg.Surface((self.SIZE, self.SIZE))
        self.screen_cursor = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)

        self.surf_cursor, self.surf_tiles, self.surf_menu, self.surf_congratz = self.create_surfaces()

        self.reset(grid)
    
    def create_surfaces(self):
        size = np.array([self.size, self.size])
        offset =  size // 2
        cursor_size = 20 - self.dim

        cursor = pg.Surface(size, pg.SRCALPHA) 
        gfxdraw.aacircle(cursor, *offset, cursor_size + 2, self.BLACK)
        gfxdraw.filled_circle(cursor, *offset, cursor_size + 2, self.BLACK)
        gfxdraw.aacircle(cursor, *offset, cursor_size, self.WHITE)
        gfxdraw.filled_circle(cursor, *offset, cursor_size, self.WHITE)

        tiles = []
        tile_rect = (0, 0, self.size - 2, self.size - 2)
        # w = self.size - 10
        # h = self.size // 12
        # shade_horiz = (self.size // 2 - w // 2, self.size - h - 5, w, h)
        # shade_verti = (h - 5, self.size // 2 - w // 2, h, w)
        k = self.size // 12; c = k // 2; t = c // 2
        points = [(c, c), (k, k), (k, self.size-k-t),   # Odd sizes
                (self.size-k, self.size-k-t), (self.size-c, self.size-c-t), (c, self.size-c-t)]

        for i in range(3):
            tile = pg.Surface(size, pg.SRCALPHA)
            pg.draw.rect(tile, self.COLORS[i], tile_rect, border_radius=3)
            
            # Shades            
            if i > 0:
                # pg.draw.rect(tile, self.SHADES[i], shade_horiz, border_radius=3)
                # pg.draw.rect(tile, self.SHADES[i], shade_verti, border_radius=3)
                pg.draw.polygon(tile, self.SHADES[i], points)

            tiles.append(tile)
        
        pos_big = (self.SIZE // 2, self.SIZE * 3 // 9)
        pos_med = (self.SIZE // 2, self.SIZE * 4 // 9)
        
        menu = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        menu.fill(self.BLACK + (200,))
        self.outline_text(menu, "Duko", pos_big)
        self.outline_text(menu, "Press any key to continue", pos_med, self.font_med)

        congratz = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        self.outline_text(congratz, "Complete!", pos_big)
        self.outline_text(congratz, "Press R to restart", pos_med, self.font_med)

        return cursor, tiles, menu, congratz

    def reset(self, grid, pos=(0, 0)):
        self._draw_grid(grid)
        if self.is_player:
            self.draw_cursor(np.array(pos))
        else:
            self.frames = [self.screen.copy()]
            self.frame = 0
            pg.display.set_caption(f"Duko - {self.frame+1}/{len(self.frames)}")
            pg.display.update()
    
    def next(self):
        if self.frame == len(self.frames)-1: return
        self.frame += 1
        pg.display.set_caption(f"Duko - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()

    def back(self):
        if self.frame == 0: return
        self.frame -= 1
        pg.display.set_caption(f"Duko - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()

    def first(self):
        self.frame = 0
        pg.display.set_caption(f"Duko - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()

    def last(self):
        self.frame = len(self.frames)-1
        pg.display.set_caption(f"Duko - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()
    
    def add_frame(self, grid):
        """Add frame with tile at pos with color"""
        self._draw_grid(grid)
        self.frames.append(self.screen.copy())
        self.frame += 1
        pg.display.set_caption(f"Duko - {self.frame+1}/{len(self.frames)}")

    def update_tile(self, pos, color):
        """Update tile at pos with color"""
        pos = np.array(pos)
        self._draw_tile(pos, color)
        pg.display.update()

    def _draw_grid(self, grid):
        self.screen_grid.fill(self.BLACK)

        for i in range(self.dim):
            for j in range(self.dim):
                x, y = i * self.size + 1, j * self.size + 1
                self.screen_grid.blit(self.surf_tiles[grid[j][i]], (x, y))

        self.screen.blit(self.screen_grid, (0, 0))
    
    def _draw_tile(self, pos, color):
        x, y = pos * self.size + 1
        self.screen_grid.blit(self.surf_tiles[color], (x, y))
        self.screen.blit(self.screen_grid, (0, 0))
    
    def draw_cursor(self, pos: np.array):
        pos *= self.size

        self.screen_cursor.fill((0, 0, 0,0))
        self.screen_cursor.blit(self.surf_cursor, pos)

        self.screen.blit(self.screen_grid, (0, 0))  # Draw grid to erase cursor
        self.screen.blit(self.screen_cursor, (0, 0))
        pg.display.update()
    
    _circle_cache = {}
    def _circlepoints(self, r):
        r = int(round(r))
        if r in self._circle_cache:
            return self._circle_cache[r]
        x, y, e = r, 0, 1 - r
        self._circle_cache[r] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points
    
    def outline_text(self, SURFACE, text, pos, font=font_big, color=WHITE, ocolor=BLACK, opx=3):
        surface = font.render(text, True, color).convert_alpha()
        w = surface.get_width() + 2 * opx 
        h = font.get_height()

        surf_outlilne = pg.Surface((w, h + 2 * opx)).convert_alpha()
        surf_outlilne.fill((0, 0, 0, 0))

        surf = surf_outlilne.copy()

        surf_outlilne.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in self._circlepoints(opx):
            surf.blit(surf_outlilne, (dx + opx, dy + opx))

        surf.blit(surface, (opx, opx))
        offset_pos = (pos[0] - w // 2, pos[1] - h // 2)
        SURFACE.blit(surf, offset_pos)
        # return surf
    
    def congrats(self):
        self.screen.blit(self.surf_congratz, (0,0))
        pg.display.update()

    def show_menu(self):
        self.screen.blit(self.surf_menu, (0, 0))
        pg.display.update()

class Duko():
    pos = [0, 0]

    def __init__(self, dim=4, render=True, is_player=True, grid=None):
        self.dim = dim

        goal = dim // 2 + dim  # Used to check if puzzle is complete
        self.goal = np.ones(self.dim, dtype=np.int8) * goal

        if grid is None:
            self.grid_init, self.fixed = self._generate_grid()
        else:
            self.grid_init = grid
            self.fixed = list(zip(*np.nonzero(grid.T))) # Transpose to get x, y

        self.grid = self.grid_init.copy()
        self.display = Display(self.grid, is_player) if render else None
            
    def reset(self):
        """Reset grid and cursor to initial state"""
        self.grid = self.grid_init.copy()
        self.pos = [0, 0]
        if self.display:
            self.display.reset(self.grid, self.pos)
    
    # Sudoku generator from 
    # https://stackoverflow.com/questions/6924216/how-to-generate-sudoku-boards-with-unique-solutions
    def _generate_grid(self):
        """Generate a grid with a unique solution"""
        # 1) Start with an empty board.
        # grid = np.zeros((self.dim, self.dim), dtype=np.int8)
        grid = np.random.randint(0, 3, size=(self.dim, self.dim))
        free_tiles = [(i, j) for i in range(self.dim) for j in range(self.dim)]
        # grid = np.array([[0 for _ in range(dim)] for _ in range(dim)], dtype=np.int8)
        # grid = np.array([[0, 0, 0, 0], [0, 1, 0, 1], [0, 0, 0, 2], [0, 1, 0, 0]], dtype=np.int8)
        # grid = np.array([[0, 0, 0, 0], [0, 1, 0, 1], [0, 0, 2, 0], [0, 1, 0, 0]], dtype=np.int8)
        # grid = np.random.randint(0, 3, (self.dim, self.dim), dtype=np.int8)

        # 2) Add a valid random color at one of the random free cells.


        # 3) Backtrack solver to check if there is a unique solution.

        # 4) Repeat 2) until unique solution.
        # for _ in range(4):
        #     x, y = np.random.randint(0, self.dim, 2)
        #     grid[x, y] = np.random.randint(1, 3)
        
        fixed = list(zip(*np.nonzero(grid.T))) # Transpose to get x, y
        return grid, fixed
        
    def run(self):
        if not self.display:
            raise Exception("Can't run without rendering")
        
        while True:
            self.process_input()
    
    def menu(self):
        self.display.show_menu()
        while True:
            event = pg.event.wait()
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()
                else:
                    break
        self.display._draw_grid(self.grid)
        pg.display.update()
    
    def process_input(self):
        """Process input from keygrid.
        - Up, down, left, right to move cursor
        - Space to toggle tile
        - Escape to quit
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.menu()
                
                if event.key == pg.K_r:
                    self.reset()

                if event.key == pg.K_UP:
                    self.move("up")
                elif event.key == pg.K_DOWN:
                    self.move("down")
                elif event.key == pg.K_LEFT:
                    self.move("left")
                elif event.key == pg.K_RIGHT:
                    self.move("right")

                if event.key == pg.K_SPACE:
                    self.action()
    
    def move(self, direction):
        if direction == "up":
            if self.pos[1] == 0:
                self.pos[1] = self.dim - 1
            else: 
                self.pos[1] -= 1
        elif direction == "down":
            if self.pos[1] == self.dim - 1:
                self.pos[1] = 0
            else:
                self.pos[1] += 1
        elif direction == "left":
            if self.pos[0] == 0:
                self.pos[0] = self.dim - 1
            else:
                self.pos[0] -= 1
        elif direction == "right":
            if self.pos[0] == self.dim - 1:
                self.pos[0] = 0
            else:
                self.pos[0] += 1
        
        if self.display:
            self.display.draw_cursor(np.array(self.pos))
    
    def action(self):
        """Toggle tile at cursor position"""
        
        if tuple(self.pos) in self.fixed:
            return # TODO: Draw shadowed locks on fixed tiles
        
        x, y = self.pos
        self.grid[y, x] = (self.grid[y, x] + 1) % 3
        self.display.update_tile(self.pos, self.grid[y, x])
        self.display.draw_cursor(np.array(self.pos))

        if self.is_complete():
            self.win()
    
    def is_complete(self):
        """Returns true if the puzzle is complete:
        - Each row and column have equal number of non-zero entrees.
        - All rows and columns are different.
        """
        A = self.grid

        # Check if all rows and columns have equal number of non-zero entrees
        if 0 in A \
            or not np.all(np.sum(A, axis=0) == self.goal) \
            or not np.all(np.sum(A, axis=1) == self.goal):
            return False

        # Check if all rows and columns are different
        for i in range(self.dim):
            for j in range(i, self.dim):
                if i != j:
                    if np.all(A[i] == A[j]) or np.all(A[:, i] == A[:, j]):
                        return False
        return True
        
    def win(self):
        """Congratulate player and wait for space to be pressed"""
        if self.display:
            self.display.congrats()

        # Wait until space is pressed   
        while True:
            event = pg.event.wait()
            if event.type == pg.QUIT:
                quit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    quit()

                if event.key == pg.K_SPACE:
                    self.reset()
                    return

class Solver():
    """
    Solver for Duko puzzles.
    """
    done_cols, done_rows = set(), set()  # assumming no complete
    done = False
    FLIP = np.array([0, 2, 1])

    def __init__(self, game: Duko):
        self.game = game
        self.display = game.display
        self.grid = game.grid.astype(int)
        self.dim = len(self.grid)
        self.dim_2 = self.dim // 2
        self.DIGITS = set(range(self.dim))
        
        self.solve()

        while True:
            self.process_input()
        
    def reset(self, new_grid=None):
        self.done_cols, self.done_rows = set(), set()
        self.grid = self.game.grid.astype(int) if new_grid is None else new_grid
        self.display.reset(self.grid)
        self.done = False
        pg.display.update()

    def process_input(self):
        """Process input from keygrid.
        - Up, down, left, right to move cursor
        - Space to toggle tile
        - Escape to quit
        """
        event = pg.event.wait()
        if event.type == pg.QUIT:
            sys.exit()
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.game.menu()
                
            if event.key == pg.K_r:
                self.reset()
            
            if event.key == pg.K_SPACE:
                print(self.done_rows)

            if event.key in (pg.K_1, pg.K_2, pg.K_3):
                if self.done:
                    return
                
                if event.key == pg.K_1:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.subsequent(self.grid.T, self.done_cols)
                    else:
                        self.subsequent(self.grid, self.done_rows)                    
                    pg.display.flip()
                
                elif event.key == pg.K_2:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.equal_count(self.grid.T, self.done_cols)
                    else:
                        self.equal_count(self.grid, self.done_rows)
                    pg.display.flip()
                
                elif event.key == pg.K_3:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.unique(self.grid.T, self.done_cols)
                    else:
                        self.unique(self.grid, self.done_rows)
                    pg.display.flip()

                if 0 not in self.grid:
                    self.display.congrats()
                    self.done = True
            
            # Frame navigation
            if event.key == pg.K_LEFT:
                self.display.back()
                # display.first() if pg.key.get_mods() & pg.KMOD_SHIFT else display.back()

            elif event.key == pg.K_RIGHT:
                self.display.next()
                # display.last() if pg.key.get_mods() & pg.KMOD_SHIFT else display.next()

    def solve(self):
        """Solve the puzzle"""
        for _ in range(100):
            self.subsequent(self.grid, self.done_rows)
            self.subsequent(self.grid.T, self.done_cols)
            self.equal_count(self.grid, self.done_rows)
            self.equal_count(self.grid.T, self.done_cols)
            self.unique(self.grid, self.done_rows)
            self.unique(self.grid.T, self.done_cols)
            if 0 not in self.grid:
                break
        else:
            print("Not solved")
        pg.display.flip()

    def subsequent(self, rows, done: set):
        """Checks for subsequent 1s and 2s in rows and cols.
        Remember to check for terminal state after calling this function.
        Returns True if any changes are made."""
        changed = False

        for r, row in enumerate(rows):
            for i in range(len(row)-1):
                if row[i] == row[i+1] != 0:
                    if i < self.dim-2 and rows[r, i+2] == 0: # if next is empty
                        rows[r, i+2] = self.FLIP[row[i]]
                        self.display.add_frame(self.grid)
                        changed = True

                    if i > 0 and rows[r, i-1] == 0: # if prev is empty
                        rows[r, i-1] = self.FLIP[row[i]]
                        self.display.add_frame(self.grid)
                        changed = True
                
            for i in range(len(row) - 2):
                if row[i] == row[i+2] != 0 and row[i+1] == 0:
                    rows[r, i+1] = self.FLIP[row[i]]
                    self.display.add_frame(self.grid)
                    changed = True

        if changed: 
            done.update(np.where(np.all(rows != 0, axis=1))[0])

        return changed

    def equal_count(self, rows, done: set):
        """Checks for equal count of 1s and 2s.
        Remember to check for terminal state after calling this function.
        param rows: 2D array (transposed to check cols)
        param done: set of rows or cols that are already done
        Returns True if any changes are made."""
        changed = False

        for r in (self.DIGITS - done):
            row = rows[r]
            
            if np.sum(row == 1) == self.dim_2:
                rows[r, np.where(row == 0)[0]] = 2
                
                self.display.add_frame(self.grid)
                done.add(r)
                changed = True

            elif np.sum(row == 2) == self.dim_2:
                rows[r, np.where(row == 0)[0]] = 1

                self.display.add_frame(self.grid)
                done.add(r)
                changed = True

        return changed

    def unique(self, rows, done: set):
        """Checks for unique rows and cols.
        Remember to check for terminal state after calling this function.
        Returns True if any changes are made."""
        changed = False

        # Find rows containing exacty two gaps
        gapped_rows_indx = np.where(np.sum(rows == 0, axis=1) == 2)[0]  # [2 3]
        candidates = rows[gapped_rows_indx]  # [[2 1 0 0], [1 0 0 2]]
        keks = rows[list(done)]  # [[2 1 1 2]]

        # Compare each candidate with other complete rows
        for i, candy in enumerate(candidates):
            # Find index of colored tiles
            idx = np.where(candy != 0)[0]  # [0 1]
            for kek in keks:
                if np.array_equal(kek[idx], candy[idx]):
                    # Replace the two gaps with complementary colors
                    gaps = np.where(candy == 0)[0]  # [2, 3]
                    rows[gapped_rows_indx[i], gaps] = self.FLIP[kek[gaps]]
                    self.display.add_frame(self.grid)

                    done.add(gapped_rows_indx[i])
                    changed = True
        
        return changed

class Generator():
    pass

# ---------- Reinforcement learning ----------------------- #
# Tabular q-learning where loosing is when filled is incomplete
# Monte Carlo learning 
from gym import spaces, Env

class EnvironmentDuko(Env):
    DT = 0.04
    def __init__(self, game):
        self.game = game
        dim = game.dim
        self.action_space = spaces.Box(low=np.array([0, 0, 1]), high=np.array([dim-1, dim-1, 2]), 
                                                                        shape=(3,), dtype=int)
        self.observation_space = spaces.Box(low=0, high=2, shape=(dim,dim), dtype=np.int8)
        self.reward_range = (0, 1)
    
    def reset(self):
        self.game.reset()
        return self.game.grid

    def reset_to(self, grid):
        self.game.grid = grid
        return self.game.grid
    
    def step(self, action):
        if action not in self.action_space:
            raise Exception(f"Invalid action: {action}")
        
        x, y, a = action
        self.game.grid[y, x] = a
        done = self.game.is_complete()
        self.render(*action)
        return self.game.grid, int(done), done
    
    def render(self, x, y, a):
        if self.game.display:
            self.game.display.update_tile(np.array([x, y]), a)
            
            self.game.process_input()
            time.sleep(self.DT)
    
    def random_action(self):
        x, y, a = self.action_space.sample()
        while (x, y) in self.game.fixed:
            x, y, a = self.action_space.sample()
        
        return np.array([x, y, a])

    def is_done(self):
        return self.game.is_complete()

    def close(self):
        pass

class Agent():
    def __init__(self, env: Env):
        self.env = env

    def policy(self, state):
        """Returns a random action"""
        return self.env.random_action()
    
    def episode(self):
        total_steps = 0
        # total_reward = 0
        state = self.env.reset()
        while True:
            action = self.policy(state)
            state, r, done = self.env.step(action)  # TODO: Doesn't work properly
            total_steps += 1
            # total_reward += r
            if done:
                print(f"Complete after {total_steps} steps!")
                break

class Test():
    """Test the game and agent based on the grid configurations in duko_configs.npz.
    The first grid in the file is a boolean array indicating if the grid is complete."""

    def __init__(self, game):
        self.env = EnvironmentDuko(game)
        self.agent = Agent(self.env)

        loaded = np.load("duko_configs.npz")
        self.grid_configs = [np.array(grid) for grid in loaded.values()]
        self.complete = self.grid_configs.pop(0)
    
    def test_all(self):
        self.test_is_complete()
        self.test_agent()
    
    def test_is_complete(self):
        for i, grid in enumerate(self.grid_configs):
            self.env.reset_to(grid)
            done = self.complete[i]
            assert(self.env.is_done() ==  done), f"grid {i} is {['NOT complete', 'complete'][done]}!\n{grid}"
    
    def test_agent(self):
        for i, grid in enumerate(self.grid_configs):
            self.env.reset_to(grid)
            done = self.complete[i]
            if done:
                print(f"grid {i} is complete!")
                continue

            self.agent.grid = grid
            print(f"Testing grid {i}...")
            self.agent.episode()
            assert(self.env.is_done()), f"grid {i} is NOT complete!\n{grid}"


if __name__ == "__main__":
        
    if len(sys.argv) == 1:
        game = Duko(4, render=True)
        game.run()
    else:
        __dim__ = 4
        if len(sys.argv) == 3:
            try:
                __dim__ = int(sys.argv[2])
            except ValueError:
                raise Exception(f"Invalid dimension: {sys.argv[2]}")
            
        setting = sys.argv[1]
        if setting in ['4', '6', '8', '10', '12']:
            game = Duko(int(setting), render=True)
            game.run()

        elif setting == "test":
            game = Duko(__dim__, render=False)
            test = Test(game)
            test.test_all()
        elif setting == "agent":
            game = Duko(__dim__, render=True)
            env = EnvironmentDuko(game)
            agent = Agent(env)
            agent.episode()
        elif setting == 'solve':
            game = Duko(__dim__, render=True, is_player=False)
            solver = Solver(game)
        else:
            raise Exception(f"Invalid setting: {setting}. Try 'test', 'agent' or 'solve")



# Mindst tre rækker/søjler med markeringer med 4 i alt
# 
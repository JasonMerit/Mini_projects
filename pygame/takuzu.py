#cd C:\Users\Jason\Documents\Mini_projects\pygame
#python takuzu.py
"""
TODO:
- When ESC is pressed copy current screen and return to it after unpasuing
- Press 1-2-3-4-5 for choosing dimension size (4, 6, 8, 10, 12)
- Complain if invalid
- Press M for hint
- Press Z for undo
- Aestetics
    - Fix tile offset
    - Add outline to font (write a congrats surface)
    - Cursor outline
    - Shadowed locks on fixed tiles upon press
    - Thomas shadows (buggy for higher dims)
    - After pausing, cursor disappears

"""

import sys, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
from pygame import gfxdraw
import numpy as np
import time

FLIP = np.array([0, 2, 1])

class Display():

    WHITE, BLACK, GREY = (244, 244, 244), (22, 22, 22), (52, 52, 52)
    RED, GREEN, BLUE = (200, 20, 20), (100, 200, 20), (255, 100, 0)
    RED, YELLOW, PURPLE = (0, 156, 255), (255, 255, 0), (128, 0, 255)
    COLORS = [GREY, BLUE, RED]
    SHADES = [None, (220, 50, 0), (0, 130, 220)]

    pg.font.init()
    font_big = pg.font.SysFont("calibri", 50, True)
    font_med = pg.font.SysFont("calibri", 30, True)

    fixed_visible = False

    def __init__(self, grid, is_player):
        self.dim = len(grid)
        self.SIZE = 480 # divisible by 4, 6, 8, 10, 12
        self.size = self.SIZE // self.dim
        self.is_player = is_player

        self.screen = pg.display.set_mode((self.SIZE, self.SIZE))
        pg.display.set_caption("Takuzu")

        self.screen_grid = pg.Surface((self.SIZE, self.SIZE))
        self.screen_cursor = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)

        self.surf_cursor, self.surf_tiles, self.surf_menu, self.surf_congratz, self.surf_fixed = self.create_surfaces()

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
        self.outline_text(menu, "Takuzu", pos_big)
        self.outline_text(menu, "Press any key to continue", pos_med, self.font_med)

        congratz = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        self.outline_text(congratz, "Complete!", pos_big)
        self.outline_text(congratz, "Press R to restart", pos_med, self.font_med)

        fixed = pg.Surface(size, pg.SRCALPHA)
        fixed.fill(self.BLACK + (200,))
        fixed.blit(self.font_big.render("M", True, self.WHITE), (self.size // 2 - 10, self.size // 2 - 20))


        return cursor, tiles, menu, congratz, fixed

    def reset(self, grid, pos=(0, 0)):
        self._draw_grid(grid)
        if self.is_player:
            self.draw_cursor(np.array(pos))
        else:
            self.frames = [self.screen.copy()]
            self.frame = 0
            pg.display.set_caption(f"Takuzu - {self.frame+1}/{len(self.frames)}")
            pg.display.update()
    
    def next(self):
        if self.frame == len(self.frames)-1: return
        self.frame += 1
        pg.display.set_caption(f"Takuzu - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()

    def back(self):
        if self.frame == 0: return
        self.frame -= 1
        pg.display.set_caption(f"Takuzu - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()

    def first(self):
        self.frame = 0
        pg.display.set_caption(f"Takuzu - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()

    def last(self):
        self.frame = len(self.frames)-1
        pg.display.set_caption(f"Takuzu - {self.frame+1}/{len(self.frames)}")
        self.screen.blit(self.frames[self.frame], (0, 0))
        pg.display.update()
    
    def add_frame(self, grid):
        """Add frame with tile at pos with color"""
        self._draw_grid(grid)
        self.frames.append(self.screen.copy())
        self.frame += 1
        pg.display.set_caption(f"Takuzu - {self.frame+1}/{len(self.frames)}")

    def update_tile(self, pos, color):
        """Update tile at pos with color"""
        pos = np.array(pos)
        self._draw_tile(pos, color)
        pg.display.update()

    def _draw_grid(self, grid):
        """Only called upon initialization and reset"""
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
    
    def show_fixed(self):
        # TODO: Draw shadowed locks on fixed tiles
        self.fixed_visible = not self.fixed_visible
        print(self.fixed_visible)

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

class Takuzu():
    pos = [0, 0]

    def __init__(self, dim=4, render=True, is_player=True, grid=None):
        self.generator = Generator()

        if grid is None:
            self.dim = dim
            self.grid, self.fixed = self._generate_grid()
        else:
            self.dim = len(grid)
            self.grid = grid
            self.fixed = list(zip(*np.nonzero(grid.T))) # Transpose to get x, y

        goal = self.dim // 2 + self.dim  # Used to check if puzzle is complete
        self.goal = np.ones(self.dim, dtype=np.int8) * goal

        self.grid_init = self.grid.copy()
        self.display = Display(self.grid, is_player) if render else None
            
    def reset(self, soft=False):
        """Reset grid and cursor to initial state.
        If soft, resets to initial state, else generates a new grid"""
        self.pos = [0, 0]

        if soft:
            self.grid = self.grid_init.copy()
        else:
            self.grid, self.fixed = self._generate_grid()
            self.grid_init = self.grid.copy()

        if self.display:
            self.display.reset(self.grid, self.pos)
        
    def valid_grid(self, grid, verbose=False):
        """Check that grid is valid."""
        dim = len(grid)
        dim_2 = dim // 2
        
        # Equal count
        if np.any(np.sum(grid == 1, axis=1) > dim_2) or np.any(np.sum(grid == 2, axis=1) > dim_2):
            print("Unequal count - rows")
            return False
        if np.any(np.sum(grid == 1, axis=0) > dim_2) or np.any(np.sum(grid == 2, axis=0) > dim_2):
            print("Unequal count - cols")
            return False
        
        # Subsequent (3 in a row)
        for r in range(dim):
            for c in range(dim):
                if c < dim-2 and grid[r, c] == grid[r, c+1] == grid[r, c+2] != 0:
                    if verbose:
                        print("Subsequent - rows")
                    return False
                if r < dim-2 and grid[r, c] == grid[r+1, c] == grid[r+2, c] != 0:
                    if verbose:
                        print("Subsequent - cols")
                    return False
        
        # Unique
        full_rows = grid[np.where(grid.all(axis=1))[0]]
        if len(full_rows) != len(np.unique(full_rows, axis=0)):
            if verbose:
                print("Duplicate - rows")
            return False
        
        full_cols = grid.T[np.where(grid.all(axis=0))[0]]
        if len(full_cols) != len(np.unique(full_cols, axis=0)):
            if verbose:
                print("Duplicate - cols")
            return False
        
        return True
        
    def _generate_grid(self):
        """Generate a grid with a unique solution"""
        grid = self.generator.generate_grid(self.dim)
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
        self.display.draw_cursor(np.array(self.pos))
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
                    # Hold down shift for hard reset
                    self.reset(1 - pg.key.get_mods() & pg.KMOD_SHIFT)

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
                if event.key == pg.K_s:
                    np.save('grid.npy', self.grid)
                    print(self.grid)
                    print("Saved grid to grid.npy")
    
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
            self.display.show_fixed()
            return 
        
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
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()

                if event.key in [pg.K_SPACE, pg.K_KP_ENTER, pg.K_r]:
                    self.reset()
                    return

class GameSolver():
    """
    Solver for Takuzu puzzles.
    """
    full_cols, full_rows = set(), set()  # assumming no complete
    done = False

    def __init__(self, game: Takuzu):
        self.game = game
        self.display = game.display
        self.grid = game.grid.astype(int)
        self.dim = len(self.grid)
        self.dim_2 = self.dim // 2
        self.DIGITS = set(range(self.dim))
        
        self.solve(self.grid)

        while True:
            self.process_input()
        
    def reset(self, new_grid=None):
        self.full_cols, self.full_rows = set(), set()
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
                print(self.full_rows)

            if event.key in (pg.K_1, pg.K_2, pg.K_3):
                if self.done:
                    return
                
                if event.key == pg.K_1:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.subsequent(self.grid.T, self.full_cols)
                    else:
                        self.subsequent(self.grid, self.full_rows)                    
                    pg.display.flip()
                
                elif event.key == pg.K_2:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.equal_count(self.grid.T, self.full_cols)
                    else:
                        self.equal_count(self.grid, self.full_rows)
                    pg.display.flip()
                
                elif event.key == pg.K_3:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.unique(self.grid.T, self.full_cols)
                    else:
                        self.unique(self.grid, self.full_rows)
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

    def solve(self, grid):
        """Solves grid in place.
        Assumes valid grid."""
        full_rows, full_cols = set(), set()
        while True:
            if self.subsequent(grid, full_rows):
                continue
            if self.subsequent(grid.T, full_cols):
                continue
            if self.equal_count(grid, full_rows):
                continue
            if self.equal_count(grid.T, full_cols):
                continue
            if self.unique(grid, full_rows):
                continue
            if self.unique(grid.T, full_cols):
                continue
            break
        pg.display.flip()

    def subsequent(self, rows, full: set):
        """Checks for subsequent 1s and 2s in rows and cols.
        Returns True if any changes are made."""
        changed = False

        for r, row in enumerate(rows):
            if r in full:
                continue

            for i in range(len(row)-1):
                if row[i] == row[i+1] != 0:
                    if i < self.dim-2 and rows[r, i+2] == 0: # if next is empty
                        rows[r, i+2] = FLIP[row[i]]
                        changed = True
                        self.display.add_frame(self.grid)
                        
                        if np.all(row != 0):
                            full.add(r)

                    if i > 0 and rows[r, i-1] == 0: # if prev is empty
                        rows[r, i-1] = FLIP[row[i]]
                        changed = True
                        self.display.add_frame(self.grid)
                        
                        if np.all(row != 0):
                            full.add(r)
                    
                if i < len(row)-2 and row[i] == row[i+2] != 0 and row[i+1] == 0:  # Gap between two same
                    rows[r, i+1] = FLIP[row[i]]
                    changed = True
                    self.display.add_frame(self.grid)
                
                    if np.all(row != 0):
                        full.add(r)

        return changed
   
    def equal_count(self, rows, full: set):
        """Checks for equal count of 1s and 2s.
        param rows: 2D array
        param full: set of rows or cols that are already full
        Returns True if any changes are made."""
        changed = False
        for r in (self.DIGITS - full):
            row = rows[r]
            if np.sum(row == 1) == self.dim_2:
                rows[r, np.where(row == 0)[0]] = 2
                full.add(r)
                changed = True
                self.display.add_frame(self.grid)

            elif np.sum(row == 2) == self.dim_2:
                rows[r, np.where(row == 0)[0]] = 1
                full.add(r)
                changed = True
                self.display.add_frame(self.grid)
        
        return changed

    def unique(self, rows, full: set):
        """Checks for unique rows and cols.
        Returns True if any changes are made."""
        changed = False

        # Find rows containing exacty two gaps
        gapped_rows_indx = np.where(np.sum(rows == 0, axis=1) == 2)[0]  # [2 3]
        candidates = rows[gapped_rows_indx]  # [[2 1 0 0], [1 0 0 2]]
        keks = rows[list(full)]  # [[2 1 1 2]]

        # Compare each candidate with other complete rows
        for i, candy in enumerate(candidates):
            # Find index of colored tiles
            idx = np.where(candy != 0)[0]  # [0 1]
            for kek in keks:
                if np.array_equal(kek[idx], candy[idx]):
                    # Replace the two gaps with complementary colors
                    gaps = np.where(candy == 0)[0]  # [2, 3]
                    rows[gapped_rows_indx[i], gaps] = FLIP[kek[gaps]]

                    full.add(gapped_rows_indx[i])
                    changed = True
                    self.display.add_frame(self.grid)
        
        return changed

class Solver():
    """General solver class.
    Helper class to Generator."""

    def solve(self, grid):
        """Returns an exhasuted grid.
        Assumes valid grid."""
        grid = grid.copy()
        while True:
            full_r = np.where(grid.all(axis=1))[0]
            full_c = np.where(grid.all(axis=0))[0]

            if self.subsequent(grid, full_r):
                continue
            if self.subsequent(grid.T, full_c):
                continue
            if self.equal_count(grid, full_r):
                continue
            if self.equal_count(grid.T, full_c):
                continue
            if self.unique(grid, full_r):
                continue
            if self.unique(grid.T, full_c):
                continue
            break
        assert(grid is not None), "Grid is None when done solving"
        return grid

    def subsequent(self, rows, full):
        """Checks for subsequent 1s and 2s in rows and cols.
        Returns True if any changes are made."""
        changed = False
        dim = len(rows)

        for r, row in enumerate(rows):
            if r in full:
                continue
            
            for i in range(len(row)-1):
                if row[i] == row[i+1] != 0:
                    if i < dim-2 and rows[r, i+2] == 0: # if next is empty
                        rows[r, i+2] = FLIP[row[i]]
                        changed = True

                    if i > 0 and rows[r, i-1] == 0: # if prev is empty
                        rows[r, i-1] = FLIP[row[i]]
                        changed = True
                    
                if i < len(row)-2 and row[i] == row[i+2] != 0 and row[i+1] == 0:  # Gap between two same
                    rows[r, i+1] = FLIP[row[i]]
                    changed = True

        return changed

    def equal_count(self, rows, full):
        """Checks for equal count of 1s and 2s.
        param rows: 2D array
        param full: set of rows or cols that are already full
        Returns True if any changes are made."""
        changed = False
        dim_2 = len(rows) // 2

        for r, row in enumerate(rows):
            if r in full:
                continue

            if np.sum(row == 1) == dim_2:
                rows[r, np.where(row == 0)[0]] = 2
                changed = True

            elif np.sum(row == 2) == dim_2:
                rows[r, np.where(row == 0)[0]] = 1
                changed = True
        
        return changed

    def unique(self, rows, full):
        """Checks for unique rows and cols.
        Returns True if any changes are made."""
        changed = False

        # Find rows containing exacty two gaps
        gapped_rows_indx = np.where(np.sum(rows == 0, axis=1) == 2)[0]  # [2 3]
        candidates = rows[gapped_rows_indx]  # [[2 1 0 0], [1 0 0 2]]
        full_rows = rows[full]  # [[2 1 1 2]]

        # Compare each candidate with other complete rows
        for i, candy in enumerate(candidates):
            # Find index of colored tiles
            idx = np.where(candy != 0)[0]  # [0 1]
            for row in full_rows:
                if np.array_equal(row[idx], candy[idx]):
                    # Replace the two gaps with complementary colors
                    gaps = np.where(candy == 0)[0]  # [2, 3]
                    rows[gapped_rows_indx[i], gaps] = FLIP[row[gaps]]

                    changed = True
        
        return changed


class Generator():
    """Generates Takuzu puzzles."""
    # https://stackoverflow.com/questions/6924216/how-to-generate-sudoku-boards-with-unique-solutions

    def __init__(self):
        self.solver = Solver()
        self.solve = self.solver.solve
    
    def valid_grid(self, grid, verbose=False):
        """Check that grid is valid."""
        dim = len(grid)
        dim_2 = dim // 2
        
        # Equal count
        if np.any(np.sum(grid == 1, axis=1) > dim_2) or np.any(np.sum(grid == 2, axis=1) > dim_2):
            if verbose:
                print("Unequal count - rows")
            return False
        if np.any(np.sum(grid == 1, axis=0) > dim_2) or np.any(np.sum(grid == 2, axis=0) > dim_2):
            if verbose:
                print("Unequal count - cols")
            return False
        
        # Subsequent (3 in a row)
        for r in range(dim):
            for c in range(dim):
                if c < dim-2 and grid[r, c] == grid[r, c+1] == grid[r, c+2] != 0:
                    if verbose:
                        print("Subsequent - rows")
                    return False
                if r < dim-2 and grid[r, c] == grid[r+1, c] == grid[r+2, c] != 0:
                    if verbose:
                        print("Subsequent - cols")
                    return False
        
        # Unique
        full_rows = grid[np.where(grid.all(axis=1))[0]]
        if len(full_rows) != len(np.unique(full_rows, axis=0)):
            if verbose:
                print("Duplicate - rows")
            return False
        
        full_cols = grid.T[np.where(grid.all(axis=0))[0]]
        if len(full_cols) != len(np.unique(full_cols, axis=0)):
            if verbose:
                print("Duplicate - cols")
            return False
        
        return True

    def generate_grid(self, dim):
        print("Generating grid...")
        new = np.zeros((dim, dim), dtype=np.int8)
        complete = self.solve_search(new)
        grid = self.subtract(complete)
        return grid
    
    def solve_search(self, grid, depth=0):
        """Solves and searches for solution.
        Returns None if no solution found or grid if solution found."""
        # print(depth)
        grid = self.solve(grid)
        assert(grid is not None), "Grid is None" 
        
        if not self.valid_grid(grid): # Invalid, so backtrack
            # print(grid,'\n')
            return None
        
        if 0 not in grid:  # Solved, so terminal state
            return grid

        # Randomly select empty cell and fill with 1 or 2
        empty_cells = list(zip(*np.where(grid == 0)))
        tile = empty_cells[np.random.randint(len(empty_cells))]
        color = np.random.randint(1, 3)

        grid[tile] = color
        result = self.solve_search(grid, depth+1)

        if result is None:
            grid[tile] = FLIP[color]
            result = self.solve_search(grid, depth+1)
        return result

    # First algorithm from stackoverflow
    def subtract(self, grid):
        """Subtracts a random tiles until one more subtraction requres solve_search."""
        
        # 2) Shuffle a list of all tiles
        tiles = [(r, c) for r in range(len(grid)) for c in range(len(grid))]
        np.random.shuffle(tiles) 

        while tiles:
            # 3) Remove a tile from grid
            tile = tiles.pop()
            color = grid[tile]
            grid[tile] = 0

            # # 4) Test uniqueness of grid
            # if not self.is_unique(grid):
            #     # 6) If not unique, add tile back and continue
            #     grid[tile] = color

            if 0 in self.solve(grid):
                grid[tile] = color

        return grid

    def is_unique(self, grid):
        """Checks if grid has unique solution."""
        return self.unique_solution(grid) == 1
    
    def unique_solution(self, grid, solved=False):
        """Solves grid.
        Returns False if multiple solutions."""

        grid = self.solve(grid)
        
        if not self.valid_grid(grid): # Invalid, so backtrack
            return False
        
        if 0 not in grid:  # Solved, so terminal state
            return 1

        # Find frist instance of 0
        zeros = np.where(grid == 0)
        tile = zeros[0][0], zeros[1][0]

        # First go left, then right
        grid[tile] = 1
        left = self.unique_solution(grid, solved)

        grid[tile] = 2
        right = self.unique_solution(grid, solved)

        if left == 2 or right == 2:
            return 2
        if left == right == 1:
            return 2
        return self.unique_solution(grid, solved)


# ---------- Reinforcement learning ----------------------- #
# Tabular q-learning where loosing is when filled is incomplete
# Monte Carlo learning 
from gym import spaces, Env

class EnvironmentTakuzu(Env):
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
    """Test the game and agent based on the grid configurations in Takuzu_configs.npz.
    The first grid in the file is a boolean array indicating if the grid is complete."""

    def __init__(self, game):
        self.env = EnvironmentTakuzu(game)
        self.agent = Agent(self.env)

        loaded = np.load("Takuzu_configs.npz")
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
        game = Takuzu(4, render=True)
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
            game = Takuzu(int(setting), render=True)
            game.run()
        if setting == 'load':
            game = Takuzu(grid=np.load('grid.npy'), render=True)
            game.run()
        elif setting == "test":
            game = Takuzu(__dim__, render=False)
            test = Test(game)
            test.test_all()
        elif setting == "agent":
            game = Takuzu(__dim__, render=True)
            env = EnvironmentTakuzu(game)
            agent = Agent(env)
            agent.episode()
        elif setting == 'solve':
            game = Takuzu(__dim__, render=True, is_player=False)
            solver = GameSolver(game)
        else:
            raise Exception(f"Invalid setting: {setting}. Try 'test', 'agent' or 'solve")



# Mindst tre rækker/søjler med markeringer med 4 i alt
# 
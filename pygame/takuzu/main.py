#cd C:\Users\Jason\Documents\Mini_projects\pygame
#python takuzu.py

#cd pygame
#pygbag takuzu

"""
# How often they are mentioned in wiki page is weight

TODO:
- History is fucked
- 2-player mode
- Color counter at every end (fix tile offset first)
- Aestetics
    - Fix tile offset
    - Thomas shadows (buggy for higher dims due to subtracting)
    - Press Z for undo (make it double redo if blue)
    - Hint shouldn't action, but show the next move with white border (depending on rule)

"""

import asyncio

import sys, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import time

# import numpy as np
import jampy as np
np.random.seed(42)

FLIP = np.array([0, 2, 1])

class Display():

    WHITE, BLACK, GREY = (244, 244, 244), (22, 22, 22), (52, 52, 52)
    RED, GREEN, BLUE = (200, 20, 20), (100, 200, 20), (0, 156, 255)
    RED, YELLOW, PURPLE = (255, 100, 0), (255, 255, 0), (128, 0, 255)
    EMPTY = (0,0,0,0)
    COLORS = [GREY, RED, BLUE]
    SHADES = [None, (220, 50, 0), (0, 130, 220)]

    pg.font.init()
    font_big = pg.font.SysFont("calibri", 50, True)
    font_med = pg.font.SysFont("calibri", 30, True)
    font_small = pg.font.SysFont("calibri", 20, True)

    SIZE = 480 # divisible by 4, 6, 8, 10, 12
    fixed_visible = False

    def __init__(self, is_player):
        self.is_player = is_player

        self.screen = pg.display.set_mode((self.SIZE, self.SIZE))
        self.screen_grid = pg.Surface((self.SIZE, self.SIZE))
        self.screen_fixed = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        self.screen_cursor = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)        

    def reset(self, grid, pos=(0, 0)):
        self.dim = len(grid)
        self.size = self.SIZE // self.dim
        pg.display.set_caption(f"Takuzu [{self.dim}]")

        self.surf_cursor, self.surf_tiles, self.surf_menu, \
            self.surf_congratz, self.surf_fixed, self.surf_invalid, \
                self.surf_dark = self.create_surfaces()

        self._draw_grid(grid)
        if self.is_player:
            self.draw_cursor(np.array(pos))
            # self.show_menu()  # HERE
        else:
            self.frames = [self.screen.copy()]
            self.frame = 0
            pg.display.set_caption(f"Takuzu - {self.frame+1}/{len(self.frames)}")
            pg.display.update()    
    
    def create_surfaces(self):
        size = np.array([self.size, self.size])
        border_radius = self.size // 12

        cursor = pg.Surface(size, pg.SRCALPHA) 
        # gfxdraw.aacircle(cursor, *offset, cursor_size + 2, self.BLACK)
        # gfxdraw.filled_circle(cursor, *offset, cursor_size + 2, self.BLACK)
        # gfxdraw.aacircle(cursor, *offset, cursor_size, self.WHITE)
        # gfxdraw.filled_circle(cursor, *offset, cursor_size, self.WHITE)
        pg.draw.rect(cursor, self.WHITE, (0, 0, self.size, self.size), 2, border_radius=border_radius)

        tiles = []
        tile_rect = (0, 0, self.size - 2, self.size - 2)
        # w = self.size - 10
        # h = self.size // 12
        # shade_horiz = (self.size // 2 - w // 2, self.size - h - 5, w, h)
        # shade_verti = (h - 5, self.size // 2 - w // 2, h, w)
        k = self.size // 12; c = k // 2; t = c // 2
        # points = [(c, c), (k, k), (k, self.size-k-t),   # Odd sizes
        #         (self.size-k, self.size-k-t), (self.size-c, self.size-c-t), (c, self.size-c-t)]
        points = [(c, c), (k, k), (k, self.size-k-t),   # Odd sizes
                (self.size-k, self.size-k-t), (self.size-c, self.size-c-t), (c, self.size-c-t)]
        # unit = self.size // 12
        # y_offset = [2, 3, 4, 5, 6][self.dim // 2 - 2]
        # _y_offset = [2, 3, 4, 5, 6][self.dim // 2 - 3]
        # points = [(unit, unit), (2 * unit, 2 * unit), (2 * unit, self.size - y_offset * unit),
        #           (self.size - y_offset * unit, self.size - y_offset * unit), 
        #           (self.size - unit, self.size - (y_offset - 1) * unit), (unit, self.size - (y_offset - 1) * unit)]
        # shadow_rect = (self.size // 24, self.size * 21 // 24, self.size * 23 // 24, self.size // 14)


        for i in range(3):
            tile = pg.Surface(size, pg.SRCALPHA)
            pg.draw.rect(tile, self.COLORS[i], tile_rect, border_radius=border_radius)
            
            # Shades            
            if i > 0:
                pg.draw.polygon(tile, self.SHADES[i], points)
                # pg.draw.rect(tile, self.SHADES[i], shadow_rect, border_bottom_left_radius=border_radius, border_bottom_right_radius=border_radius)

            tiles.append(tile)
        
        pos_big = (self.SIZE // 2, self.SIZE * 3 // 9)
        pos_med = (self.SIZE // 2, self.SIZE * 4 // 9)
        unit = self.SIZE // 24
        # Menu
        menu = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        menu.fill(self.BLACK + (200,))
        # self.outline_text(menu, "T  k   z", (self.SIZE // 2, 2 * unit), self.font_big, color=self.BLUE, centered=False)
        # self.outline_text(menu, "  a  u  u", (self.SIZE // 2, 2 * unit), self.font_big, color=self.RED, centered=False)
        self.outline_text(menu, "T  k  z  ", (self.SIZE * 6 // 17, 2 * unit), self.font_big, color=self.BLUE, centered=False)
        self.outline_text(menu, "  a  u u", (self.SIZE * 6 // 17, 2 * unit), self.font_big, color=self.RED, centered=False)
        
        self.outline_text(menu, "Rules", (self.SIZE // 2, 6 * unit), self.font_med)
        rules = ['- You cannot connect three tiles in a line', '- Equal number of colors in each row and column', '- All unique rows and unique columns']
        # No subsequent three tiles of the same color in a line
        # Jeg vil ikke sige 'row' da det beyder 'række'
        # May not connect three tiles of the same color in a line
        for i, rule in enumerate(rules):
            self.outline_text(menu, rule, (unit, (7 + i) * unit), self.font_small, centered=False)

        self.outline_text(menu, "Controls", (self.SIZE // 2, 12 * unit), self.font_med)
        controls = ["Arrow keys to move", "[Space] to select [+ shift] for hint", "[R] to restart [+ shift] for new grid", '[1]-[2]-[3]-[4]-[5] to rescale', '[Esc] to return to this screen or quit']
        for i, string in enumerate(controls):
            self.outline_text(menu, string, (unit, (13 + i) * unit), self.font_small, centered=False)
        
        self.outline_text(menu, "Press any [key]", (self.SIZE // 2, 20 * unit))
        self.outline_text(menu, "to continue", (self.SIZE // 2, 22 * unit))


        # Congrats
        congratz = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        self.outline_text(congratz, "Complete!", pos_big)
        self.outline_text(congratz, "Press R to restart", pos_med, self.font_med)
        # self.outline_text(congratz, "R", (self.SIZE // 2, pos_med[1]), self.font_med, color=self.RED, centered=False)

        # Fixed tiles
        fixed_tiles = [None]
        for i in [1, 2]:
            fixed = pg.Surface(size, pg.SRCALPHA)
            pg.draw.rect(fixed, self.SHADES[i], (self.size * 5 // 16, self.size * 4 // 10, self.size * 3 // 8, self.size * 3 // 8), border_radius=border_radius)
            # pg.draw.rect(fixed, self.SHADES[i], (self.size // 4, self.size * 3 // 10, self.size // 2, self.size // 2), border_radius=10)
            pg.draw.ellipse(fixed, self.SHADES[i], (self.size // 3, self.size * 3 // 13, self.size // 3, self.size // 2), self.size // 12)
            # draw center circle
            pg.draw.circle(fixed, self.COLORS[i], (self.size // 2, self.size * 3 // 5), self.size // 18)
            fixed_tiles.append(fixed)

        invalid = pg.Surface(size, pg.SRCALPHA)
        # draw a string !
        self.outline_text(invalid, "X", (self.size // 2, self.size // 2), self.font_big, self.BLACK)

        # Darken tiles
        dark_row = pg.Surface((self.SIZE, self.size), pg.SRCALPHA)
        dark_row.fill(self.BLACK + (50,))
        dark_col = pg.Surface((self.size, self.SIZE), pg.SRCALPHA)
        dark_col.fill(self.BLACK + (50,))

        return cursor, tiles, menu, congratz, fixed_tiles, invalid, (dark_row, dark_col)
    
    def show_invalid(self, pos):
        self.screen.blit(self.surf_invalid, (pos[0] * self.size, pos[1] * self.size))
        pg.display.update()

    def show_count(self, counts):
        self.screen.fill(self.BLACK)
        # self._draw_grid(self.grid)
        # self.draw_cursor(self.pos)
        self.outline_text(self.screen, f"{counts[0]} - {counts[1]}", (self.SIZE // 2, self.SIZE * 7 // 8), self.font_big, self.WHITE)
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
        """Only called upon reset (add_frame)"""
        self.screen_grid.fill(self.BLACK)
        self.screen_fixed.fill(self.EMPTY)

        for i in range(self.dim):
            for j in range(self.dim):
                x, y = i * self.size + 1, j * self.size + 1
                self.screen_grid.blit(self.surf_tiles[grid[j][i]], (x, y))
                if grid[j][i] != 0:  # Assumes drawn at start of grid
                    self.screen_fixed.blit(self.surf_fixed[grid[j][i]], (x, y))

        self.screen.blit(self.screen_grid, (0, 0))
    
    def _draw_tile(self, pos, color):
        x, y = pos * self.size + 1
        self.screen_grid.blit(self.surf_tiles[color], (x, y))
        self.screen.blit(self.screen_grid, (0, 0))
    
    def draw_cursor(self, pos: np.array):
        pos *= self.size

        self.screen.blit(self.screen_grid, (0, 0))  # Draw grid to erase cursor
        if self.fixed_visible:
            self.screen.blit(self.screen_fixed, (0, 0))

        self.screen_cursor.fill(self.EMPTY)
        self.screen_cursor.blit(self.surf_cursor, pos)
        # self.screen_cursor.blit(self.surf_dark[0], (0, pos[1]))
        # self.screen_cursor.blit(self.surf_dark[1], (pos[0], 0))

        self.screen.blit(self.screen_cursor, (0, 0))
        pg.display.update()
    
    def show_fixed(self):
        # TODO: Draw shadowed locks on fixed tiles
        self.fixed_visible = not self.fixed_visible
        if self.fixed_visible:
            self.screen.blit(self.screen_fixed, (0, 0))
            self.screen.blit(self.screen_cursor, (0, 0))
        else:
            self.screen.blit(self.screen_grid, (0, 0))
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
    
    def outline_text(self, SURFACE, text, pos, font=font_big, color=WHITE, ocolor=BLACK, opx=3, centered=True):
        surface = font.render(text, True, color).convert_alpha()
        w = surface.get_width() + 2 * opx 
        h = font.get_height()

        surf_outlilne = pg.Surface((w, h + 2 * opx)).convert_alpha()
        surf_outlilne.fill(self.EMPTY)

        surf = surf_outlilne.copy()

        surf_outlilne.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

        for dx, dy in self._circlepoints(opx):
            surf.blit(surf_outlilne, (dx + opx, dy + opx))

        surf.blit(surface, (opx, opx))
        if centered:
            pos = (pos[0] - w // 2, pos[1] - h // 2)
        SURFACE.blit(surf, pos)
        # return surf
    
    def congrats(self):
        self.screen.blit(self.surf_congratz, (0,0))
        pg.display.update()

    def show_menu(self, show=True):
        # Pause screen
        screen = self.surf_menu if show else self.screen_grid
        self.screen.blit(screen, (0, 0))
        pg.display.update()

class Takuzu():
    pos = [0, 0]

    def __init__(self, render=True, is_player=True):
        self.generator = Generator()
        self.solver = Solver()
        self.display = Display(is_player) if render else None
        self.resize(4)

        # self.menu()
        # self.display.congrats()
    
    def resize(self, dim):
        """Resize grid to dim x dim"""
        self.dim = dim
        self.reset()
            
    def reset(self, soft=False):
        """Reset grid and cursor to initial state.
        If soft, resets to initial state, else generates a new grid"""
        self.pos = [0, 0]

        if soft:
            self.grid = self.grid_init.copy()
            # self.history = [self.grid_init]
        else:
            self.grid_init, self.fixed = self._generate_grid()
            self.grid = self.grid_init.copy()
            # self.history = []
        self.history = [self.grid_init]

        if self.display:
            self.display.reset(self.grid, self.pos)

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
        
    def _generate_grid(self):
        """Generate a grid with a unique solution"""
        grid = self.generator.generate_grid(self.dim)
        fixed = list(zip(*np.nonzero(grid.T))) # Transpose to get x, y
        return grid, fixed
        
    def step(self):
        self.process_input()
    
    def menu(self):
        self.display.show_menu()
        return
        while True:
            event = pg.event.wait()
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()
                else:
                    self.display.show_menu(False)
                    self.display.draw_cursor(np.array(self.pos))
                    break
            
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

                elif event.key == pg.K_SPACE:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.hint()
                    else:
                        self.action()
                elif event.key == pg.K_s:
                    np.save('grid.npy', self.grid)
                    print(self.grid)
                    print("Saved grid to grid.npy")
                elif event.key == pg.K_m:
                    self.hint()
                elif event.key == pg.K_z:
                    self.undo()

                elif event.key in (pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6):
                    self.resize((event.key - pg.K_0 + 1) * 2)

                elif event.key == pg.K_p:
                    print(len(self.history), "moves")
    
    def _process_input(self):
        """Limited control when exporting to executable
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

                elif event.key == pg.K_SPACE:
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.hint()
                    else:
                        self.action()
                elif event.key == pg.K_m:
                    self.hint()

                elif event.key in (pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6):
                    self.resize((event.key - pg.K_0 + 1) * 2)

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

    last_pos = None
    is_valid = True
    def action(self):
        """Toggle tile at cursor position"""
        
        if tuple(self.pos) in self.fixed:
            self.display.show_fixed()
            return 
        
        if self.pos != self.last_pos or len(self.history) == 0:
            # print("history extended")
            self.history.append(self.grid.copy())
        else:
            # print("history replaced")
            self.history[-1] = self.grid.copy()
        # print(len(self.history), "moves")

        x, y = self.pos
        self.grid[y, x] = (self.grid[y, x] + 1) % 3
        self.display.update_tile(self.pos, self.grid[y, x])
        self.display.draw_cursor(np.array(self.pos))
        self.last_pos = self.pos.copy()

        self.is_valid = self.update_valid()
        if self.is_valid and 0 not in self.grid:
            self.win()        

    def update_valid(self):
        is_valid = self.valid_grid(self.grid)
        if not is_valid:
            pg.display.set_caption(f"Takuzu [{self.dim}] :(")
        else:
            pg.display.set_caption(f"Takuzu [{self.dim}]")
        return is_valid

    def count_colors(self):
        """Count number of tiles of each color"""
        if self.display:
            counts = [np.sum(self.grid == i, axis=j) for i in range(1, 3) for j in range(2)] # cols, rows, red, blue
            # print(counts)
            # row_blue = np.sum(self.grid == 1, axis=1)
            # row_red = np.sum(self.grid == 2, axis=1)
            # col_blue = np.sum(self.grid == 1, axis=0)
            # col_red = np.sum(self.grid == 2, axis=0)
            self.display.show_count(counts)
        
    def win(self):
        """Congratulate player and wait for space to be pressed"""
        if self.display:
            self.display.congrats()

        # Wait until space is pressed   
        return
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

    def hint(self):
        """Show a hint"""
        if not self.is_valid: return

        action = self.solver.get_next(self.grid)
        (y, x), color = action

        self.pos = [x, y]
        self.display.draw_cursor(np.array(self.pos))

    def undo(self):
        """Undo last move"""
        if len(self.history) > 0:
            self.grid = self.history.pop()
            self.display._draw_grid(self.grid)
            # print(self.grid)
            self.display.draw_cursor(np.array(self.pos))
        
            self.update_valid()

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
            changed, new = self.subsequent(grid.T, full_c, True)
            if changed:
                grid = new.T
                continue

            if self.equal_count(grid, full_r):
                continue
            changed, new = self.equal_count(grid.T, full_c, True)
            if changed:
                grid = new.T
                continue

            if self.unique(grid, full_r):
                continue
            changed, new = self.unique(grid.T, full_c, True)
            if changed:
                grid = new.T
                continue
            break
        return grid

    def subsequent(self, rows, full, transposed=False):
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

        if transposed:
            return changed, rows
        return changed

    def equal_count(self, rows, full, transposed=False):
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
                rows[r, np.where(row == 0)[0]] = 2  # TODO: TypeError: jdarray.__setitem__ key must be int or tuple, not <class 'jampy.jdarray'>
                changed = True

            elif np.sum(row == 2) == dim_2:
                rows[r, np.where(row == 0)[0]] = 1
                changed = True
        
        if transposed:
            return changed, rows
        return changed

    def unique(self, rows, full, transposed=False):
        """Checks for unique rows and cols.
        Returns True if any changes are made."""
        changed = False

        # Find rows containing exacty two gaps
        gapped_rows_indx = np.where(np.sum(rows == 0, axis=1) == 2)[0]  # [2 3]
        candidates = rows[gapped_rows_indx]  # [[2 1 0 0], [1 0 0 2]]
        # print(full)
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
        
        if transposed:
            return changed, rows
        return changed

    def get_next(self, grid):
        """Returns the next grid in the sequence.
        Assumes valid grid."""
        grid = grid.copy()

        full_r = np.where(grid.all(axis=1))[0]
        full_c = np.where(grid.all(axis=0))[0]

        if action := self._subsequent(grid, full_r):
            return action
        if action := self._subsequent(grid.T, full_c):
            (y, x), color = action 
            return (x, y), color
        if action := self._equal_count(grid, full_r):
            return action
        if action := self._equal_count(grid.T, full_c):
            (y, x), color = action 
            return (x, y), color
        if action := self._unique(grid, full_r):
            return action
        if action := self._unique(grid.T, full_c):
            (y, x), color = action 
            return (x, y), color
        raise Exception("No action found")
        
    def _subsequent(self, rows, full):
        """Checks for subsequent 1s and 2s in rows and cols.
        Returns True if any changes are made."""
        dim = len(rows)

        for r, row in enumerate(rows):
            if r in full:
                continue
            
            for i in range(len(row)-1):
                if row[i] == row[i+1] != 0:
                    if i < dim-2 and rows[r, i+2] == 0: # if next is empty
                        return (r, i+2), FLIP[row[i]]

                    if i > 0 and rows[r, i-1] == 0: # if prev is empty
                        return (r, i-1), FLIP[row[i]]
                    
                if i < len(row)-2 and row[i] == row[i+2] != 0 and row[i+1] == 0:  # Gap between two same
                    return (r, i+1), FLIP[row[i]]

    def _equal_count(self, rows, full):
        """Checks for equal count of 1s and 2s.
        param rows: 2D array
        param full: set of rows or cols that are already full
        Returns True if any changes are made."""
        dim_2 = len(rows) // 2

        for r, row in enumerate(rows):
            if r in full:
                continue

            if np.sum(row == 1) == dim_2:
                return (r, np.where(row == 0)[0][0]), 2

            elif np.sum(row == 2) == dim_2:
                return (r, np.where(row == 0)[0][0]), 1
        
    def _unique(self, rows, full):
        """Checks for unique rows and cols.
        Returns True if any changes are made."""

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
                    gaps = np.where(candy == 0)[0][0]  # [2, 3]
                    return (gapped_rows_indx[i], gaps), FLIP[row[gaps]]


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
                # try:
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
        new = np.zeros((dim, dim), dtype=np.int8)
        complete = self.solve_search(new)
        # return complete
        grid = self.subtract(complete)
        return grid
    
    def solve_search(self, grid, depth=0):
        """Solves and searches for solution.
        Returns None if no solution found or grid if solution found."""
        # print(depth)
        # print(grid)
        grid = self.solve(grid)
        
        if not self.valid_grid(grid): # Invalid, so backtrack
            return None
        
        if 0 not in grid:  # Solved, so terminal state
            return grid

        # Randomly select empty cell and fill with 1 or 2
        # empty_cells = np._where(grid == 0)
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
# from gym import spaces, Env

# class EnvironmentTakuzu(Env):
#     DT = 0.04
#     def __init__(self, game):
#         self.game = game
#         dim = game.dim
#         self.action_space = spaces.Box(low=np.array([0, 0, 1]), high=np.array([dim-1, dim-1, 2]), 
#                                                                         shape=(3,), dtype=int)
#         self.observation_space = spaces.Box(low=0, high=2, shape=(dim,dim), dtype=np.int8)
#         self.reward_range = (0, 1)
    
#     def reset(self):
#         self.game.reset()
#         return self.game.grid

#     def reset_to(self, grid):
#         self.game.grid = grid
#         return self.game.grid
    
#     def step(self, action):
#         if action not in self.action_space:
#             raise Exception(f"Invalid action: {action}")
        
#         x, y, a = action
#         self.game.grid[y, x] = a
#         done = self.game.is_complete()
#         self.render(*action)
#         return self.game.grid, int(done), done
    
#     def render(self, x, y, a):
#         if self.game.display:
#             self.game.display.update_tile(np.array([x, y]), a)
            
#             self.game.process_input()
#             time.sleep(self.DT)
    
#     def random_action(self):
#         x, y, a = self.action_space.sample()
#         while (x, y) in self.game.fixed:
#             x, y, a = self.action_space.sample()
        
#         return np.array([x, y, a])

#     def is_done(self):
#         return self.game.is_complete()

#     def close(self):
#         pass

# class Agent():
#     def __init__(self, env: Env):
#         self.env = env

#     def policy(self, state):
#         """Returns a random action"""
#         return self.env.random_action()
    
#     def episode(self):
#         total_steps = 0
#         # total_reward = 0
#         state = self.env.reset()
#         while True:
#             action = self.policy(state)
#             state, r, done = self.env.step(action)  # TODO: Doesn't work properly
#             total_steps += 1
#             # total_reward += r
#             if done:
#                 print(f"Complete after {total_steps} steps!")
#                 break


EXPORT = True
async def main():
    if len(sys.argv) == 1:
        game = Takuzu(render=True)
        if EXPORT:
            game.process_input = game._process_input
        
        while True:
            game.step()
            await asyncio.sleep(0)
        
    # else:
    #     setting = sys.argv[1]
    #     if setting == 'load':
    #         game = Takuzu(grid=np.load('grid.npy'), render=True)
    #         game.run()
    #     elif setting == "test":
    #         game = Takuzu(render=False)
    #         test = Test(game)
    #         test.test_all()
    #     elif setting == "agent":
    #         game = Takuzu(render=True)
    #         env = EnvironmentTakuzu(game)
    #         agent = Agent(env)
    #         agent.episode()
    #     elif setting == 'solve':
    #         game = Takuzu(render=True, is_player=False)
    #         solver = GameSolver(game)
    #     else:
    #         raise Exception(f"Invalid setting: {setting}. Try 'test', 'agent' or 'solve")

if __name__ == "__main__":
    asyncio.run(main())
    



# Mindst tre rækker/søjler med markeringer med 4 i alt
# Monte carlo søge træ - klam branching factor
# Standard AI metoder til søgning (Modern Approach) - Value function estimates duration until termination or complete. Then search and pick the one with the fewest.

# 
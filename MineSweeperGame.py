import colorsys
import numpy as np
from sys import exit

from scipy.ndimage import label, binary_dilation
import pygame as pg

dir_x = [1, 1, 0,-1,-1,-1, 0, 1]
dir_y = [0,-1,-1,-1, 0, 1, 1, 1]

size = 24
WHITE, GREY, BLACK = (240, 240, 240),  (200, 200, 200), (0, 0, 0)
colors = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (42, 42, 148),  # Blue, Green, Red, d_Blue
        (128, 0 ,0), (42, 148, 148), BLACK, GREY]  			 # d_Red, turqoise, Black, Grey

pg.display.set_caption('MineSweeper')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

class MineSweeper():
    """ 
    Following 2d arrays are used
    - mines: 1 for mines
    - grid: is map of all elements (-1 for mines, 0 for empty and rest for numbers)
    - player what is currently revealed to player (-2 for Hidden)
    """
    W, H, M = 0, 0, 0
    mines, grid, player = 0, 0, 0

    def __init__(self, width, height, mine_count):
        self.W, self.H, self.M = width, height, mine_count
        self.screen = pg.display.set_mode([width * size, height * size])

        self.restart()
        self.is_game_over = False
        self.draw()

        while True:
            self.process_input()

    # ---------- Public --------------

    def left_click(self, point):
        # Handles tuple or list or np.array
        # @Returns player
        point_of_explosion = self.sweep(tuple(point))
        if point_of_explosion:  # BOOM
            self.is_game_over = True
            self.game_over(point_of_explosion)

        else:
            if self.is_won():  # WIN
                self.game_over()
            else:
                self.draw()
        
        return self.player

    def right_click(self, point):
        # Handles tuple or list or np.array
        self.flag(tuple(point))
        self.draw()
    
    def reset(self):
        # @Returns fresh player
        self.restart()
        return self.player

    # ---------- Visualizing --------
    
    # TODO Instead of filling with black, and drawing over, fill grey and add shadow and glare, then add thin darker grey grid lines
    # TODO Redundant code. Refactor with helper draw_square(point)

    def draw(self):
        self.screen.fill(BLACK)
        for x in range(self.W):
            for y in range(self.H):
                # Draw square
                rect = pg.Rect(x*size, y*size, size-1, size-1)
                pg.draw.rect(self.screen, GREY, rect, 0)

                # Draw number
                n = self.player[y, x]
                if n == 0:  # Empty
                    rect = pg.Rect(x*size, y*size, size-1, size-1)
                    pg.draw.rect(self.screen, WHITE, rect, 0)
                elif n == -1:  # Flag
                    xs, ys = x * size, y * size
                    points=[(xs + 10, ys + 4), (xs + 18, ys + 9), (xs + 10, ys + 14)]  # Flag
                    pg.draw.polygon(self.screen, colors[2], points)
                    pg.draw.line(self.screen, BLACK, (xs + 10, ys + 4), (xs + 10, ys + 20))  # Pole

                elif n > 0:
                    txt = font2.render(str(n), 1, colors[n-1])
                    self.screen.blit(txt, (8 + x * size, y * size))
        pg.display.flip()
        # Only update rect on screen
        # pg.display.update([pg.Rect(0, 0, self.W * size / 2, self.H * size), # Left side
        #                    pg.Rect(self.W * size / 2, 0, self.W * size / 2, self.H * size / 2)])  # Top right
        

    def game_over_txt(self):
        txt = font1.render("Game Over", 1, BLACK)
        self.screen.blit(txt, (self.W * size / 10, self.H / 4 * size))

        txt = font2.render("Press 'R' to try again", 1, BLACK)
        self.screen.blit(txt, (self.W * size / 10 + size, self.H * 3 / 7 * size))

        pg.display.flip()

    def game_won_txt(self):
        txt = font1.render("Game Won", 1, BLACK)
        self.screen.blit(txt, (self.W * size / 10, self.H / 4 * size))

        txt = font2.render("Press 'R' to try again", 1, BLACK)
        self.screen.blit(txt, (self.W * size / 10 + size, self.H * 3 / 7 * size))

        pg.display.flip()
        
    def show_mines(self, point_of_explosion):
        points = np.argwhere(self.mines)
        for y, x in points:
            rect = pg.Rect(x*size, y*size, size-1, size-1)
            pg.draw.rect(self.screen, WHITE, rect, 0)
            pg.draw.circle(self.screen, BLACK, ((x + 0.5) * size, (y + 0.5) * size), 5)
        
        y, x = point_of_explosion
        rect = pg.Rect(x*size, y*size, size-1, size-1)
        pg.draw.rect(self.screen, colors[2], rect, 0)
        pg.draw.circle(self.screen, BLACK, ((x + 0.5) * size, (y + 0.5) * size), 5)
        
        pg.display.flip()

    def show_all(self):
        for x in range(self.W):
            for y in range(self.H):
                xs, ys = x * size, y * size
                rect = pg.Rect(xs, ys, size-1, size-1)
                pg.draw.rect(self.screen, WHITE, rect, 0)

                # Draw flags on mine
                if self.mines[y, x]:
                    points=[(xs + 10, ys + 4), (xs + 18, ys + 9), (xs + 10, ys + 14)]  # Flag
                    pg.draw.polygon(self.screen, colors[2], points)
                    pg.draw.line(self.screen, BLACK, (xs + 10, ys + 4), (xs + 10, ys + 20))  # Pole
                    continue
                
                # Draw number
                n = self.grid[y, x]
                if n == 0: continue
                rect = pg.Rect(xs, ys, size-1, size-1)
                pg.draw.rect(self.screen, GREY, rect, 0)
                txt = font2.render(str(n), 1, colors[n-1])
                self.screen.blit(txt, (8 + x * size, y * size))
        pg.display.flip()
        
    	


    # ------------ Game logic -------------------

    def restart(self):
        self.mines = self.place_mines()
        # print(mines)
        self.grid = self.fill_grid(self.mines)
        # print(grid)
        self.player = np.full(self.mines.shape, -2, dtype=int) 

    def guess(self):
        return np.random.randint(self.H), np.random.randint(self.W)

    def place_mines(self):
        X = np.zeros((self.H, self.W), dtype=int)  # 1 where mines

        for i in range(self.M):
            point = self.guess()
            while X[point]:  # Until empty cell found
                point = self.guess()
            
            X[point] = 1

        return X

    def fill_grid(self, mines):
        kernel = np.zeros((self.H+2, self.W+2), dtype=int)
        Y = kernel.copy()
        kernel[1:-1, 1:-1] = mines

        # Offset kernel and +1 for every mine in all directions
        for y, x in zip(dir_x, dir_y):
            temp = np.roll(kernel, x, axis=0)  # Roll x-direction
            Y += np.roll(temp, y, axis=1) 	   # Roll y_direction

        Y = Y[1:-1, 1:-1]
        Y[mines == 1] = -1 # Set mine occupied squares to -1

        return Y

    def reveal(self, point):
        # @Returns truth table of revealed area from point
        # Assumed point is hidden
        # Revealed area are connected hidden and edges

        # Initilize groups before? - Yes, because grid is static throughout game
        A = self.grid.copy()
        A[A != 0] = 1    # Convert all to 1 except empty
        A = 1 - A        # Flip to identify empties
        A, n = label(A)  # Label groups
        # indices = np.indices(A.shape).T[:,:,[1, 0]]  # Create indices for extraction later
        # indices = np.indices(A.shape).T  # Create indices for extraction later

        
        
        # Find the group, i, where point belongs (the connected hidden)
        for i in range(1, n+1):
            # if list(point) in indices[A == 1].tolist():  # 'x in X' only work for lists
            if list(point) in np.argwhere(A == i).tolist():  # My version
                break
        # print("GROUP", i)

        # Dilate this group once (the edge)
        A[A != i] = 0  # Erase all other groups
        A = binary_dilation(A)            # Dilate binary image and produce truth table
        A = np.logical_and(A, 1 - self.mines)  # Keep mines hidden

        # Return A and execute rest outside to avoid out of scope referencing of player and grid
        np.copyto(self.player, self.grid, where=A)  # Copy over where appropiate


    def sweep(self, point: tuple):
        """ 
        @Params: point (y, x)
        @Returns Point of exploding mine or None
        Updates player following
        - Positive, then only updates that number
        - Negative, GAMEOVER
        - 0, flood all 0s and adjacent numbers
        """
        if self.player[point] == -1: return None  # Flagged can't be sweeped
        
        v = self.grid[point]
        if v == -1:
            return point
        
        if v == 0:  # Picked empty
            self.reveal(point)
            # Actually do the update here instead of in reveal
        else:  # Picked number
            self.player[point] = v

        return None

    def flag(self, point: tuple):
        if self.player[point] > 0: return
        self.player[point] = -1 if self.player[point] != -1 else -2


    def game_over(self, point_of_explosion=None):
        if point_of_explosion:
            self.show_mines(point_of_explosion)
            #self.game_over_txt()
        else:
            self.show_all()
            #self.game_won_txt()

    def is_won(self):
        # Determine if game won by all numbers (non-mines and non-blanks) uncovered
        A = self.player >= 0
        return np.all(A != self.mines)

    # ----- Input handling -----

    def process_input(self):
        event = pg.event.wait()

        if event.type == pg.QUIT:
            pg.quit()
            exit()

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            if event.key == pg.K_r:
                self.restart()
                self.is_game_over = False
                self.draw()
            if event.key == pg.K_SPACE:
                pass
        
        elif event.type == pg.MOUSEBUTTONUP and not self.is_game_over:
            pos = pg.mouse.get_pos()
            point = np.array(pos)[::-1] // size  # Flip and map to grid
            if event.button == 1:
                self.left_click(point)

            elif event.button == 3:  # Right click to flag
                self.right_click(point)

    




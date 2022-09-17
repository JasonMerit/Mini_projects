import colorsys
import numpy as np
from sys import exit
import csv


from scipy.ndimage import label, binary_dilation
import pygame as pg

# TODO Chording?
# TODO Save win rate after restarting
# TODO Timer
# TODO History of moves within a WxH 2d list
# np.random.seed(99)
dir_x = [1, 1, 0,-1,-1,-1, 0, 1]
dir_y = [0,-1,-1,-1, 0, 1, 1, 1]

size = 24
WHITE, GREY, BLACK = (240, 240, 240),  (200, 200, 200), (0, 0, 0)
colors = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (42, 42, 148),  # Blue, Green, Red, d_Blue
        (128, 0 ,0), (42, 148, 148), BLACK, (160, 160, 160)]  			 # d_Red, turqoise, Black, Grey

pg.display.set_caption('MineSweeper')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

class MineSweeper():
    """ 
    Following 2d arrays are used
    - mines: 1 for mines
    - grid: is map of all elements (-1 for mines, 0 for empty and rest for numbers)
    - player what is currently revealed to player (0, hidden, -1, flagged, -2 for Hidden)
    """
    W, H, M = 0, 0, 0
    mines, grid, player = 0, 0, 0
    first = True
    replay = False
    # groups, G = 0, 0
    history = [] # E.g. ("s", (4, 3)) for sweeping at (4, 3)

    ready_to_chord = False

    def __init__(self, width=0, height=0, mine_count=0, mines=[]):
        
        

        # self.reset()
        self.is_game_over = False
        if len(mines) > 0:
            replay = True
            self.mines = mines
            self.H, self.W = mines.shape
            self.mine_count = sum(sum(mines))
            self.screen = pg.display.set_mode([self.W * size, self.H * size])
            self.restart(False)  # Soft reset
        else:
            self.W, self.H, self.M = width, height, mine_count
            self.screen = pg.display.set_mode([width * size, height * size])
            self.restart() 

        
    
    # ---------- Public --------------
    # history = []
    def left_click(self, point):
        point_of_explosion = self.sweep(tuple(point))
        if point_of_explosion:  # BOOM
            self.is_game_over = True
            self.game_over(point_of_explosion)

        else:
            if self.is_won():  # WIN
                print("WIN")
                self.game_over()
        
    def right_click(self, point):
        self.flag(tuple(point))
    
    def right_left_click(self, point):
        point_of_explosion = self.chord(tuple(point))
        if point_of_explosion:  # BOOM
            self.is_game_over = True
            self.game_over(point_of_explosion)
        else:
            if self.is_won():  # WIN
                print("WIN")
                self.game_over()
        
    
    def reset(self):
        self.restart()
        # self.left_click(self.guess())  # Auto first move

    # ---------- Visualizing --------
    
    def draw(self):
        # Numbered white
        # Empty white
        # Else grey
        self.screen.fill(BLACK)
        for x in range(self.W):
            for y in range(self.H):
                n = self.player[y, x]

                # Draw square 
                rect = pg.Rect(x*size, y*size, size-1, size-1)
                color = WHITE if n >= 0 else GREY
                pg.draw.rect(self.screen, color, rect, 0)

                # Draw number or flag
                if n == -1:  # Flag
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
        
    def draw_cell(self, point):
        # Draw and update screen at point
        # Called from right click and when sweeping a number
        y, x = point
        xs, ys = x * size, y * size
        
        rect = pg.Rect(xs, ys, size-1, size-1)

        n = self.player[point]
        if n == -1:
            pg.draw.rect(self.screen, GREY, rect, 0)
            points=[(xs + 10, ys + 4), (xs + 18, ys + 9), (xs + 10, ys + 14)]  # Flag

            pg.draw.polygon(self.screen, colors[2], points)
            pg.draw.line(self.screen, BLACK, (xs + 10, ys + 4), (xs + 10, ys + 20))  # Pole
        elif n == -2:
            pg.draw.rect(self.screen, GREY, rect, 0)
        else:
            pg.draw.rect(self.screen, WHITE, rect, 0)
            txt = font2.render(str(n), 1, colors[n-1])
            self.screen.blit(txt, (8 + x * size, y * size))


        pg.display.update(rect)        



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
                    pg.draw.rect(self.screen, GREY, rect, 0)
                    points=[(xs + 10, ys + 4), (xs + 18, ys + 9), (xs + 10, ys + 14)]  # Flag
                    pg.draw.polygon(self.screen, colors[2], points)
                    pg.draw.line(self.screen, BLACK, (xs + 10, ys + 4), (xs + 10, ys + 20))  # Pole
                    continue
                
                # Draw number
                n = self.grid[y, x]
                if n == 0: continue
                txt = font2.render(str(n), 1, colors[n-1])
                self.screen.blit(txt, (8 + x * size, y * size))
        pg.display.flip()
        
    	


    # ------------ Game logic -------------------
    def first_move(self, point):
        # Ensures first sweep is safe and touching is clear of mines TODO
        if self.mines[point] == 1:
            y, x = np.nonzero(self.mines == 0)
            y, x = y[0], x[0]
            self.mines[y, x] = 1
            self.mines[point] = 0
            # self.grid = self.fill_grid(self.mines)
            self.restart(False)
        self.draw()
    
    def restart(self, hard=True):
        if hard:
            self.mines = self.place_mines()
        self.player = np.full(self.mines.shape, -2, dtype=int) 
        self.grid = self.fill_grid(self.mines)
        self.first = True
        self.is_game_over = False

        self.draw()
        
        
        # print(mines)
        # print(grid)

    def guess(self):
        return (np.random.randint(self.H), np.random.randint(self.W))

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
        # Called when sweeping an empty square
        # Revealed area are connected hidden and edges
        

        A, n = label(self.grid == 0, np.ones((3, 3)))  # Label groups of empties
        
        # Find the group, i, where point belogs (the connected hidden)
        for i in range(1, n+1): # List
        # for i in range(1, self.G+1): # List
            # if list(point) in np.argwhere(self.groups == i).tolist():  # My version
            if list(point) in np.argwhere(A == i).tolist():  # My version
                break
        # print("GROUP", i)

        # Dilate this group once (the edge)
        # A = self.groups.copy()
        A[A != i] = 0  # Erase all other groups
        A = binary_dilation(A, np.ones((3, 3)))            # Dilate binary image and produce truth table
        # A = np.logical_and(A, 1 - self.mines)              # Keep mines and empty hidden 
        A[self.mines == 1] = False

        return A
        


    def sweep(self, point: tuple):
        """ 
        @Params: point (y, x)
        @Returns Point of exploding mine or None
        Updates player following
        - Positive, then only updates that number
        - Negative, GAMEOVER
        - 0, flood all 0s and adjacent numbers
        """
        if self.first:
            self.first_move(point)
            self.first = False
        
        self.history.append(("s", point))
        if self.player[point] == -1: return None  # Flagged can't be sweeped
        
        v = self.grid[point]
        if v == -1:
            print(self.history)
            return point
        
        if v == 0:  # Picked empty
            revealed = self.reveal(point)
            np.copyto(self.player, self.grid, where=revealed)  # Copy over where appropiate
            self.draw()
        else:  # Picked number
            self.player[point] = v
            self.draw_cell(point)

        return None

    def flag(self, point: tuple):
        self.history.append(("f", point))
        if self.player[point] >= 0: return
        self.player[point] = -1 if self.player[point] != -1 else -2
        self.draw_cell(tuple(point))
    
    def chord(self, point: tuple):
        # Perform chording on satisfied numbered cell
        # Reveals all touching cells
        # TODO Keep list of all satisfied numbers?
        self.history.append(("c", point))
        if self.player[point] <= 0:
            return None

        revealed = []
        flagged = 0
        for y, x in zip(dir_y, dir_x):
            yn, xn = point[0] + y, point[1] + x
            if not(0 <= yn < self.H) or not(0 <= xn < self.W): # OOB
                continue

            v = self.player[yn, xn]
            if v == -1:
                flagged += 1
            elif v == -2:
                revealed.append((yn, xn))
        
        if flagged != self.player[point]:  # Return if unsatisfied
            return None
        
        for point in revealed:
            explosion = self.sweep(point)
            if explosion: return explosion

    def game_over(self, point_of_explosion=None):
        # print(self.history)
        if not self.replay:
            with open("last_mines.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(self.mines)
            with open("last_moves.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(self.history)
        if point_of_explosion:
            self.show_mines(point_of_explosion)
            #self.game_over_txt()
        else:
            self.show_all()
            #self.game_won_txt()

    def is_won(self):
        # Won if all non mines reveled to player
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
                self.reset()
                
            if event.key == pg.K_SPACE:
                return "sweep"

            if event.key == pg.K_k:
                pos = pg.mouse.get_pos()
                point = np.array(pos)[::-1] // size  # Flip and map to grid
                self.right_left_click(point)
            
            if event.key == pg.K_1:
                return 1
            
            if event.key == pg.K_2:
                return 2
        
        # elif event.type == pg.MOUSEBUTTONDOWN and not self.is_game_over:
        #     self.ready_to_chord = True
        #     print("DOWN")


        elif event.type == pg.MOUSEBUTTONUP and not self.is_game_over:
            # print("UP")
            pos = pg.mouse.get_pos()
            point = np.array(pos)[::-1] // size  # Flip and map to grid
            
            if event.button == 1:
                # print("LEFT CLICK")
                self.left_click(point)

            elif event.button == 2:
                # print("CHORDING")
                self.right_left_click(point)
                # self.ready_to_chord = False

            elif event.button == 3:  # Right click to flag
                # print("RIGHT CLICK")
                self.right_click(point)






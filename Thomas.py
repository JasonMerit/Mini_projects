import numpy as np
from sys import exit

from scipy.ndimage import label, binary_dilation
import pygame as pg
import time


#class MineSweeper():
W, H, M = 10, 10, 10
np.random.seed(0)

dir_x = [1, 1, 0,-1,-1,-1, 0, 1]
dir_y = [0,-1,-1,-1, 0, 1, 1, 1]

""" 
Following 2d arrays are used
- mines: 1 for mines
- grid: is map of all elements (-1 for mines, 0 for empty and rest for numbers)
- player what is currently revealed to player (-2 for Hidden)
"""

# ---------- Visualizing --------
size = 24
dif = 500 * 0.8 / W
offset = 500 / 2 - dif * W / 2
screen = pg.display.set_mode([W * size, H * size])

WHITE, GREY, BLACK = (255, 255, 255),  (200, 200, 200), (0, 0, 0)

colors = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (42, 42, 148),  # Blue, Green, Red, d_Blue
		  (128, 0 ,0), (42, 148, 148), BLACK, GREY]  			 # d_Red, turqoise, Black, Grey

pg.display.set_caption('MineSweeper')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

def draw():
	screen.fill(GREY)
	for x in range(W):
		for y in range(H):
			# Draw square
			rect = pg.Rect(x*size, y*size, size, size)
			pg.draw.rect(screen, BLACK, rect, 1)

			# Draw number
			n = player[y, x]
			if n == 0:
				rect = pg.Rect(x*size, y*size, size, size)
				pg.draw.rect(screen, WHITE, rect, size)
			elif n > 0:
				txt = font2.render(str(n), 1, colors[n-1])
				screen.blit(txt, (8 + x * size, y * size))

	pg.display.flip()
	

def game_over_txt():
	txt = font1.render("Game Over", 1, BLACK)
	screen.blit(txt, (W * size / 10, H / 4 * size))

	txt = font2.render("Press 'R' to try again", 1, BLACK)
	screen.blit(txt, (W * size / 10 + size, H * 3 / 7 * size))

	pg.display.flip()
	
def show_mines():
	points = np.argwhere(mines)
	for y, x in points:
		pg.draw.circle(screen, BLACK, ((x + 0.5) * size, (y + 0.5) * size), 5)
	
	pg.display.flip()


# ------------ Game logic -------------------

def restart():
	mines = place_mines(M)
	# print(mines)
	grid = fill_grid(mines)
	# print(grid)
	player = np.full(mines.shape, -2, dtype=int) 

	return mines, grid, player

def guess():
	return np.random.randint(H), np.random.randint(W)

def place_mines(n):
	X = np.zeros((H, W), dtype=int)  # 1 where mines

	for i in range(n):
		point = guess()
		while X[point]:  # Until empty cell found
			point = guess()
		
		X[point] = 1

	return X

def fill_grid(mines):
	kernel = np.zeros((H+2, W+2), dtype=int)
	Y = kernel.copy()
	kernel[1:-1, 1:-1] = mines

	# Offset kernel and +1 for every mine in all directions
	for y, x in zip(dir_x, dir_y):
		temp = np.roll(kernel, x, axis=0)  # Roll x-direction
		Y += np.roll(temp, y, axis=1) 	   # Roll y_direction

	Y = Y[1:-1, 1:-1]
	Y[mines == 1] = -1 # Set mine occupied squares to -1

	return Y



def sweep(point):
	# @Params: point (y, x)
	# Updates player following
	# - Positive, then only updates that number
	# - Negative, GAMEOVER
	# - 0, flood all 0s and adjacent numbers
	# @Returns False if game over
	
	v = grid[point]
	print(v)
	if v == -1:
		return False
	
	if v == 0:  # Picked empty
		reveal(point)
	else:
		player[point] = v

	return True
	
def reveal(point):
	# @Returns truth table of revealed area from point
	# Assumed point is hidden
	# Revealed area are connected hidden and edges

	# Initilize groups before? - Yes, because grid is static throughout game
	A = grid.copy()
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
	A = np.logical_and(A, 1 - mines)  # Keep mines hidden

	# Return A and execute rest outside to avoid out of scope referencing of player and grid
	np.copyto(player, grid, where=A)  # Copy over where appropiate

def game_over():
	game_over_txt()
	show_mines()

# ----- Input handling -----

def process_input():
	event = pg.event.wait()

	if event.type == pg.QUIT:
		pg.quit()
		exit()

	elif event.type == pg.KEYDOWN:
		if event.key == pg.K_ESCAPE:
			pg.quit()
			exit()
		if event.key == pg.K_r:
			global mines, grid, player, is_game_over
			mines, grid, player = restart()
			is_game_over = False
			draw()
		if event.key == pg.K_SPACE:
			pass
	
	elif event.type == pg.MOUSEBUTTONDOWN and not is_game_over:
		if event.button == 1:
			pos = pg.mouse.get_pos()
			point = np.array(pos)[::-1] // size  # Flip and map to grid
			if not sweep(tuple(point)):
				is_game_over = True
				game_over()
			else:
				draw()
		elif event.button == 3:
			pass # Flag???

mines, grid, player = restart()
is_game_over = False
draw()

while True:
	process_input()

mines, grid, player = restart()
games = 10
while games:
	if not sweep(guess()):
		mines, grid, player = restart()
		games -= 1




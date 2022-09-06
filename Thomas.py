import numpy as np
from sys import exit

from scipy.ndimage import label, binary_dilation
import time


W, H, M = 10, 10, 10
np.random.seed(0)

dir_x = [1, 1, 0,-1,-1,-1, 0, 1]
dir_y = [0,-1,-1,-1, 0, 1, 1, 1]

""" 
Following 2d arrays are used
- mines is 1 for mines
- grid is map of all elements (-1 for mines, 0 for empty and rest for numbers)
- player what is currently revealed to player (-2 for Hidden)
"""
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
	# Updates player following
	# - Positive, then only updates that number
	# - Negative, GAMEOVER
	# - 0, flood all 0s and adjacent numbers
	# @Returns False if game over
	
	v = grid[point]
	
	if v == -1:
		print("GAME OVER")
		player[point] = 404
		print(player)
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







mines, grid, player = restart()
games = 10
while games:
	if not sweep(guess()):
		mines, grid, player = restart()
		games -= 1




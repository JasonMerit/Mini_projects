import numpy as np
import pyautogui
import cv2
import time
from sys import exit
"""
http://www.minesweeper.info/wiki/Strategy
- Only have basic pattern

Optimizing ideas: 
	- Keep track of cells that are exhausted
	- Subtract mines from touching numbers (this fucks up screenshot / 
	  or not, don't update numbers, only initilize after sweep). 
	  Perhaps have 10 represent exhausted number. 

TODO:
	- Termination conditions (gameover or complete) - check for smiley :D
"""


# grid consists of types -2: hidden, -1: mine, 0: clean, 1-8 number of touching bombs
A = 24
W, H = 24, 16
offset = 10
x0, y0 = 334, 228
grid = np.full((H, W), -2, dtype=int)

# Direction starting right going counter clockwise
dir_x = [1, 1, 0,-1,-1,-1, 0, 1]
dir_y = [0,-1,-1,-1, 0, 1, 1, 1]

# Taking screenshot
def grab_square(x, y):
	# Used to capture prototype image used for template
	# image = grab_square(7, 3)
	image = pyautogui.screenshot(region=(x0 + A*x, y0 + A*y, A, A))
	return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def grab_grid():
	image = pyautogui.screenshot(region=(x0, y0, W*A, H*A))  #  left, top, width, and height
	return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)



# Finding multiple elements
def get_positions(n: int, capture):
	img_rgb = cv2.imread('images/screenshot.png')
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	template = cv2.imread('images/' + str(n) + '.png',0)
	w, h = template.shape[::-1]

	res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
	threshold = 0.8
	loc = np.where(res >= threshold)

	if not capture:
		return zip(*loc[::-1])
	n = 0
	for pt in zip(*loc[::-1]):
		n += 1
		cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
	print(n)
	    
	cv2.imshow('output',img_rgb)
	cv2.waitKey(0)
# get_positions()


def update_grid(capture=False):
	screenshot()
	for i in range(0, 6):
		pts = get_positions(i, capture)
		if capture:  # For debugging
			continue
		pts = [((x + 3) // A, (y + 3) // A) for x, y in pts]  # Map to grid // Better way???
		pts = list(set(pts))  									# Remove redundancy (due to low theshold)
		for x, y in pts:
			# print(i, ")", x, y)
			# print(i, ")", (x+3) // A, (y+3) // A)
			# grid[(y+3) // A, (x+3) // A] = i  # Odd placement by opencv so +3
			grid[y, x] = i

def get_empty_neighbors(x, y):
	neighbors = set()
	# neighbors = []
	count = 0
	
	# Iterate over all directions and append point if hidden or mine
	for i, j in zip(dir_x, dir_y):
		if y+j < 0 or y+j >= H or x+i < 0 or x+i >= W:  # Out of bounds
			continue
		if grid[y+j, x+i] >= 0:  # A number or clean
			continue

		elif grid[y+j, x+i] == -2:  # Hidden!
			# neighbors.append((x+i, y+j))
			neighbors.add((x+i, y+j))
		count += 1
	
	return neighbors, count

def get_clean_neighbors(x, y):
	neighbors = []
	mines_count = 0
	
	# Iterate over all directions and append point if clean
	for i, j in zip(dir_x, dir_y):
		if y+j < 0 or y+j >= H or x+i < 0 or x+i >= W:  # Out of bounds
			continue
		if grid[y+j, x+i] >= 0:  # A number or clean
			continue

		elif grid[y+j, x+i] == -2:  # Hidden!
			neighbors.append((x+i, y+j))
		else:  # Mine!
			mines_count += 1
	
	return neighbors, mines_count

def get_touching(x, y):
	# Returns count of touching mines and hidden
	mine_count = 0
	hidden = set()
	
	# Iterate over all directions
	for i, j in zip(dir_x, dir_y):
		if y+j < 0 or y+j >= H or x+i < 0 or x+i >= W:  # Out of bounds
			continue
		if grid[y+j, x+i] == -1:  # Marked mine
			mine_count += 1
		elif grid[y+j, x+i] == -2:  # Hidden
			hidden.add((x+i, y+j))
	
	return mine_count, hidden


def basic_pattern():
	# Returns point of next move
	mines = set()
	# mines = []

	# Find basic patterns (If a number is touching the same number of squares, then the squares are all mines)
	for y, row in enumerate(grid):
		for x, v in enumerate(row):
			if v < 1:
				continue

			empty_neighbours, count = get_empty_neighbors(x, y)
			if empty_neighbours and v == count:  # If exists hidden neighbor and condition
				# print(v, "==", count, "at (", x, y, ")")
				mines = mines.union(empty_neighbours)
				# return empty_neighbours
	return mines

def get_clean():
	# Returns list of points that are found clean
	cleans = []

	for y, row in enumerate(grid):
		for x, v in enumerate(row):
			if v < 1:
				continue

			clean_neighbors, mines_count = get_clean_neighbors(x, y)
			if clean_neighbors and v == mines_count:  # If exists hidden and mines accounted
				cleans += clean_neighbors

	return list(set(cleans))

def get_chords():
	# Returns list of points of numbers that can chord
	chords = set()
	targets = set()
	for y, row in enumerate(grid):
		for x, v in enumerate(row):
			if v < 1:
				continue

			mine_count, touching_hidden = get_touching(x, y)
			# If any hidden, mines accounted and chord not already taken care of
			if touching_hidden and v == mine_count and touching_hidden.isdisjoint(targets):
				targets.union(touching_hidden)
				chords.add((x, y))
	return chords



def guess():
	v = 0
	while v != -2:
		x, y = np.random.randint(W), np.random.randint(H)
		v = grid[y, x]
	
	return [(x, y)]




def flag(points):
	if not points:
		return
	
	for x, y in points:
		grid[y, x] = -1
		pyautogui.click(x=x0+x*A + offset, y=y0+y*A + offset, button="right")

def sweep(points):
	for x, y in points:
		pyautogui.click(x=x0+x*A + offset, y=y0+y*A + offset)
		# Updates grid based on screenshot

def chord(points):
	# Chord by pressing left and right click simultaniusouly on numbered cell touching unmarked mines
	if not points:
		return

	for x, y in points:
		pyautogui.mouseDown(x=x0+x*A + offset, y=y0+y*A + offset, button="right")
		pyautogui.mouseDown(x=x0+x*A + offset, y=y0+y*A + offset)
		pyautogui.mouseUp()
		pyautogui.mouseUp(button="right")


def screenshot():
	image = grab_grid()
	cv2.imwrite("images/screenshot.png", image)

def restart():
	pyautogui.press("f2")
	global grid
	grid = np.full((H, W), -2, dtype=int)
	sweep(guess())
	update_grid()
	

def alt_tab():
	pyautogui.keyDown("altleft")
	pyautogui.press("tab")
	pyautogui.keyUp("altleft")


alt_tab()

# screenshot()
# update_grid(True)
# exit()

n = 1
for i in range(n):

	restart()
	done = False
	# for i in range(10):
	while not done:
		update_grid()

		mines = basic_pattern()
		flag(mines)

		# cleans = get_clean()
		# if cleans:
		# 	sweep(cleans)

		chords = get_chords()  # Redundany in two numbered may clear the same
		chord(chords)

		# done = not (mines or cleans)
		done = not (mines or chords)
		# if done:
		# 	sweep(guess())
		# 	done = False
alt_tab()
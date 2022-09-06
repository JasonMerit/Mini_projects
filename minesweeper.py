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
	- Should I perform known action immediatly, or finish finding all consquences?
	  in similar way, should I update grid immediatly
	- Have a queue so that cells just uncovered come first, or if empty iterate whole grid life before
	- To update grid, iterate over each cell and take cell screenshots, then update grid based on color value. 


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

# Object identification info
smiley_region = (602, 170, 38, 38)

# ----- Object identification -----
def alt_tab():
	pyautogui.keyDown("altleft")
	pyautogui.press("tab")
	pyautogui.keyUp("altleft")

def screenshot():
	image = grab_grid()
	cv2.imwrite("images/screenshot.png", image)

def grab_square(x, y):
	# Used to capture prototype image used for template
	# image = grab_square(7, 3)
	image = pyautogui.screenshot(region=(x0 + A*x, y0 + A*y, A, A))
	return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def grab_grid():
	image = pyautogui.screenshot(region=(x0, y0, W*A, H*A))  #  left, top, width, and height
	return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


# Finding multiple elements
def get_positions(n: int, image, capture):
	# img_rgb = cv2.imread('images/screenshot.png')
	img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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

def display_captures(img_rgb):
	for i in range(0, 6):
		img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
		template = cv2.imread('images/' + str(i) + '.png',0)
		w, h = template.shape[::-1]

		res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		threshold = 0.8
		loc = np.where(res >= threshold)
		n = 0
		for pt in zip(*loc[::-1]):
			n += 1
			cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
		print(n)
		    
		cv2.imshow('output',img_rgb)
		cv2.waitKey(0)

def update_grid(image, capture=False):
	for i in range(0, 6):
		pts = get_positions(i, image, capture)
		if capture:  # For debugging
			continue
		pts = [((x + 3) // A, (y + 3) // A) for x, y in pts]  # Map to grid // Better way???
		pts = list(set(pts))  									# Remove redundancy (due to low theshold)
		for x, y in pts:
			grid[y, x] = i

# ----- Solving -----

def restart():
	pyautogui.press("f2")
	global grid
	grid = np.full((H, W), -2, dtype=int)

def start():
	start = guess()
	sweep([start])
	return start

def guess():
	v = 0
	while v != -2:
		x, y = np.random.randint(W), np.random.randint(H)
		v = grid[y, x]
	
	return (y, x)


def get_empty_neighbors(x, y):
	neighbors = set()
	# neighbors = []
	count = 0  # Mines + hidden
	
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

# ----- Mutators -----
def flag(points):
	if not points:
		return
	
	for y, x in points:
		grid[y, x] = -1
		pyautogui.click(x=x0+x*A + offset, y=y0+y*A + offset, button="right")

def sweep(points):
	for y, x in points:
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



# ---- Getters ----
	
def get_neighbors(point):
	# Returns different sets of (y, x) and count of touching mines
	y, x = point
	hidden = set()
	equals = set()
	one_uppers = set()
	mine_count = 0
	
	# Iterate over all directions
	for i, j in zip(dir_x, dir_y):
		if y+j < 0 or y+j >= H or x+i < 0 or x+i >= W:  # Out of bounds
			continue
		
		visit = (y+j, x+i)
		match grid[visit]:
			case 0:
				continue
			case -1:
				mine_count += 1
			case -2:
				hidden.add(visit)
			case _:
				if grid[y, x] == grid[visit]:  # 1-1
					# if y-j < 0 or y-j >= H or x-i < 0 or x-i >= W or grid[y-j, x-i] == 0:  # Open opposite
					equals.add(visit)	
				elif grid[y, x] - grid[visit] == -1:  # 1-2
					# if y-j < 0 or y-j >= H or x-i < 0 or x-i >= W or grid[y-j, x-i] == 0:  # Open opposite
					one_uppers.add(visit)

	return hidden, equals, one_uppers, mine_count
	

def get_hidden(point):
	# Returns hidden neighbors
	y, x = point
	hidden = set()
	
	# Iterate over all directions
	for i, j in zip(dir_x, dir_y):
		if y+j < 0 or y+j >= H or x+i < 0 or x+i >= W:  # Out of bounds
			continue
		
		if grid[(y+j, x+i)]	== -2:
			hidden.add((y+j, x+i))

	return hidden

def find_numbers():
	# @Returns points of all numbered cells
	points = []

	for y, row in enumerate(grid):
		for x, v in enumerate(row):
			if v > 0:
				points.append((y, x))
	return points

def step(point):
	""" @Returns mines, cleared
	- If N == M + H, then H => M
	- If N == M,     then H => C
	- If difference of 1-1 leaves 1 hidden, then clean
	- If difference of 1-2 leaves 1 hidden, then mine
	"""
 
	v = grid[point]
	hidden, equals, one_uppers, mine_count = get_neighbors(point)

	if v == len(hidden) + mine_count:  # Equal number and touching, so hidden are mines
		return hidden, []

	if v == mine_count:  # Mines accounted, so hidden are cleared
		return [], hidden

	for equal in equals:  # 1-1 patterns
		# If opposite touching is clear or edge


		equal_hidden = get_hidden(equal)
		diff = equal_hidden.difference(hidden)
		if len(diff) == 1:
			return [], diff

	for upper in one_uppers:  # 1-2 patterns
		upper_hidden = get_hidden(upper)
		diff = upper_hidden.difference(hidden)
		if len(diff) == 1:
			return diff, []

	return [], []


def is_gameover():
	image = pyautogui.screenshot(region=smiley_region)
	image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

	img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	template = cv2.imread('images/smiley.png',0)

	res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
	return np.any(res < 0.9)


# alt_tab()

# image = grab_grid()
# update_grid(image)
# print(grid[0:3, 11:14])
alt_tab()
# image = cv2.imread('images/screenshot.png')
# display_captures(image)
# alt_tab()
# exit()

n = 1
for i in range(n):
	restart()
	# start = start()
	update_grid(grab_grid())
	# Q = []
	# Q += find_numbers()
	done = False
	# for i in range(10):
	while not done:
	# while Q:
		if is_gameover():
			print("PEPSI")
			alt_tab()
			exit()

		update_grid(grab_grid())

		# if not Q:
		# 	Q += find_numbers()
		
			

		# move = Q.pop()
		# mines, cleans = step(move)

		
		mines = basic_pattern()
		if mines:
			# print(mines)
			flag(mines)

		# if cleans:
		# 	# print(cleans)
		# 	sweep(cleans)
		cleans = get_clean()
		if cleans:
			sweep(cleans)

		# chords = get_chords()  # Redundany in two numbered may clear the same
		# chord(chords)

		done = not (mines or cleans)
		# done = not (mines or cleans)
		# if done:
		# 	sweep(guess())
		# 	done = False
alt_tab()
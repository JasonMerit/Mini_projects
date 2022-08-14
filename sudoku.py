import pygame as pg
# https://www.geeksforgeeks.org/building-and-visualizing-sudoku-game-using-pygame/
import sys
import copy
import random as rng

screen = pg.display.set_mode([500, 600])
pg.display.set_caption('Sudoku')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

dif = 500 / 9

# o = [0, 0, 0, 0, 0, 0, 0, 0, 0]
p = [1, 2, 3, 4, 5, 6, 7, 8, 9]
# grid = [o.copy()].copy()*9

# grid = [[0, 0, 0,  0, 0, 0,  0, 0, 0],
# 		[0, 0, 0,  0, 0, 0,  0, 0, 0],
# 		[0, 0, 0,  0, 0, 0,  0, 0, 0],

# 		[0, 0, 0,  0, 0, 0,  0, 0, 0],
# 		[0, 0, 0,  0, 0, 0,  0, 0, 0],
# 		[0, 0, 0,  0, 0, 0,  0, 0, 0],

# 		[0, 0, 0,  0, 0, 0,  0, 0, 0],
# 		[0, 0, 0,  0, 0, 0,  0, 0, 0],
# 		[0, 0, 0,  0, 0, 0,  0, 0, 0]]
# grid = [[0, 3, 0,  1, 0, 5,  0, 9, 0],
# 		[0, 0, 7,  0, 0, 0,  8, 0, 0],
# 		[0, 0, 0,  0, 6, 0,  0, 0, 0],

# 		[0, 1, 0,  2, 0, 3,  0, 5, 0],
# 		[0, 0, 0,  0, 0, 4,  0, 0, 0],
# 		[5, 0, 0,  0, 0, 0,  0, 0, 9],

# 		[0, 6, 0,  0, 9, 0,  0, 0, 0],
# 		[0, 0, 0,  0, 4, 0,  0, 2, 0],
# 		[0, 0, 3,  6, 0, 2,  0, 0, 7]]


def  randomize_grid():
	grid = [[rng.randint(1, 9) if rng.random() < 0.5 else 0 for j in range(9)] for i in range(9)]

	# Delete all illegal entrees
	for j in range(9):
		for i in range(9):
			v = grid[j][i]
			if v == 0:
				continue

			# Row rule
			for x in range(9):
				if grid[j][x] == v and x != i:
					grid[j][x] = 0

			# Column rule
			for y in range(9):
				if grid[y][i] == v and y != j:
					grid[y][i] = 0

			# Box rule
			it, jt = (i // 3, j // 3)
			for y in range(jt * 3, jt * 3 + 3):
				for x in range(it * 3, it * 3 + 3):
					if grid[y][x] == v and (y != j and x != i):
						grid[y][x] = 0

	return grid

def init():
	# Returns potentials given grid, visits to current state, empty stack, and complete state

	grid = randomize_grid()

	P = [[p.copy() for j in range(9)] for i in range(9)]

	# Replace starting cells
	for y in range(len(P)):
		for x in range(len(P[0])):
			if grid[y][x]:
				P[y][x] = grid[y][x]

	# Row rule
	for y in range(len(P)):
		rem = []
		for x in range(len(P[y])):
			k = P[y][x]
			if isinstance(k, int):
				rem.append(k)
		for x in range(len(P[y])):
			if isinstance(P[y][x], int):
				continue
			P[y][x] = [n for n in P[y][x] if n not in rem]

	# Column rule
	for x in range(len(P[0])):
		rem = []
		for y in range(len(P)):
			if isinstance(P[y][x], int):
				rem.append(P[y][x])
		for y in range(len(P)):
			if isinstance(P[y][x], int):
				continue
			P[y][x] = [n for n in P[y][x] if n not in rem]

	# Box rule
	for it in range(3):
		for jt in range(3):
			rem = []
			for y in range(jt * 3, jt * 3 + 3):
				for x in range(it * 3, it * 3 + 3):
					if isinstance(P[y][x], int):
						rem.append(P[y][x])
			for y in range(jt * 3, jt * 3 + 3):
				for x in range(it * 3, it * 3 + 3):
					if isinstance(P[y][x], int):
						continue
					P[y][x] = [n for n in P[y][x] if n not in rem]

	return P

def draw(P):
    screen.fill((255, 255, 255))
    # Draw the lines
        
    for i in range(9):
        for j in range(9):
            if isinstance(P[j][i], int):
 
                # Fill blue color in already numbered grid
                pg.draw.rect(screen, (0, 153, 153), (i * dif, j * dif, dif + 1, dif + 1))
 
                # Fill grid with default numbers specified
                text1 = font1.render(str(P[j][i]), 1, (0, 0, 0))
                screen.blit(text1, (i * dif + 15, j * dif))
            
            else:
            	# Fill grid with potential numbers
            	for p in P[j][i]:
	                txt = font2.render(str(p), 1, (0, 0, 0))
	                x = 17 * ((p % 3 + 2) % 3) + 5
	                y = 17 * (p // 3.1)
	                screen.blit(txt, (i * dif + x, j * dif + y))


    # Draw lines horizontally and vertically to form grid          
    for i in range(10):
        if i % 3 == 0 :
            thick = 7
        else:
            thick = 1
        pg.draw.line(screen, (0, 0, 0), (0, i * dif), (500, i * dif), thick)
        pg.draw.line(screen, (0, 0, 0), (i * dif, 0), (i * dif, 500), thick)
    pg.display.flip()

def find_next(P, potential_count: int = 1) -> tuple:
	# Returns coords of next cell

	for j in range(9):
		for i in range(9):
			if isinstance(P[j][i], list) and len(P[j][i]) == potential_count:
				return (i, j)
	return (-1, -1)

def is_complete(P):
	# Iterate over each cell and check type == list
	for j in range(9):
		for i in range(9):
			if isinstance(P[j][i], list):
				return False
	return True

def collapse(P, x, y):
	# Updates potential placements following the three rules
	# Returns P' or False if invalid
	v = P[y][x] 

	# Row rule
	for i in range(len(P[0])):
		if isinstance(P[y][i], int) or v not in P[y][i]:
			continue
		
		P[y][i].remove(v)
		if len(P[y][i]) == 0:
			return False

	# Column rule
	for j in range(len(P)):
		if isinstance(P[j][x], int) or v not in P[j][x]:
			continue
		
		P[j][x].remove(v)
		if len(P[j][x]) == 0:
			return False

	# Box rule
	it, jt = (x // 3, y // 3)
	for j in range(jt * 3, jt * 3 + 3):
		for i in range(it * 3, it * 3 + 3):
			if isinstance(P[j][i], int) or v not in P[j][i]:
				continue
			
			P[j][i].remove(v)
			if len(P[j][i]) == 0:
				return False
	return P

kek = 0
def solve(P):
	global kek
	# Actualize certain potentials but return if this leads to invalid grid
	P_prime = copy.deepcopy(P)
	x, y = find_next(P)
	while x != -1:
		P_prime[y][x] = P_prime[y][x][0]
		P_prime = collapse(P_prime, x, y)
		if not P_prime:
			return False

		if show:
			process_input(P_prime)

		x, y = find_next(P_prime)

	# Continue with collapsed grid
	P = P_prime

	# Determine if complete
	if is_complete(P):
		kek += 1
		print(kek)
		if kek == 2:
			return True
		return False

	
	# Recursively make a decision over the cell with the least potential

	# Iterate until cell with least potential is found
	x = -1
	i = 1
	while x == -1:
		i += 1
		assert(i < 10)
		
		x, y = find_next(P, i)
		
	# Recursively call solve over possible decisions
	p = P[y][x].copy()
	for v in p:
		# Make tentative assignment
		P[y][x] = v

		# Collapse choice
		P_prime = copy.deepcopy(P)
		P_prime = collapse(P_prime, x, y)

		if show:
			process_input(P_prime)

		# Return if success
		if(solve(P_prime)):
			return True

		# Else fail, and try again
		P[y][x] = p

	# Trigger backtracking
	return False

def process_input(P = None):
	if t and P:
		clock.tick(t)
		draw(P)
		return
	while True:
		event = pg.event.wait()

		if event.type == pg.QUIT:
			pg.quit()
			sys.exit()

		elif event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				pg.quit()
				sys.exit()
			if event.key == pg.K_SPACE and P:
				draw(P)
				print("continue")
				return

				# global done
				# if not done:
				# 	done = step()
				# 	draw()
				# else:
				# 	print("BOARD IS COMPLETE")
			if event.key == pg.K_r:
				P = init()
				global kek
				kek = 0
				draw(P)
				print("reset")
				solve(P)

P = init()
draw(P)
clock = pg.time.Clock()
pg.event.clear()
t = 0
show = True

solve(P)
while True:
	process_input()
    
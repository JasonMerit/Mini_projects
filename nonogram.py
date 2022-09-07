import numpy as np
import pygame as pg
from copy import deepcopy
import sys

"""
Lingo
- Filled is 1, crossed is -1 and empty 0
- Marked is 1 or -1
"""


# H are conditions horizontal conditions and V vertical
# V = [[8, 1], [1, 3, 1], [3, 1], [4], [1, 2], [2, 1], [2, 4], [1, 3, 2], [6, 1, 1], [7, 2]]
# H = [[2,1,3], [1,1,2], [1,1,2], [1,2], [2,3], [3,4], [4,3,1], [1,5,1], [1,2,2,1], [1,2,1,3]] # Heart
V = [[6], [2,3,1], [1,1,3,2,1], [1,1,1,2,2,1], [1,2,1,1,6,1], [1,2,1,3,4], [2,2,8,2,1], [1,1,5,3,2], [1,1,2,3,6], [1,3,1,1,3,4,1],
	[2,1,3,3,5], [1,6,1,3], [4,4], [2,2,1], [2,1,2], [2,2], [2,2], [4], [1,2,1], [2]]
H = [[1,5,2], [2,2,2,1], [3,1,4], [1,3,6,2], [7,5], [2,3,1,1], [4,3,1,1], [2,3,3,2], [1,6,5], [2,1,2,1,1,3],
	[1,1,3,4], [1,1,1,1,2,1], [1,1,1,2,1], [2,2,3], [2,2,4], [2,2,4], [2,2,4], [1,2,4], [2,1,2,1], [2,2,1]] # 1-160
N = len(H)
G = [[0 for i in range(len(V))] for j in range(len(H))]
D = [[], []]  # Keep score of Done lines (H, V)

def action():
	print("next")
	extend()
	fill_gaps()
	fill_overlaps()

def fill_complete():
	# Fill out grid where there are full lines

	# Seek full lines
	full_V = [i for i in range(N) if not (i in D[0]) and sum(V[i]) + len(V[i]) - 1 == N]
	full_H = [i for i in range(N) if not (i in D[1]) and sum(H[i]) + len(H[i]) - 1 == N]
	D[0] += full_V
	D[1] += full_H
	# print(D)

	# Fill out
	for v in full_V:
		y = 0
		for length in V[v]:
			for _ in range(length):
				assert(G[y][v] != -1)
				G[y][v] = 1
				y += 1
			if y != N:
				G[y][v] = -1
			y += 1

	for h in full_H:
		x = 0
		for length in H[h]:
			for _ in range(length):
				assert(G[h][x] != -1)
				G[h][x] = 1
				x += 1
			if x != N:
				G[h][x] = -1
			x += 1

	# Fill in satisfied conditions with -1
	# Find as sum of marked equalling sum of conditions
	# return
	done_V = []
	for i in range(N):
		if i in D[0]:  # Skip completed
			continue

		marked = 0
		for j in range(N):
			marked += G[j][i]

		if marked == sum(V[i]):
			done_V.append(i)

	# Extremely easy for H
	done_H = [i for i in range(N) if not (i in D[1]) and sum(H[i]) == sum(G[i])]

	# Cross out done
	for h in done_H:
		for i, e in enumerate(G[h]):
			if e == 1:
				continue
			G[h][i] = -1

	for v in done_V:
		for j in range(N):
			if G[j][v] == 1:
				continue
			G[j][v] = -1
	
	D[0] += done_V
	D[1] += done_H

def extend():
# def action():
	# Extend edges by seeking in from all sides
	# TODO keep iterating different perspectives until convergence

	# Left-right
	for j in range(N):
		# Continue if done or first empty
		if j in D[1] or G[j][0] == 0:
			continue

		x = 0
		# Starting from crossed shift until filled
		while G[j][x] == -1:
			x += 1

		# Quit if empty start
		if G[j][x] == 0:
			continue

		# Iterate over the horizontal conditions and fill out 
		for length in H[j]:
			# Mark whole length in condition
			while length:
				if G[j][x] == 0:
					G[j][x] = 1
				length -= 1
				x += 1
			
			# Cross out after end
			if x != N:
				G[j][x] = -1
				
				# Iterate over coming crossed
				while x < N and G[j][x] == -1:
					x += 1 

			# Keep going?
			if x == N or G[j][x] == 0:
				break


	# Right-left
	for j in range(N):
		# Continue if done or LAST empty
		if j in D[1]:
			continue

		x = N-1
		# Starting from crossed shift until filled
		while G[j][x] == -1:
			x -= 1

		# Quit if empty start
		if G[j][x] == 0:
			continue

		# Iterate over the horizontal conditions REVERSED and fill out 
		for length in H[j][::-1]:
			# Mark whole length in condition
			while length:
				if G[j][x] == 0:
					G[j][x] = 1
				length -= 1
				x -= 1
			
			# Cross out after end
			if x != -1 and G[j][x] != 1:
				G[j][x] = -1
				
				# Iterate over coming crossed
				while x > 0 and G[j][x] == -1:
					x -= 1 

			# Keep going?
			if x == 0 or G[j][x] == 0:
				break


	# Top-down
	for i in range(N):
		# Continue if done
		if i in D[0]:
			continue

		y = 0
		# Starting from crossed shift until filled
		while G[y][i] == -1:
			y += 1

		# Quit if empty start
		if G[y][i] == 0:
			continue
		
		# Iterate over the vertical conditions and fill out 
		for length in V[i]:
			# Mark whole length in condition
			while length:
				if G[y][i] == 0:
					print(i, y)
					G[y][i] = 1
				length -= 1
				y += 1
			
			# Cross out after end (within bounds)
			if y != N:
				G[y][i] = -1

				# Iterate over coming crossed
				while y < N and G[y][i] == -1:
					y += 1 

			# Keep going?
			if y == N or G[y][i] == 0:
				break
	
	# Bottom-top
	for i in range(N):
		# Continue if done
		if i in D[0]:
			continue
		
		y = N-1
		# Starting from crossed shift until filled
		while G[y][i] == -1:
			y -= 1

		# Quit if empty start
		if G[y][i] == 0:
			continue
		
		# Iterate over the vertical conditions REVERSED and fill out 
		for length in V[i][::-1]:
			# Mark whole length in condition
			while length:
				if G[y][i] == 0:
					G[y][i] = 1
				length -= 1
				y -= 1
			
			# Cross out after end (within bounds)
			if y != -1:
				G[y][i] = -1

				# Iterate over coming crossed
				while y > 0 and G[y][i] == -1:
					y -= 1 

			# Keep going?
			if y == 0 or G[y][i] == 0:
				break

def update_complete():
	done_V = []
	for i in range(N):
		if i in D[0]:  # Skip completed
			continue

		marked = 0
		for j in range(N):
			if G[j][i] != 0:
				marked += 1
		print(i, ")", marked, "==", N)
		if marked == N:
			done_V.append(i)
	print(done_V)

def fill_gaps():
	# If crossed + sum(conditions) = N its complete
	fill_V = []
	for i in range(N):
		if i in D[0]:  # Skip already done
			continue

		crossed = 0
		for j in range(N):
			if G[j][i] == -1:
				crossed += 1
		if crossed + sum(V[i]) == N:
			fill_V.append(i)

	fill_H = [i for i in range(N) if not (i in D[1]) and G[i].count(-1) + sum(H[i]) == N]

	# Fill them
	for v in fill_V:
		for j in range(N):
			if G[j][v] != 0:
				continue
			G[j][v] = 1

	for h in fill_H:
		for i, e in enumerate(G[h]):
			if e != 0:
				continue
			G[h][i] = 1

	D[0] += fill_V
	D[1] += fill_H
	# If count(marked) = sum(conditions) its complete

	cross_V = []
	for i in range(N):
		if i in D[0]:  # Skip already done
			continue

		marked = 0
		for j in range(N):
			if G[j][i] == 1:
				marked += 1
		if marked == sum(V[i]):
			cross_V.append(i)


	cross_H = [i for i in range(N) if not (i in D[1]) and G[i].count(1) == sum(H[i])]

	# Cross them
	for v in cross_V:
		for j in range(N):
			if G[j][v] != 0:
				continue
			G[j][v] = -1

	for h in cross_H:
		for i, e in enumerate(G[h]):
			if e != 0:
				continue
			G[h][i] = -1

	D[0] += cross_V
	D[1] += cross_H

def fill_overlaps():
# def action():
	# Find overlaps from opposing sides

	# Vertical overlaps
	for i in range(N):
		reach = sum(V[i]) + len(V[i]) - 1
		overlap = N - reach
		
		# Is any conditional able to make use of overlap?
		if not any(v > overlap for v in V[i]):
			continue

		# Fíll them from top
		y = overlap
		for length in V[i]:  # [6]
			if length < overlap:
				y += length + 1
				continue
			length -= overlap
			while length and y != N:
				assert(G[y][i] != -1)
				G[y][i] = 1
				length -= 1
				y += 1

			if y != N:
				y += 1 + overlap
	
	# Horizontal overlaps
	for j in range(N):
		reach = sum(H[j]) + len(H[j]) - 1
		overlap = N - reach
		
		# Is any conditional able to make use of overlap?
		if not any(h > overlap for h in H[j]):
			continue
		
		# Fíll them from left
		x = overlap
		for length in H[j]:
			if length < overlap:
				x += length + 1
				continue
			length -= overlap
			while length and x != N:
				assert(G[j][x] != -1)
				G[j][x] = 1
				length -= 1
				x += 1

			if x != N:
				x += 1 + overlap



def show():
	print(np.array(G))


fill_complete()
# fill_overlaps()
# extend()
# extend()
# extend()
# fill_gaps()
# fill_gaps()
# fill_gaps()
# print(D)




# sys.exit()

dif = 500 * 0.8 / N 
offset = 500 / 2 - dif * N / 2
screen = pg.display.set_mode([500, 600])

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (199, 80, 80)

pg.display.set_caption('Nonogram')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

history = [deepcopy(G)]  # State history
h = 0
def draw():
	screen.fill(BLUE)

	# Draw lines horizontally and vertically to form grid
	for i in range(N + 1):
		thickness = 2 if i % 5 == 0 else 1
		pg.draw.line(screen, BLACK, (offset, offset + i * dif), (offset + dif * N, offset + i * dif), thickness)
		pg.draw.line(screen, BLACK, (offset + i * dif, offset), (offset + i * dif, offset + dif * N), thickness)
	
	# Draw numbers
	screen.blit(font1.render(str(h), 1, BLACK), (14, 3))
	forset = 25
	for i in range(N):
		txt = font2.render(str(i), 1, BLACK)
		screen.blit(txt, (2.5*forset + i * dif, forset))
		screen.blit(txt, (forset, 2.5*forset + i * dif))

	# Draw squares
	for i in range(N):
		for j in range(N):
			match G[i][j]:
				case 0:
					continue

				case 1:
					rect = pg.Rect(offset + j * dif, offset + i * dif, dif, dif)
					pg.draw.rect(screen, BLACK, rect)

				case -1:
					pg.draw.line(screen, BLACK, (offset + j * dif, offset + i * dif), \
								(offset + (j + 1) * dif, offset + (i + 1) * dif), 3)
					pg.draw.line(screen, BLACK, (offset + j * dif, offset + (i + 1) * dif), \
								(offset + (j + 1) * dif, offset + i * dif), 3)

	pg.display.flip()

def process_input():
	global h, G, history
	while True:
		event = pg.event.wait()

		if event.type == pg.QUIT:
			pg.quit()
			sys.exit()

		elif event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				pg.quit()
				sys.exit()
			if event.key == pg.K_SPACE:
				if h == len(history)-1:
					action()

					if history[h] != G:
						history.append(deepcopy(G))
						h += 1
				else:
					G = history[h+1]
					h += 1
			
			if event.key == pg.K_RIGHT:
				if h < len(history)-1:
					h += 1
					G = history[h]
			elif event.key == pg.K_LEFT:
				if h > 0:
					h -= 1
					G = history[h]

			draw()
			


draw()
process_input()
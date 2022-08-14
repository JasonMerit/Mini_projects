import math
import numpy as np
from Othello import OthelloBoard
from copy import deepcopy


class AlphaBeta():

	def policy(self, board, player):
		value = sum(sum(board.board, []))
		return value * player

	def alpha_beta(self, board, depth, alpha, beta, turn):
		pass

	def mini_max(self, board, depth, player):
		process_input()
		print("kek")
		# Assumes black is maximizing
		if depth == 0:
			return self.policy(board, player), None

		# Determine possible moves for player
		moves = []
		if player == -1:
			moves = board.generate_moves()

		else:
			board.reverse()
			moves = board.generate_moves()
			board.reverse()

		if len(moves) == 0: # This is accounted for in OthelloBoard.step()
			pass

		# Explore all moves and determine best
		if player == -1:
			max_score = -1000
			return_move = None

			pre_board = deepcopy(board.board)
			# Make move, determine score, and reset board to before move was taken
			for move in moves:
				new_board, kek = board.move(move[0], move[1], player)

				score, m = self.mini_max(board, depth - 1, -player)
				board.board = pre_board

				if score > max_score:
					max_score = score
					reutrn_move = move

			return max_score, return_move

		min_score = 1000
		return_move = None

		pre_board = deepcopy(board.board)
		# Make move, determine score, and reset board to before move was taken
		for move in moves:
			new_board, kek = board.move(move[0], move[1], player)

			score, m = self.mini_max(board, depth - 1, -player)
			board.board = pre_board

			if score < min_score:
				min_score = score
				reutrn_move = move
				
		return min_score, return_move






AB = AlphaBeta()




import pygame as pg
import sys

screen = pg.display.set_mode([500, 600])

dif = 500 / 8
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 144, 103)

pg.display.set_caption('OthelloAI')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)
pg.event.clear()

OB = OthelloBoard()

def draw():
	screen.fill(GREEN)

	# Draw lines horizontally and vertically to form grid
	for i in range(9):
		pg.draw.line(screen, BLACK, (0, i * dif), (500, i * dif), 1)
		pg.draw.line(screen, BLACK, (i * dif, 0), (i * dif, 500), 1)

	# Draw circle hints
	pg.draw.circle(screen, BLACK, (125, 125), 4)
	pg.draw.circle(screen, BLACK, (125, 375), 4)
	pg.draw.circle(screen, BLACK, (375, 125), 4)
	pg.draw.circle(screen, BLACK, (375, 375), 4)
	
	# Draw disks
	b = OB.board
	for j in range(8):
		for i in range(8):
			if b[j][i] == 0:
				continue

			if b[j][i] == 1:
				pg.draw.circle(screen, WHITE, (i * dif + dif / 2, j * dif + dif / 2), 25)
			else:
				pg.draw.circle(screen, BLACK, (i * dif + dif / 2, j * dif + dif / 2), 25)

	# Draw potential moves
	p = OB.generate_moves()
	for x, y in p:
		pg.draw.circle(screen, BLACK, (x * dif + dif / 2, y * dif + dif / 2), 25, 1)

	# Draw who's turn it is
	color = WHITE if OB.turn == 1 else BLACK
	pg.draw.circle(screen, color, (50, 550), 25)

	# Draw lead
	lead = sum(sum(OB.board, []))
	colors = (WHITE, BLACK) if lead > 0 else (BLACK, WHITE)
	lead = str(abs(lead))
	pg.draw.circle(screen, colors[0], (450, 550), 25)	
	txt = font1.render(lead, 1, colors[1])
	screen.blit(txt, (437 - (len(lead) - 1) * 9, 520))



	pg.display.flip()

def process_input():
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
				# a = (np.random.randint(8), np.random.randint(8))
				# state = OB.step(a)
				# while not state[0]: # Loop until valid move
				# 	a = (np.random.randint(8), np.random.randint(8))
				# 	state = OB.step(a)
				# if state[2]:
				# 	print("Reward: ", state[1])
				# 	OB.reset()

				return

			if event.key == pg.K_r:
				OB.reset()

			if event.key == pg.K_w:
				print(OB.find_winner())
			if event.key == pg.K_k:
				OB.reverse()

			draw()
			return

		elif event.type == pg.MOUSEBUTTONDOWN:
			pos = pg.mouse.get_pos()
			x, y = int(pos[0] // 62.5), int(pos[1] // 62.5)
			state = OB.step([x, y])
			if state[2]:
				print("Reward: ", state[1])
				OB.reset()

			draw()
			return

draw()

AB.mini_max(OB, 3, OB.turn)

# while True:
# 	process_input()
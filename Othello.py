# https://github.com/oliverzhang42/reinforcement-learning-othello/blob/master/OthelloBoard.py
from copy import deepcopy


class OthelloBoard():

	dirx = [-1, 0, 1, -1, 1, -1, 0, 1]
	diry = [-1, -1, -1, 0, 0, 1, 1, 1]

	def __init__(self):
		self.reset()

	def reset(self):
		self.board = [[0 for i in range(8)] for j in range(8)]
		self.board[4][4] = 1
		self.board[3][4] = -1
		self.board[4][3] = -1
		self.board[3][3] = 1

		self.turn = -1
		self.pass_counter = 0

	def move(self, x, y, player): # Assumes valid position

		b = self.board
		tot = 0 # Total number of pieces captured

		b[y][x] = player

		for d in range(8): # 8 directions
			ctr = 0 # Captured pieces along d direction
			
			for i in range(8): # board size
				dx = x + self.dirx[d] * (i + 1)
				dy = y + self.diry[d] * (i + 1)
				
				if dx < 0 or dx > 7 or dy < 0 or dy > 7:
					ctr = 0; break
				elif b[dy][dx] == player:
					break
				elif b[dy][dx] == 0:
					ctr = 0; break
				else:
					 ctr += 1

			for i in range(ctr):
				dx = x + self.dirx[d] * (i + 1)
				dy = y + self.diry[d] * (i + 1)
				b[dy][dx] = player
			tot += ctr

		return (b, tot)


	def test_move(self, b, x, y, player): # Assumes valid position

		tot = 0 # Total number of peices captured

		b[y][x] = player

		for d in range(8): # 8 directions
			ctr = 0 # Captured pieces along d direction
			
			for i in range(8): # board size
				dx = x + self.dirx[d] * (i + 1)
				dy = y + self.diry[d] * (i + 1)
				
				if dx < 0 or dx > 7 or dy < 0 or dy > 7:
					ctr = 0; break
				elif b[dy][dx] == player:
					break
				elif b[dy][dx] == 0:
					ctr = 0; break
				else:
					 ctr += 1

			for i in range(ctr):
				dx = x + self.dirx[d] * (i + 1)
				dy = y + self.diry[d] * (i + 1)
				b[dy][dx] = player
			tot += ctr

		return (b, tot)


	def valid_move(self, x, y, player):
		# Invalid if out of bounds, occupied, or results in zero captures

		if x < 0 or x > 7 or y < 0 or y > 7:
			return False
		if self.board[y][x] != 0:
			return False
		kek, tot = self.test_move(deepcopy(self.board), x, y, player)
		if tot == 0:
			return False
		return True


	def generate_moves(self):
		# Test each position for valid move

		possible_moves = []

		for j in range(8):
			for i in range(8):
				if self.valid_move(i, j, self.turn):
					possible_moves.append((i, j))
		return possible_moves

	def reverse(self):
		d = {1: -1, 0: 0, -1: 1}

		for j in range(8):
			for i in range(8):
				self.board[j][i] = d[self.board[j][i]]

	def find_winner(self):
		# Return True if 1 (White) wins

		count = sum(sum(self.board, []))
		if count > 0:
			return 1
		if count < 0:
			return -1
		return 0


	def step(self, action):
		# @returns observation, reward, done, info
		x, y = action[0], action[1]
		reward = 0
		done = False

		# Determine if any move is possible
		if len(self.generate_moves()) == 0: 
			# Pass
			self.turn *= -1
			self.pass_counter += 1

			if self.pass_counter == 2:
				# Both players pass
				done = True
				reward = self.find_winner()

			return deepcopy(self.board), reward, done, {}

		# Invalid move rewards other player wins (how is invalid move possible? - Agent doesn't know rules)
		if not self.valid_move(x, y, self.turn):
			done = True
			reward = -1 * self.turn
			return [], reward, done, {}

		else:
			self.pass_counter = 0
			self.move(x, y, self.turn)
			self.turn *= -1
			return deepcopy(self.board), reward, done, {}

		







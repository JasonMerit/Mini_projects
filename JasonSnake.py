"""
Script implementing snake environment using vectors 
to store positions and deque for quick popping and appending.
Todo: 
 - Playback (Seed, actions)
"""

import sys, random
import pygame as pg
import numpy as np
from collections import deque
from gym import logger, spaces

WHITE, GREY, BLACK = (240, 240, 240),  (200, 200, 200), (0, 0, 0)
YELLOW, RED = (200, 200, 0), (200, 0, 0) 
MOVE = [pg.K_RIGHT, pg.K_UP, pg.K_LEFT, pg.K_DOWN]
STEP = [pg.K_UP, pg.K_LEFT, pg.K_RIGHT]

pg.init()
pg.display.set_caption('SnakeAI')
pg.font.init()

class Screen():

	def __init__(self, W, H):
		self.size = 24
		self.W, self.H = W, H
		self.screen = pg.display.set_mode([W * self.size, H * self.size])
		self.font = pg.font.Font(None, 25)
		self.reset()

	def _draw_rect(self, point, color):
		pos = point * self.size
		rect = pg.Rect(pos.x+1, pos.y+1, self.size-2, self.size-2)
		pg.draw.rect(self.screen, color, rect, 0)
		pg.display.update(rect)

	def render(self, head, fruit, clear=None):
		# Assumes Vector2D args
		self._draw_rect(head, YELLOW)

		if fruit != self.fruit:
			self.fruit = fruit
			self._draw_rect(fruit, RED)

		if clear:
			self._draw_rect(clear, BLACK)
			

	def reset(self, snake=None, fruit=None):
		self.screen.fill(BLACK)
		pg.display.flip()

		if not snake:
			self.fruit = Vector2D((-1, -1))  # Must be Vector2D type
		else:
			for s in snake:
				self._draw_rect(s, YELLOW)
			self._draw_rect(fruit, RED)

	def win(self, head):
		# self.screen.fill(YELLOW)
		self._draw_rect(head, YELLOW)

		text = self.font.render("You win!", True, BLACK)
		SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.get_surface().get_size()
		text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
		self.screen.blit(text, text_rect)

		pg.display.flip()

class Vector2D():

	def __init__(self, point):
		self._x, self._y = point
		self._p = self._y, self._x  # State indexing

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	@property
	def p(self):
		return self._p
	
	@x.setter
	def x(self, v):
		self._x = v
		self._p = self._p[0], v

	@y.setter
	def y(self, v):
		self._y = v
		self._p = v, self._p[1]

	@p.setter
	def p(self, tp):
		self._x, self._y = tp
		self._p = self._y, self._x

	def __repr__(self):
		return str((self.x, self.y))

	def __add__(self, o):
		return Vector2D((self.x + o.x, self.y + o.y))

	def __mul__(self, k):
		return Vector2D((k*self.x, k*self.y))

	# def __rmul__(self, o):
	# 	return self.x*o.x + self.y*o.y

	def __eq__(self, o):
		return self.x == o.x and self.y == o.y

class Snake():
	# Contains a deque of Vector2D for snake
	# Represents state as ndarray image

	def __init__(self, dim=(10, 10), seed=None, rendering=True, absolute_movement=False, wrap=False, 
				auto=False, ai=True, fps=30, rewards=(0, 1.0, 1.0)):
		self.W, self.H, = dim
		self.rendering = rendering
		self.penalty, self.reward_fruit, self.reward_win = rewards
		self.absolute_movement = absolute_movement if not auto else False
		self.wrap = wrap; self.fps = fps
		self.rng = random.Random(seed)  # Accepts None!

		self.directions = [Vector2D((1, 0)), Vector2D((0, -1)),  # RIGHT, UP
						   Vector2D((-1, 0)), Vector2D((0, 1))]  # LEFT, DOWN
		self.rel_directions = [0, 1, -1]  # Forward, Left, Right			 

		self.start = (self.W // 2, self.H // 2)
		self.points = []

		self.action_space = spaces.Discrete(2)
        # self.observation_space = spaces.Box(-high, high, dtype=np.float32)

		if rendering:
			self.screen = Screen(self.W, self.H)

		self.reset()
		if auto:
			self._auto()
		elif not ai:
			while True:
				self.process_input()

	def __iter__(self):
		for point in self.points:
			yield point

	def __len__(self):
		return len(self.points)

	def __repr__(self):
		return str(self.points)

	def _auto(self):
		clock = pg.time.Clock()

		while True:
			clock.tick(self.fps)
			s, r, done = self.step(self.sample())
			# print(s, r)
			self.process_input()

	def _move(self, direction):
		# Determine new head position and translate
		# @Returns: head, fruit, clear, reward, terminated
		
		# Get new head, wrap and check collision
		head = self.points[-1] + self.directions[direction]  # new head = last element + direction
		if self.wrap:  # Wrapping
			if head.x < 0: head.x = self.W-1
			elif head.x >= self.W: head.x = 0
			if head.y < 0: head.y = self.H-1
			elif head.y >= self.H: head.y = 0
		terminated = self._is_collide(head)  # Call before appending head

		if terminated:
			self.done = True
			return head, self.fruit, None, 0, terminated
		
		# Translate body by appending new head and removing
		# tail, if no fruit otherwise keep tail. 		
		self.points.append(head)
		self.facing = direction

		reward = 0
		clear = None
		if head == self.fruit: # Munched fruit!
			if len(self) != self.H * self.W:
				self.fruit = self._place_fruit()
				reward = self.reward_fruit
			else: 	# Snake full length
				self.state = np.ones((self.W, self.H), dtype=int)

				if self.rendering:
					self.screen.win(head)

				return head, self.fruit, None, self.reward_win, True
		else:
			clear = self.points.pop(0)
			reward = self.penalty

		if self.rendering:
			self.screen.render(head, self.fruit, clear)

		self.t += 1
		# if self.t % 1000 == 0: print(f't = {self.t}')

		return head, self.fruit, clear, reward, terminated

	def step(self, action=0):
		# Take action and updates state.
		# @Params: relative move direction
		# @Returns: state, reward, done

		# Convert action to absolute and move
		a = self.rel_directions[action]
		a = (self.facing + a) % 4  
		head, fruit, clear, reward, terminated = self._move(a)

		# Update state accordingly
		if not terminated:	
			self.state[head.p] = 1
			self.state[fruit.p] = 2
			if clear:
				self.state[clear.p] = 0

		return self.state, reward, terminated

	def sample(self):
		# Todo: Use gyms action space instead
		return self.rng.randint(0,2)

	def reset(self):
		self.done = False
		self.facing = 1  # Start facing up
		self.points.clear()
		state = np.zeros((self.H, self.W), dtype=int)				   
		
		head = Vector2D(self.start)
		self.points.append(head)
		self.fruit = self._place_fruit()

		state[head.p] = 1
		state[self.fruit.p] = 2

		if self.rendering:
			self.screen.reset()
			self.screen.render(head, self.fruit)
		
		self.state = state
		self.t = 0
		return state

	def close(self):
		pg.display.quit()
		pg.quit()
		sys.exit()

	def _place_fruit(self):
		place = lambda: Vector2D((self.rng.randint(0, self.W-1), self.rng.randint(0, self.H-1)))
		point = place()
		while point in self.points:
			point = place()

		return point

	def _is_collide(self, head):
		# Colliding with self or OOB.
		return head in self.points or head.x < 0 or head.x >= self.W or head.y < 0 or head.y >= self.H


	def process_input(self):
		# event = pg.event.wait()
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.close()

			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					self.close()

				if event.key == pg.K_r:
					self.reset()
				if event.key == pg.K_SPACE:
					self.rendering = not self.rendering
					if self.rendering:
						self.screen.reset(self, self.fruit)

				if self.absolute_movement:
					if event.key in MOVE:
						self._move(MOVE.index(event.key))
				else:
					if event.key in STEP:
						obs = self.step(STEP.index(event.key))



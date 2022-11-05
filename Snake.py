"""
Script implementing snake environment using vectors 
to store positions and deque for quick popping and appending.
Todo: 
 - Playback (Seed, actions)
 - Limit global clutter
"""

import sys, random
import pygame as pg
import numpy as np
from collections import deque
from gym import logger, spaces

WHITE, GREY, BLACK = (240, 240, 240),  (200, 200, 200), (0, 0, 0)
YELLOW, RED = (200, 200, 0), (200, 0, 0) 

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
		rect = pg.Rect(pos.x, pos.y, self.size, self.size)
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

	def win(self):
		self.screen.fill(YELLOW)

		text = self.font.render("You win!", True, BLACK)
		SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.get_surface().get_size()
		text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
		self.screen.blit(text, text_rect)

		pg.display.flip()

class Vector2D():

	def __init__(self, point):
		self.x, self.y = point
		self.p = self.y, self.x  # State indexing

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

	def __init__(self, dim=(10, 10), seed=None, rendering=True, rewards=(0, 1.0, 1.0)):
		self.W, self.H, = dim
		self.rendering = rendering
		self.penalty, self.reward_fruit, self.reward_win = rewards
		
		if seed:
			self.rng = random.Random(seed)

		self.directions = [Vector2D((1, 0)), Vector2D((0, -1)),  # RIGHT, UP
						   Vector2D((-1, 0)), Vector2D((0, 1))]  # LEFT, DOWN
		self.rel_directions = [0, 1, -1]  # Forward, Left, Right			 

		self.start = (self.W // 2, self.H // 2)
		self.points = deque()

		if rendering:
			self.screen = Screen(self.W, self.H)

		self.reset()

	def __iter__(self):
		for point in self.points:
			yield point

	def __len__(self):
		return len(self.points)

	def step(self, action=0):
		# Relative movement. Updates state.
		# @Returns: state, reward, done
		k = self.rel_directions[action]
		head, fruit, clear, reward, terminated = self._move((self.facing + k) % 4)
		
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
		return state

	def _place_fruit(self):
		place = lambda: Vector2D((self.rng.randint(0, self.W-1), self.rng.randint(0, self.H-1)))
		point = place()
		while point in self.points:
			point = place()

		return point

	def _is_collide(self, head):
		# Colliding with self or OOB. 
		return head in self.points or head.x < 0 or head.x >= self.W or head.y < 0 or head.y >= self.H

	def _move(self, direction):
		# Check collision, pushfront new head position and change facing. 
		# Also remove tail if not eat fruit and draw changes.
		# @Returns: head, fruit, clear, reward, terminated
		# if self.done:
		# 	print("OOFED")
		# 	return 
		head = self.points[0] + self.directions[direction]
		terminated = self._is_collide(head)  # Call before appending head
		
		
		if terminated:
			self.done = True
			return head, self.fruit, None, 0, terminated

		self.points.appendleft(head)
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
					self.screen.win()

				return head, self.fruit, None, self.reward_win, True
		else:
			clear = self.points.pop()
			reward = self.penalty

		if self.rendering:
			self.screen.render(head, self.fruit, clear)

		return head, self.fruit, clear, reward, terminated

	def process_input(self):
		# event = pg.event.wait()
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.display.quit()
				pg.quit()
				sys.exit()

			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					pg.display.quit()
					pg.quit()
					sys.exit()

				if event.key == pg.K_r:
					self.reset()
				if event.key == pg.K_SPACE:
					self.rendering = not self.rendering
					if self.rendering:
						self.screen.reset(self, self.fruit)

				if absolute:
					if event.key in movement:
						self._move(movement.index(event.key))
				else:
					if event.key in stepment:
						obs = self.step(stepment.index(event.key))

absolute = True
render = True
seed = random.randrange(sys.maxsize)
movement = [pg.K_RIGHT, pg.K_UP, pg.K_LEFT, pg.K_DOWN]
stepment = [pg.K_UP, pg.K_LEFT, pg.K_RIGHT]
snake = Snake((5, 5), seed=seed, rendering=render)

# while True:
	# snake.process_input()

clock = pg.time.Clock()

done = False
r = 0
while True:
	# clock.tick(10)
	# s, r, done = snake.step(snake.sample())
	snake.process_input()
	# print(s, r)

"""
Script implementing snake environment using vectors 
to store positions and deque for quick popping and appending.
"""

import sys
import pygame as pg
import random
from collections import deque

class Vector2D():

	def __init__(self, x, y):
		self.x, self.y = x, y
		self.p = (y, x)  # Used by board indexing

	def __repr__(self):
		return str((self.x, self.y))

	def __add__(self, o):
		return Vector2D(self.x + o.x, self.y + o.y)

	def __eq__(self, o):
		return self.x == o.x and self.y == o.y


class Snake():
	# Contains a deque of Vector2D for snake and numpy 2darray for board

	def __init__(self, points, dim=(10, 10), seed=None):
		self.W, self.H = dim
		if seed:
			random.seed = seed

		self.facing = 0						
		self.directions = [Vector2D(-1, 0), Vector2D(0, -1),  # UP, LEFT
						   Vector2D(1, 0), Vector2D(0, 1)]    # DOWN, RIGHT

		self.points = deque()
		if points:
			for y, x in points:
				self.points.append(Vector2D(y, x))

		self._place_fruit()

	def __repr__(self):
		return " -> ".join(str(p) for p in self.points)

	def __iter__(self):
		for point in self.points:
			yield point

	def _place_fruit(self):
		point = Vector2D(random.randint(0, self.H), random.randint(0, self.W))
		while point in self.points:
			point = Vector2D(random.randint(0, self.H), random.randint(0, self.W))

		self.fruit = point

	def _is_collide(self, head):
		# Colliding with self or OOB. 
		return head in self.points or head.x < 0 or head.x >= self.W or head.y < 0 or head.y >= self.H

	def _move(self, direction):
		# Check collistion, pushfront new head position and change facing. 
		# Also remove tail if not eat fruit.
		# Returns True if dead
		head = self.points[0] + self.directions[direction]
		
		if self._is_collide(head):
			print("OOF")
			return True

		self.points.appendleft(head)
		self.facing = direction
		
		if head != self.fruit:
			self.points.pop()
		else:
			self.place_fruit()

		print(self)

	def step(self, action=0):
		# 0: forward, 1: left, 2: right

		# Determine direction from facing
		self._move(0)



snake = Snake([(5, 5), (6, 5)])
print(snake)


snake._move(0)
snake._move(0)
snake._move(0)
snake._move(0)
snake._move(0)
snake._move(0)

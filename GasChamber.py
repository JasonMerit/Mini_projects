"""Simulate a gas chamber experiment confined within a circle that expands and contracts."""

import pygame as pg
import numpy as np
from random import randint, random
from math import pi, sqrt, cos, sin

pg.init()

W, H = 800, 800
size = 1
screen = pg.display.set_mode((W * size, H * size))
pg.display.set_caption('Gas Chamber')
clock = pg.time.Clock()


# ---------- Constants --------
WHITE, GREY, BLACK = (255, 255, 255),  (200, 200, 200), (0, 0, 0)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
FPS = 60
R = 100
EXTERNAL_FORCE = 1.0
BALL_COUNT = 20

# ---------- Variables --------
running = True

# ---------- Helper Functions --------
magnitude = lambda v: sqrt(v[0]**2 + v[1]**2)

# ---------- Classes --------

class Ball:

    def __init__(self, pos, vel, r):
        self.r = r
        self.x, self.y = pos
        self.dx, self.dy = vel
        self.color = (magnitude((self.dx, self.dy)) * 50, 0, 0)
    
    def update(self):
        self.move()
        self.draw()

    def move(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        pg.draw.circle(screen, self.color, (self.x, self.y), self.r)
    
    def rebound(self, dx, dy):
        # Change velocity
        self.dx = dx
        self.dy = dy
        self.color = (magnitude((dx, dy)) * 50, 0, 0)

    def collide(self, other):
        # Collision check
        d = sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        return d <= self.r + other.r

class Chamber:

    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x, self.y = W * size // 2, H * size // 2
        self.temp = 0
        self.dx, self.dy = 0, 0
        self.r = R
        self.balls = []
        for _ in range(BALL_COUNT):
            self.balls.append(Ball(self.random_position(), (random() * 6 - 3, random() * 6 - 3), 4))
    
    def random_position(self):
        # random position within the circular chamber
        v = 2 * pi * random()
        r = self.r * sqrt(random())
        x = r * cos(v) + self.x - 2
        y = r * sin(v) + self.y - 2
        return x, y

    def update(self):
        for i, ball in enumerate(self.balls):
            ball.update()
            if amount := self.collide_ball(ball):  # Collide with chamber
                self.expand(amount)
                self.brownian_motion(ball.dx, ball.dy)
            for other in self.balls[i+1:]: # Collide with other balls
                if ball.collide(other):
                    # elastic collision
                    temp = ball.dx, ball.dy
                    ball.rebound(other.dx, other.dy)
                    other.rebound(temp[0], temp[1])
        self.contract()
        self.move()
        self.draw()
    
    def move(self): # Move chamber
        self.x += self.dx * 0.01
        self.y += self.dy * 0.01

    def draw(self):
        screen.fill(GREY)

        pg.draw.circle(screen, BLACK, (self.x, self.y), self.r, int(self.r))
        for ball in self.balls:
            ball.draw()
        pg.display.flip()
    
    def collide_ball(self, ball):
        # Collide with chamber
        dx = self.x - ball.x
        dy = self.y - ball.y
        d = sqrt(dx ** 2 + dy ** 2)
        if d > self.r - ball.r:
            # Calculate new velocity
            v = (ball.dx, ball.dy)
            n = (dx, dy)
            v = self.reflect(v, n)
            ball.rebound(v[0], v[1])
            return magnitude(v)
            return np.dot(v, n) * 0.01

    def reflect(self, v, n):
        """Reflect vector v about normal n."""
        n = (n[0] / sqrt(n[0] ** 2 + n[1] ** 2), n[1] / sqrt(n[0] ** 2 + n[1] ** 2))
        v = (v[0] - 2 * (v[0] * n[0] + v[1] * n[1]) * n[0], v[1] - 2 * (v[0] * n[0] + v[1] * n[1]) * n[1])
        return v
        

    def expand(self, amount=1):
        self.r += amount

    def contract(self):
        self.r -= EXTERNAL_FORCE
    
    def brownian_motion(self, dx, dy):
        self.dx -= dx
        self.dy -= dy

    def collide_wall(self):
        if self.x < self.r or self.x > W * size - self.r:
            self.dx *= -1
        if self.y < self.r or self.y > H * size - self.r:
            self.dy *= -1

    def add_ball(self, pos):
        self.balls.append(Ball(pos, (random() * 6 - 3, random() * 6 - 3), 4))

    def remove_ball(self):
        if self.balls:
            self.balls.pop()



def process_events():
    global running
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                chamber.add_ball(event.pos)
            elif event.button == 3:
                chamber.remove_ball()
        if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_r:
                    chamber.reset()

# ---------- Main Loop --------
if __name__ == '__main__':
    chamber = Chamber()
    while running:
        process_events()
        chamber.update()
        clock.tick(FPS)
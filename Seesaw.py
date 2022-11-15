"""Simulate seesaw with two masses."""
import pygame as pg
from math import *

pg.init()

W, H = 400, 400
size = 1
screen = pg.display.set_mode((W * size, H * size))
pg.display.set_caption('Seesaw')
clock = pg.time.Clock()

# ---------- Constants --------
WHITE, GREY, BLACK = (255, 255, 255),  (200, 200, 200), (0, 0, 0)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
FPS = 60

# ---------- Variables --------
running = True

# ---------- Helper Functions --------

# ---------- Classes --------
class Seesaw:
    def __init__(self, x, y, w, h, m1, m2):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.m1 = m1
        self.m2 = m2
        self.a = 0
        self.ang = 0
        self.ang_vel = 0
        self.ang_acc = 0.0001
        self.ang_friction = 0.999
        self.ang_gravity = 0.1
        self.color = (255, 255, 255)

    def update(self):
        self.draw()
        self.move()

    def draw(self):
        print(self.ang)
        """Draw the seesaw using its angle."""
        left_x = self.x + self.w // 2 - self.w // 2 * cos(self.ang)
        left_y = self.y + self.h // 2 - self.w // 2 * sin(self.ang)
        right_x = self.x + self.w // 2 + self.w // 2 * cos(self.ang)
        right_y = self.y + self.h // 2 + self.w // 2 * sin(self.ang)
        pg.draw.line(screen, self.color, (left_x, left_y), (right_x, right_y), 5)
        pg.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))

    def move(self):
        self.ang += self.ang_vel
        self.ang_vel += self.ang_acc
        self.ang_acc *= self.ang_friction
        self.ang_acc += self.ang_gravity

    def apply_force(self, force):
        self.ang_acc += force
    

# ---------- Main Loop --------
seesaw = Seesaw(100, 100, 200, 20, 10, 10)
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False

    seesaw.update()
    pg.display.update()





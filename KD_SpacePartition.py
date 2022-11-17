from VectorMath import V
import pygame as pg
import math
import random
"""Uniform Grid Partition collision detection algorithm"""
import numpy as np
from random import randint

# grid = [[ randint(0,4) for x in range(0,4)] for y in range(0,4)]
# print(grid)
# quit()
pg.init()
pg.font.init()
pg.display.set_caption("KD_Space_Partition")
W, H = 800, 600
count = 20
win = pg.display.set_mode((W, H))
font = pg.font.SysFont('Calibri', 15)
# random.seed(1122)
RED, BLUE = (255,0,0), (0,0,255)

class Ball:
    def __init__(self, pos, vel, acc, radius, color):
        self.p = V(pos)
        self.v = V(vel)
        self.a = V(acc)
        self.r = radius
        self.color = color

        self.m = self.r ** 2
    
    def draw(self, win, color, n=-1):
        pg.draw.circle(win, color, tuple(self.p), self.r)
        # draw number
        if n != -1:
            textsurface = font.render(str(n), False,(255, 255, 255))
            win.blit(textsurface, tuple(self.p - V((3,7))))

        
    
    def __repr__(self) -> str:
        return str(self.p)

# 10 balls
balls = []
r = 10
for _ in range(count):
    pos = (random.randint(r, W-r), random.randint(r, H-r))
    ball = Ball(pos, (0, 0), (0, 0), r, (255, 0, 0))
    ball.draw(win, RED)
    balls.append(ball)


potential_collisions=set()
D = ["Vertical", "Horizontal"]

def kd_partition(balls, depth=0):
    
    # sort balls by x or y
    axis = depth % 2
    balls.sort(key=lambda ball: ball.p[axis])

    textsurface = font.render(D[axis], False,(255, 255, 255))
    win.blit(textsurface, (10, 10))
    for i, ball in enumerate(balls):
        ball.draw(win, BLUE, i)
    pg.display.update()
    win.fill((0,0,0))  # TURN OFF TO SEE PRIORS

    while True:
        # wait for pg event
        event = pg.event.wait()
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()
            else:
                for i, ball in enumerate(balls):
                    ball.draw(win, RED)
                break
    
    if len(balls) < 2:
        return

    # split balls into two groups
    mid = len(balls) // 2
    a, b = balls[mid-1], balls[mid]
    
    # compare median balls for potential collision
    if abs(a.p[axis] - b.p[axis]) < a.r + b.r:
        potential_collisions.add((a, b))

    # draw split according to axis
    if axis == 0:
        A = (b.p.x - a.p.x) / 2 + a.p.x
        pg.draw.line(win, (255, 255, 255), (A, 0), (A, H))
    else:
        A = (a.p.y - b.p.y) / 2 + b.p.y
        pg.draw.line(win, (255, 255, 255), (0, A), (W, A))

    kd_partition(balls[:mid])
    kd_partition(balls[mid:])

     

pg.display.update()
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()

    

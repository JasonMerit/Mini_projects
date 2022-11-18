from VectorMath import V
import pygame as pg
import math
import random
"""Uniform Grid Partition collision detection algorithm"""
import numpy as np
from random import randint

pg.init()
pg.font.init()
pg.display.set_caption("Bounding Volume Hierarchies")
W, H = 800, 600
count = 5
win = pg.display.set_mode((W, H))
font = pg.font.SysFont('Calibri', 15)
clock = pg.time.Clock()
random.seed(11)
WHITE, GREY, BLACK = (255, 255, 255), (128, 128, 128), (0, 0, 0)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
KEK = 0
render = True

class Ball:
    def __init__(self, pos: tuple, vel: tuple, acc: tuple, radius, color):
        self.p = V(pos)
        self.v = V(vel)
        self.a = V(acc)
        self.r = radius
        self.color = color

        self.m = self.r ** 2
    
    @property
    def x(self):
        return self.p.x
    
    @property
    def y(self):
        return self.p.y
    
    @property
    def left(self):
        return self.p.x - self.r
    
    @property
    def right(self):
        return self.p.x + self.r
    
    @property
    def top(self):
        return self.p.y - self.r
    
    @property
    def bot(self):
        return self.p.y + self.r
    
    @property
    def rect(self):
        return pg.Rect(self.left, self.top, self.r*2, self.r*2)
    
    def draw(self, win, color=None, n=-1):
        if color is None:
            color = self.color
        pg.draw.circle(win, color, tuple(self.p), self.r)
        # draw number
        if n != -1:
            textsurface = font.render(str(n), False,(255, 255, 255))
            win.blit(textsurface, tuple(self.p - V((3,7))))
    
    def collides_with(self, other):
        return self.p.dist_squared(other.p) < (self.r + other.r) ** 2

    def __repr__(self) -> str:
        return str(self.p)

def get_balls():
    balls = []
    r = 50
    for _ in range(count):
        pos = (random.randint(r, W-r), random.randint(r, H-r))
        ball = Ball(pos, (0, 0), (0, 0), r, (255, 0, 0))
        ball.draw(win, RED)
        balls.append(ball)
    return balls


def bvh_partition(balls, depth=0):
    
    # sort balls by axis
    axis = depth % 2
    balls.sort(key=lambda ball: ball.p[axis])

    # textsurface = font.render(D[axis], False,(255, 255, 255))
    # win.blit(textsurface, (10, 10))
    for i, ball in enumerate(balls):
        ball.draw(win, BLUE, i)
    pg.display.update()
    # win.fill((0,0,0))  # TURN OFF TO SEE PRIORS

    while True: # wait for pg event
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
    left, right = balls[:mid], balls[mid:]

    # encompass each groups with a single rectangle
    Ab1, Ab2 = balls[0], balls[mid-1]
    Bb1, Bb2 = balls[mid], balls[-1]

    # determine rect dimensions
    if axis == 0:
        Ax = Ab1.left
        Ay = min(ball.top for ball in left)
        Aw = Ab2.right - Ax
        Ah = max(ball.bot for ball in left) - Ay

        Bx = Bb1.left
        By = min(ball.top for ball in right)
        Bw = Bb2.right - Bx
        Bh = max(ball.bot for ball in right) - By
    else:
        Ax = min(ball.left for ball in left)
        Ay = Ab1.top
        Aw = max(ball.right for ball in left) - Ax
        Ah = Ab2.bot - Ay

        Bx = min(ball.left for ball in right)
        By = Bb1.top
        Bw = max(ball.right for ball in right) - Bx
        Bh = Bb2.bot - By


    # check for intersection of rects if both splits contain exactly 1 ball
    color = BLUE
    if (len(left), len(right)) == (1, 1) and  (Ax < Bx + Bw and Ax + Aw > Bx and Ay < By + Bh and Ah + Ay > By):
        potential_collisions.add((Ab2, Bb1))
        color = RED
    
    # draw rectangles
    pg.draw.rect(win, color, (Ax, Ay, Aw, Ah), 2)
    pg.draw.rect(win, color, (Bx, By, Bw, Bh), 2)
    pg.display.update()
    

    
    # compare median balls for potential collision
    # if abs(a.p[axis] - b.p[axis]) < a.r + b.r:
    #     potential_collisions.add((a, b))

    # # draw split according to axis
    # if axis == 0:
    #     A = (b.p.x - a.p.x) / 2 + a.p.x
    #     pg.draw.line(win, (255, 255, 255), (A, 0), (A, H))
    # else:
    #     A = (a.p.y - b.p.y) / 2 + b.p.y
    #     pg.draw.line(win, (255, 255, 255), (0, A), (W, A))

    bvh_partition(balls[:mid], depth+1)
    bvh_partition(balls[mid:], depth+1)

class BVH:
    "Skewed to the right"

    def __init__(self, balls, parent=None, rect=None, depth=0, render=False):
        self.balls = balls
        self.parent = parent
        self.rect: pg.Rect = rect
        self.depth = depth
        self.render = render
        self.ball : Ball = None
        self.left = None
        self.right = None

        # draw balls in this node blue
        for i, ball in enumerate(balls):
            ball.draw(win, BLUE, i)
        pg.display.update()

        # wait()

        self.build_tree(balls, depth % 2)
    
    def __repr__(self) -> str:
        return "Leaf" if self.ball else "Node"
    
    def build_tree(self, balls, axis):
        if len(balls) == 1:
            self.ball = balls[0]
            return
        
        # sort balls by axis
        balls.sort(key=lambda ball: ball.p[axis])

        # split balls into two groups
        mid = len(balls) // 2
        left, right = balls[mid-1], balls[mid]

        # encompass each groups
        A_rect = left.rect.unionall([ball.rect for ball in balls[:mid-1]])
        B_rect = right.rect.unionall([ball.rect for ball in balls[mid+1:]])

        if self.render:
                pg.display.update()
                wait()
                pg.draw.rect(win, BLUE, A_rect, 2)
                pg.draw.rect(win, BLUE, B_rect, 2)
        
        self.left = BVH(balls[:mid], self, A_rect, self.depth+1, self.render)
        self.right = BVH(balls[mid:], self, B_rect, self.depth+1, self.render)
        


    def build_tree1(self, balls, axis):
        if len(balls) == 1:
            self.ball = balls[0]
            return
        
        balls.sort(key=lambda ball: ball.p[axis])
        
        mid = len(balls) // 2

        # encompass each groups with a single rectangle
        # Check if either group is singular for easier rect calculation
        Ab1, Ab2 = balls[0], balls[mid-1]
        Bb1, Bb2 = balls[mid], balls[-1]

        A_rect = Ab2.rect.unionall([ball.rect for ball in balls[:mid-1]])
        B_rect = Bb1.rect.unionall([ball.rect for ball in balls[mid+1:]])

        # singular groups
        if Bb1 == Bb2:
            self.left = BVH([Ab1], self, Ab1.rect, self.depth+1, self.render)
            self.right = BVH([Bb1], self, Bb1.rect, self.depth+1, self.render)
            if self.render:
                pg.display.update()
                wait()
                pg.draw.rect(win, BLUE, Ab1.rect, 2)
                pg.draw.rect(win, BLUE, Bb1.rect, 2)
            return  
        # B contains two balls
        if Ab1 == Ab2:
            self.left = BVH([Ab1], self, Ab1.rect, self.depth+1, self.render)
            
            # if axis == 0:
            #     Bx = Bb1.left
            #     By = min(ball.top for ball in balls[mid:])
            #     Bw = Bb2.right - Bx
            #     Bh = max(ball.bot for ball in balls[mid:]) - By
            # else:
            #     Bx = min(ball.left for ball in balls[mid:])
            #     By = Bb1.top
            #     Bw = max(ball.right for ball in balls[mid:]) - Bx
                # Bh = Bb2.bot - By
            # right_rect = pg.Rect(Bx, By, Bw, Bh)
            # self.right = BVH(balls[mid:], self, right_rect, self.depth+1, self.render)
            right_rect = Bb1.rect.union(Bb2.rect)
            self.right = BVH(balls[mid:], self, Bb1.rect.union(Bb2.rect), self.depth+1, self.render)
            if self.render:
                pg.display.update()
                wait()
                pg.draw.rect(win, BLUE, Ab1.rect, 2)
                pg.draw.rect(win, BLUE, right_rect, 2)
            return
        # determine rect dimensions
    
        if axis == 0:
            Ax = Ab1.left
            Ay = min(ball.top for ball in balls[:mid])
            Aw = Ab2.right - Ax
            Ah = max(ball.bot for ball in balls[:mid]) - Ay

            Bx = Bb1.left
            By = min(ball.top for ball in balls[mid:])
            Bw = Bb2.right - Bx
            Bh = max(ball.bot for ball in balls[mid:]) - By
        else:
            Ax = min(ball.left for ball in balls[:mid])
            Ay = Ab1.top
            Aw = max(ball.right for ball in balls[:mid]) - Ax
            Ah = Ab2.bot - Ay

            Bx = min(ball.left for ball in balls[mid:])
            By = Bb1.top
            Bw = max(ball.right for ball in balls[mid:]) - Bx
            Bh = Bb2.bot - By
    
        left_rect = pg.Rect(Ax, Ay, Aw, Ah)
        right_rect = pg.Rect(Bx, By, Bw, Bh)

        # draw rectangles
        if self.render:
            pg.display.update()
            wait()
            pg.draw.rect(win, BLUE, left_rect, 2)
            pg.draw.rect(win, BLUE, right_rect, 2)

        self.left = BVH(balls[:mid], self, left_rect, self.depth+1, self.render)
        self.right = BVH(balls[mid:], self, right_rect, self.depth+1, self.render)
  
    def get_collisions(self, render=False):
        yield from self.left.intersects_with(self.right, render)
    
    def bigger_than(self, rect: pg.Rect):
        return self.rect.width * self.rect.height > rect.width * rect.height
    
    def intersects_with(self, other: 'BVH', render=False):
        # global KEK
        # print(KEK)
        # KEK += 1
        if render:
            if self.rect:
                pg.draw.rect(win, RED, self.rect, 2)
                pg.display.update()
                if other.rect:
                    pg.draw.rect(win, RED, other.rect, 2)
                    pg.display.update()
                else:
                    other.ball.draw(win, RED)
                    pg.display.update()
            wait()
            if self.rect: pg.draw.rect(win, BLUE, self.rect, 2)
            if other.rect: pg.draw.rect(win, BLUE, other.rect, 2)

        # Check own children
        if self.left:
            yield from self.left.intersects_with(self.right, render)
        if other.left:
            yield from other.left.intersects_with(other.right, render)

        # Return if rects not intersecting
        if not self.rect.colliderect(other.rect):
            return 
        
        if self.ball and other.ball:
            if self.ball.collides_with(other.ball):
                if render:
                    print("COLLISION")
                    self.ball.draw(win, RED)
                    other.ball.draw(win, RED)
                    pg.display.update()
                    wait()
                    self.ball.draw(win, BLUE)
                    other.ball.draw(win, BLUE)
                yield (self.ball, other.ball)
            return 
        
        if other.ball and self.ball is None:
            yield from self.left.intersects_with(other, render)
            yield from self.right.intersects_with(other, render)
            return 
        
        if self.ball and other.ball is None:
            yield from other.left.intersects_with(self, render)
            yield from other.right.intersects_with(self, render)
            return 
        
        # Both this and other have children
        yield from self.left.intersects_with(other.left, render)
        yield from self.left.intersects_with(other.right, render)
        yield from self.right.intersects_with(other.left, render)
        yield from self.right.intersects_with(other.right, render)

def wait():
    waiting = True        
    while waiting:
        # wait for pg event
        event = pg.event.wait()
        waiting = process_event(event)

def process_event(event):
    if event.type == pg.QUIT:
        pg.quit()
        quit()
    elif event.type == pg.KEYDOWN:
        if event.key == pg.K_ESCAPE:
            pg.quit()
            quit()
        if event.key == pg.K_r:
            go()
        if event.key == pg.K_SPACE:
            return False
    return True

def naive(balls):
    """Check for ball collisions"""
    k = 0
    for i in range(len(balls)):
        a = balls[i]
        for j in range(i+1, len(balls)):
            b = balls[j]
            if a.collides_with(b):
                k += 1
    return k

def go():
    while True:
        win.fill((0, 0, 0))
        balls = get_balls()
        bvh = BVH(balls, render=render)
        kek = list(bvh.get_collisions(render=render))
        print(f'BVH: {len(kek)} collisions')
        print(f'Naive: {naive(balls)} collisions')
        for a, b in kek:
            a.draw(win, RED)
            b.draw(win, RED)
        text = font.render("GAME OVER", 12, (255, 255, 255))
        win.blit(text, (W/2 - text.get_width()/2, 350))
        global KEK
        print(KEK)
        KEK = 0
        pg.display.update()
        print()
        clock.tick(2)
        for event in pg.event.get():
            if not process_event(event):
                return


def test_against_naive_collision_count():
    for seed in range(1000):
        random.seed(seed)
        balls = get_balls()
        bvh = BVH(balls)
        kek = list(bvh.get_collisions())
        lol = naive(balls)
        if len(kek) != lol:
            print(f'ERROR: {len(kek)} != {lol}')
            print(f'Seed: {seed}')
            return seed
    print("GREAT SUCCESS")

def test():
    # Place two balls close to each other near center
    win.fill((0, 0, 0))
    # random positions
    pos_a = (random.randint(0, W), random.randint(0, H))
    pos_b = (random.randint(0, W), random.randint(0, H))
    pos_c = (random.randint(0, W), random.randint(0, H))

    A = Ball(pos_a, (10, 0), (10, 0), 10, RED)
    B = Ball(pos_b, (-10, 0), (10, 0), 10, BLUE)
    C = Ball(pos_c, (0, 0), (10, 0), 10, GREEN)

    A.draw(win)
    B.draw(win)
    C.draw(win)
    
    pg.draw.rect(win, WHITE, A.rect, 2)
    pg.draw.rect(win, WHITE, B.rect, 2)
    pg.draw.rect(win, WHITE, C.rect, 2)

    # union of rects
    rect = A.rect.unionall([B.rect, C.rect])
    pg.draw.rect(win, WHITE, rect, 2)

    pg.display.flip()


pg.display.update()
test()
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()
            if event.key == pg.K_SPACE:
                go()
            if event.key == pg.K_t:
                test()

    

import numpy as np
import pygame as pg
from pygame.math import Vector2 as V2
from typing import List, Tuple
import time
from random import randint, choice, seed
from math import sqrt

"""
TOOD:
    - Spinning wall bounce adds to velocity, but should velocity add to spin?
      It seems that if radial_speed > lin_speed, then spin is reduced otherwise
      spin is increased opposite sign of friction or same sign velocity component.
"""


# W, H = 200, 130
W, H = 400, 510
HUD_OFFSET = 50

BALL_COUNT = 20
RADIUS = 16
SPIN_THRESH = 10
MAX_SPEED = 200
MAX_OMEGA = 500
ROT_FRIC = 0.6
WALL_FRIC = 0.9


BRICK_SIZE = 400 // 7 #60
BRICK_HITS = 10
BRICKS_PER_ROW = 7

RIGHT, UP, LEFT, DOWN = V2(1, 0), V2(0, -1), V2(-1, 0), V2(0, 1)
k = 1#sqrt(2) / 2
RIGHT_UP, RIGHT_DOWN, LEFT_DOWN, LEFT_UP = V2(k, -k), V2(k, k), V2(-k, k), V2(-k, -k)
DIRECTIONS = [RIGHT, RIGHT_UP, UP, LEFT_UP, LEFT, LEFT_DOWN, DOWN, RIGHT_DOWN, -1]
DIRECTION_NAMES = ["RIGHT", "RIGHT_UP", "UP", "LEFT_UP", "LEFT", "LEFT_DOWN", "DOWN", "RIGHT_DOWN", "NONE"]
DIRS = [(0, -1), (-1, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Prioritize non diagonal directions
KEK = 0

pg.init()
pg.font.init()
seed(30)

# screens
screen = pg.display.set_mode((W, H + HUD_OFFSET))
pg.display.set_caption("Brick Breaker")

hud_screen = pg.Surface((W, HUD_OFFSET))
hud_rect = hud_screen.get_rect()
hud_rect.top = H

ball_screen = pg.Surface((W, H))
ball_screen_rect = ball_screen.get_rect()

brick_screen = pg.Surface((W, H))
brick_screen_rect = brick_screen.get_rect()

# phsyics
clock = pg.time.Clock()
FPS = 60
dt = 1 / FPS
GRAVITY = V2(0, 0)

# colors and font
WHITE, GREY, BLACK_, BLACK = (255, 255, 255), (100, 100, 100), (15, 15, 15), (0, 0, 0)
RED, GREEN, BLUE = (255, 50, 50), (0, 255, 0), (100, 100, 255)
YELLOW, CYAN, MAGENTA = (255, 255, 0), (0, 255, 255), (255, 0, 255)
BROWN, ORANGE, PURPLE = (108, 44, 0), (255, 128, 0), (174, 0, 174)
BEIGE, PINK, TURQUOISE = (255, 255, 128), (255, 128, 255), (128, 255, 255)
EGG, LIME, TEAL = (255, 255, 192), (128, 255, 128), (0, 128, 128)
COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, BEIGE, PINK, EGG, LIME]
FONT = pg.font.SysFont("Arial", 30)
BRICK_FONT = pg.font.SysFont("Arial", 20)

ball_screen.set_colorkey(BLACK)  # important to let ball screen be transparent


def hud(text):
        hud_screen.fill(BROWN)
        # score_text = FONT.render("Score: " + str(self.score), True, WHITE)
        # hud_screen.blit(score_text, (10, 10))
        text = FONT.render(str(text), True, WHITE)
        hud_screen.blit(text, (10, 10))
        screen.blit(hud_screen, (0, H))
        pg.display.update(hud_rect)

class Ball():
    def __init__(self, pos, velocity, omega, radius, color):
        self.pos = V2(pos)
        self.vel = V2(velocity)
        
        self.thickness = radius // 8  # thickness of the blue plus

        self.omega = omega
        self.spinning = True

        self.radius = radius
        self.color = color
        self.angle = 0
    
    @property
    def rect(self):
        """Bounding rectangle"""
        return pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, 2 * self.radius, 2 * self.radius)
    
    @property
    def bounds(self):
        """Return left, right, top, bottom bounds of the ball"""
        return self.pos.x - self.radius, self.pos.x + self.radius, self.pos.y - self.radius, self.pos.y + self.radius

    def draw(self):
        pg.draw.circle(ball_screen, self.color, self.pos, self.radius)

        # blue plus
        if self.spinning:
            dx = self.radius * np.cos(np.radians(self.angle))
            dy = self.radius * np.sin(np.radians(self.angle))
            pg.draw.line(ball_screen, BLACK_, self.pos - (dx, dy), self.pos + (dx, dy), self.thickness)
            pg.draw.line(ball_screen, BLACK_, self.pos + (-dy, dx), self.pos + (dy, -dx), self.thickness)

        # and bounds
        # pg.draw.rect(ball_screen, RED, self.rect, 1)

    def update(self):
        self.wall_bounce()
        self.vel += GRAVITY * dt
        self.pos += self.vel * dt
        if self.spinning:
            self.angle += self.omega * dt
            self.angle %= 360
    
    def kinematic(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.pos.x -= 1
        if keys[pg.K_d]:
            self.pos.x += 1
        if keys[pg.K_w]:
            self.pos.y -= 1
        if keys[pg.K_s]:
            self.pos.y += 1
        if keys[pg.K_q]:
            self.angle -= 1
        if keys[pg.K_e]:
            self.angle += 1
            
    def brick_bounce(self, normal, depth):
        """Bounce off a surface with a given normal"""
        # self.pos -= normal * self.radius
        # Check if ball is actuall inside the brick
        # if self.vel.dot(normal) < 0:  # if ball is moving towards the brick
        #     self.vel += 2 * self.vel.dot(normal) * normal  # bounce off the brick
        
        if normal in [RIGHT, LEFT]:
            self.vel.x *= -1
        if normal in [UP, DOWN]:
            self.vel.y *= -1
        if normal in [RIGHT_UP, RIGHT_DOWN, LEFT_DOWN, LEFT_UP]:
            self.vel *= -1
        self.pos += normal * depth

    def wall_bounce1(self):
        """Continuous collision detection and response using lerping"""
        if self.pos.x - self.radius < 0:  # Left wall
            tc = (self.radius - self.pos.x) / self.vel.x
            self.pos.x += tc * (self.vel.x)
            self.vel.x *= -1
        if self.pos.x + self.radius > W: # Right wall
            tc = (W - self.radius - self.pos.x) / self.vel.x      
            self.pos.x += tc * (self.vel.x)
            self.vel.x *= -1
        if self.pos.y - self.radius < 0: # Top wall
            tc = (self.radius - self.pos.y) / self.vel.y
            self.pos.y += tc * (self.vel.y)
            self.vel.y *= -1
        if self.pos.y + self.radius > H: # Bottom wall
            tc = (H - self.radius - self.pos.y) / self.vel.y      
            self.pos.y += tc * (self.vel.y)
            self.vel.y *= -1

    def wall_bounce2(self):
        """Spinning collision detection and response"""
        # https://www.youtube.com/watch?v=Tb19Y_PR7jk&t=307s
        if self.pos.x - self.radius < 0: # Left wall
            self.pos.x = self.radius
            # self.omega += (1 - WALL_FRIC) * self.vel.x / self.radius
            self.vel.x *= -WALL_FRIC
            if self.spinning:
                self.vel.y += (1 - ROT_FRIC) * self.omega * self.radius * dt
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH
        elif self.pos.x + self.radius > W: # Right wall
            self.pos.x = W - self.radius
            self.vel.x *= -WALL_FRIC
            if self.spinning:
                self.vel.y -= (1 - ROT_FRIC) * self.omega * self.radius * dt
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH
        if self.pos.y - self.radius < 0: # Top wall
            self.pos.y = self.radius
            # self.omega += (1 - WALL_FRIC) * self.vel.x * 10
            self.vel.y *= -WALL_FRIC
            if self.spinning:
                self.vel.x -= (1 - ROT_FRIC) * self.omega * self.radius * dt  # flip sign because hitting top flips friction direction
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH
        elif self.pos.y + self.radius > H: # Bottom wall
            self.pos.y = H - self.radius
            # self.omega -= (1 - WALL_FRIC) * self.vel.x * 10
            self.vel.y *= -WALL_FRIC
            hud(self.omega)
            if self.spinning:
                self.vel.x += (1 - ROT_FRIC) * self.omega * self.radius * dt
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH
            

    def wall_bounce(self):
        """Discrete collision detection and response"""
        if self.pos.x < self.radius: # Left wall
            self.pos.x = self.radius
            self.vel.x *= -1
        elif self.pos.x + self.radius > W: # Right wall
            self.pos.x = W - self.radius
            self.vel.x *= -1
        if self.pos.y < self.radius: # Top wall
            self.pos.y = self.radius
            self.vel.y *= -1
        elif self.pos.y + self.radius > H: # Bottom wall
            self.pos.y = H - self.radius
            self.vel.y *= -1

class Brick():
    def __init__(self, index, size, color):
        j, i = index
        self.pos = V2(i, j) * size
        self.j, self.i = index  # for grid lookup
        self.size = V2(size)
        self.color = color
        self.hits = BRICK_HITS

        self.rect = pg.Rect(self.pos, self.size)        
        self.left, self.right = self.pos.x, self.pos.x + self.size.x
        self.top, self.bot = self.pos.y, self.pos.y + self.size.y

        self.corner = None

    def draw(self):
        pg.draw.rect(brick_screen, self.color, self.rect)
        # pg.draw.rect(brick_screen, GREY, (self.pos.x, self.pos.y + self.size.y - 5, self.size.x, 3))
        pg.draw.rect(brick_screen, BLACK, self.rect, 3)
        
        text = BRICK_FONT.render(str(self.hits), True, BLACK)
        brick_screen.blit(text, self.pos + (self.size.x // 2 - text.get_width() // 2, self.size.y // 2 - text.get_height() // 2))

        if self.corner:
            pg.draw.circle(brick_screen, RED, self.corner, 5)
    
    def collide(self, ball: Ball, heading: V2):
        """Check if ball is colliding with brick from heading. Return collision depth"""
        if heading in [LEFT, RIGHT, UP, DOWN]:
            # check if this side intersects with ball boundary
            if heading == LEFT:  # ball is moving left so side is right
                depth = ball.radius + self.right - ball.pos.x
                if depth > 0 and self.right < ball.pos.x + ball.radius:                      
                    return depth
            elif heading == RIGHT:
                depth = ball.pos.x + ball.radius - self.left
                if depth > 0 and self.left > ball.pos.x - ball.radius:
                    return depth
            elif heading == UP:
                depth = ball.radius + self.bot - ball.pos.y
                if depth > 0 and self.bot < ball.pos.y + ball.radius:
                    return depth
            elif heading == DOWN:
                depth = ball.pos.y + ball.radius - self.top
                if depth > 0 and self.top > ball.pos.y - ball.radius:
                    return depth

        elif heading in [LEFT_UP, RIGHT_UP, LEFT_DOWN, RIGHT_DOWN]:
            # check if this corner is contained by ball
            corner = self.pos + (self.size.x * (heading.x < 0), self.size.y * (heading.y < 0))
            depth = ball.radius - (corner - ball.pos).length()
            if depth > 0:
                return depth

    def hit(self, value):
        self.hits -= value
        if self.hits <= 0:
            self.hits = 0
            return True
        # else:
        #     self.color = BRICK_COLORS[self.hits - 1]
        #     return False

    def __repr__(self) -> str:
        return f'Brick{(self.j, self.i)}'
        return 'Brick({}, {})'.format(self.pos, self.color)

class Player():
    def __init__(self):
        self.ball_count = BALL_COUNT
        # self.lives = LIVES
        self.x = W // 2
        self.a = 90

    def draw(self):
        ball_screen.fill(BLACK)
        pg.draw.circle(ball_screen, WHITE, (self.x, H - 50), 10)
        screen.blit(ball_screen, (0, 0))
        pg.display.update(ball_screen_rect)

    def play(self):
        """Aim and shoot ball"""
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE]:
            self.ball_count -= 1
            return True
        if keys[pg.K_a]:
            self.x -= 5
        if keys[pg.K_d]:
            self.x += 5

        if keys[pg.K_e]:
            self.a += 1
        if keys[pg.K_q]:
            self.a -= 1
        
        self.draw()
        
        

class Game():
    """Game class
    Call draw_bricks() whenever bricks are updated.
    Use hud() to display text on screen."""

    def __init__(self):
        self.reset()
        # brick_screen.fill(BLACK)
        self.draw_bricks()
        self.malthe = Player()
        # pg.display.update(brick_screen_rect)
    
    """Game functions"""
    def reset(self):
        self.score = 0 
        self.ball = None       
        # self.ball : Ball = Ball((150, 150), (500,-100), 0, RADIUS, BLUE)
        # self.ball = Ball((100, 100), (-500,100), 0, RADIUS, RED)
        # self.ball = Ball((W // 2, H // 2), (0,0), 0, RADIUS, RED)
        

        # balls
        # self.balls : List[Ball] = [Ball((W // 2, H // 2), (200, 300), 1000, RADIUS, RED)]
        self.balls : List[Ball] = []
        for _ in range(BALL_COUNT):
            pos = (randint(RADIUS, W - RADIUS), randint(RADIUS, H - RADIUS))
            vel = (randint(-MAX_SPEED, MAX_SPEED), randint(-MAX_SPEED, MAX_SPEED))
            omega = randint(-MAX_OMEGA, MAX_OMEGA)
            self.balls.append(Ball(pos, vel, omega, RADIUS, choice(COLORS)))
        
        # bricks
        
        # self.bricks = [Brick((W // 2, H // 2), BRICK_SIZE, choice(COLORS))]
        self.bricks : List[Brick] = []
        empty_row = [None] * BRICKS_PER_ROW
        # self.grid : List[List[Brick]] = [empty_row.copy() for _ in range(BRICKS_PER_ROW)]
        self.grid : List[List[Brick]] = [empty_row]
        # j, i = 3, 3
        # brick = Brick((j, i), BRICK_SIZE, choice(COLORS))
        # self.bricks.append(brick)
        # self.grid[j][i] = brick        


        # randomly fill screen with bricks
        for j in range(BRICKS_PER_ROW):
            row = empty_row.copy()
            for i in range(BRICKS_PER_ROW):
                if randint(0, 1): continue
                brick = Brick((j+1, i), BRICK_SIZE, choice(COLORS))
                self.bricks.append(brick)
                row[i] = brick
            self.grid.append(row)
        

    def update(self):
        if self.ball:
            self.ball.kinematic()
            self.brick_collide(self.ball)

        for ball in self.balls:
            ball.update()
            self.brick_collide(ball)
    
    def events(self):
        global dt
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print(event.pos)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                if event.key == pg.K_r:
                    self.reset()
                if event.key == pg.K_SPACE:
                    dt = dt * 0.25
            
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    dt *= 4

    def draw_balls(self):
        # self.draw_bricks()  # delete later
        screen.blit(brick_screen, (0, 0))
        # screen.fill(BLACK)
        ball_screen.fill(BLACK)
        if self.ball:
            self.ball.draw()
        for ball in self.balls:
            ball.draw()
        
        
        screen.blit(ball_screen, (0, 0))
        pg.display.update()

    def run(self):
        hud("kek")
        while True:
            # let player aim and shoot ball
            while True:
                done = self.malthe.play()
                if done: break
                self.events()
                clock.tick(FPS)
                
            self.update()
            self.events()
            self.draw_balls()
            clock.tick(FPS)
    
    """Brick functions"""
    def draw_bricks(self):
        brick_screen.fill(BLACK)  # necessary?
        for brick in self.bricks:
            brick.draw()
        screen.blit(brick_screen, (0, 0))

    def pos2grid(self, pos):
        x, y = pos // BRICK_SIZE
        return (int(y), int(x))

    def brick_collide(self, ball: Ball):
        j, i = self.pos2grid(ball.pos)
        # check neighbors
        for di, dj in DIRS:
            if 0 <= j + dj < len(self.grid) and 0 <= i + di < len(self.grid[0]):
                brick = self.grid[j + dj][i + di]
                if brick is None:
                    continue
                if depth := brick.collide(ball, V2(di, dj)): # COLLISION!
                    # alter ball position and velocity
                    ball.pos -= depth * V2(di, dj)                          
                    if dj == 0: ball.vel.x *= -1
                    elif di == 0: ball.vel.y *= -1
                    else: ball.vel *= -1
                    
                    # update brick
                    destroyed = brick.hit(1)
                    if destroyed:
                        self.remove_brick(brick)  
                    self.draw_bricks()                  
                    return
    
    def remove_brick(self, brick: Brick):
        self.score += 1
        self.bricks.remove(brick)
        self.grid[brick.j][brick.i] = None
        
        
        

    


if __name__ == "__main__":
    game = Game()
    game.run()



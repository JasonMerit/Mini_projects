import pygame as pg
from pygame.locals import *
from sys import exit
from random import randint, uniform
import random
from math import cos, sin, pi

# Constants
POWERUP_SPAWN_CHANCE = 0.1
FPS = 60

# Rainbow colors
RAINBOW = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
PINK, PURPLE, ORANGE, BROWN = (255, 0, 255), (255, 0, 128), (255, 128, 0), (128, 64, 0)
BLACK, WHITE, YELLOW, RED, GREEN, BLUE = (0, 0, 0), (255, 255, 255), (255, 255, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)

RIGHT, DOWN, LEFT, UP = 0, 1/2*pi, pi, 3/2*pi

# Pygame initialization
pg.init()
font = pg.font.SysFont("Arial", 24)

# helper functions
collision = lambda a, b: a.x > b.x and a.x < b.x + b.width and a.y > b.y and a.y < b.y + b.height
random_direction = lambda: uniform(0, 2*pi)

# Classes
class Ball:

    def __init__(self, x, y, radius, speed, angle, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.angle = angle
        self.color = color
    
    def move(self):
        x, y = pg.math.Vector2(cos(self.angle), sin(self.angle)) * self.speed
        self.x += x
        self.y += y

        if self.y < 0:
            self.angle = -self.angle
        
        if self.x < 0 or self.x > 800:
            self.angle = pi - self.angle
        
        if self.y > 600:
            self.speed = 0
            self.x = 400
            self.y = 300
            self.angle = uniform(0, 2*pi)
            self.speed = 5
            return True
    
    def bounce(self, other):
        if collision(self, other):
            self.angle = -self.angle
            self.speed += 0.05

            if isinstance(other, Paddle):
                self.angle = pi - self.angle
                # alter angle based on where the ball hit the paddle
                if self.x < other.x + other.width/2:
                    self.angle -= pi/6
                else:
                    self.angle += pi/6
                
            elif isinstance(other, Brick):
                other.destroy()
                if self.x < other.x or self.x > other.x + other.width:
                    self.angle = pi - self.angle
                if self.y < other.y or self.y > other.y + other.height:
                    self.angle = -self.angle
                if random.random() < POWERUP_SPAWN_CHANCE:
                    powerup = Powerup(other.x, other.y, 10, random.choice(RAINBOW))
                    return powerup
                return True
    
    def draw(self, win):
        pg.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)
            
class Paddle:

    def __init__(self, x, y, width, height, speed, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.acceleration = 0
        self.force = 0.4
        self.color = color        
    
    def move(self):
        keys = pg.key.get_pressed()
        direction = (keys[pg.K_d] or keys[pg.K_RIGHT]) - (keys[pg.K_a] or keys[pg.K_LEFT])
        
        # smooth movement
        self.acceleration += direction * self.force
        if direction == 0:
            if self.acceleration < 0:
                self.acceleration += self.force
            elif self.acceleration > 0:
                self.acceleration -= self.force
        
        self.x += self.acceleration
        if self.x < 0:
            self.x = 0
            self.acceleration = 0
        elif self.x > 800 - self.width:
            self.x = 800 - self.width
            self.acceleration = 0
    
    def draw(self, surface):
        pg.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
    
class Brick:

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.alive = True
    
    def draw(self, surface):
        pg.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
    
    def destroy(self):
        self.alive = False

class Powerup:

    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
    
    def move(self):
        self.y += self.speed

        if self.y > 600:
            return True
    
    def draw(self, surface):
        pg.draw.rect(surface, self.color, (self.x, self.y, 20, 20))

class Game:
    
        def __init__(self):
            self.screen = pg.display.set_mode((800, 600))
            self.clock = pg.time.Clock()
            self.fps = 60
            self.running = True
            self.playing = False
            self.font = pg.font.SysFont('Arial', 30)
            self.paddle = Paddle(400, 550, 200, 20, 10, (0, 255, 0))
            self.total_bricks = 50
            self.reset()
        
        def run(self):
            while self.running:
                self.clock.tick(self.fps)
                self.events()
                self.update()
                self.draw()
        
        def events(self):
            for event in pg.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    if event.key == K_r:
                        self.reset()
                    if event.key == K_SPACE:
                        self.playing = True
        
        def update(self):
            if self.playing:
                # Paddle movement
                self.paddle.move()

                # Ball movement    
                for ball in self.balls:
                    if ball.move():
                        if len(self.balls) == 1:
                            self.balls.append(Ball(400, 300, 10, 5, uniform(0, pi), BLUE))
                            self.lives -= 1
                            if self.lives <= 0:
                                self.game_over()
                        self.balls.remove(ball)
                    
                    # Ball bouncing
                    ball.bounce(self.paddle)

                    # Brick collision
                    for brick in self.bricks:
                        if brick.alive:
                            bounce = ball.bounce(brick)
                            if bounce:
                                if isinstance(bounce, Powerup):
                                    self.powerups.append(bounce)
                                self.bricks.remove(brick)
                                self.score += 1
                                if self.score == self.total_bricks:
                                    self.playing = False
                                    self.draw_text('YOU WIN!', 100, GREEN, 400, 300)
                                    pg.display.update()
                                    pg.time.delay(3000)
                # Powerup movement                                    
                for powerup in self.powerups:
                    if powerup.move():
                        self.powerups.remove(powerup)
                    elif collision(powerup, self.paddle):
                        self.powerups.remove(powerup)
                        ball = random.choice(self.balls)
                        self.balls.append(Ball(ball.x, ball.y, 10, 5, random_direction(), (0, 0, 255)))
        
        def reset(self):
            self.score = 0
            self.lives = 39
            angle = DOWN
            angle += uniform(-0.1, 0.1)
            ball = Ball(400, 300, 10, 5, angle, (0, 0, 255))
            ball.angle = angle
            ball.x = 400
            ball.y = 300
            ball.speed = 5
            self.balls = [ball]
            self.paddle.x = 400
            self.paddle.y = 550
            self.bricks = []
            for i in range(self.total_bricks // 5):
                for j in range(self.total_bricks // 10):
                    color = RAINBOW[j]
                    self.bricks.append(Brick(80 + i * 70, 80 + j * 30, 60, 20, color))
            self.powerups = []
        
        def draw(self):
            self.screen.fill((0, 0, 0))
            for ball in self.balls:
                ball.draw(self.screen)
            self.paddle.draw(self.screen)
            
            # bricks
            for brick in self.bricks:
                if brick.alive:
                    brick.draw(self.screen)
            # powerups
            for powerup in self.powerups:
                powerup.draw(self.screen)

            # ui
            if not self.playing:
                self.draw_text('Press Space to Play', 40, GREEN, 400, 300)
            for i in range(self.lives):
                pg.draw.rect(self.screen, RED, (20 + i * 30, 20, 20, 20))
            for i in range(self.total_bricks - self.score):
                pg.draw.rect(self.screen, WHITE, (20 + i * 5, 50, 3, 15))
            
            # update display
            pg.display.update()

        def draw_text(self, text, size, color, x, y):
            font = pg.font.SysFont('Calibri', size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
            self.screen.blit(text_surface, text_rect)
        
        def game_over(self):
            self.draw_text('GAME OVER', 100, RED, 400, 300)
            pg.display.update()
            pg.time.delay(3000)
            self.reset()

if __name__ == '__main__':
    game = Game()
    game.run()
    pg.quit()
    exit()

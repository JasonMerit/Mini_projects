"""Rigid tetris game using pymunk physics engine."""
# C:\Users\Jason\AppData\Local\Programs\Python\Python310\Lib\site-packages\pymunk\examples
import pygame as pg
import pymunk as pm
import pymunk.pygame_util
from pymunk import Vec2d
import random
import math
import numpy as np
from random import randint
from pygame.locals import *

class Tetrimino:
    """Tetrimino class."""
    
    def __init__(self, space, x, y, color):
        self.space = space
        self.color = color
        self.x = x
        self.y = y
        self.body = pm.Body(1, 100)
        self.body.position = x, y
        self.shape = pm.Poly.create_box(self.body, (30, 30))
        self.shape.color = color
        self.shape.elasticity = 0.5
        self.shape.friction = 0.5
        self.shape.collision_type = 1
        self.shape.density = 0.1
        self.space.add(self.body, self.shape)
        self.body.velocity = 0, 0
        self.body.angular_velocity = 0
        self.body.angle = 0
        self.body.torque = 0
        self.body.force = 0, 0
        self.body.velocity_func = self.velocity_func
        self.body.position_func = self.position_func
        self.body.rotation_func = self.angle_func
        self.body.angle_func = self.angle_func
        self.body.torque_func = self.torque_func
        self.body.force_func = self.force_func

    def velocity_func(self, body, gravity, damping, dt):
        """Velocity function."""
        body.velocity = 0, 0
    
    def position_func(self, body, dt):
        """Position function."""
        body.position = self.x, self.y
    
    def angle_func(self, body, dt):
        """Angle function."""
        self.tetrimino_rotation_matrix = np.array([[math.cos(math.radians(rot)), -math.sin(math.radians(rot))], [math.sin(math.radians(rot)), math.cos(math.radians(rot))]])
        self.tetrimino_rotation_matrix_inv = np.linalg.inv(self.tetrimino_rotation_matrix)
        self.tetrimino_rotation = np.matmul(self.tetrimino_rotation_matrix, self.tetrimino_rotation)
    
    def torque_func(self, body, dt):
        """Torque function."""
        body.torque = 0
    
    def force_func(self, body, gravity, damping, dt):
        """Force function."""
        body.force = 0, 0
    
    def update(self):
        """Update function."""
        self.x = self.body.position.x
        self.y = self.body.position.y
    
    def draw(self, screen):
        """Draw function."""
        pg.draw.rect(screen, self.color, (self.x, self.y, 30, 30))
    
    def move(self, x, y):
        """Move function."""
        self.x = x
        self.y = y
        self.body.position = x, y
    

class Tetris:

    def __init__(self):
        """Initialize the game."""
        self.screen = pg.display.set_mode((600, 600))
        self.clock = pg.time.Clock()
        self.space = pm.Space()
        self.space.gravity = 0, 0
        self.space.damping = 0.9
        self.draw_options = pm.pygame_util.DrawOptions(self.screen)
        self.tetriminos = []
        self.tetrimino = None
        self.tetrimino_color = None
        self.tetrimino_x = None
        self.tetrimino_y = None
        self.tetrimino_type = None
        self.tetrimino_rotation = None
        self.tetrimino_rotation_count = None
        self.tetrimino_rotation_matrix = None
        self.tetrimino_rotation_matrix_inv = None
        self.tetrimino_rotation_matrix

    def run(self):
        """Run the game."""
        self.running = True
        while self.running:
            self.dt = self.clock.tick(60)
            self.event_loop()
            self.update()
            self.draw()
        pg.quit()
    
    def event_loop(self):
        """Event loop."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                elif event.key == pg.K_LEFT:
                    self.tetrimino.move(self.tetrimino.x - 30, self.tetrimino.y)
                elif event.key == pg.K_RIGHT:
                    self.tetrimino.move(self.tetrimino.x + 30, self.tetrimino.y)
                elif event.key == pg.K_UP:
                    # rotate tetrimino
                    self.tetrimino_rotation_count += 1
                    # if self.tetrimino_rotation_count == 4:
                    #     self.tetrimino_rotation_count = 0
                    rot = 45
                    self.tetrimino_rotation_matrix = np.array([[math.cos(math.radians(rot)), -math.sin(math.radians(rot))], [math.sin(math.radians(rot)), math.cos(math.radians(rot))]])
                    self.tetrimino_rotation_matrix_inv = np.linalg.inv(self.tetrimino_rotation_matrix)
                    self.tetrimino_rotation = np.matmul(self.tetrimino_rotation_matrix, self.tetrimino_rotation)
                    self.tetrimino.body.angle = math.radians(rot)

                elif event.key == pg.K_DOWN:
                    self.tetrimino.move(self.tetrimino.x, self.tetrimino.y + 30)
                elif event.key == pg.K_SPACE:
                    self.tetrimino.move(self.tetrimino.x, self.tetrimino.y + 30)
    
    def update(self):
        """Update function."""
        self.space.step(1/60)
        self.tetrimino.update()
    
    def draw(self):
        """Draw function."""
        self.screen.fill((0, 0, 0))
        # self.space.debug_draw(self.draw_options)
        self.tetrimino.draw(self.screen)
        pg.display.flip()
    
    def new_tetrimino(self):
        """New tetrimino function."""
        self.tetrimino_color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)])
        self.tetrimino_x = 300
        self.tetrimino_y = 0
        self.tetrimino_type = random.choice([1, 2, 3, 4, 5, 6, 7])
        self.tetrimino_rotation_count = 0
        self.tetrimino_rotation_matrix = np.array([[1, 0], [0, 1]])
        self.tetrimino_rotation_matrix_inv = np.array([[1, 0], [0, 1]])
        self.tetrimino_rotation = self.tetrimino_rotation_matrix.dot(np.array([self.tetrimino_x, self.tetrimino_y]))
        self.tetrimino = Tetrimino(self.space, self.tetrimino_x, self.tetrimino_y, self.tetrimino_color)
        self.tetriminos.append(self.tetrimino)
    

if __name__ == "__main__":
    tetris = Tetris()
    tetris.new_tetrimino()
    tetris.run()
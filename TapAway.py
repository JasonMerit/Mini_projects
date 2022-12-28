"""TapAway copycat for 3d exercise

Main object is a 3d list Cube containing custom object Box.
Box has a heading and coordinates.

Rendering is done

"""

import pygame as pg
import numpy as np
from pygame.math import Vector2 as V2
from math import sin, cos, radians

W, H = 600, 600
FOV_V = 45
FOV_H = FOV_V*W/H

SCALE = 100
circle_pos = V2(W/2, H/2)

BLACK, GRAY, WHITE = (25, 25, 25), (100, 100, 100), (230, 230, 230)

verticies = np.array([
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, -1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, -1, 1],
    [-1, 1, 1]
    ])

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )

p_mat = np.array([[1, 0, 0], [0, 1, 0]])


class Box():
    
    def __init__(self, y, x, z, heading):
        self.y, self.x, self.z = y, x, z
        self.heading = heading
    
    def push(self):
        pass

class Game():
    
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((W, H))
        pg.display.set_caption("TapAway")
        self.clock = pg.time.Clock()
        self.fps = 60
    
    def new(self):
        self.angle = 0
        self.run()
    
    def run(self):
        while True:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
    
    def update(self):
        self.angle += 1
        if self.angle > 360:
            self.angle = 0
        self.rot_y = np.array([[cos(radians(self.angle)), 0, sin(radians(self.angle))], [0, 1, 0], [-sin(radians(self.angle)), 0, cos(radians(self.angle))]])
        
    
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    quit()
    
    def draw(self):
        self.screen.fill(BLACK)
        points = []
        for vert in verticies:
            rot_point = np.dot(self.rot_y, vert)
            point = np.dot(p_mat, rot_point)
            points.append(point)

            x, y = point * SCALE + circle_pos
            pg.draw.circle(self.screen, WHITE, (int(x), int(y)), 5)


        pg.display.flip()   

if __name__ == '__main__':
    g = Game()
    g.new()

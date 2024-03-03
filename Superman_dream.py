# # # """
# # # TODO
# # # 1) 
# # # - Play around with code to see how it works
# # # - Update draw ball method to take a ball object
# # # - Create a ball class that collides with the walls
# # # """

import pygame as pg
from pygame import Vector2, gfxdraw as gfx
import bezier as bz
import numpy as np
from random import randrange, uniform

BLACK, GREY, WHITE = (21, 21, 21), (128, 128, 128), (211, 211, 211)
GREEN = (40, 255, 40)
# GRADIENT = [1.        , 0.79012346, 0.60493827, 0.44444444, 0.30864198,
#        0.19753086, 0.11111111, 0.04938272, 0.01234568, 0.        ]
k = 40
x = np.linspace(0, 1, k)
GRADIENT = x**2
# GRADIENT = np.linspace(0, 1, k)**1
GRADIENT = GRADIENT[::-1]

class Ball(pg.sprite.Sprite):
    

    def __init__(self, pos, vel, radius=10, color=WHITE):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((3*radius, 3*radius))
        self.image.set_colorkey(GREEN)
        self.image.fill(GREEN)
        pg.draw.circle(self.image, color, (radius, radius), radius-1)
        self.rect = self.image.get_rect(center = pos)

        self.pos = Vector2(pos)
        self.vel = Vector2(vel)

    @property
    def x(self):
        return self.pos.x
    
    @property
    def y(self):
        return self.pos.y

    def update(self):
        raise NotImplementedError
    
    def place_at(self, pos):
        SCREEN.fill(BLACK, self.rect)
        self.pos = Vector2(pos)
        self.rect.center = self.pos
        SCREEN.blit(self.image, self.rect)

class Rocket(Ball):
    hyper_jumping = False
    jump_height = 400
    jump_width = 200
    jump_step = 0

    def __init__(self, pos, vel):
        super().__init__(pos, vel, 10, WHITE)
        self.parts = [Ball(pos, vel, 8, WHITE) for _ in range(2)]
    
    def get_curve(self):
        return bz.Curve(
            [[self.x, self.x + self.jump_width//2, self.x + self.jump_width], 
            [self.y, self.y - self.jump_height, self.y]], 2)

    def update(self):
        if not self.jump_step:
            SCREEN.fill(BLACK, self.rect)
            self.pos += self.vel
            self.rect.center = self.pos

            if pg.key.get_pressed()[pg.K_SPACE]:
                self.jump_step = len(GRADIENT)
                self.curve = self.get_curve()
                self.entree_point = Vector2(self.x + self.jump_width, self.y)
            else:
                SCREEN.blit(self.image, self.rect)

        else: # hyper jumping
            self.jump_step -= 1
            point = self.curve.evaluate(GRADIENT[self.jump_step])[:, 0].tolist()
            self.parts[0].place_at(point)
            point[1] = H - point[1]
            self.parts[1].place_at(point)

            if self.jump_step == 0:
                self.pos = self.entree_point
                self.rect.center = self.pos

                # self.vel.x *= 2
                for s in stars:
                    s.speed_up()

        if self.pos.x > W + self.rect.width//2:
            self.pos.x = - self.rect.width//2
        if self.pos.y < -self.rect.height//2:
            self.pos.y = H + self.rect.height//2
        if self.pos.y > H + self.rect.height//2:
            self.pos.y = -self.rect.height//2
        


class Star(Ball):
    vel_range = 0.5, 1
    def __init__(self):
        pos = randrange(0, W), randrange(0, H)
        super().__init__(pos, (-uniform(*self.vel_range), 0), 5)
        
    
    def speed_up(self):
        self.vel.x *= 2
        self.vel_range = tuple(2*x for x in self.vel_range)

    def update(self):
        # STAR_SCREEN.fill(BLACK, self.rect)
        self.pos += self.vel
        if self.pos.x < -self.rect.width//2:
            self.pos = Vector2(W + self.rect.width, randrange(0, H))
            self.vel = Vector2(-uniform(*self.vel_range), 0)

        self.rect.center = self.pos
        SCREEN.blit(self.image, self.rect)

def process_input():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                quit()
            
            if event.key == pg.K_r:
                global stars, rocket
                stars, rocket = restart()

def restart():
    stars = [Star() for _ in range(W*H//2000)]
    rocket = Rocket((100, H//2), (1, 0))
    return stars, rocket

if __name__ == "__main__":
    W, H = 1700, 900
    SCREEN = pg.display.set_mode((W, H))

    FPS = 60
    clock = pg.time.Clock()
    JUMP = Vector2(50, 0)

    stars, rocket = restart()
    # stars = [Star() for _ in range(W*H//2000)]
    # rocket = Rocket((100, H//2), (1, 0))
    while True:
        SCREEN.fill(BLACK)
        rocket.update()
        for s in stars:
            s.update()

        process_input()
        pg.display.update()
        clock.tick(FPS)



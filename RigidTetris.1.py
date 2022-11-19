"""Tetris but with rigid rects that rotate and move continuously."""

import pygame as pg
import numpy as np
import random
from math import cos, sin, radians
from typing import List, Tuple
from pygame import gfxdraw as gfx

# Define some tetris colors 
WHITE, GREY, BLACK = (255, 255, 255), (128, 128, 128), (0, 0, 0)

TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED = (0, 255, 255), (0, 0, 255), (255, 165, 0), (255, 255, 0), (0, 255, 0), (165, 0, 165), (255, 0, 0)
COLORS = [TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# Define pygame objects
W, H = 400, 600 # (1920, 1080)
SIZE = 40
pg.init()
screen = pg.display.set_mode((W, H))
pg.display.set_caption("Rigid Tetris")
clock = pg.time.Clock()
FPS = 30

class Vec():
    """A 2D vector class."""
    def __init__(self, x, y=None) -> None:
        if y is None:
            self.x, self.y = x
        else:
            self.x, self.y = x, y
    
    def __repr__(self) -> str:
        return f"Vec({self.x}, {self.y})"
    
    @property
    def t(self) -> Tuple[int, int]:
        return self.x, self.y
    
    def draw(self, color: Tuple[int, int, int], radius: int = 5) -> None:
        """Draw a circle at the vector's position."""
        pg.draw.circle(screen, color, self.t, radius)
    
    def dot(self, other: 'Vec') -> float:
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vec') -> float:
        return self.x * other.y - self.y * other.x
    
    def rotate(self, degr: float) -> 'Vec':
        """Rotate the vector by degr degrees."""
        rad = radians(degr)
        self.x = self.x * cos(rad) - self.y * sin(rad)
        self.y = self.x * sin(rad) + self.y * cos(rad)
    
    def rotate_around(self, point: 'Vec', degr: float) -> 'Vec':
        """Rotate the vector around point by degr degrees."""
        rad = - radians(degr)
        x, y = self.x - point.x, self.y - point.y
        self.x = x * cos(rad) - y * sin(rad) + point.x
        self.y = x * sin(rad) + y * cos(rad) + point.y

    def __add__(self, other) -> 'Vec':
        if isinstance(other, tuple):
            return Vec(self.x + other[0], self.y + other[1])
        return Vec(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vec') -> 'Vec':
        if isinstance(other, tuple):
            return Vec(self.x - other[0], self.y - other[1])
        return Vec(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other: float) -> 'Vec':
        return Vec(self.x * other, self.y * other)
    
    def __rmul__(self, other: float) -> 'Vec':
        return Vec(self.x * other, self.y * other)

class Line():
    """A line class."""
    
    def __init__(self, start: Vec, end: Vec) -> None:
        self.start, self.end = start, end
    
    def __repr__(self) -> str:
        return f"Line({self.start}, {self.end})"
    
    def draw(self, color, width: int = 2) -> None:
        """Draw the line on the screen."""
        pg.draw.line(screen, color, self.start.t, self.end.t, width)
    
    def intersects(self, other: "Line") -> bool:
        """Check if the line intersects with another line."""
        # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        p = self.start
        r = self.end - self.start
        q = other.start
        s = other.end - other.start
        if r.cross(s) == 0:
            return False
        t = (q - p).cross(s) / r.cross(s)
        u = (q - p).cross(r) / r.cross(s)
        return 0 <= t <= 1 and 0 <= u <= 1

    def intersection(self, other: "Line") -> Vec:
        """Return the intersection point of the line and another line."""
        # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        p = self.start
        r = self.end - self.start
        q = other.start
        s = other.end - other.start
        t = (q - p).cross(s) / r.cross(s)
        return p + r * t

class Block():
    """Rectangle that can rotate. 
    Defined by two vector sides and their shared origin.
    ----->
    |
    |
    |"""
    def __init__(self, x, y, w, h):
        """x, y define top left corner."""
        self.x, self.y = x, y
        self.w, self.h = w, h

        self.a, self.b = Vec(x + w, y), Vec(x, y)
        self.c, self.d = Vec(x, y + h), Vec(x + w, y + h)
        self.lines = [Line(self.a, self.b), Line(self.b, self.c), Line(self.c, self.d), Line(self.d, self.a)]

        self.surf_og = pg.Surface((w, h))
        self.surf_og.set_colorkey(BLACK)
        self.surf_og.fill(WHITE)

        self.surf = self.surf_og.copy()
        self.surf.set_colorkey(BLACK)
        self.rect = self.surf.get_rect()
        self.rect.center = (x+w//2, y+h//2)

        self.angle = 0

    def __repr__(self) -> str:
        return f"Block({self.x}, {self.y}, {self.w}, {self.h})"

    def rotate(self, degr: float) -> None:
        old_center = self.rect.center
        self.angle = (self.angle + degr) % 360
        new_surf = pg.transform.rotate(self.surf_og, self.angle)
        self.rect = new_surf.get_rect()
        self.rect.center = old_center
        self.surf = new_surf

        point = Vec(old_center[0], old_center[1])
        self.a.rotate_around(point, degr)
        self.b.rotate_around(point, degr)
        self.c.rotate_around(point, degr)
        self.d.rotate_around(point, degr)
    
    def rotate_around(self, point: Vec, degr: float) -> None:
        old_center = self.rect.center
        self.angle = (self.angle + degr) % 360
        # new_surf = pg.transform.rotate(self.surf_og, self.angle)
        new_surf = pg.transform.rotozoom(self.surf_og, self.angle, 1)
        rotated_offset = Vec(new_surf.get_rect().center) - Vec(self.surf_og.get_rect().center)

        self.rect = new_surf.get_rect(center=(point+rotated_offset).t)
        # self.rect.center = old_center
        self.surf = new_surf

        self.a.rotate_around(point, degr)
        self.b.rotate_around(point, degr)
        self.c.rotate_around(point, degr)
        self.d.rotate_around(point, degr)
    
    def intersects(self, other: 'Block' = None):
        """Check if intersects with other block."""
        intersect = []
        for line in self.lines:
            for line2 in other.lines:
                if line.intersects(line2):
                    intersect.append((line, line2))
        return intersect
    
    def translate(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.center = (self.x + self.w/2, self.y + self.h/2)

        self.a += Vec(dx, dy)
        self.b += Vec(dx, dy)
        self.c += Vec(dx, dy)
        self.d += Vec(dx, dy)
        self.lines = [Line(self.a, self.b), Line(self.b, self.c), Line(self.c, self.d), Line(self.d, self.a)]

    def test(self, other):
        """Check if the rectangle intersects with another rectangle."""
        intersect = self.intersects(other)
        if intersect:
            for line, line2 in intersect:
                line.draw(RED)
                line2.draw(RED)
                point = line.intersection(line2)
                point.draw(RED, 5)

    def draw(self):
        screen.blit(self.surf, self.rect)
        for line in self.lines:
            line.draw(GREEN)
        # pg.draw.rect(screen, RED, self.rect, 2)

        


class Tetromino():
    """Tetromino of 4 blocks. Outer corners as properties for rendering."""


    def __init__(self, x, y, color, size):
        # pg.sprite.Sprite.__init__(self)
        # self.image = pg.Surface((size, size))
        # self.image.set_colorkey(BLACK)
        # self.image.fill(GREEN)
        # self.image_rot = self.image.copy()
        # self.image.fill(GREEN)

        # self.rect = self.image.get_rect()
        # self.rect.center = (x, y)
        # self.rect.x = x
        # self.rect.y = y
        self.center = Vec(x, y)
        self.size = size
        self.color = color
        self.blocks : List[Block] = []
        self.blocks.append(Block(x-size, y, size, size))
        self.blocks.append(Block(x-size, y - size, size, size))
        self.blocks.append(Block(x, y, size, size))
        self.blocks.append(Block(x, y - size, size, size))

        # save corners for polygon drawing
        self.corners = []
        for block in self.blocks:
            self.corners.append(block.a)
            self.corners.append(block.b)
            self.corners.append(block.c)
            self.corners.append(block.d)

    @staticmethod
    def sample():
        return Tetromino(W // 2, 0, random.choice(COLORS), 20)

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y
        for rect in self.blocks:
            rect.update(x, y)
    
    def __iter__(self):
        return iter(self.blocks)

    def draw(self, surface):
        for block in self.blocks:
            block.draw()
        

    def rotate(self, rev=False):
        k = 5
        if rev:
            k *= -1
        for block in self.blocks:
            # block.rotate(k)
            block.rotate_around(self.center, k)

    def move(self, x, y):
        self.center += (x, y)
        for block in self.blocks:
            block.translate(x, y)
    
    def collides_with(self, other):
        for block in self.blocks:
            for other_block in other:
                if block.rect.colliderect(other_block.rect):
                    return True
        return False
    
    def wall_collision(self):
        """Check if any outer corners are outside the screen."""
        outer_corners = [self.blocks[0].a, self.blocks[0].b, self.blocks[0].c, self.blocks[0].d]

class Game:
    def __init__(self):        
        self.tetromino : Tetromino = None
        self.tetrominos : List[Tetromino] = []

        # self.reset()
        self.tetromino = Tetromino(W//2, H//2, COLORS[0], SIZE)
        self.tetrominos.append(self.tetromino)

        # For testing
        self.block = Block(W // 4, H // 3, SIZE, SIZE)
        # self.block.rotate(45)
        self.rect = pg.Rect(W // 4, H // 2, SIZE, SIZE)
        self.points = np.array([self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft])
        self.points = self.points - self.rect.center
        self.rot_speed = 15
        self.rotation_matrix = np.array([[np.cos(np.radians(self.rot_speed)), -np.sin(np.radians(self.rot_speed))], 
                                         [np.sin(np.radians(self.rot_speed)), np.cos(np.radians(self.rot_speed))]])
        # print(pg.display.list_modes())
        # self.I = [
        #     Line(Vec(0, 0), Vec(4 * SIZE, 0)),
        #     Line(Vec(4 * SIZE, SIZE), Vec(4 * SIZE, SIZE)),
        #     Line(Vec(4 * SIZE, SIZE)), Vec(0, SIZE),
        #     Line(Vec(0, SIZE), Vec(0, 0))
        # ]
        # https://static.wikia.nocookie.net/tetrisconcept/images/3/3d/SRS-pieces.png/revision/latest?cb=20060626173148
        center = np.array([SIZE, SIZE]) + np.array([SIZE, SIZE]) // 2

        self.I = np.array([[0, 0], [4, 0], [4, 1], [0, 1]]) * SIZE
        self.I -= np.array([SIZE * 2, SIZE // 2]) # center
        self.Ic = np.array([100, 100])
        
        self.J = np.array([[0, 0], [1, 0], [1, 1], [3, 1],
                           [3, 2], [0, 2]]) * SIZE
        self.J -= np.array([1, 1]) * SIZE + np.array([SIZE // 4, SIZE // 4])                                                      
        self.Jc = np.array([300, 100])

        self.L = np.array([[0, 1], [2, 1], [2, 0], 
                           [3, 0], [3, 2], [0, 2]]) * SIZE
        self.L -= np.array([2, 1]) * SIZE + np.array([-SIZE // 4, SIZE // 4])                           
        self.Lc = np.array([100, 300])

        self.O = np.array([[0, 0], [2 , 0], [2, 2], [0, 2]]) * SIZE 
        self.O -= np.array([SIZE, SIZE]) # center
        self.Oc = np.array([300, 300])
        
        self.S = np.array([[0, 1], [1, 1], [1, 0], [3, 0], [3, 1], 
                           [2, 1], [2, 2], [0, 2]]) * SIZE
        self.S -= np.array([1, 1]) * SIZE + np.array([SIZE // 2, 0]) # center
        self.Sc = np.array([100, 500])

        self.T = np.array([[0, 1], [1, 1], [1, 0], [2, 0], [2, 1], 
                           [3, 1], [3, 2], [0, 2]]) * SIZE
        self.T -= np.array([1, 1]) * SIZE + np.array([SIZE // 2, SIZE // 4]) # center
        self.Tc = np.array([300, 500])

        self.Z = np.array([[0, 0], [2, 0], [2, 1], [3, 1], [3, 2], 
                           [1, 2], [1, 1], [0, 1]]) * SIZE
        self.Z -= np.array([1, 1]) * SIZE + np.array([SIZE // 2, 0]) # center
        self.Zc = np.array([200, 400])

        self.tetrominos = [self.I, self.J, self.L, self.O, self.S, self.T, self.Z]
        self.tetromino_centers = [self.Ic, self.Jc, self.Lc, self.Oc, self.Sc, self.Tc, self.Zc]
        

    def reset(self):
        self.tetrominos.clear()
        self.tetromino = Tetromino.sample()
        self.tetrominos.append(self.tetromino)

    def run(self):
        while True:
            clock.tick(FPS)
            self.events()
            self.update()
            self.block.test(self.tetromino.blocks[0])
            self.draw()

    def update(self):
        pass
        # if self.tetromino.rect.y + self.tetromino. >= H:
        #     self.tetromino.move(0, -)
        #     self.tetromino = Tetromino.sample()
        #     self.tetrominos.append(self.tetromino)
        # for tetromino in self.tetrominos:
        #     for block in tetromino.blocks:
        #         if block.rect.y + block.h >= H:
        #             self.tetromino.move(0, -)
        #             self.tetromino = Tetromino(0, 0, COLORS[random.randint(0, 4)], )
        #             self.tetrominos.append(self.tetromino)
    
    def __iter__(self):
        return iter(self.tetrominos)


    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                if event.key == pg.K_r:
                    self.reset()

        keys = pg.key.get_pressed()
        if keys[pg.K_e]:
            self.tetromino.rotate(True)
        elif keys[pg.K_q]:
            self.tetromino.rotate()
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.tetromino.move(0, -3)
        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.tetromino.move(0, 3)
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.tetromino.move(-3, 0)
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.tetromino.move(3, 0)
                

    def draw(self):
        screen.fill(BLACK)
        # for tetromino in self.tetrominos:
        #     tetromino.draw(screen)
        
        # self.block.draw() # other
        # pg.draw.rect(screen, RED, self.rect, 0) # rect
        # self.block.test(self.tetromino.blocks[0]) # this
        # self.points = self.rotation_matrix @ self.points

        # Rotate points around their rect center
        # self.points = self.points @ self.rotation_matrix
        # self.points = self.points * 1.01
        # gfx.aapolygon(screen, self.points + self.rect.center, RED) # polygon
        # gfx.filled_polygon(screen, self.points + self.rect.center, RED) # polygon

        

        for i in range(len(COLORS)):
            self.tetrominos[i] = self.tetrominos[i] @ self.rotation_matrix
            gfx.aapolygon(screen, self.tetrominos[i] + self.tetromino_centers[i], COLORS[i]) # polygon
            gfx.filled_polygon(screen, self.tetrominos[i] + self.tetromino_centers[i], COLORS[i]) # polygon
            gfx.circle(screen, self.tetromino_centers[i][0], self.tetromino_centers[i][1], 10, WHITE) # circle
            


        pg.display.flip()
    

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
    







"""Tetris but with rigid rects that rotate and move continuously.

The game is played with the arrow keys. The left and right arrow keys
move the block left and right. The up arrow key rotates the block
clockwise. The down arrow key rotates the block counter-clockwise.
The space bar drops the block to the bottom of the screen.

The game ends when a block reaches the top of the screen.

TODO
- Better collision detection
- Rotation that sticks at 90 degree angles or soft body physics like
- Undo method from Game class that undoes to before collision between Tetrominoes
- Shapely intersection method for collision detection only works if the difference is expressed in one polygon

"""

import pygame as pg
import numpy as np
import random, time
from math import cos, sin, radians
from typing import List, Tuple, NewType
from pygame import gfxdraw as gfx
import matplotlib.path as mpltPath
import shapely.geometry as shp
from shapely import affinity

Tetromino = NewType('Tetromino', np.ndarray)
# Define some tetris colors 
WHITE, GREY, BLACK = (255, 255, 255), (128, 128, 128), (0, 0, 0)

TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED = (0, 255, 255), (0, 0, 255), (255, 165, 0), (255, 255, 0), (0, 255, 0), (165, 0, 165), (255, 0, 0)
COLORS = [TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# Define pygame objects
W, H = 400, 600 # (1920, 1080)
SIZE = 40
FPS = 30

# Define tetromino shapes # https://static.wikia.nocookie.net/tetrisconcept/images/3/3d/SRS-pieces.png/revision/latest?cb=20060626173148
I = np.array([[0, 0], [4, 0], [4, 1], [0, 1]]) * SIZE - np.array([SIZE * 2, SIZE // 2])
J = np.array([[0, 0], [1, 0], [1, 1], [3, 1], [3, 2], [0, 2]]) * SIZE - np.array([1, 1]) * SIZE - np.array([SIZE // 4, SIZE // 4])         
L = np.array([[0, 1], [2, 1], [2, 0], [3, 0], [3, 2], [0, 2]]) * SIZE - np.array([2, 1]) * SIZE - np.array([-SIZE // 4, SIZE // 4])                           
O = np.array([[0, 0], [2 , 0], [2, 2], [0, 2]]) * SIZE - np.array([SIZE, SIZE])
S = np.array([[0, 1], [1, 1], [1, 0], [3, 0], [3, 1], [2, 1], [2, 2], [0, 2]]) * SIZE - np.array([1, 1]) * SIZE - np.array([SIZE // 2, 0])
T = np.array([[0, 1], [1, 1], [1, 0], [2, 0], [2, 1], [3, 1], [3, 2], [0, 2]]) * SIZE - np.array([1, 1]) * SIZE - np.array([SIZE // 2, SIZE // 4])
Z = np.array([[0, 0], [2, 0], [2, 1], [3, 1], [3, 2], [1, 2], [1, 1], [0, 1]]) * SIZE - np.array([1, 1]) * SIZE - np.array([SIZE // 2, 0])
TETROMINOS = [I, J, L, O, S, T, Z]
I, J, L, O, S, T, Z = range(7)
names = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

CLEAR_LINE = shp.Polygon([(0, H // 2), (W, H // 2), (W, H // 2 + SIZE), (0, H // 2 + SIZE)])
MIN_AREA = 0.5 * SIZE ** 2
MOVE_SPEED = 3


R = 2 # Rotation speed degrees per frame
ROTATION = np.array([[np.cos(np.radians(R)), -np.sin(np.radians(R))], [np.sin(np.radians(R)), np.cos(np.radians(R))]])
def rotation_matrix(theta): return np.array([[np.cos(np.radians(theta)), -np.sin(np.radians(theta))], [np.sin(np.radians(theta)), np.cos(np.radians(theta))]])
def draw_bounds(screen, bounds): gfx.polygon(screen, [(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])], RED)

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

class Tetromino():
    """Defined by position and list of points. Accessing the points will return the points displaced by the position."""
    # TODO minimize use of self._points + self.pos

    def __init__(self, pos, piece: int, rot=None) -> None:
        self.pos = np.array(pos)  # Center of the tetromino - predefined for all?
        # self.last_pos = self.pos.copy()
        self._points = TETROMINOS[piece]  # Points of the tetromino - defines the shape
        self.type = names[piece]
        self.color = COLORS[piece]
        
        if rot:
            self._points = self._points @ rotation_matrix(rot)

    def __iter__(self):
        return iter(self._points + self.pos)
    
    def __repr__(self):
        return f"Tetromino({self.pos}, {names[self.piece]})"
    
    def __str__(self):
        return f"{names[self.piece]} at {self.pos}"

    @staticmethod
    def sample(pos):
        return Tetromino(pos, random.randint(0, 6))
    
    @property
    def points(self): # check if already done for this frame
        return self._points + self.pos
    
    @property
    def shape(self):
        return shp.Polygon(self.points)
    
    @shape.setter
    def shape(self, value):
        self._points = value - self.pos
    
    def rotate(self, rev=False, degr=None):
        """Rotate the tetromino. If rev is True, rotate in the opposite direction. Called before move"""
        self._points = np.dot(self._points, ROTATION.T) if rev else np.dot(self._points, ROTATION)
        if self.is_wall():
            self._points = np.dot(self._points, ROTATION.T) if not rev else np.dot(self._points, ROTATION)
    
    def move(self, x, y):
        """Move the tetromino by x and y and wall check. Called before update."""
        self.pos += (x, y)
        if self.is_wall():
            self.pos -= (x, 0)

    def update(self):
        """Called every frame. Move the tetromino down and floor check. Called before undo."""
        self.pos += [0, 1]
        if self.is_floor():
            self.pos -= [0, 1]
            return True
        # self.last_pos = self.pos.copy()
    

    def undo(self):  # Useless
        """Undo the last move. Called after collision with other tetromino."""
        print(self.pos, "->", self.last_pos)
        self.pos = self.last_pos
    
    def draw(self, screen):
        points = self._points + self.pos
        gfx.aapolygon(screen, points, self.color) # polygon
        gfx.filled_polygon(screen, points, self.color) # filled polygon
        draw_bounds(screen, self.shape.bounds)

    
    def is_floor(self):  # TODO collect floor and wall into singular bound check
        """Check if the tetromino is at the bottom of the screen."""
        bounds = self.shape.bounds
        return bounds[3] >= H
    
    def is_wall(self):
        """Check if the tetromino is at the side of the screen."""
        bounds = self.shape.bounds        
        return bounds[0] < 0 or bounds[2] > W
    
    def intersects(self, other: Tetromino = None) -> bool:
        """Return True if the tetromino intersects with another tetromino. 
        If no other tetromino is given, check if the tetromino intersects with the clear line."""
        if other:
            return self.shape.intersects(other.shape)
        else:
            return self.shape.intersects(CLEAR_LINE)
    
    def cut(self):
        """Cut off part of tetromino intersecting clear line. Returns True if resulting tetromino is bigger than minimum area."""     
        difference = self.shape - CLEAR_LINE
        if difference.area > MIN_AREA:
            try:
                self._points = difference.exterior.coords[:-1] - self.pos
            except:
                pass
            return True

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((W, H))
        pg.display.set_caption("Rigid Tetris")
        self.clock = pg.time.Clock()
        self.spawn = (W // 2, 0)
        
        self.reset()  

    def reset(self):
        self.tetromino = Tetromino.sample(self.spawn)
        self.tetrominos : List[Tetromino] = []  # Keeps track of dead tetrominos
        self.t = 0  # Frame counter

    def new_tetromino(self):
        if self.t < 4:  # Game over
            self.reset()
            return
        # assert(time > 0.2), "Tetrominoes are spawning too fast! " + str(time)
        self.tetrominos.append(self.tetromino)
        self.tetromino = Tetromino.sample(self.spawn)
        self.t = 0
    
    """Main game loop"""
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.events()
            self.move()
            self.update()
            self.draw()

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
                if event.key == pg.K_SPACE:
                    self.new_tetromino()
                if event.key == pg.K_t:
                    self.test_event()

    def move(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_e]:
            self.tetromino.rotate(True)
        elif keys[pg.K_q]:
            self.tetromino.rotate()
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.tetromino.move(0, -MOVE_SPEED)
        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.tetromino.move(0, MOVE_SPEED)
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.tetromino.move(-MOVE_SPEED, 0)
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.tetromino.move(MOVE_SPEED, 0)

    def update(self):
        self.t += 1
        if self.tetromino.update():
            self.new_tetromino()
        
        # check for collisions
        for other in self.tetrominos:
            if self.tetromino.intersects(other):
                self.new_tetromino()
                break
        
    def draw(self):
        self.screen.fill(BLACK)
        self.tetromino.draw(self.screen)
        for tetromino in self.tetrominos:
            tetromino.draw(self.screen)

        pg.display.flip()

    """Test methods"""
    def test(self, test_num):
        test_init = getattr(self, f"test_{test_num}_init")
        test_init()
        self.test_event = getattr(self, "test_" + str(test_num) + "_event")
        test_method = getattr(self, "test_" + str(test_num))
        print("Running test", test_num)
        while True:
            self.clock.tick(FPS)
            test_method()
            self.events()
    
    def test_1_init(self):
        self.pos = (W // 4, H // 2 - 30)
        # self.tetromino = Tetromino(self.pos, I, 90)
        self.tetromino = Tetromino(self.pos, S, 90)
        
    def test_1_event(self):
        print("> ")

    def test_1(self):
        # self.move()
        # print(self.tetromino.shape.minimum_clearance)

        # self.tetromino.rotate()

        self.screen.fill(BLACK)
        
        gfx.aapolygon(self.screen, self.tetromino.shape.exterior.coords, GREEN)
        gfx.filled_polygon(self.screen, self.tetromino.shape.exterior.coords, GREEN)

        if self.tetromino.intersects():
            try:
                disjoint = self.tetromino.shape - CLEAR_LINE
                gfx.aapolygon(self.screen, disjoint.exterior.coords, YELLOW)
                gfx.filled_polygon(self.screen, disjoint.exterior.coords, YELLOW)
                disjoint = self.tetromino.shape & CLEAR_LINE
                gfx.aapolygon(self.screen, disjoint.exterior.coords, WHITE)
                gfx.filled_polygon(self.screen, disjoint.exterior.coords, WHITE)
            except:
                pass
            # if self.tetromino.cut():
            #     try:
            #         disjoint = self.tetromino.shape - CLEAR_LINE
            #         gfx.polygon(self.screen, YELLOW, disjoint.exterior.coords)
            #     except:
            #         pass
            # else:
            #     self.tetromino = Tetromino.sample(self.pos)
        gfx.filled_circle(self.screen, *self.tetromino.pos, 5, BLACK)
        gfx.filled_polygon(self.screen, CLEAR_LINE.exterior.coords, RED + (100,)) # filled polygon      
        pg.display.flip()

if __name__ == "__main__":
    game = Game()
    game.test(1)
    # game.run()
    







"""Tetris but with rigid rects that rotate and move continuously.

The game is played with the arrow keys. The left and right arrow keys
move the block left and right. The up arrow key rotates the block
clockwise. The down arrow key rotates the block counter-clockwise.
The space bar drops the block to the bottom of the screen.

The game ends when a block reaches the top of the screen.


The code makes heavy use of the shapely module.
https://shapely.readthedocs.io/en/stable/manual.html

TODO
- Dinamically change the size of the screen based on the size of the blocks.
- Rotation that sticks at 90 degree angles or soft body physics like
- Collision tolerance to cut corners. Determine intersection area, and if below, response, otherwise place.
- Consider better game over conditions, current is an infinite incrementer t
- While holding down, make 4 collision checks per frame

NOTE
- Use shapely.ops.transform(func, geom) to map all points in a shape
- Use STR-packed R-tree for collision detection and recreate the tree after each line deletion
- Convert to numpy arrays using np.asarry
- SNnapping is a thing
- Consider scoring based on area covered in line

"""

import pygame as pg
import numpy as np
import random, time
from typing import List, Tuple, NewType
from pygame import gfxdraw as gfx
import shapely.geometry as shp
from shapely import affinity
random.seed(42)



Tetromino = NewType('Tetromino', np.ndarray)
# Define some tetris colors 
WHITE, GREY, BLACK = (255, 255, 255), (128, 128, 128), (0, 0, 0)

# TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED = (0, 255, 255), (0, 0, 255), (255, 165, 0), (255, 255, 0), (0, 255, 0), (165, 0, 165), (255, 0, 0)
TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED = (0, 255, 255, 180), (0, 0, 255, 180), (255, 165, 0, 180), (255, 255, 0, 180), (0, 255, 0, 180), (165, 0, 165, 180), (255, 0, 0, 180)
RED_ = (255, 0, 0)
COLORS = [TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# Define pygame objects
SIZE = 80
W, H = SIZE * 10, SIZE * 15 # (1920, 1080)
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

CLEAR_LINE = [(0, 0), (W, 0), (W, SIZE), (0, SIZE)]
LINE_AREA = W * SIZE * 0.8  # Controls the ratio of area a line must be covered for it to clear
MIN_AREA = 0.5 * SIZE ** 2  # How small a piece can be before it is considered starved and removed from the game
MOVE_SPEED = 3
K = 3


R = 3 # Rotation speed degrees per frame
ROTATION = np.array([[np.cos(np.radians(R)), -np.sin(np.radians(R))], [np.sin(np.radians(R)), np.cos(np.radians(R))]])
def rotation_matrix(theta): return np.array([[np.cos(np.radians(theta)), -np.sin(np.radians(theta))], [np.sin(np.radians(theta)), np.cos(np.radians(theta))]])
def draw_bounds(screen, bounds): gfx.aapolygon(screen, [(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])], RED)

class Tetromino():
    """Purely defined from shapely Polygon"""

    def __init__(self, pos, piece: int, rot=None) -> None:
        self.shape = shp.Polygon(TETROMINOS[piece])
        self.shape = affinity.translate(self.shape, *pos)
        self.type = names[piece]
        self.color = COLORS[piece]

        if rot:
            self.shape = affinity.rotate(self.shape, rot, origin=pos)        


    @staticmethod
    def sample(pos):
        return Tetromino(pos, I)
        return Tetromino(pos, random.randint(0, 6))
    
    @property
    def pos(self, int_=True):
        if int_:
            return tuple(map(int, self.shape.centroid.coords[0]))
        return self.shape.representative_point().coords[0]
    
    def rotate(self, rev=False, degr=None):
        """Rotate the tetromino. If rev is True, rotate in the opposite direction. Called before move"""
        degr = degr if degr else R        
        new_shape = affinity.rotate(self.shape, -degr if rev else degr, use_radians=False)
            
        if self.is_wall(new_shape.bounds):
            return
        self.shape = new_shape
    
    def move(self, x, y):
        """Move the tetromino by x and y and wall check. Called before update."""
        new_shape = affinity.translate(self.shape, x, y)
        if self.is_wall(new_shape.bounds):
            return
        self.shape = new_shape

    def update(self):
        """Called every frame. Move the tetromino down and floor check. Called before undo."""
        new_shape = affinity.translate(self.shape, 0, MOVE_SPEED)
        if self.is_floor(new_shape.bounds):
            return True
        self.shape = new_shape
    
    def draw(self, screen):
        """Draw the tetromino on the screen."""
        gfx.aapolygon(screen, self.shape.exterior.coords, self.color)
        gfx.filled_polygon(screen, self.shape.exterior.coords, self.color)   

    
    def is_floor(self, bounds):  # TODO collect floor and wall into singular bound check
        """Check if the tetromino is at the bottom of the screen."""
        return bounds[3] > H
    
    def is_wall(self, bounds):
        """Check if the tetromino is outside the side of the screen."""
        return bounds[0] < 0 or bounds[2] > W
    
    def intersects(self, other) -> bool:
        """Return True if the tetromino intersects with another tetromino. 
        If no other tetromino is given, check if the tetromino intersects with the clear line."""
        return self.shape.intersects(other.shape) if isinstance(other, Tetromino) else self.shape.intersects(other)
    
    def cut(self, line):
        """Cut off part of tetromino intersecting line. Returns True if resulting tetromino is bigger than minimum area."""     
        difference = self.shape - line
        # check type of returned object
        if difference.area > MIN_AREA:
            if isinstance(difference, shp.Polygon):
                self.shape = difference
            elif isinstance(difference, shp.MultiPolygon):
                # TODO define new tetrominoes from resulting polygons
                self.shape = difference[0]
            else:
                raise TypeError('Unknown type of difference')
        else:
            return True # if the tetromino is too small, return True to delete it

class Game:
    def __init__(self):
        pg.init()
        self.font = pg.font.SysFont('Arial', 30)
        self.screen = pg.display.set_mode((W, H))
        pg.display.set_caption("Rigid Tetris")
        self.clock = pg.time.Clock()
        self.spawn = (W // 2, 0)

        # Create field of CLEAR_LINEs
        lines = []
        for i in range(0, H, SIZE):
            line = shp.Polygon(CLEAR_LINE)
            line = affinity.translate(line, 0, i)
            lines.append(line)
        
        self.lines = lines
        
        self.reset()  
    
    @property  # y property? - to signal shapes no mutation
    def shapes(self):
        return (shape for shape in self.tetrominos.shape)

    def reset(self):
        self.tetromino = Tetromino.sample(self.spawn)
        self.tetrominos : List[Tetromino] = []  # Keeps track of dead tetrominos
        self.t = 0  # Frame counter

    def new_tetromino(self):
        if self.t < 4:  # Game over
            self.reset()
            return      
        
        # Add tetromino to list of dead tetrominos
        self.tetrominos.append(self.tetromino)
        self.tetromino = Tetromino.sample(self.spawn)
        self.t = 0

        # check if any lines are full
        cleared = self.clear_lines()
        if cleared:
            print(f'{cleared} lines cleared')

    def clear_line(self, line, intersecting: List[Tetromino]):
        """Clear a single line by clearing intersection with line. Returns True if any tetromino died of starvation."""
        for tetromino in intersecting:
            if tetromino.cut(line):
                self.tetrominos.remove(tetromino)

    def clear_lines(self):
        """Check if any lines are full and clear them. Returns the number of lines cleared."""
        cleared = 0
        for line in self.lines:
            area = 0.0 # area of tetrominos intersecting with line
            intersecting = []
            for tetromino in self.tetrominos:
                if tetromino.intersects(line):
                    area += (tetromino.shape & line).area
                    intersecting.append(tetromino)
            
            # Clear line
            if area >= LINE_AREA:
                print("clear line")
                self.clear_line(line, intersecting)
                cleared += 1

        return cleared
    
    """Main game loop"""
    def run(self, debug=False):
        if not debug:
            while True:
                self.clock.tick(FPS)
                self.events()
                self.move()
                self.update()
                self.draw()
        else:
            while True:
                self.clock.tick(FPS)
                self.events()
                self.move()
                self.update()
                self.debug()

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
            self.tetromino.rotate(False)
        elif keys[pg.K_q]:
            self.tetromino.rotate(True)
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.tetromino.move(0, -K * MOVE_SPEED)
        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.tetromino.move(0, K *MOVE_SPEED)
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.tetromino.move(-K *MOVE_SPEED, 0)
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.tetromino.move(K *MOVE_SPEED, 0)

    def update(self):
        self.t += 1

        # Update tetromino
        if self.tetromino.update():
            self.new_tetromino()
        
        # check for tetromino collisions
        self.collision_detection()        

    def draw(self):
        self.screen.fill(BLACK)

        # draw SIZExSIZE grid
        for i in range(0, W, SIZE):
            for j in range(0, H, SIZE):
                pg.draw.rect(self.screen, GREY, (i, j, SIZE, SIZE), 1)

        # Draw tetrominos
        self.tetromino.draw(self.screen)
        for tetromino in self.tetrominos:
            tetromino.draw(self.screen)

        pg.display.flip()

    def debug(self):
        self.screen.fill(BLACK)

        # draw SIZExSIZE grid
        for i in range(0, W, SIZE):
            for j in range(0, H, SIZE):
                pg.draw.rect(self.screen, GREY, (i, j, SIZE, SIZE), 1)

        # draw tetrominos
        self.tetromino.draw(self.screen)
        for tetromino in self.tetrominos:
            tetromino.draw(self.screen)

        self.draw_bounds(self.tetromino.shape.bounds)
        for t in self.tetrominos:
            self.draw_bounds(t.shape.bounds)

        pg.display.flip()
    
    def draw_bounds(self, bounds):
        gfx.aapolygon(self.screen, [(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])], RED)

    """Collision methods"""
    def collision_detection(self):
        for other in self.tetrominos:
            if self.tetromino.intersects(other):
                self.collision_response()
                break
    
    def collision_response(self):
        self.new_tetromino()

    """Test methods"""
    def test(self, test_num):
        getattr(self, f"test_{test_num}_init")()
        self.test_event = getattr(self, "test_" + str(test_num) + "_event")
        test_method = getattr(self, "test_" + str(test_num))
        
        print("Running test", test_num)
        while True:
            self.clock.tick(FPS)
            test_method()
            self.events()
    
    def test_1_init(self):
        raise NotImplementedError("test_1 not implemented")
    def test_1_event(self):
        raise NotImplementedError("test_1 not implemented")
    def test_1(self):
        raise NotImplementedError("test_1 not implemented")


if __name__ == "__main__":
    game = Game()
    # game.test(1)
    game.run(debug=True)
    







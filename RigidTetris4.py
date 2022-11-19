"""Tetris but with rigid rects that rotate and move continuously.

The game is played with the arrow keys. The left and right arrow keys
move the block left and right. The up arrow key rotates the block
clockwise. The down arrow key rotates the block counter-clockwise.
The space bar drops the block to the bottom of the screen.

The game ends when a block reaches the top of the screen.


The code makes heavy use of the shapely module.
https://shapely.readthedocs.io/en/stable/manual.html

TODO
- Proper boundary checking. Currently tetriminos are cut within and leaving pieces out of bounds - make line longer?
- Have cut define new tetrimones for MultyPoly (currently just replaces with a piece of the cut)
- Rotation that sticks at 90 degree angles or soft body physics like
- Collision tolerance to cut corners. Determine intersection area, and if below, response, otherwise place.
- Consider better game over conditions, current is an infinite incrementer t
- Make more frequent collision checks for faster bodies
- Extend screen bounds to determine accurate boundary collisions


BUG
- When finding extracting shapes fromt split in cut using geoms, a moot warning is given
- Pieces are accumulating when cut, possible causes:
    - Out of bounds pieces are not being removed
    - Small area check not working properæy - the one liner
    - The cut is not being applied properly



NOTE
- Use shapely.ops.transform(func, geom) to map all points in a shape
- Use STR-packed R-tree for collision detection and recreate the tree after each line deletion
- Convert to numpy arrays using np.asarry
- Snapping is a thing

CONSIDER
- Consider scoring based on area covered in line
- Settle pieces after a certain amount of time?
- Keep small tetrimos for cluttering the screen and cool spashing of small bodies

"""

import pygame as pg
import numpy as np
import random, time
from typing import List, Tuple, NewType
from pygame import gfxdraw as gfx, Vector2 as V2
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
SIZE = 80#120
W, H = SIZE * 10, SIZE * 15
FPS = 30
dt = 1 / FPS

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

# CLEAR_LINE = [(-50, 0), (W+50, 0), (W+50, SIZE), (-50, SIZE)]
CLEAR_LINE = [(0, 0), (W, 0), (W, SIZE), (0, SIZE)]
LINE_AREA = W * SIZE * 0.8  # Controls the ratio of area a line must be covered for it to clear
MIN_AREA = 0.5 * SIZE ** 2  # How small a piece can be before it is considered starved and removed from the game
MOVE_SPEED, ROT_SPPED = 10, 30
FLOOR_FRIC, WALL_FRIC, ROT_FRIC = 0.3, 0.8, 0.9
ACC = (0, 100)
FORCE = 1.4
K = 3


R = 3 # Rotation speed degrees per frame
ROTATION = np.array([[np.cos(np.radians(R)), -np.sin(np.radians(R))], [np.sin(np.radians(R)), np.cos(np.radians(R))]])
def rotation_matrix(theta): return np.array([[np.cos(np.radians(theta)), -np.sin(np.radians(theta))], [np.sin(np.radians(theta)), np.cos(np.radians(theta))]])
def draw_bounds(screen, bounds): gfx.aapolygon(screen, [(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])], RED)

class Tetromino():
    """Purely defined from shapely Polygon
    This acts as kinematic body when current, and otherwise is dynamic.
    Transitions from kinematic KIN to dynamic when it hits the floor.

    
    shape.bounds = (minx, miny, maxx, maxy)

    TODO
    - limit calls to shapes.centroid
    
    """

    def __init__(self, piece=0, shape=None, pos=(W // 2, 0), rot=None) -> None:
        if shape is None:
            self.shape = shp.Polygon(TETROMINOS[piece])
            self.shape = affinity.translate(self.shape, *pos)
            if rot:
                self.shape = affinity.rotate(self.shape, rot, origin=pos)
        else:
            self.shape = shape

        self.piece = piece
        self.type = names[piece]
        self.color = COLORS[piece]

        # Physics
        self.is_kinematic = True # Kinematic or dynamic
        self.pos = V2(pos)
        self.vel = V2(0, 50*MOVE_SPEED)
        self.acc = 100 # y component
        self.omega = 0
        self.mass = 1 # Updates when cut

        # self.inertia = 1
        # self.friction = 0.1
        # self.force = V2(0, 0)
        # self.torque = 0

    """Kinematic methods"""
    def move(self):
        """Move the tetromino by x and y and wall check. Called before update."""
        if self.shape.bounds[3] > H:  # Early check to transition to dynamic
            return True

        keys = pg.key.get_pressed()
        
        if keys[pg.K_e]:  # Rotation
            self.omega += ROT_SPPED
        elif keys[pg.K_q]:
            self.omega += -ROT_SPPED

        if keys[pg.K_w] or keys[pg.K_UP]:  # Vertical
            self.vel.y -= K * MOVE_SPEED
        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vel.y += K * MOVE_SPEED

        if keys[pg.K_a] or keys[pg.K_LEFT]: # Horizontal
            self.vel.x -= K * MOVE_SPEED
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vel.x += K * MOVE_SPEED
        
        self.update()
        
    def slam(self):
        """Slam downwards"""
        self.vel *= FORCE


    """Dynamic methods"""
    def update(self):
        """Intrinsic collisions of boundary. Updates shape"""
        # self.vel.y += self.acc * dt if not self.boundary_collision() else 0
        if self.boundary_collision():
            self.vel.y = 0
            # self.omega = 0
            return
        self.vel.y += self.acc * dt
        self.omega *= ROT_FRIC

        self.shape = affinity.rotate(self.shape, self.omega * dt, origin=self.shape.centroid.coords[0])
        self.shape = affinity.translate(self.shape, *(self.vel * dt))
    
    def boundary_collision(self):
        """Discrete collision detection and response. Returns True if tetromino is floor"""
        left, _, right, bot = self.shape.bounds

        if left < 0 or right > W: # Wall
            self.vel.x *= -WALL_FRIC

        if bot > H: # Floor
            self.vel.y *= -FLOOR_FRIC            
            return True
    
    def draw(self, screen):
        """Draw the tetromino on the screen."""
        gfx.aapolygon(screen, self.shape.exterior.coords, self.color)
        gfx.filled_polygon(screen, self.shape.exterior.coords, self.color)

        # center in int
        center = tuple(map(int, self.shape.centroid.coords[0]))
        gfx.filled_circle(screen, *center, 5, WHITE) 

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
                # print(f"Created {len(difference.geoms)} new pieces from cut")
                self.shape = difference.geoms[0]
                return [Tetromino(piece=self.piece, shape=split) for split in difference.geoms[1:] if split.area > MIN_AREA]
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
    
    # @property  # y property? - to signal shapes no mutation
    # def shapes(self):
    #     return (shape for shape in self.tetrominos.shape)

    def reset(self):
        self.bag = []
        self.score = 0
        self.tetrominos : List[Tetromino] = []  # Keeps track of dead tetrominos
        self.t = 10  # Frame counter
        self.current = Tetromino(piece=self.sample_bag(), pos=self.spawn)

    def new_tetromino(self):
        if self.t < 2:  # Game over
            self.reset()
            return      
        
        # Add tetromino to list of dead tetrominos
        self.tetrominos.append(self.current)
        self.current = Tetromino(piece=self.sample_bag(), pos=self.spawn)
        self.t = 0

        # check if any lines are full
        self.score += self.clear_lines()
    
    def sample_bag(self):
        """Return a list of tetrominoes in the bag."""
        if self.bag == []:
            self.bag = [0, 1, 2, 3, 4, 5, 6]
            random.shuffle(self.bag)
        
        return self.bag.pop()
        

    def clear_line(self, line, intersecting: List[Tetromino]):
        """Clear a single line by clearing intersection with line. Returns True if any tetromino died of starvation."""
        for tetromino in intersecting:
            result = tetromino.cut(line)
            if isinstance(result, bool):
                self.tetrominos.remove(tetromino)
            elif isinstance(result, list):
                self.tetrominos.extend(result)
            
        print(f'{len(self.tetrominos)} tetrominos')

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
                self.clear_line(line, intersecting)
                cleared += 1

        return cleared
    
    """Main game loop"""
    def run(self, debug=False):
        if not debug:
            while True:
                self.clock.tick(FPS)
                self.events()
                self.update()
                self.draw()
        else:
            while True:
                self.clock.tick(FPS)
                self.events()
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
                if event.key == pg.K_p:  # pause
                    while True:
                        event = pg.event.wait()
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_p:
                                break
                            elif event.key == pg.K_ESCAPE:
                                pg.quit()
                                quit()
                if event.key == pg.K_r:
                    self.reset()
                if event.key == pg.K_SPACE:
                    self.current.slam()
                    self.new_tetromino()
                if event.key == pg.K_t:
                    self.test_event()

     

    def update(self):
        self.t += 1

        # Update current kinematics
        if self.current.move():
            self.new_tetromino()
        
        # Update the tetrominos dynamics
        for tetromino in self.tetrominos:
            tetromino.update()

        
        # check for tetromino collisions
        self.collision_detection()        

    def draw(self):
        self.screen.fill(BLACK)

        # draw SIZExSIZE grid
        for i in range(0, W, SIZE):
            for j in range(0, H, SIZE):
                pg.draw.rect(self.screen, GREY, (i, j, SIZE, SIZE), 1)

        # Draw tetrominos
        self.current.draw(self.screen)
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
        self.current.draw(self.screen)
        for tetromino in self.tetrominos:
            tetromino.draw(self.screen)

        self.draw_bounds(self.current.shape.bounds)
        for t in self.tetrominos:
            self.draw_bounds(t.shape.bounds)

        pg.display.flip()
    
    def draw_bounds(self, bounds):
        gfx.aapolygon(self.screen, [(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])], RED)

    """Collision methods"""
    def collision_detection(self):
        """Collision detection bettween tetriminos and placement check."""
        for i, a in enumerate(self.tetrominos):
            for b in self.tetrominos[i+1:]:
                if a.intersects(b):
                    self.collision_response(a, b)

        # Current tetromino placement
        for tetro in self.tetrominos:
            if self.current.intersects(tetro):
                self.new_tetromino()
                break
    
    def collision_response(self, a: Tetromino, b: Tetromino):
        """Collision response between two tetrominos."""
        # a.vel, b.vel = b.vel, a.vel  # swap velocities
        self.collision_displacement(a, b)
    
    def collision_displacement(self, a: Tetromino, b: Tetromino):
        """Displace two tetrominos to avoid sticking."""
        pass




        

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
    game.run(debug=False)
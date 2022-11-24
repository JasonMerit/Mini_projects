"""Tetris but with rigid rects that rotate and move continuously.

The game is played with the arrow keys. The left and right arrow keys
move the block left and right. The up arrow key rotates the block
clockwise. The down arrow key rotates the block counter-clockwise.
The space bar drops the block to the bottom of the screen.

The game ends when a block reaches the top of the screen.

TODO
- Rotation that sticks at 90 degree angles or soft body physics like
- Collision tolerance to cut corners. Determine intersection area, and if below, response, otherwise place.
- Consider better game over conditions, current is an infinite incrementer t
- Sweep and prune
- TMI in shape.intersects: Only intereted in max displacement (requires velocity)
- Let moment of inertia be approximated by a circle or the minimum bounding box
- Test get_normal()

BUG
- Pieces are accumulating when cut, possible causes:
    - Out of bounds pieces are not being removed
    - Small area check not working properæy - the one liner
    - The cut is not being applied properly

Assumptions
- Tetriminos are always convex


NOTE
- Intuitive collision https://fotino.me/2d-parametric-collision-detection/ but computationally heavy
- Cops are hard to distribute in all scanarious, see BUG INTERSECT 1

CONSIDER
- Consider scoring based on area covered in line
- Settle pieces after a certain amount of time?
- Keep small tetrimos for cluttering the screen and cool spashing of small bodies
- Make more frequent collision checks for faster bodies
- repeat collision checks until no collisions
- Simplyfing everything by abusing rotation and assuming at rot = 0 all sides are cardinal
- - then fragments may suffer, but perhaps treat them differently.

Status
- Boundary collision works great by forcing the piece to stay within the bounds before updating
- Shape is supreme with intersection and everything

Beauty over speed
- seg_intersect coincident

Common errors
- <class 'pygame.math.Vector2'> returned a result with an error set - give a tuple instead or use * to unpack 
- not .copy()ing the shape when creating a new tetromino




"""

import pygame as pg
import numpy as np
import random, time, sys
from typing import List, Tuple, NewType
from math import sin, cos, radians
from pygame import gfxdraw as gfx, Vector2 as V2

random.seed(42)

Tetromino = NewType('Tetromino', object)
Shape = NewType('Shape', object)
Line = NewType('Line', Tuple[V2, V2])
# Define some tetris colors 
WHITE, GREY, BLACK = (255, 255, 255), (128, 128, 128), (0, 0, 0)

# TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED = (0, 255, 255), (0, 0, 255), (255, 165, 0), (255, 255, 0), (0, 255, 0), (165, 0, 165), (255, 0, 0)
TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED = (0, 255, 255, 180), (0, 0, 255, 180), (255, 165, 0, 180), (255, 255, 0, 180), (0, 255, 0, 180), (165, 0, 165, 180), (255, 0, 0, 180)
RED_ = (255, 0, 0)
COLORS = [TURQUOISE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# Define pygame objects
SIZE = 80#120
AREA = 4 * SIZE ** 2
W, H = SIZE * 10, SIZE * 15
FPS = 60
dt = 1 / FPS

# Define tetromino shapes # https://static.wikia.nocookie.net/tetrisconcept/images/3/3d/SRS-pieces.png/revision/latest?cb=20060626173148
# Remember to .copy when using
I = np.array([[0, 0], [4, 0], [4, 1], [0, 1]]) * SIZE
J = np.array([[0, 0], [1, 0], [1, 1], [3, 1], [3, 2], [0, 2]]) * SIZE
L = np.array([[0, 1], [2, 1], [2, 0], [3, 0], [3, 2], [0, 2]]) * SIZE
O = np.array([[0, 0], [2 , 0], [2, 2], [0, 2]]) * SIZE
S = np.array([[0, 1], [1, 1], [1, 0], [3, 0], [3, 1], [2, 1], [2, 2], [0, 2]]) * SIZE
T = np.array([[0, 1], [1, 1], [1, 0], [2, 0], [2, 1], [3, 1], [3, 2], [0, 2]]) * SIZE
Z = np.array([[0, 0], [2, 0], [2, 1], [3, 1], [3, 2], [1, 2], [1, 1], [0, 1]]) * SIZE
TETROMINOS = [I, J, L, O, S, T, Z]
SHAPES = [I, L, J, O, S, T, Z]
I, J, L, O, S, T, Z = range(7)
NAMES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
SPAWNS = [(-2*SIZE, 0), (-3*SIZE//2, -SIZE), (-3*SIZE//2, -SIZE), (-SIZE, -SIZE), (-3*SIZE//2, -SIZE), (-3*SIZE//2, -SIZE), (-3*SIZE//2, -SIZE)]
CENTROIDS = np.array(([2*SIZE, SIZE//2], [7*SIZE//4, 5*SIZE//4], [5*SIZE//4, 5*SIZE//4], 
                      [SIZE, SIZE], [6*SIZE//4, SIZE], [3*SIZE//2, 5*SIZE//4], [6*SIZE//4, SIZE]))
PERIMETERS = np.power(np.array([8, 10, 10, 8, 10, 10, 10]) * SIZE, 2)                      
CLEAR_FIELD = np.array([[W // 2, SIZE // 2], [0, 0], [W, 0], [W, SIZE], [0, SIZE]])  # + centroid

LINE_AREA = W * SIZE * 0.8  # Controls the ratio of area a line must be covered for it to clear
MIN_AREA = 0.5 * SIZE ** 2  # How small a piece can be before it is considered starved and removed from the game
MOVE_SPEED, ROT_SPEED = 2, 5
FLOOR_FRIC, WALL_FRIC, ROT_FRIC = 0.2, 0.4, 0.3
GRAV, MOI = 100, SIZE ** 4 # pi * D^4/64
FORCE = 1.4

# Minimizing
MAX_SPEED, MAX_OMEGA = 100, 100

# helper functions

def seg_intersect(a1: V2, a2: V2, b1: V2, b2: V2) -> V2: # A(a1 -> a2) and B(b1 -> b2) are line segments
    # When parallel, seg_intersect should return average of overlapping segments
    db = b2 - b1
    da = a2 - a1
    denom = da.cross(db)
    if denom == 0: # parallel, check for coincident
        # check if lines are on same axis (numerators from outside different = 0)
        d0 = a1 - b1
        if db.cross(d0) != 0 or da.cross(d0) != 0: 
            return V2(0, 0)

        # project points onto line
        dot_a1 = a1.dot(db)
        dot_a2 = a2.dot(db)
        dot_b1 = b1.dot(db)
        dot_b2 = b2.dot(db)
        # find overlap
        min_a, max_a = min(dot_a1, dot_a2), max(dot_a1, dot_a2)
        min_b, max_b = min(dot_b1, dot_b2), max(dot_b1, dot_b2)
        if min_a > max_b or min_b > max_a: # no overlap
            return V2(0, 0)

        # return center of overlap over larger segment
        return (a1 + a2) / 2 if max_a - min_a < max_b - min_b else (b1 + b2) / 2
    
    d0 = a1 - b1
    ua = db.cross(d0) / denom
    if ua < 0 or ua > 1: return V2(0, 0) # out of range

    ub = da.cross(d0) / denom
    if ub < 0 or ub > 1: return V2(0, 0) # out of range

    return a1 + da * ua

def _seg_intersect(a1: V2, a2: V2, b1: V2, b2: V2) -> V2: # Same but ignore parallel lines
    db = b2 - b1
    da = a2 - a1
 
    denom = da.cross(db)
    if denom == 0: return V2(0, 0)# parallel, fuck it
        
    d0 = a1 - b1
    ua = db.cross(d0) / denom
    if ua < 0 or ua > 1: return V2(0, 0) # out of range

    ub = da.cross(d0) / denom
    if ub < 0 or ub > 1: return V2(0, 0) # out of range

    return a1 + da * ua

def perp(v): return V2(-v.y, v.x)
    
# debug: check if this is correct
def get_normal(a, b): return perp(a - b) # left normal (because clockwise polygon) 
    


class Shape():
    """Shape class
    
    Keep centroid and corners in one matrix, since centroid remains constant relative to corners.

    Attributes:
        id (int): piece type
        array (np.array): 2D array of V2 (clockwise)
        corners (list): list of V2 exterior coordinates. Saved as array[1:]
        polygon (list): corners, but looped around
        centroid (V2): centroid of shape (axis of rotation). Saved as array[0]
    """

    def __init__(self, id, pos=(W // 2, 0), rot=0, array=None):
        """Initialize shape. id piece type (color, centroid, corners), pos, array (centroid, corners)"""
        self.id = id
        self.color = COLORS[id]
        self.perimeter = PERIMETERS[id]
        self.rot = 0 # rotation in degrees - changed in rotate()
        if array is None:
            self.array = np.concatenate(([CENTROIDS[id]], SHAPES[id]))  # First entree is centroid
            self.translate(SPAWNS[id])  # offset depending on tetrimino
        else:            
            self.array = array
        
        self.translate(pos)
        self.rotate(rot)


    @property
    def corners(self) -> List[V2]: # get corners as V2 objects
        return [V2(*corner) for corner in self.array[1:]]
    
    @property
    def polygon(self) -> List[V2]: # get corners looped around as V2 objects
        return [V2(*corner) for corner in np.concatenate((self.array[1:], self.array[1].reshape(1, 2)))]
    
    @property
    def centroid(self) -> V2:
        return V2(*self.array[0])
    
    @property
    def lines(self) -> List[Line]:
        """Get list of lines of shape"""
        return [(a, b) for a, b in zip(self.polygon, self.polygon[1:])]
    
    """properties requiring calculation"""
    def bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box of shape (minx, miny, maxx, maxy)"""
        xs, ys = zip(*self.corners)
        return min(xs), min(ys), max(xs), max(ys)
    
    def normals(self):
        """Get list of normals of shape""" # defined as left normal
        return [get_normal(a, b) for a, b in zip(self.polygon, self.polygon[1:])]
    
    

    """Geometry methods"""
    def bounds_intersect(self, other: Shape):
        """Check if bounding boxes intersect"""
        a = self.bounds()
        b = other.bounds()
        return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
    
    def poly_line(self, line):
        """Check if line intersects polygon by looping through THIS shape's lines"""
        for a, b in zip(self.polygon, self.polygon[1:]):
            if poi := seg_intersect(a, b, *line):
                normal = - perp(line[1] - line[0])
                return a, poi, normal # or b
    
    def intersect(self, other: Shape):
        """Check if two polygons intersect by looping over their lineslines
        # http://jeffreythompson.org/collision-detection/poly-poly.php"""
        a_lines = self.lines
        b_lines = other.lines

        pois = []
        b_crossed = []
        b_indx = []
        a_indx = []
        a_crossed = []
        for i, line_a in enumerate(a_lines):
            
            a_intersected = False
            for j, line_b in enumerate(b_lines):
                if intersect := seg_intersect(*line_a, *line_b):
                    pois.append(intersect)
                    if not line_b in b_crossed:
                        b_crossed.append(line_b)
                        b_indx.append(j)
                    a_intersected = True

            if a_intersected:
                a_crossed.append(line_a)
                a_indx.append(i)
        
        if pois == []:
            return
        
        a_indx.sort()                
        b_indx.sort() # May not appear in order due to funny looping

        a_cops = []
        b_cops = []
        # upcoming is dirty as fuck, but it works
        # note that a poly point appears twice in the line going in and the other going out.
        if len(a_indx) % 2 == 0: # ignore parallel

            # control for wrapping around
            kek = False
            if a_indx[-1] - a_indx[-2] > 2: # <--- this size is sketchy
                indx = a_indx.pop()
                indx -= len(a_lines)
                a_indx.insert(0, indx) 
                kek = True
            
            # third find cop that a cointains
            for a1_indx, a2_indx in zip(a_indx[0::2], a_indx[1::2]): # pairwise
                separation = a2_indx - a1_indx
                if separation == 1: # one cop
                    cop = a_lines[a1_indx][1]
                    a_cops.append(cop)
                elif separation == 2: # two cop
                    cop = a_lines[a1_indx][1]
                    a_cops.append(cop)
                    cop = a_lines[a2_indx][0]
                    a_cops.append(cop)
                else:
                    if DEBUG:
                        raise ValueError(f"BUG INTERSECT 1. Index: {a_indx}")

        if len(b_indx) % 2 == 0: # ignore parallel and single line (no cop)

            # control for wrapping around
            if b_indx[-1] - b_indx[-2] > 2: # <--- this size is sketchy
                indx = b_indx.pop()
                indx -= len(b_lines)
                b_indx.insert(0, indx) 

            # fourth find cop that b cointains
            for b1_indx, b2_indx in zip(b_indx[0::2], b_indx[1::2]): # pairwise
                separation = b2_indx - b1_indx
                if separation == 1: # one cop
                    cop = b_lines[b1_indx][1]
                    b_cops.append(cop)
                elif separation == 2: # two cop
                    cop = b_lines[b1_indx][1]
                    b_cops.append(cop)
                    cop = b_lines[b2_indx][0]
                    b_cops.append(cop)
                else:
                    if DEBUG:
                        raise ValueError(f"BUG INTERSECT 1. Indeces: {b_indx}")
        
        return pois, a_cops, b_cops, a_crossed, b_crossed
        
    
    def project(self, axis): # for sweep and prune!
        """Project shape onto axis"""
        # https://www.youtube.com/watch?v=JZBQLXgSGfs
        dots = [corner.dot(axis) for corner in self.corners]
        return min(dots), max(dots)

    def contains(self, point):
        """Check if point is inside shape"""
        raise NotImplementedError("Contains not implemented - or needed. Use intersection instead")
        
    def compute_centroid(self):  # Used for fragmented shapes
        points = self.polygon
        C = V2(0, 0)
        A = 0
        for i in range(len(points)-1):
            a, b = points[i], points[i+1]
            x = V2(a.x, b.x)
            y = V2(a.y, b.y)
            
            cross = x.cross(y)
            C += (a + b) * cross

            A += (cross)

        self.area = 1/2 * A
        self.array[0] = C / (6 * A)
    
    # def compute_length(self):
    #     """Compute length of shape"""
    #     length = 0
    #     for a, b in zip(self.polygon, self.polygon[1:]):
    #         length += (b - a).length()
    #     self.length = length
 
    """Transformations"""
    def translate(self, vector):
        """Translate shape by vector"""  # odd behavior when translating by a V2
        # self.array += np.array(vector)
        self.array = np.add(self.array, vector, out=self.array, casting="unsafe")

    def translate_to(self, vector):
        """Translate shape to vector"""
        self.array = vector + self.array - self.centroid
    
    def rotate(self, degrees):
        """Rotate the shape by a given degrees around its center."""
        self.rot += degrees % 360
        center = self.array[0]  # remember center before rotation
        self.array = self.array - center  # no need to rotate centroid - but if not, polygone becomes black hole
        self.array = np.dot(self.array, np.array([[np.cos(np.radians(degrees)), -np.sin(np.radians(degrees))], [np.sin(np.radians(degrees)), np.cos(np.radians(degrees))]]))
        self.array = self.array + center
    
    def rotate_around(self, degrees, vector): # unchecked
        """Rotate the shape by a given degrees around a given point."""
        self.rot += degrees % 360
        self.array = self.array - vector  # no need to rotate centroid - but if not, polygone becomes black hole
        self.array = np.dot(self.array, np.array([[np.cos(np.radians(degrees)), -np.sin(np.radians(degrees))], [np.sin(np.radians(degrees)), np.cos(np.radians(degrees))]]))
        self.array = self.array + vector
    
    def rotate_to(self, degrees):
        """Rotate the shape to a given degrees around its center."""
        self.rotate(degrees - self.rot)
        self.rot = degrees

    def scale(self, factor):
        """Scale the shape by a given factor around its center."""
        center = self.array[0]  # remember center before scaling
        self.array = self.array - center
        self.array = self.array * factor
        self.array = self.array + center
        
    """Dunders"""
    def __iter__(self): # iterate over corners
        return iter(self.array[1:])  # Skip centroid
    
    def __str__(self):
        return f'{np.around(self.array[1:], 2)}'
        # return f'Shape: {NAMES[self.id]}, Centroid: {self.centroid}, Count: {len(self.array)}'
    
    def __repr__(self) -> str:
        return NAMES[self.id]
    
    

class Tetromino():
    """Mainly defined from shapely's Polygon
    This acts as a kinematic body when current, and otherwise is dynamic.
    Transitions from kinematic to dynamic is tentative, but is checked first thing in move().
    Transisitions if hits the floor or another shape or vel_y < 0.

    METHODS
    -------
    - move() - Moves the tetromino based on player input
    - physics_step() - Updates the tetromino's position and velocity + boundary collision
    - cut() - Cuts the tetromino where it intersects with a line being cleared

    TODO
    - limit calls to shapes.centroid - have another point in polygon for this.
    
    """

    def __init__(self, piece=0, pos=(W // 2, 0), rot=0, shape=None) -> None:
        if shape is None:
            self.shape = Shape(piece, pos, rot)
        else:
            self.shape = shape

        self.piece = piece
        self.type = NAMES[piece]
        self.color = COLORS[piece]

        # Physics
        self.pos = V2(pos)
        self.vel = V2(0, 50*MOVE_SPEED)
        self.omega = 0
        self.mass = SIZE ** 2 # Updates when cut
        self.moi = MOI#MOI # Updates when cut

        self.KEK = 0

    def kinematic(self): # Used to debug with precise movement
        keys = pg.key.get_pressed()
        
        rotate = (keys[pg.K_e] - keys[pg.K_q]) * ROT_SPEED
        if rotate:
            self.shape.rotate(rotate)

        dx = (keys[pg.K_d] - keys[pg.K_a]) * MOVE_SPEED
        dy = (keys[pg.K_s] - keys[pg.K_w]) * MOVE_SPEED
        if dx or dy:
            self.shape.translate((dx, dy))

        if keys[pg.K_f]:
            self.shape.rotate_to(0)
    
    def kinematic_other(self): # Used to debug with precise movement
        keys = pg.key.get_pressed()
        
        rotate = (keys[pg.K_RSHIFT] - keys[pg.K_END]) * ROT_SPEED
        if rotate:
            self.shape.rotate(rotate)

        dx = (keys[pg.K_RIGHT] - keys[pg.K_LEFT]) * MOVE_SPEED
        dy = (keys[pg.K_DOWN] - keys[pg.K_UP]) * MOVE_SPEED
        if dx or dy:
            self.shape.translate((dx, dy))

    def move(self):
        """Move the tetromino by x and y and wall check. Called before update."""
        if self.floor():
            return True # <------
        
        keys = pg.key.get_pressed()
        
        if keys[pg.K_e]:  # Rotation
            self.omega -= ROT_SPEED
        elif keys[pg.K_q]:
            self.omega += ROT_SPEED

        if keys[pg.K_w] or keys[pg.K_UP]:  # Vertical
            self.vel.y -= MOVE_SPEED
        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vel.y += MOVE_SPEED

        if keys[pg.K_a] or keys[pg.K_LEFT]: # Horizontal
            self.vel.x -= MOVE_SPEED
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vel.x += MOVE_SPEED
        
        if keys[pg.K_f]:
            self.vel = V2(0, 0)
            self.omega = 0
        
        self.physics_step()
        
    def slam(self):
        """Slam downwards"""
        self.vel *= FORCE

    
    """Dynamic methods"""
    def physics_step(self):
        """Intrinsic collisions of boundary. Updates shape"""
        self.boundary_collision()

        if not self.floor():
            self.vel.y += GRAV * dt
        # clamp rotation
        self.omega = min(max(self.omega, -MAX_OMEGA), MAX_OMEGA)

        self.shape.rotate(self.omega * dt)
        self.shape.translate(self.vel * dt)
    
    def floor(self):
        """Check if the tetromino is on the floor."""
        # get the bounds y maximum
        y_max = max(self.shape.array[:, 1])
        if y_max >= H:
            return True
    
    def boundary_collision(self):
        """Discrete boundary collision detection and response"""
        # Continuous with reflection vector calculated using pygame vector.reflect
        left, top, right, bot = self.shape.bounds()  # absolute positions

        if left < 0: # Wall
            dx = -left
            self.shape.translate((dx, 0))
            self.vel.x *= -WALL_FRIC
            self.omega *= -ROT_FRIC
        
        elif right > W: # Wall
            dx = W - right
            self.shape.translate((dx, 0))
            self.vel.x *= -WALL_FRIC
            dx = W - right
            self.omega *= -ROT_FRIC

        if bot > H: # Floor
            dy = H - bot
            self.shape.translate((0, dy))
            self.vel.y *= -FLOOR_FRIC    
            self.omega *= -ROT_FRIC

        elif top < - 2 * SIZE: # Ceiling
            dy = - (2 * SIZE + top)
            self.shape.translate((0, dy))
            self.vel.y *= -WALL_FRIC     
            self.omega *= -ROT_FRIC
    
    def draw(self, screen):
        """Draw the tetromino on the screen."""
        gfx.aapolygon(screen, self.shape.corners, self.color)
        gfx.filled_polygon(screen, self.shape.corners, self.color)
                    
    def draw_debug(self, screen):
        A = self.shape.bounds()
        gfx.aapolygon(screen, [(A[0], A[1]), (A[2], A[1]), (A[2], A[3]), (A[0], A[3])], RED)

        for p in self.shape.corners:
            pg.draw.circle(screen, RED, p, 2)   
    
    """Field relevant methods"""
    def within_field(self, field: Shape):
        """Check if the tetromino is within the field 
        and return an approximate area of intersect."""
        # First find any line ENTERING the field
        _, field_top, _, field_bot = field.bounds()
        top_line = Line((W, field_top), (0, field_top))
        left_vec = V2(-1, 0)
        bot_line = Line((W, field_bot), (0, field_bot))
        for line in self.shape.lines:
            top_intersect = seg_intersect(*line, *top_line)
            if top_intersect:
                break
            bot_intersect = seg_intersect(*line, *bot_line)
            if bot_intersect:
                break
            if not field.within(p):
                return False
        return True

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
    """Game class implementing Tetris with rigid tetrominoes
    
    METHODS
    -------
    - run() - The main game loop
    - update() - Update current tetromino with player input + gravity
    - physics() - Update the physics sizes of all tetrominoes + boundary checks
    - collision() - Check for collisions among tetrominoes by polygon intersection + collision response
    """

    def __init__(self):
        pg.init()
        self.font1 = pg.font.SysFont('NewTimesRoman', 100)
        self.font2 = pg.font.SysFont('NewTimesRoman', 40)
        self.screen = pg.display.set_mode((W, H))
        pg.display.set_caption("Rigid Tetris")
        self.clock = pg.time.Clock()

        self.fields = [Shape(-1, (0, h), 0, CLEAR_FIELD.copy()) for h in range(0, H, SIZE)]
        self.reset()

    def reset(self):
        self.bag = []
        self.score = 0
        self.tetrominos : List[Tetromino] = []  # Keeps track of dead tetrominos
        self.t = 10  # Frame counter
        self.current = Tetromino(piece=self.sample_bag(), pos=(W // 2, 0))

    def new_tetromino(self):
        if self.t < 2:  # Game over
            self.reset()
            return      
        
        # Add tetromino to list of dead tetrominos
        self.tetrominos.append(self.current)
        self.current = Tetromino(piece=self.sample_bag())
        self.t = 0

        # check if any lines are full
        # self.score += self.clear_lines
    
    def sample_bag(self):
        """Return a list of tetrominoes in the bag."""
        if self.bag == []:
            self.bag = [0, 1, 2, 3, 4, 5, 6]
            random.shuffle(self.bag)
        
        return self.bag.pop()
        
    def clear_line(self, field, intersecting: List[Tetromino]):
        """Clear a single line by clearing intersection with line. Returns True if any tetromino died of starvation."""
        for tetromino in intersecting:
            result = tetromino.cut(field)
            if isinstance(result, bool):  # if tetromino is too small
                self.tetrominos.remove(tetromino)
            elif isinstance(result, list): # if tetromino was split
                self.tetrominos.extend(result)
            
        print(f'{len(self.tetrominos)} tetrominos')

    def clear_lines(self):
        """Check if any lines are full and clear them. Returns the number of lines cleared."""
        cleared = 0
        for f in self.fields:
            area = 0.0 # area of tetrominos intersecting with line
            intersecting = []
            for tetromino in self.tetrominos:
                if a := tetromino.within_field(f):
                    area += a
                    intersecting.append(tetromino)
            
            # Clear line
            if area >= LINE_AREA:
                self.clear_line(f, intersecting)
                cleared += 1

        return cleared
    
    
    """Main game loop"""
    def run(self, debug=False):
        if not debug:
            while True:
                self.clock.tick(FPS)
                self.events()
                self.update()
                self.physics()
                self.collision()
                self.draw()
        else:
            while True:
                self.clock.tick(FPS)
                self.events()
                self.update()
                self.physics()
                self.collision()
                self.debug()

    def pause(self, key=None):
        """Wait for key to be pressed to return"""
        
        # overlay darkness to imply pause
        gfx.box(self.screen, (0, 0, W, H), BLACK + (150, ))
        txt = self.font1.render("PAUSED", True, WHITE)
        self.screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - txt.get_height() // 2))
        txt = self.font2.render("Press P to resume", True, WHITE)
        self.screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 + txt.get_height()))
        pg.display.update()

        while True:
            event = pg.event.wait()
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                elif key is None or event.key == key:
                    return

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
                    self.pause(pg.K_p)
                if event.key == pg.K_r:
                    self.reset()
                if event.key == pg.K_SPACE:
                    self.current.slam()
                    self.new_tetromino()
                if event.key == pg.K_t:
                    self.test_event()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print(event.pos)

    def update(self):
        # Update current kinematics
        if self.current.move(): # calls update too
        # if self.current.kinematic():
            self.new_tetromino()

    def physics(self):
        self.t += 1
        # Update the tetrominos dynamics + boundary check
        for tetromino in self.tetrominos:
            tetromino.physics_step()
        
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
    
    def draw_ui(self, text, pos):
        txt = self.font1.render(str(text), True, WHITE)
        self.screen.blit(txt, (pos[0] - txt.get_width() // 2, pos[1] - txt.get_height() // 2))
        pg.display.update()

    def debug(self, flip=True):
        self.screen.fill(BLACK)

        # draw SIZExSIZE grid
        for i in range(0, W, SIZE):
            for j in range(0, H, SIZE):
                pg.draw.rect(self.screen, GREY, (i, j, SIZE, SIZE), 1)

        # draw tetrominos
        self.current.draw(self.screen)
        self.current.draw_debug(self.screen)
        
        for t in self.tetrominos:
            t.draw(self.screen)
            t.draw_debug(self.screen)

        color = (255, 0, 0, 20)
        for f in self.fields:
            gfx.aapolygon(self.screen, f.corners, color)
            gfx.filled_polygon(self.screen, f.corners, color)

        if flip:
            pg.display.flip()

    """Collision methods"""


    def collision(self):  # Swep and prune
        """Collision detection bettween tetriminos and placement check."""
        for i, a in enumerate(self.tetrominos):
            for b in self.tetrominos[i+1:]:
                if not a.shape.bounds_intersect(b.shape):
                    continue
                if result := a.shape.intersect(b.shape):  # returns poi and normal
                    self.collision_response(a, b)

        # Current tetromino placement
        for other in self.tetrominos:
            if self.current.shape.intersect(other.shape):
                self.new_tetromino()
                break
    
    def collision_response(self, a: Tetromino, b: Tetromino):
        """Collision response between two tetrominos.
        
        Args:
            a (Tetromino): First tetromino
            b (Tetromino): Second tetromino
            poe (V2): Point of tetrimino a that intersects with b
            poi (V2): Point of intersection
            normal (V2): Normal of collision"""
        
        a.vel, b.vel = b.vel * WALL_FRIC, a.vel * WALL_FRIC  # No point of intersection, swap velocities (cop out)
        a.omega, b.omega = a.omega * WALL_FRIC, b.omega * WALL_FRIC



        """Test methods"""
    
    
    def test(self, test_num):
        print("Running test", test_num)
        getattr(self, f"test_{test_num}_init")()
        self.test_event = getattr(self, "test_" + str(test_num) + "_event")
        test_method = getattr(self, "test_" + str(test_num))
        
        while True:
            self.clock.tick(FPS)
            test_method()
            self.events()

    def test_1_init(self):  # cutting
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 5
        ROT_SPEED = 1
        self.current = Tetromino(L, pos=(W // 2, H // 2 - 50), rot = 3 * 90)
        self.f = self.fields[8]
        self.f.scale(2)
    
    def test_1_event(self):
        pass
    
    def test_1(self):
        self.current.kinematic()
        self.debug(False)
        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)
        pg.draw.line(self.screen, GREEN, *self.current.shape.lines[0], 2)

        _, field_top, _, field_bot = self.f.bounds()
        top_line = [V2(W, field_top), V2(0, field_top)]
        left_vec = V2(-1, 0)
        bot_line = [V2(W, field_bot), V2(0, field_bot)]
        top_intersect, bot_intersect = V2(0, 0), V2(0, 0)
        intersecting_lines = []
        pois = []
        lines = self.current.shape.lines
        for line in lines:
            top_intersect = seg_intersect(*line, *top_line)
            if top_intersect:
                pois.append(top_intersect)
                intersecting_lines.append(line)
                if (line[1] - line[0]).cross(left_vec) > 0:
                    break
            # bot_intersect = seg_intersect(*line, *bot_line)
            # if bot_intersect:
            #     break
        
        if intersecting_lines == []:
            pg.display.flip()
            return

        # Either first entree is ingoring, or we have two lines
        if len(intersecting_lines) == 1:
            # accumaluate length until we hit the top again
            # pg.draw.line(self.screen, WHITE, *line, 5)
            indx = lines.index(line)
            total_len = (line[1] - top_intersect).length()
            pg.draw.line(self.screen, WHITE, top_intersect, line[1], 5)
            
            while True:
                indx += 1
                line = lines[indx]
                poi = seg_intersect(*line, *top_line)
                if poi:
                    total_len += (line[0] - poi).length()
                    pg.draw.line(self.screen, WHITE, poi, line[0], 5)
                    pois.append(poi)
                    break
                else:
                    total_len += (line[1] - line[0]).length()
                    pg.draw.line(self.screen, WHITE, *line, 5)
            self.draw_ui(round(total_len / 10, 3), (300, 200))

        else:
            # pg.draw.line(self.screen, WHITE, *intersecting_lines[0], 5)
            line_indx = [lines.index(intersecting_lines[0]), lines.index(intersecting_lines[1])]
            # pg.draw.circle(self.screen, WHITE, top_intersect, 5)
            # pg.draw.circle(self.screen, WHITE, line[1], 5)

            total_len = (line[1] - top_intersect).length()
            pg.draw.line(self.screen, WHITE, line[1], top_intersect, 5)
            i = line_indx[1]
            while i != line_indx[0]:
                i = (i + 1) % len(lines)
                total_len += (lines[i][1] - lines[i][0]).length()
                # pg.draw.line(self.screen, WHITE, *lines[i], 5)
            
            
            total_len += (lines[i][0] - pois[0]).length()
            # pg.draw.line(self.screen, WHITE, lines[i][0], pois[0], 5)
            # pg.draw.circle(self.screen, BLACK, lines[i][0], 10)
            pg.draw.circle(self.screen, BLACK, pois[0], 10)

            self.draw_ui(round(total_len / 10, 3), (500, 200))
        
        LEN = 0
        for line in lines:
            LEN += (line[1] - line[0]).length()
        
        self.draw_ui(round(LEN / 10, 3), (500, H - 300))


            

            
        
        # if bot_intersect:
        #     pg.draw.circle(self.screen, RED, bot_intersect, 5)
        




        pg.display.flip()

        



DEBUG = False
if __name__ == "__main__":
    game = Game()
    game.test(1)
    game.run(debug=True)




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
CLEAR_FIELD = np.array([[W // 2, SIZE // 2], [0, 0], [W, 0], [W, SIZE], [0, SIZE]])  # + centroid

LINE_AREA = W * SIZE * 0.8  # Controls the ratio of area a line must be covered for it to clear
MIN_AREA = 0.5 * SIZE ** 2  # How small a piece can be before it is considered starved and removed from the game
MOVE_SPEED, ROT_SPEED = 10, 5
FLOOR_FRIC, WALL_FRIC, ROT_FRIC = 0.9, 1, 0.9
GRAV, MOI = 0, SIZE ** 4 # pi * D^4/64
FORCE = 1.4
K = 3
KEK = 0

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
        # for line in other.lines:
        #     for a, b in zip(self.polygon, self.polygon[1:]):
        #         if poi := seg_intersect(a, b, *line):
        #             normal = - perp(line[1] - line[0])
        #             return a, poi, normal # or b
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

        # self.inertia = 1
        # self.friction = 0.1
        # self.force = V2(0, 0)
        # self.torque = 0
    
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
        # if self.vel.y < 0:
        # if self.shape.bounds[3] > H:  # TRANSITION TO DYNAMIC
        #     return True # <------
        
        keys = pg.key.get_pressed()
        
        if keys[pg.K_e]:  # Rotation
            self.omega -= ROT_SPEED
        elif keys[pg.K_q]:
            self.omega += ROT_SPEED

        if keys[pg.K_w] or keys[pg.K_UP]:  # Vertical
            self.vel.y -= K * MOVE_SPEED
        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.vel.y += K * MOVE_SPEED

        if keys[pg.K_a] or keys[pg.K_LEFT]: # Horizontal
            self.vel.x -= K * MOVE_SPEED
        elif keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.vel.x += K * MOVE_SPEED
        
        if keys[pg.K_f]:
            self.vel = V2(0, 0)
            self.omega = 0
            GRAV = 0
        # event = pg.event.get()
        # if event and event[0].type == pg.KEYDOWN:
        #     if event[0].key == pg.K_g:
        #         if GRAV == 0:
        #             GRAV = 100
        #         else:
        #             GRAV = 0
        #             self.vel.y = 0
        #             self.vel.x = 0
        #             self.omega = 0
            
        
        self.physics_step()
        
    def slam(self):
        """Slam downwards"""
        self.vel *= FORCE

    
    """Dynamic methods"""
    def physics_step(self):
        """Intrinsic collisions of boundary. Updates shape"""
        # self.vel.y += GRAV * dt if not self.boundary_collision() else - self.vel.y
        self.boundary_collision()

        self.vel.y += GRAV * dt
        # self.omega *= ROT_FRIC
        self.shape.rotate(self.omega * dt)
        self.shape.translate(self.vel * dt)
        # self.shape = affinity.rotate(self.shape, self.omega * dt, origin=self.shape.centroid.coords[0])
        # self.shape = affinity.translate(self.shape, *(self.vel * dt))
    
    def boundary_collision(self):
        """Discrete boundary collision detection and response"""
        # Continuous with reflection vector calculated using pygame vector.reflect
        left, top, right, bot = self.shape.bounds()  # absolute positions

        if left < 0: # Wall
            dx = -left
            self.shape.translate((dx, 0))
            # self.shape = affinity.translate(self.shape, dx, 0)
            self.vel.x *= -WALL_FRIC
            self.omega *= -1
        
        elif right > W: # Wall
            dx = W - right
            self.shape.translate((dx, 0))
            # self.shape = affinity.translate(self.shape, dx, 0)
            self.vel.x *= -WALL_FRIC
            dx = W - right
            self.omega *= -1

        if bot > H: # Floor
            dy = H - bot
            self.shape.translate((0, dy))
            # self.shape = affinity.translate(self.shape, 0, dy)
            self.vel.y *= -FLOOR_FRIC    
            self.omega *= -1

        if top < - 2 * SIZE: # Ceiling
            dy = - (2 * SIZE + top)
            self.shape.translate((0, dy))
            # self.shape = affinity.translate(self.shape, 0, dy)
            self.vel.y *= -WALL_FRIC     
            self.omega *= -1
    
    def draw(self, screen):
        """Draw the tetromino on the screen."""
        gfx.aapolygon(screen, self.shape.corners, self.color)
        gfx.filled_polygon(screen, self.shape.corners, self.color)
                    
    def draw_debug(self, screen):
        A = self.shape.bounds()
        gfx.aapolygon(screen, [(A[0], A[1]), (A[2], A[1]), (A[2], A[3]), (A[0], A[3])], RED)

        for p in self.shape.corners:
            pg.draw.circle(screen, RED, p, 2)   

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

        self.field = [Shape(-1, (0, h), 0, CLEAR_FIELD.copy()) for h in range(0, H, SIZE)]
        self.points_of_intersection = []  # debugging
        self.reset()

    
    def reset(self):
        self.bag = []
        self.score = 0
        self.tetrominos : List[Tetromino] = []  # Keeps track of dead tetrominos
        self.t = 10  # Frame counter
        self.current = Tetromino(piece=self.sample_bag(), pos=(W // 2, H // 2))
        

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
        
    def clear_line(self, line, intersecting: List[Tetromino]):
        """Clear a single line by clearing intersection with line. Returns True if any tetromino died of starvation."""
        for tetromino in intersecting:
            result = tetromino.cut(line)
            if isinstance(result, bool):  # if tetromino is too small
                self.tetrominos.remove(tetromino)
            elif isinstance(result, list): # if tetromino was split
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

        # added debugger stuff
        for poi in self.points_of_intersection:
            pg.draw.circle(self.screen, RED, poi, 3)
        
        color = (255, 0, 0, 20)
        for f in self.field:
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
                    self.collision_response(a, b, *result)

        # Current tetromino placement - delete? why?
        # for tetro in self.tetrominos:
        #     if self.current.intersects(tetro.shape):
        #         self.new_tetromino()
        #         breaks
    
    def collision_response(self, a: Tetromino, b: Tetromino, pois: List[V2], 
            a_cops: List[V2], b_cops: List[V2], a_lines, b_lines):
        """Collision response between two tetrominos.
        
        Args:
            a (Tetromino): First tetromino
            b (Tetromino): Second tetromino
            poe (V2): Point of tetrimino a that intersects with b
            poi (V2): Point of intersection
            normal (V2): Normal of collision"""
        # ----- Collision resolutionn ------- 
        # move them opposite their velocity - how should it be distributed?

        # Determine the displacement with highest depth
        a_biggest_displacement = V2(0, 0)
        biggest_len = -1
        intersect_a = V2(0, 0)
        intersect_line_b = None
        # print(f'lines: {a_lines}, {b_lines}')

        for a_cop in a_cops:
            for line_b in b_lines:
                line = (a_cop, a_cop - a.vel)  # From a_cop to direction of prior position
                intersect = seg_intersect(*line, *line_b)
                if not intersect:
                    continue
                displacement = intersect - a_cop  # resolution displacement
                if (length := displacement.length_squared()) > biggest_len:
                    pg.draw.circle(self.screen, WHITE, intersect, 5)
                    pg.draw.line(self.screen, WHITE, *line, 5)
                    a_biggest_displacement = displacement
                    biggest_len = length
                    intersect_a = intersect
                    intersect_line_b = line_b

        # repeat for other tetromino
        b_biggest_displacement = V2(0, 0)
        biggest_len = -1
        intersect_b = V2(0, 0)
        intersect_line_a = None

        for b_cop in b_cops:
            for line_a in a_lines:
                line = (b_cop, b_cop - b.vel)  # From b_cop to direction of prior position
                intersect = seg_intersect(*line, *line_a)
                if not intersect:
                    continue
                displacement = intersect - b_cop  # resolution displacement
                if (length := displacement.length_squared()) > biggest_len:
                    pg.draw.circle(self.screen, WHITE, intersect, 5)
                    pg.draw.line(self.screen, WHITE, *line, 5)
                    b_biggest_displacement = displacement
                    biggest_len = length
                    intersect_b = intersect
                    intersect_line_a = line_a
        
        # self.points_of_intersection = []
        # self.lines_of_intersection = []
        if intersect_a:
            a.shape.translate(a_biggest_displacement)
            # self.points_of_intersection.append(intersect_a)
            # self.lines_of_intersection.append(intersect_line_b)
        if intersect_b:
            b.shape.translate(b_biggest_displacement)
            # self.points_of_intersection.append(intersect_b)
            # self.lines_of_intersection.append(intersect_line_a)
        # if self.points_of_intersection != []:
        #     collision_point = self.points_of_intersection[0]#(intersect_a + intersect_b) / 2 - average?
        #     intersection_line = self.lines_of_intersection[0]
        
        collision_point = intersect_a if intersect_a else intersect_b
        if collision_point:
            collision_line = intersect_line_a if intersect_line_a else intersect_line_b
        else:
            print("No collision point found")
            a.vel, b.vel = b.vel, a.vel  # No point of intersection, swap velocities (cop out)
            return
            # pg.display.flip()
            # self.pause()
            # print("No collision point")

        # ----- Collision response -------
        ra = collision_point - a.shape.centroid
        rb = collision_point - b.shape.centroid
        va = a.vel
        vb = b.vel
        wa = a.omega
        wb = b.omega
        nb = get_normal(*collision_line).normalize()
        Ia, Ib = a.moi, b.moi
        ma, mb = a.mass, b.mass

        numer = -2 * (va.dot(nb) - vb.dot(nb) + wa * (ra.cross(nb)) - wb * (ra.cross(nb)))
        denom = ma + mb + (Ia / ra.cross(nb) ** 2) + (Ib / rb.cross(nb) ** 2)

        J = numer / denom * nb
        va_ = va + J / ma
        vb_ = vb - J / mb
        wa_ = wa + ra.cross(J) / Ia # or wa + J.cross(ra) / Ia
        wb_ = wb - rb.cross(J) / Ib # or wb - J.cross(rb) / Ib - copilot

        a.vel, b.vel, a.omega, b.omega = va_, vb_, wa_, wb_
    

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
    
    def test_1_init(self):  
        # http://jeffreythompson.org/collision-detection/poly-poly.php
        global MOVE_SPEED
        MOVE_SPEED = 2
        self.current = Tetromino(T, pos=(180, 390))
        self.other = Tetromino(L, pos=(200, 300))

    def test_1_event(self): # test_event()
        # get mouse poisiton
        mouse_pos = pg.mouse.get_pos()	
        print(mouse_pos)

    def test_1(self): # Colission detection using lines 
        
        self.current.kinematic()
        self.debug(False)
        self.other.draw(self.screen)
        self.other.draw_debug(self.screen)

        a_lines = self.current.shape.lines
        b_lines = self.other.shape.lines
        
        # 2 lines
        # a_line = a_lines[0]
        # b_line = b_lines[0]
        # color = RED if seg_intersect(*a_line, *b_line) else WHITE
        # pg.draw.line(self.screen, color, *a_line, 5)

        # poly_line
        # a_line = a_lines[0]
        # pg.draw.line(self.screen, BLUE, *a_line, 5)
        # for line in b_lines:  # Check across all b_lines
        #     color = RED if seg_intersect(*a_line, *line) else WHITE
        #     pg.draw.line(self.screen, color, *line, 5)

        # poly_poly
        # for line_a in a_lines: # Check mutually across all lines and draw normal of collision
        #     for line_b in b_lines:
        #         if intersect := seg_intersect(*line_a, *line_b):
        #             # get normal of line_a
        #             normal = - perp(line_b[1] - line_b[0])
        #             break
        #     if intersect:
        #         break
        # self.other.color = RED if intersect else GREEN
        # if intersect:
        #     pg.draw.circle(self.screen, BLUE, intersect, 5)
        #     pg.draw.line(self.screen, WHITE, intersect, intersect + normal, 5)



      # # contains method - ignores parallel for now
        # first pass discover all intersecting lines and note the indices
        # also the point of intersections - specific order?
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
        
        a_indx.sort()                
        b_indx.sort() # May not appear in order due to funny looping
        # print(f'A was crossed {len(a_crossed)} times')
        # print(f'B was crossed {len(b_crossed)} times')
        # print()
        a_cops = []
        b_cops = []
        if pois:
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


            for line in a_crossed:
                pg.draw.line(self.screen, WHITE, *line, 5)
            for line in b_crossed:
                pg.draw.line(self.screen, WHITE, *line, 5)

            for poi in pois:
                pg.draw.circle(self.screen, BLUE, poi, 5)
            for cop in a_cops:
                pg.draw.circle(self.screen, RED, cop, 5)
            for cop in b_cops:
                pg.draw.circle(self.screen, GREEN, cop, 5)


                
        pg.display.flip()
        return
        
        pg.display.flip()

    def test_2_init(self):
        global MOVE_SPEED
        MOVE_SPEED = 5
        # self.current = Tetromino(T, pos=(300, 420), rot=45)
        # self.other = Tetromino(L, pos=(200, 300))
        self.current = Tetromino(Z, pos=(W // 2, H // 2))
        self.other = Tetromino(S, pos=(W // 2, H // 2))
        
        
    def test_2_event(self):
        if self.disp is not None:
            self.current.shape.translate(self.disp)

    def test_2(self): # sizes for collision reponse
        """
        How do I determine pop when colliding?
        Currently the first line that intersects breaks the loop, 
        so the pop is the ending point in that line. I.e. line[1]
        This works fine, except for the first line where the pop is line[0].
        This has been confirmed by reversing the order of the lines.
        
        """
        self.current.kinematic()
        self.other.kinematic_other()
        self.debug(False)
        self.other.draw(self.screen)
        self.other.draw_debug(self.screen)

        # assume current is moving and other is moving in the opposite direction
        self.current.vel = V2(-1, -1) * SIZE
        self.other.vel = - self.current.vel
        

        intersects = self.current.shape.bounds_intersect(self.other.shape)
        if intersects:
            result = self.current.shape.intersect(self.other.shape)
            if result:
                pois, a_cops, b_cops, a_lines, b_lines = result
                # print(len(a_cops), len(b_lines))

                # Determine the displacement with highest depth
                biggest_displacement = V2(0, 0)
                biggest_len = 0.0

                for a_cop in a_cops:
                    for line_b in b_lines:
                        line = (a_cop, a_cop - self.current.vel)  # From a_cop to direction of prior position
                        intersect = seg_intersect(*line, *line_b)
                        if not intersect:
                            continue
                        displacement = intersect - a_cop  # resolution displacement
                        if (len := displacement.length_squared()) > biggest_len:
                            # pg.draw.circle(self.screen, WHITE, intersect, 5)
                            # pg.draw.line(self.screen, WHITE, *line, 5)
                            biggest_displacement = displacement
                            biggest_len = len

                # self.current.shape.translate(biggest_displacement)
                # self.pause()
                
                biggest_displacement = V2(0, 0)
                biggest_len = 0.0

                for b_cop in b_cops:
                    for line_a in a_lines:
                        line = (b_cop, b_cop - self.current.vel)  # From b_cop to direction of prior position
                        intersect = seg_intersect(*line, *line_a)
                        if not intersect:
                            continue
                        displacement = intersect - b_cop  # resolution displacement
                        if (len := displacement.length_squared()) > biggest_len:
                            biggest_displacement = displacement
                            biggest_len = len
                
                self.other.shape.translate(biggest_displacement)
        
       
                    
                        

                
        pg.display.flip()
    
    
    def test_3_init(self):  # cutting
        global MOVE_SPEED
        MOVE_SPEED = 5
        self.current = Tetromino(T, pos=(W // 2, H // 2 - 50), rot = 3 * 90)
        self.f = self.field[8]
        self.f.scale(2)
        

    def test_3_event(self):
        # cut the piece
        print("cutting")
        shape = self.current.shape
        self.last_array = deepcopy(shape.array)
        # self.curts is a list of pairs of pois and corresponding lines on tetris piece
        # It will always have length 2 or 4

        
        
        # first check if first is leaving or entering field - assuming top for now so V2(-10, 0)
        try:
            first = self.line_top_cuts[0]
        except:
            
            return
        if V2(-10, 0).cross(first[1] - first[0]) > 0:
            self.line_top_cuts.insert(0, self.line_top_cuts.pop(-1))
            self.point_top_cuts.insert(0, self.point_top_cuts.pop(-1))
        # iterate pairwise over lines such that 'a' leads in and 'b' leads out
        # first find indices of lines w.r.t. shape.lines
        # then replace the points in shape.array

        # max diff is len(lines) - 1
        before = len(shape.array)
        k = before- 1
        for i, (line_a, line_b) in enumerate(zip(self.line_top_cuts[0::2], self.line_top_cuts[1::2])):
            # indices of lines in shape.lines + offset
            print(shape.lines.index(line_a), shape.lines.index(line_b))
            a = (shape.lines.index(line_a) + 2) % k   # centroid + end of line
            b = (shape.lines.index(line_b) + 1) % k # centroid
            diff = abs(b  - a)
            print(f'b:{b} - a:{a} = {diff}')
            
            if a == b: # special case must add
                shape.array = np.insert(shape.array, a, self.point_top_cuts[i], axis=0)
                shape.array[b+1] = self.point_top_cuts[i+1] # shift by 1 because of insert

            else:
                shape.array = np.delete(shape.array, slice(a+1, b), axis=0)
                shape.array[a] = self.point_top_cuts[i]
                shape.array[b-diff+1] = self.point_top_cuts[i+1]

        print(f'{before-1} -> {len(shape.array)-1}')
        print()

        # self.pause()

    def test_3(self):   # Calculate the area of the encompassed tetromino
        self.current.kinematic()
        self.debug(False)
        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)
        pg.draw.line(self.screen, GREEN, *self.current.shape.lines[0], 5)
        for corner in self.current.shape.corners:
            pg.draw.circle(self.screen, GREEN, corner, 5)
        

        f_corners = self.f.corners
        top_line = [f_corners[0], f_corners[1]]
        bot_line = [f_corners[2], f_corners[3]]

        # pg.draw.line(self.screen, WHITE, *top_line, 5)
        # pg.draw.line(self.screen, WHITE, *bot_line, 5)
        self.cuts : List[List[V2], Line] = []  # points and lines intersected
        self.line_top_cuts = []
        # self.line_bot_cuts = []
        self.point_top_cuts = []
        # self.point_bot_cuts = []

        total_area = 0
        u, v = None, None
        i = 0 
        lines = self.current.shape.lines
        while i < len(lines):
            line = lines[i]
            i += 1
            # draw line
            # find intersection with top and bot
            # skip if lines start and end is outside the field
            if line[0][1] < f_corners[0][1] and line[1][1] < f_corners[0][1]:
                pg.draw.line(self.screen, WHITE, *line, 5)
                continue
            if line[0][1] > f_corners[2][1] and line[1][1] > f_corners[2][1]:
                pg.draw.line(self.screen, WHITE, *line, 5)
                continue
            # if they are within both, delete completely!
            top_intersect = seg_intersect(*line, *top_line)
            # bot_intersect = seg_intersect(*line, *bot_line)
            if top_intersect: # Found first entree!
                print(i)
                break
        
        anchor = top_intersect # first point a, i.e. anchor
        # pg.draw.circle(self.screen, BLACK, top_intersect, 5)
        pg.draw.line(self.screen, YELLOW, top_intersect, line[1], 5)
        # iterate over rest of lines until breaking out again
        while i < len(lines): # go through all points that are within the field
            line = lines[i]
            i += 1

            top_intersect = seg_intersect(*line, *top_line)
            if top_intersect: # last point c
                b, c = line[0], top_intersect
                pg.draw.line(self.screen, YELLOW, b, c, 5)
                u = anchor - b
                v = c - b
                area = v.cross(u)
                if area > 0:
                    # pg.draw.polygon(self.screen, WHITE, [a, b, c])
                    total_area += area
                break
        
            b, c = line
            pg.draw.line(self.screen, YELLOW, b, c, 5)
            u = anchor - b
            v = c - b
            area = v.cross(u)
            if i == 6:
                pg.draw.polygon(self.screen, WHITE, [anchor, b, c])
            kek = 0
            if area > 0 and i == 6:  # positive contribution (with some negative maybe)
                # pg.draw.polygon(self.screen, WHITE, [a, b, c])
                total_area += area
                # pg.draw.polygon(self.screen, WHITE, [a, b, c])
            
                # check for negative area by intersecting prior lines
                # check the two vetors u and v which will cross exactly twice each
                line_u = [anchor, b]
                line_v = [anchor, c]
                # pg.draw.line(self.screen, GREEN, *line_v, 5)
                # for j in range(3, i-1):#(i-1):
                j = 3
                pre_line = lines[j]
                pg.draw.line(self.screen, TURQUOISE, *pre_line, 5)
                pg.draw.line(self.screen, TURQUOISE, *lines[4], 5)
                intersect_u = _seg_intersect(*pre_line, *line_u)
                intersect_v = seg_intersect(*pre_line, *line_v)
                if intersect_u:
                    u = intersect_u - b
                    # pg.draw.line(self.screen, PURPLE, intersect_u, b, 5)
                    pg.draw.circle(self.screen, BLACK, intersect_u, 5)
                if intersect_v:
                    v = intersect_v - b
                    # pg.draw.line(self.screen, GREEN, *line_v, 5)
                    # pg.draw.line(self.screen, PURPLE, intersect_v, b, 5)
                    pg.draw.circle(self.screen, WHITE, intersect_v, 5)
                
                j = 4
                intersect_u = _seg_intersect(*pre_line, *lines[j])
                intersect_v = seg_intersect(*pre_line, *lines[j])
                if intersect_u:
                    u = intersect_u - b
                    # pg.draw.line(self.screen, PURPLE, intersect_u, b, 5)
                    pg.draw.circle(self.screen, BLACK, intersect_u, 5)
                if intersect_v:
                    v = intersect_v - b
                    # pg.draw.line(self.screen, GREEN, *line_v, 5)
                    # pg.draw.line(self.screen, PURPLE, intersect_v, b, 5)
                    pg.draw.circle(self.screen, WHITE, intersect_v, 5)

                    
                
                # if intersect_u and intersect_v:

                #     break # one must be parallel (u)
                # pg.draw.polygon(self.screen, WHITE, [b, intersect_u, intersect_v])
                
                area = -2#v.cross(u)
                if area < 0:  # subtract negative area
                    # pg.draw.polygon(self.screen, WHITE, [a, b, c])
                    total_area += area
                    


        total_area /= 2
        self.draw_ui(round(total_area, 2), (W // 2, 100))
                
        pg.display.flip()
        
        
from copy import deepcopy



DEBUG = False
if __name__ == "__main__":
    game = Game()
    game.test(3)
    game.run(debug=True)



"""Junkyard"""

"""SAT"""
def test_1_init(self):  # Seperating axis theorem 
        global MOVE_SPEED
        MOVE_SPEED = 2
        self.axis = V2(1, -1).normalize()  # Normalize for quantitive size of overlap, otherwise just return bool
        self.axis_ = V2(1, 1).normalize()
        degres = self.axis.angle_to((1, 0))
        self.current = Tetromino(L, pos=(380, 200), rot=degres)
        self.other = Tetromino(L, pos=(200, 300), rot=degres)

        A = self.current.shape.bounds
        B = self.other.shape.bounds

def test_1_event(self): # test_event()
    pass

def test_1(self): # test_method 
    # https://gamedevelopment.tutsplus.com/tutorials/collision-detection-using-the-separating-axis-theorem--gamedev-169
    self.current.kinematic()
    self.debug(False)
    self.other.draw(self.screen)
    self.other.draw_debug(self.screen)

    pg.draw.line(self.screen, WHITE, V2(250, 500), V2(250, 500) + self.axis * 100, 5)

    part = 1
    # A is other and current B

    if part == 0:
        # Aligned to axis of 45 degrees and V2(1, -1) in one direction only
        A_ce = self.other.shape.centroid
        B_ce = self.current.shape.centroid
        A_co = self.other.shape.corners[1]
        B_co = self.current.shape.corners[0]

        pg.draw.line(self.screen, BLUE, A_ce, B_ce, 5)
        pg.draw.line(self.screen, BLUE, A_ce, A_co, 5)
        pg.draw.line(self.screen, BLUE, B_ce, B_co, 5)

        C = B_ce - A_ce
        A = A_co - A_ce
        B = B_co - B_ce

        projC = C.dot(self.axis)
        projA = A.dot(self.axis)
        projB = B.dot(self.axis)
        pg.draw.line(self.screen, RED, V2(240, 480), V2(240, 480) + self.axis * projC, 5)
        pg.draw.line(self.screen, RED, V2(220, 450), V2(220, 450) + self.axis * projA, 5)
        pg.draw.line(self.screen, RED, V2(300, 410), V2(300, 410) + self.axis * projB, 5)

        gap = projC - projA + projB
        if gap > 0: print("gap")
        elif gap == 0: print("touching") # happens at least when parallel
        else: print("overlap")
        
    if part == 1:
        # prepare vector from origin to corner that will be projected (from origin, so no need to subtract)
        A_corners = self.other.shape.corners
        B_corners = self.current.shape.corners

        # finding min and max projections
        minA = min([corner.dot(self.axis) for corner in A_corners])
        maxA = max([corner.dot(self.axis) for corner in A_corners])
        minB = min([corner.dot(self.axis) for corner in B_corners])
        maxB = max([corner.dot(self.axis) for corner in B_corners])

        pg.draw.circle(self.screen, RED, V2(250, 500) + self.axis * minA, 5)
        pg.draw.circle(self.screen, RED, V2(250, 500) + self.axis * maxA, 5)
        pg.draw.circle(self.screen, RED, V2(250, 500) + self.axis * minB, 5)
        pg.draw.circle(self.screen, RED, V2(250, 500) + self.axis * maxB, 5)

        # check if overlap
        if maxA < minB or maxB < minA:
            print("no overlap")
        else:
            print("overlap") # return half overlap

    if part == 2:
        # get normals
        A_normals = self.other.shape.normals()
        B_normals = self.current.shape.normals()

        # draw normals
        for normal in A_normals:
            pg.draw.line(self.screen, RED, self.other.shape.centroid + normal * SIZE, self.other.shape.centroid + normal * (SIZE + 15), 5)
        for normal in B_normals:
            pg.draw.line(self.screen, RED, self.current.shape.centroid + normal * SIZE, self.current.shape.centroid + normal * (SIZE + 15), 5)

    if part == 3:
        # generalize to all axes (skip those that are parallel to any prior axis)
        A_normals = self.other.shape.normals()
        axis = A_normals[2]

        A_corners = self.other.shape.corners
        B_corners = self.current.shape.corners

        minA = min([corner.dot(axis) for corner in A_corners])
        maxA = max([corner.dot(axis) for corner in A_corners])
        minB = min([corner.dot(axis) for corner in B_corners])
        maxB = max([corner.dot(axis) for corner in B_corners])

        pg.draw.circle(self.screen, RED, V2(250, 500) + axis * minA, 5)
        pg.draw.circle(self.screen, RED, V2(250, 500) + axis * maxA, 5)
        pg.draw.circle(self.screen, RED, V2(250, 500) + axis * minB, 5)
        pg.draw.circle(self.screen, RED, V2(250, 500) + axis * maxB, 5)

        
    pg.display.flip()
    return
    

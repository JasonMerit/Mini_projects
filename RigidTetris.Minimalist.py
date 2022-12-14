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
SIZE = 40#120
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
PERIMETERS = np.power(np.array([10, 10, 10, 8, 10, 10, 10]) * SIZE, 2)                      
CLEAR_FIELD = np.array([[W // 2, SIZE // 2], [0, 0], [W, 0], [W, SIZE], [0, SIZE]])  # + centroid
CLEAR_TRESH = 5 * W // 4#8

LINE_AREA = W * SIZE * 0.8  # Controls the ratio of area a line must be covered for it to clear
MIN_AREA = 0.5 * SIZE ** 2  # How small a piece can be before it is considered starved and removed from the game
MOVE_SPEED, ROT_SPEED = 2, 5
FLOOR_FRIC, WALL_FRIC, ROT_FRIC = 0.2, 0.4, 0.3
GRAV, MOI = 30, SIZE ** 4 # pi * D^4/64
FORCE = 1.4

# Minimizing
MAX_SPEED, MAX_OMEGA = 100, 100

# helper functions
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (800,45)

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

    def __init__(self, id, pos=(0, 0), rot=0, array=None):
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
        
        if pos:
            self.translate(pos)
        if rot:
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

    def contains_point(self, point):
        """Check if point is inside shape with ray casting pointing up"""
        # If odd number of intersections, point is inside
        UP = V2(0, - 4 * SIZE)
        intersections = 0
        for line in self.lines:
            if seg_intersect(point, point + UP, *line):
                intersections += 1
        return intersections % 2 == 1
    
    @staticmethod # https://stackoverflow.com/questions/9692448/how-can-you-find-the-centroid-of-a-concave-irregular-polygon-in-javascript
    def compute_centroid(pts: List[V2]):
        """Return the centroid of a polygon (loops around)."""
        area = 0
        x, y = 0, 0,
        i, j = 0, len(pts) - 1
        while i < len(pts):
            p1, p2 = pts[i], pts[j]
            f = p1.cross(p2)
            area += f
            x += (p1.x + p2.x) * f
            y += (p1.y + p2.y) * f
            j = i; i += 1
        area *= 3
        return V2(x, y) / area, area
    
    def morp_into(self, corners: List[V2]):
        """Morph shape into new corners"""
        corners.append(corners[0])  # close the loop
        centroid, area = Shape.compute_centroid(corners)
        array = [centroid] + corners
        self.area = area
        self.array = np.array([[p.x, p.y] for p in array])
    
    @staticmethod
    def morph(corners: List[V2]):
        """Morph shape into new corners"""
        corners.append(corners[0])  # close the loop
        centroid, area = Shape.compute_centroid(corners)
        array = [centroid] + corners
        return np.array([[p.x, p.y] for p in array]), area
 
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
        self.rot += degrees
        self.rot = self.rot % 360
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
    """Tetromino class
    This acts as a kinematic body when current, and otherwise is dynamic.
    Transitions from kinematic to dynamic is tentative, but is checked first thing in move().
    Transisitions if hits the floor or another shape or vel_y < 0.

    METHODS
    -------
    - move() - Moves the tetromino based on player input
    - physics_step() - Updates the tetromino's position and velocity + boundary collision
    - cut() - Cuts the tetromino where it intersects with a line being cleared
    
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

    def fragment_into(self, corners: list, second_corners: list = []):
        """Assumes corners is non-empty"""
        if second_corners == []:
            return
        self.shape.morp_into(corners)
        if second_corners != []:
            # Create a new tetromino and return it
            array, area = Shape.morph(second_corners)
            if area < SIZE:
                shape = Shape(self.piece, pos=(0, 0), array=array)
                second = Tetromino(piece=self.piece, shape=shape)
                second.vel.x, second.vel.y = self.vel.x, self.vel.y  #V2 has no copy method
                second.omega = self.omega
                return second

    """ THE FUCKING SHIT ALGORITHM"""
    def cut(self, field: Shape):
        """Cut off part of tetromino intersecting line. Assumes at least one intersection exists. 
        Returns the two collection of corners as a list."""
        # 1) First find the first point of intersection
        # 2) Then distribute all passed points into approbriate lists
        # 3) Now iterate through rest of polygon, knowing which to append to
        # Only return cut if more than 3 points, and if only one survices,
        # ensure it is the first entree in the return statement. 
        _, field_top, _, field_bot = field.bounds()
        top_line = [V2(W, field_top), V2(0, field_top)]
        bot_line = [V2(W, field_bot), V2(0, field_bot)]
        top_intersect, bot_intersect = V2(0, 0), V2(0, 0)
        lines = self.shape.lines
        A, B = [], []  # Always appending either pois or starts of lines
        top_n, bot_n = 0, 0 # Only return if they intersect field exactly twice


        # -------------------- 1) -------------------
        i = 0
        while i < len(lines):
            line = lines[i]
            if line[0].y < field_top and line[1].y < field_top or line[0].y > field_bot and line[1].y > field_bot: # Above or below field
                i += 1
                continue
            else:
                top_intersect = seg_intersect(*line, *top_line)
                bot_intersect = seg_intersect(*line, *bot_line)
                if top_intersect or bot_intersect:
                    break
                else:  # Contained within field
                    i += 1
        else: # i = len(lines) -> no intersection -> all outside or all inside. Raycast to find out
            if field.contains_point(self.shape.centroid):
                return [], []
            else:
                raise ValueError("Poor arguments: No intersection found.")
        
        
        # -------------------- 2) -------------------
        if top_intersect and bot_intersect: # both, so outside and two new polygons
            top_n, bot_n = 1, 1
            inside = False
            if (line[1] - line[0]).cross(V2(-1, 0)) < 0:
                B.append(line[0])
            else:
                A.append(line[0])  
            A.append(top_intersect)
            B.append(bot_intersect)

        elif top_intersect:
            top_n = 1
            if inside := (line[1] - line[0]).cross(V2(-1, 0)) > 0:
                A.append(lines[0][0])
                for j in range(i):                    
                    A.append(lines[j][1])
            A.append(top_intersect)

        elif bot_intersect:
            bot_n = 1
            if inside := (line[1] - line[0]).cross(V2(-1, 0)) < 0:
                for j in range(i+1):                    
                    B.append(lines[j][0])
            B.append(bot_intersect)
        
        # -------------------- 3) -------------------
        for j in range(i+1, len(lines)):
            line = lines[j]
            top_intersect = seg_intersect(*line, *top_line)
            bot_intersect = seg_intersect(*line, *bot_line)

            if top_intersect and bot_intersect: # both, so inside
                top_n += 1; bot_n += 1
                if (line[1] - line[0]).cross(V2(-1, 0)) < 0:
                    B.append(line[0])
                else:
                    A.append(line[0])
                A.append(top_intersect)
                B.append(bot_intersect)

            elif top_intersect:
                top_n += 1
                if not inside:
                    A.append(line[0])
                A.append(top_intersect)
                inside = not inside

            elif bot_intersect:
                bot_n += 1
                if not inside:
                    B.append(line[0])
                B.append(bot_intersect)
                inside = not inside
            elif not inside:
                # outside, so append depending on which side of field
                if line[0].y < field_top:
                    A.append(line[0])
                else:
                    B.append(line[0])              
        
        # don't return if less than three points or intersected more than twice
        if top_n != 2 or len(A) < 3:
            A = []
        if bot_n != 2 or len(B) < 3:
            B = []
        elif A == []:
            return B, A # flip em
        return A, B 
    
    def __repr__(self):
        return f"{NAMES[self.piece]} at {self.shape.centroid}"

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
        print(self.current)

    def new_tetromino(self):
        self.tetrominos.append(self.current)
        self.clear_lines()
        if self.t < 2:  # Game over
            self.reset()
            return      
        
        # Add tetromino to list of dead tetrominos
        self.current = Tetromino(piece=self.sample_bag(), pos=(W // 2, 0))
        self.t = 0
        print(self.current)

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
            A, B = tetromino.cut(field)
            fragment = self.current.fragment_into(A, B)
            if fragment:
                self.tetrominos.append(fragment)
            

    def clear_lines(self):
        """Check if any lines are full and clear them. Returns the number of lines cleared."""
        # TODO: Preparea a query for each field
        # Ray cast from right to left to find intersections with lines
        # and if the length of intersection is equal to the length of the line, clear it

        for field in self.fields:
            ray = [V2(*field.corners[1]), V2(*field.corners[0])]
            total_length = 0.0
            intersecting = []
            for t in self.tetrominos:
                poi = None
                for line in t.shape.lines:
                    # compute intersection with ray
                    intersection = seg_intersect(*ray, *line)
                    if intersection:
                        intersecting.append(t)
                        if poi:
                            total_length += abs(poi.x - intersection.x)
                            break
                        else:
                            poi = intersection
            if total_length > 69: # here
                self.clear_line(field, intersecting)
                self.score += 1
    
    
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
        if key:
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
        txt = self.font2.render(str(text), True, WHITE)
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
        MOVE_SPEED = 4
        ROT_SPEED = 1
        self.current = Tetromino(T, pos=(W // 2, H // 2), rot = 80)
        self.f = self.fields[8]
    
    def test_1_event(self):
        pass
    
    def test_1(self): # Compute length of cut
        self.current.kinematic()
        self.debug(False)
        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)
        # pg.draw.line(self.screen, BLACK, *self.current.shape.lines[0], 2)

        _, field_top, _, field_bot = self.f.bounds()
        top_line = [V2(W, field_top), V2(0, field_top)]
        bot_line = [V2(W, field_bot), V2(0, field_bot)]
        top_intersect, bot_intersect = V2(0, 0), V2(0, 0)
        lines = self.current.shape.lines

        total_len = 0.0
        def get_len(p1, p2): return (p1 - p2).length()
        # Don't know whether starting outside or inside until first intersection, keep track of length though
        i = 0
        while i < len(lines):
            line = lines[i]
            if line[0].y < field_top and line[1].y < field_top: # Above field
                i += 1
                continue
            elif line[0].y > field_bot and line[1].y > field_bot: # Below field
                i += 1
                continue
            else:
                top_intersect = seg_intersect(*line, *top_line)
                bot_intersect = seg_intersect(*line, *bot_line)
                if top_intersect or bot_intersect:
                    break
                else:  # Contained within field
                    total_len += get_len(*line)
                    i += 1
        else: # i = len(lines) -> no intersection -> all outside or all inside. Raycast to find out
            if self.f.contains_point(self.current.shape.centroid):
                self.draw_ui("Fully contained", (100, 100))
            else:
                self.draw_ui("No intersection", (100, 100))
                return
        
        # Find where initial line ends (insde or outside)
        if top_intersect and bot_intersect: # both, so outside
            pg.draw.line(self.screen, TURQUOISE, bot_intersect, top_intersect, 2)
            total_len += get_len(bot_intersect, top_intersect)
            inside = False

        elif top_intersect:
            inside = (line[1] - line[0]).cross(V2(-1, 0)) > 0
            if inside:
                pg.draw.line(self.screen, BLUE, line[1], top_intersect, 2)
                total_len += get_len(line[1], top_intersect)
            else:
                pg.draw.line(self.screen, PURPLE, line[0], top_intersect, 2)
                total_len += get_len(line[0], top_intersect)
                for j in range(i):
                    pg.draw.line(self.screen, RED, *lines[j], 2)
                    total_len += get_len(*lines[j])

        elif bot_intersect:
            inside = (line[1] - line[0]).cross(V2(-1, 0)) < 0
            if inside:
                pg.draw.line(self.screen, ORANGE, line[1], bot_intersect, 2)
                total_len += get_len(line[1], bot_intersect)
            else:
                pg.draw.line(self.screen, GREEN, line[0], bot_intersect, 2)
                total_len += get_len(line[0], bot_intersect)
                for j in range(i):
                    pg.draw.line(self.screen, YELLOW, *lines[j], 2)
                    total_len += get_len(*lines[j])
            
        # if inside:
        #     self.draw_ui("Inside", (100, 100))
        # else:
            # self.draw_ui("Outside", (100, 100))
        # Continue to rest of lines taking off from i+1
        # for line in lines[i+1:]:

        # pg.display.flip()
        # return
        for j in range(i+1, len(lines)):
            line = lines[j]
            top_intersect = seg_intersect(*line, *top_line)
            bot_intersect = seg_intersect(*line, *bot_line)

            if top_intersect and bot_intersect: # both, so inside
                pg.draw.line(self.screen, WHITE, bot_intersect, top_intersect, 2)
                total_len += get_len(bot_intersect, top_intersect)

            elif top_intersect:
                if inside:
                    pg.draw.line(self.screen, WHITE, line[0], top_intersect, 2)
                    total_len += get_len(line[0], top_intersect)
                else:
                    pg.draw.line(self.screen, WHITE, line[1], top_intersect, 2)
                    total_len += get_len(line[1], top_intersect)
                inside = not inside

            elif bot_intersect:
                if inside:
                    pg.draw.line(self.screen, WHITE, line[0], bot_intersect, 2)
                    total_len += get_len(line[0], bot_intersect)
                else:
                    pg.draw.line(self.screen, WHITE, line[1], bot_intersect, 2)
                    total_len += get_len(line[1], bot_intersect)
                inside = not inside
            else:
                if inside:
                    pg.draw.line(self.screen, WHITE, *line, 2)
                    total_len += get_len(*line)
            
        self.draw_ui(f"Total length: {round(total_len, 1)}", (100, 150))


        # draw indices on each line
        # for i, line in enumerate(lines):
        #     self.draw_ui(i, (line[1] + line[0]) / 2)
            # self.draw_ui(i, line[1])



        pg.display.flip()
        return

        
    def test_2_init(self):  # cutting
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 1
        ROT_SPEED = 3
        self.current = Tetromino(T, pos=(W // 2, H // 2), rot = 270)
        self.other = None
        self.f = self.fields[8]

        # self.test_2()
        # self.test_2_event()
    
    def test_2_event(self):
        print(f'A: {len(self.A)}, B: {len(self.B)}')
        for i, a in enumerate(self.A):
            pg.draw.circle(self.screen, RED, a, 10)
            self.draw_ui(i+1, a)
        for i, b in enumerate(self.B):
            pg.draw.circle(self.screen, GREEN, b, 10)
            self.draw_ui(i+1, b)
        self.draw_ui(f"Rot: {self.current.shape.rot}", (100, 100))
        self.pause()

        # if self.A:
        #     self.current.fragment_into(self.A)

    
    def test_2(self): # Compute length of cut
        self.current.kinematic()
        self.debug(False)
        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)
        pg.draw.line(self.screen, BLACK, *self.current.shape.lines[0], 3)

        _, field_top, _, field_bot = self.f.bounds()
        top_line = [V2(W, field_top), V2(0, field_top)]
        bot_line = [V2(W, field_bot), V2(0, field_bot)]
        top_intersect, bot_intersect = V2(0, 0), V2(0, 0)
        lines = self.current.shape.lines

        # cutting info - make new shape entirely        
        self.A = []
        self.B = []

        top_n, bot_n = 0, 0  # Only return if they intersect field exactly twice


        total_len = 0.0
        def get_len(p1, p2): return (p1 - p2).length()
        # Don't know whether starting outside or inside until first intersection, keep track of length though
        i = 0
        while i < len(lines):
            line = lines[i]
            if line[0].y < field_top and line[1].y < field_top: # Above field
                i += 1
                continue
            elif line[0].y > field_bot and line[1].y > field_bot: # Below field
                i += 1
                continue
            else:
                top_intersect = seg_intersect(*line, *top_line)
                bot_intersect = seg_intersect(*line, *bot_line)
                if top_intersect or bot_intersect:
                    break
                else:  # Contained within field
                    total_len += get_len(*line)
                    i += 1
        else: # i = len(lines) -> no intersection -> all outside or all inside. Raycast to find out
            if self.f.contains_point(self.current.shape.centroid):
                self.draw_ui("Fully contained", (100, 100))
            else:
                self.draw_ui("No intersection", (100, 100))
                return
        
        # ALWAYS APPENDING START OF LINE
        # Find where initial line ends (insde or outside)
        if top_intersect and bot_intersect: # both, so outside and two new polygons
            top_n += 1; bot_n += 1
            pg.draw.line(self.screen, TURQUOISE, bot_intersect, top_intersect, 2)
            total_len += get_len(bot_intersect, top_intersect)
            inside = False
            

            if (line[1] - line[0]).cross(V2(-1, 0)) < 0:
                self.B.append(line[0])
            else:
                self.A.append(line[0])    
            self.A.append(top_intersect)
            self.B.append(bot_intersect)


        elif top_intersect:
            top_n += 1
            inside = (line[1] - line[0]).cross(V2(-1, 0)) > 0
            if inside:
                
                pg.draw.line(self.screen, BLUE, line[1], top_intersect, 2)
                total_len += get_len(line[1], top_intersect)
                self.A.append(lines[0][0])           # start
                for j in range(i):                    
                    self.A.append(lines[j][1])
            else:
                pg.draw.line(self.screen, PURPLE, line[0], top_intersect, 2)
                total_len += get_len(line[0], top_intersect)
                for j in range(i):                    
                    pg.draw.line(self.screen, RED, *lines[j], 2)
                    total_len += get_len(*lines[j])
            self.A.append(top_intersect)  # ORDERING IMPORTANT

        elif bot_intersect:
            bot_n += 1
            inside = (line[1] - line[0]).cross(V2(-1, 0)) < 0
            if inside:
                pg.draw.line(self.screen, ORANGE, line[1], bot_intersect, 2)
                total_len += get_len(line[1], bot_intersect)
                for j in range(i+1):                    
                    self.B.append(lines[j][0])
                
            else:
                pg.draw.line(self.screen, GREEN, line[0], bot_intersect, 2)
                total_len += get_len(line[0], bot_intersect)
                for j in range(i):
                    # self.A.append(lines[j][0])
                    pg.draw.line(self.screen, YELLOW, *lines[j], 2)
                    total_len += get_len(*lines[j])
            self.B.append(bot_intersect)
        
        
        # self.draw_ui(f'inside: {inside}', (100, 200))
        # pg.display.flip()
        # return
        # return -------------------------------------------------
        for j in range(i+1, len(lines)):
            line = lines[j]
            top_intersect = seg_intersect(*line, *top_line)
            bot_intersect = seg_intersect(*line, *bot_line)

            if top_intersect and bot_intersect: # both, so inside
                top_n += 1; bot_n += 1
                # self.A.append(line[1])
                pg.draw.line(self.screen, WHITE, bot_intersect, top_intersect, 2)
                total_len += get_len(bot_intersect, top_intersect)
                if (line[1] - line[0]).cross(V2(-1, 0)) < 0:
                    self.B.append(line[0])
                else:
                    self.A.append(line[0])
                self.B.append(bot_intersect)
                self.A.append(top_intersect)

            elif top_intersect:# and top_n != 2:
                top_n += 1
                if inside:
                    pg.draw.line(self.screen, WHITE, line[0], top_intersect, 2)
                    total_len += get_len(line[0], top_intersect)
                else:
                    self.A.append(line[0])
                    pg.draw.line(self.screen, WHITE, line[1], top_intersect, 2)
                    total_len += get_len(line[1], top_intersect)
                self.A.append(top_intersect)
                inside = not inside

            elif bot_intersect:# and bot_n != 2:
                bot_n += 1
                if inside:
                    pg.draw.line(self.screen, WHITE, line[0], bot_intersect, 2)
                    total_len += get_len(line[0], bot_intersect)
                else:
                    self.B.append(line[0])
                    pg.draw.line(self.screen, WHITE, line[1], bot_intersect, 2)
                    total_len += get_len(line[1], bot_intersect)
                self.B.append(bot_intersect)
                inside = not inside
            else:
                if inside:
                    pg.draw.line(self.screen, WHITE, *line, 2)
                    total_len += get_len(*line)
                else:
                    # outside, so append depending on which side of field
                    if line[0].y < field_top:
                        self.A.append(line[0])
                        # self.A.append(line[1])
                    else:
                        self.B.append(line[0])              
                        # self.B.append(line[1])              
                    continue
        
        if top_n != 2:
            self.A = []
        if bot_n != 2:
            self.B = []

        pg.display.flip()
        return

    def test_3_init(self):  # cutting
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 1
        ROT_SPEED = 1
        self.current = Tetromino(T, pos=(W // 2, H // 2), rot = 3 * 91)
        self.other = None
        self.f = self.fields[8]
    
    def test_3_event(self):
        # create two new shapes from A and B
        self.A, self.B = self.current.cut(self.f)
        if self.A:
            self.other = self.current.fragment_into(self.A, self.B)
            if self.other:
                self.tetrominos.append(self.other)
            # self.new_tetromino()
    
    def test_3(self): # Cut testing
        
        pg.display.flip()
        self.debug(False)

        self.update()
        # self.current.kinematic()
        self.physics()
        
        # if self.other:
        #     self.other.kinematic_other()
        #     corners = self.other.shape.corners
        #     color = self.other.shape.color
        #     gfx.aapolygon(self.screen, corners, color)
        #     gfx.filled_polygon(self.screen, corners, color)

        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)

    def test_4_init(self):  # cutting
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 1
        ROT_SPEED = 1
        self.current = Tetromino(L, pos=(W // 2, H // 2), rot = 3 * 91)
        self.other = None
        self.f = self.fields[8]
        self.A, self.B = self.current.cut(self.f)
        if self.A:
            self.current.fragment_into(self.A, self.B)
    
    def test_4_event(self):
        # create two new shapes from A and B
        if self.A:
            self.other = self.current.fragment_into(self.A, self.B)
            if self.other:
                self.tetrominos.append(self.other)
            self.new_tetromino()
    
    def test_4(self): # Compute centroid
        
        pg.display.flip()
        self.debug(False)

        self.current.kinematic()
        
        if self.other:
            self.other.kinematic_other()
            corners = self.other.shape.corners
            color = self.other.shape.color
            gfx.aapolygon(self.screen, corners, color)
            gfx.filled_polygon(self.screen, corners, color)

        shape = self.current.shape
        for corner in shape.corners:
            pg.draw.circle(self.screen, (255, 255, 255), corner, 3)

        # https://stackoverflow.com/questions/9692448/how-can-you-find-the-centroid-of-a-concave-irregular-polygon-in-javascript
        def get_centroid(pts: List[V2]):
            """Return the centroid of a polygon (loops around)."""
            area = 0
            x, y = 0, 0,
            i, j = 0, len(pts) - 1
            while i < len(pts):
                p1, p2 = pts[i], pts[j]
                f = p1.cross(p2)
                area += f
                x += (p1.x + p2.x) * f
                y += (p1.y + p2.y) * f
                j = i; i += 1
            return V2(x, y) / (area * 3)
            # for ( var i=0, j=nPts-1 ; i<nPts ; j=i++ ) {
            #     p1 = pts[i]; p2 = pts[j];
            #     f = p1.x*p2.y - p2.x*p1.y;
            #     twicearea += f;          
            #     x += ( p1.x + p2.x ) * f;
            #     y += ( p1.y + p2.y ) * f;
            # }
            # f = twicearea * 3;
            # return { x:x/f, y:y/f };
        
        centroid = get_centroid(shape.polygon)
        pg.draw.circle(self.screen, (255, 0, 0), centroid, 3)

    def test_5_init(self): # Clear lines
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 1
        ROT_SPEED = 1
        self.current = Tetromino(L, pos=(W // 2, H // 2), rot = 3 * 91)
        # create other shapes to fill the field
        self.tetrominos = []
        for i in range(7):
            rot = random.randint(0, 360)
            piece = random.randint(0, 6)
            self.tetrominos.append(Tetromino(piece, pos=(i * SIZE * 2, H // 2), rot = rot))

        self.other = None
        self.f = self.fields[8]
        self.ray = [V2(W, H // 2 + SIZE), V2(-W, H // 2+ SIZE)]
        self.LEN = CLEAR_TRESH
    
    def test_5_event(self):
        self.draw_ui(f'Len: {round(self.len, 2)} / {self.LEN}', (200, 100))
        self.pause()
    
    def test_5(self):  # Clearline - assume all are within field
        self.current.kinematic()
        self.debug(False)
        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)

        

        # compute length of ray that is within the pieces
        # ray will intersect exactly twice with each piece

        def clear_line(ray):
            total_length = 0.0
            for t in self.tetrominos:
                poi = None
                for line in t.shape.lines:
                    # compute intersection with ray
                    intersection = seg_intersect(*ray, *line)
                    if intersection:
                        if poi:
                            total_length += abs(poi.x - intersection.x)
                            pg.draw.line(self.screen, WHITE, intersection, poi, 1)
                            break
                        else:
                            poi = intersection
                        # draw line
            self.len = total_length
            return total_length > 200
        
        for field in self.fields:
            ray = [V2(*field.corners[1]), V2(*field.corners[0])]
            if clear_line(ray):
                pg.draw.line(self.screen, BLACK, *ray, 1)
        

                 

        pg.display.flip()


DEBUG = False
if __name__ == "__main__":
    game = Game()
    # game.test(3)
    game.run(debug=True)




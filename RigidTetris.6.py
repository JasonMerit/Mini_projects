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
- V2 does not copy, you have to do it elementwise




"""

import pygame as pg
import numpy as np
import random, time, sys, math
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
FIELD = np.array([[0, 0], [W, 0], [W, SIZE], [0, SIZE]]) # Field is a rectangle
SHAPES = [I, L, J, O, S, T, Z, FIELD]
I, J, L, O, S, T, Z = range(7)
NAMES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
SPAWNS = [(-2*SIZE, 0), (-3*SIZE//2, -SIZE), (-3*SIZE//2, -SIZE), (-SIZE, -SIZE), (-3*SIZE//2, -SIZE), (-3*SIZE//2, -SIZE), (-3*SIZE//2, -SIZE)]
SPAWNS = [V2(*s) + [W // 2, 0] for s in SPAWNS]
CENTROIDS = np.array(([2*SIZE, SIZE//2], [7*SIZE//4, 5*SIZE//4], [5*SIZE//4, 5*SIZE//4], 
                      [SIZE, SIZE], [6*SIZE//4, SIZE], [3*SIZE//2, 5*SIZE//4], [6*SIZE//4, SIZE]))
PERIMETERS = np.power(np.array([10, 10, 10, 8, 10, 10, 10]) * SIZE, 2)                      
CLEAR_FIELD = np.array([[W // 2, SIZE // 2], [0, 0], [W, 0], [W, SIZE], [0, SIZE]])  # + centroid
CLEAR_TRESH = 8 * SIZE#8

LINE_AREA = W * SIZE * 0.8  # Controls the ratio of area a line must be covered for it to clear
MIN_AREA = 0.5 * SIZE ** 2  # How small a piece can be before it is considered starved and removed from the game
MOVE_SPEED, ROT_SPEED = 2, 5
FLOOR_FRIC, WALL_FRIC, ROT_FRIC = 0.2, 0.4, 0.3#0.8,0.8,0.8
GRAV, MOI = 30, SIZE ** 4 # pi * D^4/64
FORCE = 1.4

# Minimizing
MAX_SPEED, MAX_OMEGA = 100, 100

# helper functions
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (800,45)

# def seg_intersect(a1: V2, a2: V2, b1: V2, b2: V2) -> V2: # A(a1 -> a2) and B(b1 -> b2) are line segments
#     # When parallel, seg_intersect should return average of overlapping segments
#     db = b2 - b1
#     da = a2 - a1
#     denom = da.cross(db)
#     if denom == 0: # parallel, check for coincident
#         # check if lines are on same axis (numerators from outside different = 0)
#         d0 = a1 - b1
#         if db.cross(d0) != 0 or da.cross(d0) != 0: 
#             return V2(0, 0)

#         # project points onto line
#         dot_a1 = a1.dot(db)
#         dot_a2 = a2.dot(db)
#         dot_b1 = b1.dot(db)
#         dot_b2 = b2.dot(db)
#         # find overlap
#         min_a, max_a = min(dot_a1, dot_a2), max(dot_a1, dot_a2)
#         min_b, max_b = min(dot_b1, dot_b2), max(dot_b1, dot_b2)
#         if min_a > max_b or min_b > max_a: # no overlap
#             return V2(0, 0)

#         # return center of overlap over larger segment
#         return (a1 + a2) / 2 if max_a - min_a < max_b - min_b else (b1 + b2) / 2
    
#     d0 = a1 - b1
#     ua = db.cross(d0) / denom
#     if ua < 0 or ua > 1: return V2(0, 0) # out of range

#     ub = da.cross(d0) / denom
#     if ub < 0 or ub > 1: return V2(0, 0) # out of range

#     return a1 + da * ua

# def _seg_intersect(a1: V2, a2: V2, b1: V2, b2: V2) -> V2: # Same but ignore parallel lines
#     db = b2 - b1
#     da = a2 - a1
 
#     denom = da.cross(db)
#     if denom == 0: return V2(0, 0)# parallel, fuck it
        
#     d0 = a1 - b1
#     ua = db.cross(d0) / denom
#     if ua < 0 or ua > 1: return V2(0, 0) # out of range

#     ub = da.cross(d0) / denom
#     if ub < 0 or ub > 1: return V2(0, 0) # out of range

#     return a1 + da * ua

# def perp(v): return V2(-v.y, v.x)
    
class Line():
    """Line defined by a pair of 2d vectors representing the start and end points"""

    def __init__(self, start=V2(0, 0), end=V2(0, 0)):
        self.a = start
        self.b = end
        
        # self.normal = get_normal(start, end)
        # self.length = (end - start).length()
    
    @property
    def v(self): return self.b - self.a

    def translate(self, vector):
        self.a += vector
        self.b += vector
    
    def __repr__(self):
        return f'Line({self.a}, {self.b})'
    
    def __eq__(self, other: Line):
        assert(isinstance(other, Line)), f'Cannot compare Line with {type(other)}'
        return self.a == other.a and self.b == other.b
    
    def seg_intersect(self, other: Line):
        """Returns the point of intersection between two line segments. 
        If the lines are parallel, returns the average of the overlapping segments"""
        # When parallel, seg_intersect should return average of overlapping segments
        # return seg_intersect(self.a, self.b, other.a, other.b)
        db = other.b - other.a
        da = self.b - self.a
        denom = da.cross(db)
        if denom == 0: # parallel, check for coincident
            # check if lines are on same axis (numerators from outside different = 0)
            d0 = self.a - other.a
            if db.cross(d0) != 0 or da.cross(d0) != 0: 
                return V2(0, 0)

            # project points onto line
            dot_a1 = self.a.dot(db)
            dot_a2 = self.b.dot(db)
            dot_b1 = other.a.dot(db)
            dot_b2 = other.b.dot(db)
            # find overlap
            min_a, max_a = min(dot_a1, dot_a2), max(dot_a1, dot_a2)
            min_b, max_b = min(dot_b1, dot_b2), max(dot_b1, dot_b2)
            if min_a > max_b or min_b > max_a: # no overlap
                return V2(0, 0)

            # return center of overlap over larger segment
            return (self.a + self.b) / 2 if max_a - min_a < max_b - min_b else (other.a + other.b) / 2
        
        d0 = self.a - other.a
        ua = db.cross(d0) / denom
        if ua < 0 or ua > 1: return V2(0, 0) # out of range

        ub = da.cross(d0) / denom
        if ub < 0 or ub > 1: return V2(0, 0) # out of range

        return self.a + da * ua
    
    def _seg_intersect(self, other: Line): # ignoring parallel
        """Returns the point of intersection between two line segments."""
        db = other.b - other.a
        da = self.b - self.a
        denom = da.cross(db)
        if denom == 0: return V2(0, 0) # parallel, fuck it
        
        d0 = self.a - other.a
        ua = db.cross(d0) / denom
        if ua < 0 or ua > 1: return V2(0, 0) # out of range

        ub = da.cross(d0) / denom
        if ub < 0 or ub > 1: return V2(0, 0) # out of range

        return self.a + da * ua

    def get_normal(self): # checkem
        v = self.v
        return V2(v.y, -v.x)
    
    def get_midpoint(self):
        return (self.a + self.b) / 2
    
    def draw(self, screen, color, size=5):
        if not self: return
        pg.draw.line(screen,color,self.a,self.b,2)
        rotation = math.degrees(math.atan2(self.a[1]-self.b[1], self.b[0]-self.a[0]))+90
        pg.draw.polygon(screen, color, ((self.b[0]+size*math.sin(math.radians(rotation)), 
                                        self.b[1]+size*math.cos(math.radians(rotation))), 
                                        (self.b[0]+size*math.sin(math.radians(rotation-120)), 
                                        self.b[1]+size*math.cos(math.radians(rotation-120))), 
                                        (self.b[0]+size*math.sin(math.radians(rotation+120)), 
                                        self.b[1]+size*math.cos(math.radians(rotation+120)))))

    def __bool__(self):
        return not (self.a == V2(0, 0) and self.b == V2(0, 0))
    
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

    def __init__(self, id, pos=V2(0, 0), rot=0, frag=False):
        """Initialize shape. id piece type (color, centroid, corners), pos, array (centroid, corners)"""
        self.id = id
        self.color = COLORS[id]
        self.perimeter = PERIMETERS[id]
        self.rot = 0 # rotation in degrees - changed in rotate()

        if frag:
            return

        self.array = np.concatenate(([CENTROIDS[id]], SHAPES[id].copy()))  # First entree is centroid
        # self.translate(SPAWNS[id])  # offset depending on tetrimino
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
        """Using the Line class"""
        return [Line(a, b) for a, b in zip(self.polygon, self.polygon[1:])]
    
    @property
    def top(self) -> float:
        return min([corner.y for corner in self.corners])
    
    @property
    def bot(self) -> float:
        return max([corner.y for corner in self.corners])

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box of shape (minx, miny, maxx, maxy)"""
        xs, ys = zip(*self.corners)
        return min(xs), min(ys), max(xs), max(ys)
    
    @property
    def normals(self):
        """Get list of normals of shape""" # defined as left normal
        return [get_normal(a, b) for a, b in zip(self.polygon, self.polygon[1:])]
    
    

    """Geometry methods"""
    def bounds_intersect(self, other: Shape):
        """Check if bounding boxes intersect"""
        a = self.bounds
        b = other.bounds
        return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
    
    def poly_line(self, line):
        """Check if line intersects polygon by looping through THIS shape's lines"""
        for a, b in zip(self.polygon, self.polygon[1:]):
            if poi := seg_intersect(a, b, *line):
                normal = - perp(line[1] - line[0])
                return a, poi, normal # or b    

    def intersect1(self, other: Shape): # Unused
        """Check if two polygons intersect by looping over their lines
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
            if Line(point, point + UP)._seg_intersect(line):
                intersections += 1
        return intersections % 2 == 1
    
    @staticmethod # https://stackoverflow.com/questions/9692448/how-can-you-find-the-centroid-of-a-concave-irregular-polygon-in-javascript
    def compute_centroid(pts: List[V2]):
        """Return the centroid of a polygon (loops around)."""
        first = pts[0]
        last = pts[-1]
        if first.x != last.x or first.y != last.y:
            pts = pts.copy()
            pts.append(first)
        twicearea = 0
        x, y = 0, 0,
        i, j = 0, len(pts) - 1
        while i < len(pts):
            p1, p2 = pts[i], pts[j]
            f = (p1.y - first.y) * (p2.x - first.x) - (p2.y - first.y) * (p1.x - first.x)
            twicearea += f
            x += (p1.x + p2.x - 2 * first.x) * f
            y += (p1.y + p2.y - 2 * first.y) * f
            j = i; i += 1
        f = twicearea *  3
        return V2(x / f + first.x, y / f + first.y), twicearea / 2

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
    
    def __repr__(self) -> str:
        return NAMES[self.id]
    

class Fragment(Shape):
    """Fragment of a shape"""
    def __init__(self, id: int, corners: List[V2], velocity, omega):
        if corners == []:
            self.valid = False
            return
        centroid, area = self.compute_centroid(corners)
        if area < 10:
            self.valid = False
            return
        self.valid = True

        self.array = np.concatenate(([centroid], corners))
        super().__init__(id, frag=True)

        self.vel = V2(0, 0)
        self.vel.x, self.vel.y = velocity.x, velocity.y
        self.omega = omega

        self.area = area
        self.mass = area * SIZE  # meh
        self.moment = area // 100 # not implemented
        
    
    def draw(self, screen):
        """Draw fragment"""
        gfx.aapolygon(screen, self.corners, self.color)
        gfx.filled_polygon(screen, self.corners, self.color)
        # pg.draw.circle(screen, WHITE, self.centroid, 5)
    
    """Dynamic methods"""
    def physics_step(self):
        """Intrinsic collisions of boundary. Updates shape"""
        self.boundary_collision()

        if not self.floor():
            self.vel.y += GRAV * dt
        # clamp rotation
        self.omega = min(max(self.omega, -MAX_OMEGA), MAX_OMEGA)

        self.rotate(self.omega * dt)
        self.translate(self.vel * dt)
    
    def floor(self):
        """Check if the tetromino is on the floor."""
        # get the bounds y maximum
        y_max = max(self.array[:, 1])
        if y_max >= H:
            return True
    
    def boundary_collision(self):
        """Discrete boundary collision detection and response"""
        # Vector.Cross (cp, v) / cp.sqrMagnitude;
        # Continuous with reflection vector calculated using pygame vector.reflect
        left, top, right, bot = self.bounds  # absolute positions

        if left < 0: # Wall
            dx = -left
            self.translate((dx, 0))
            self.vel.x *= -WALL_FRIC
            self.omega *= -ROT_FRIC
        
        elif right > W: # Wall
            dx = W - right
            self.translate((dx, 0))
            self.vel.x *= -WALL_FRIC
            dx = W - right
            self.omega *= -ROT_FRIC

        if bot > H: # Floor
            dy = H - bot
            self.translate((0, dy))
            self.vel.y *= -FLOOR_FRIC    
            self.omega *= -ROT_FRIC

        elif top < - 2 * SIZE: # Ceiling
            dy = - (2 * SIZE + top)
            self.translate((0, dy))
            self.vel.y *= -WALL_FRIC     
            self.omega *= -ROT_FRIC
        
    def cut(self, field: Shape):
        """Cut the fragment with a shape"""
        return 
    
class Tetromino(Shape):
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

    def __init__(self, piece=0, pos=(W // 2, 0), rot=0) -> None:
        super().__init__(piece, pos, rot)
        self.color = COLORS[piece]

        # Physics
        self.pos = V2(pos)
        self.vel = V2(0, 50*MOVE_SPEED)
        self.omega = 0
        self.mass = SIZE ** 2 # Updates when cut
        self.moment = MOI#MOI # Updates when cut # not implemented currently

        self.KEK = 0

    def kinematic(self): # Used to debug with precise movement
        keys = pg.key.get_pressed()
        
        rotate = (keys[pg.K_e] - keys[pg.K_q]) * ROT_SPEED
        if rotate:
            self.rotate(rotate)

        dx = (keys[pg.K_d] - keys[pg.K_a]) * MOVE_SPEED
        dy = (keys[pg.K_s] - keys[pg.K_w]) * MOVE_SPEED
        if dx or dy:
            self.translate((dx, dy))

        if keys[pg.K_f]:
            self.rotate_to(0)
    
    def kinematic_other(self): # Used to debug with precise movement
        keys = pg.key.get_pressed()
        
        rotate = (keys[pg.K_RSHIFT] - keys[pg.K_END]) * ROT_SPEED
        if rotate:
            self.rotate(rotate)

        dx = (keys[pg.K_RIGHT] - keys[pg.K_LEFT]) * MOVE_SPEED
        dy = (keys[pg.K_DOWN] - keys[pg.K_UP]) * MOVE_SPEED
        if dx or dy:
            self.translate((dx, dy))

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

        self.rotate(self.omega * dt)
        self.translate(self.vel * dt)
    
    def floor(self):
        """Check if the tetromino is on the floor."""
        # get the bounds y maximum
        y_max = max(self.array[:, 1])
        if y_max >= H:
            return True
    
    def boundary_collision(self):
        """Discrete boundary collision detection and response"""
        # Continuous with reflection vector calculated using pygame vector.reflect
        left, top, right, bot = self.bounds  # absolute positions

        if left < 0: # Wall
            dx = -left
            self.translate((dx, 0))
            self.vel.x *= -WALL_FRIC
            self.omega *= -ROT_FRIC
        
        elif right > W: # Wall
            dx = W - right
            self.translate((dx, 0))
            self.vel.x *= -WALL_FRIC
            self.omega *= -ROT_FRIC

        if bot > H: # Floor
            dy = H - bot
            self.translate((0, dy))
            self.vel.y *= -FLOOR_FRIC    
            self.omega *= -ROT_FRIC

        elif top < - 2 * SIZE: # Ceiling
            dy = - (2 * SIZE + top)
            self.translate((0, dy))
            self.vel.y *= -WALL_FRIC     
            self.omega *= -ROT_FRIC
    
    def collide_with(self, other: Tetromino):
        """Returns displacement vectors if collition, otherwise empty V2"""
        # compute intersection - assume only two points of intersection
        cunt = V2(0, 0)  # Point of collision
        side = Line()  # Get the normal from this

        pois = []
        lines_crossed = []
        for line2 in other.lines:
            for line1 in self.lines:
                intersection = line1._seg_intersect(line2)
                if intersection:
                    pois.append(intersection)
                    lines_crossed.append((line1, line2))
                    if len(pois) == 2:
                        break                    
            if len(pois) == 2:
                break

        if len(lines_crossed) != 2:  # No intersection
            return V2(0, 0), V2(0, 0), V2(0, 0), V2(0, 0)

        cunt1, cunt2 = V2(0, 0), V2(0, 0)
        # Find contained point by abusing lines appearance in lines_crossed
        # Either all lines are different or one appears twice
        (line_a1, line_b1), (line_a2, line_b2) = lines_crossed
        side = Line() # side of interest when resolving later
        if line_a1 == line_a2 or line_b1 == line_b2: # twice appearence => one cunt
            # one cunt must appear at start and end of cross respectively
            if line_a1 == line_a2: # same line, so b point is contained
                side = line_a1
                if line_b1.a == line_b2.b:  # match the cunt
                    cunt2 = line_b1.a
                else:
                    cunt2 = line_b1.b
            else:
                side = line_b1
                if line_a1.a == line_a2.b:  # match the cunt
                    cunt1 = line_a1.a
                else:
                    cunt1 = line_a1.b

        else: # all unique => 2 cunts. can only check cunts
            if line_b1.a == line_b2.b:
                cunt2 = line_b1.a
            else:
                cunt2 = line_b1.b
            if line_a1.a == line_a2.b:  # match the cunt
                    cunt1 = line_a1.a
            else:
                cunt1 = line_a1.b

        
        # Now find the displacement required to resolve cunts
        disp_a, disp_b = V2(0, 0), V2(0, 0)
        
        if cunt1 and cunt2: # Both have cunts
            # I know that the cunt was caused by velocities, so I need 
            # to find the relevant side for both cunts
            cunt_line = Line(cunt1, cunt1 - self.vel)
            intersect = cunt_line._seg_intersect(line_b1)
            side_b = Line()
            if intersect:
                side_b = line_b1
            else:
                intersect = cunt_line._seg_intersect(line_b2)
                if intersect: # if not, other object caused collision!
                    side_b = line_b2
            if side_b:
                disp_a = intersect - cunt1
                side = side_b
                cunt = cunt2
            
            # Other piece
            cunt_line = Line(cunt2, cunt2 - other.vel)
            intersect = cunt_line._seg_intersect(line_a1)
            side_a = Line()
            if intersect:
                side_a = line_a1
            else:
                intersect = cunt_line._seg_intersect(line_a2)
                if intersect:
                    side_a = line_a2
            if side_a:
                disp_b = intersect - cunt2
                side = side_a
                cunt = cunt1
            
            # Since I have two, displacement becomre more complicated
            # First check if both even came up with a side to intersect with
            # - this may not occur depending on their velocities
            # For now just pick the one with the highest velocity
            if side_a and side_b:
                if self.vel.length_squared() > other.vel.length_squared():
                    disp_b = V2(0, 0)
                    side = side_a
                    cunt = cunt2
                else:
                    disp_a = V2(0, 0)
                    side = side_b
                    cunt = cunt1

        elif cunt1: # Only self has a cunt
            cunt = cunt1
            cunt_line = Line(cunt1, cunt1 - self.vel)
            intersect = cunt_line._seg_intersect(side)

            if intersect:
                disp_a = intersect - cunt1
            else:
                cunt_line = Line(cunt1, cunt1 + other.vel)
                intersect = cunt_line._seg_intersect(side)
                disp_b = cunt1 - intersect
        
        elif cunt2:
            cunt = cunt2
            # Now using the cunts, find minimal displacement to resolve instersection
            # Assuming intersection occurs on side of velocity pointing to
            cunt_line = Line(cunt2, cunt2 - other.vel)
            intersect = cunt_line._seg_intersect(side) # move b                

            if intersect: # Bias towards moving the piece with cunt
                disp_b = intersect - cunt2
            else: # must move other piece then
                cunt_line = Line(cunt2, cunt2 + self.vel)
                intersect = cunt_line._seg_intersect(side)
                disp_a = cunt2 - intersect
        
        normal = side.get_normal()
        return disp_a, disp_b, cunt, normal

    def draw(self, screen):
        """Draw the tetromino on the screen."""
        gfx.aapolygon(screen, self.corners, self.color)
        gfx.filled_polygon(screen, self.corners, self.color)
                    
    def draw_bounds(self, screen):
        A = self.bounds
        gfx.aapolygon(screen, [(A[0], A[1]), (A[2], A[1]), (A[2], A[3]), (A[0], A[3])], RED)

    """Field relevant methods"""

    """ THE FUCKING SHIT ALGORITHM"""
    def cut(self, field: Shape):
        """Cut off part of tetromino intersecting line. Assumes at least one intersection exists. 
        Returns the two collection of corners as a list."""
        # TODO: Generalize to multiple fragments instead of only A and B
        # 1) First find the first point of intersection
        # 2) Then distribute all passed points into approbriate lists
        # 3) Now iterate through rest of polygon, knowing which to append to
        # Only return cut if more than 3 points, and if only one survices,
        # ensure it is the first entree in the return statement. 
        field_top, field_bot = field.top, field.bot
        top_line = Line(V2(W, field_top), V2(0, field_top))
        bot_line = Line(V2(W, field_bot), V2(0, field_bot))
        top_intersect, bot_intersect = V2(0, 0), V2(0, 0)
        lines = self.lines
        A, B = [], []  # Always appending either pois or starts of lines
        top_n, bot_n = 0, 0 # Only return if they intersect field exactly twice


        # -------------------- 1) -------------------
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.a.y < field_top and line.b.y < field_top or line.a.y > field_bot and line.b.y > field_bot: # Above or below field
                i += 1
                continue
            else:
                top_intersect = line._seg_intersect(top_line)
                bot_intersect = line._seg_intersect(bot_line)
                if top_intersect or bot_intersect:
                    break
                else:  # Contained within field
                    i += 1
        else: # i = len(lines) -> no intersection -> all outside or all inside. Raycast to find out
            if field.contains_point(self.centroid):
                return [], []
            else:
                raise ValueError("Poor arguments: No intersection found.")
        
        
        # -------------------- 2) -------------------
        if top_intersect and bot_intersect: # both, so outside and two new polygons
            top_n, bot_n = 1, 1
            inside = False
            if line.v.cross(V2(-1, 0)) < 0:
                for j in range(i+1):                    
                    B.append(lines[j].a)
            else:
                for j in range(i+1):                    
                    A.append(lines[j].a)
            A.append(top_intersect)
            B.append(bot_intersect)

        elif top_intersect:
            top_n = 1
            if inside := line.v.cross(V2(-1, 0)) > 0:
                for j in range(i+1):                    
                    A.append(lines[j].a)
            A.append(top_intersect)

        elif bot_intersect:
            bot_n = 1
            if inside := line.v.cross(V2(-1, 0)) < 0:
                for j in range(i+1):                    
                    B.append(lines[j].a)
            B.append(bot_intersect)
        
        # -------------------- 3) -------------------
        for j in range(i+1, len(lines)):
            line = lines[j]
            top_intersect = line.seg_intersect(top_line)
            bot_intersect = line.seg_intersect(bot_line)

            if top_intersect and bot_intersect: # both, so inside
                top_n += 1; bot_n += 1
                if line.v.cross(V2(-1, 0)) < 0:
                    B.append(line.a)
                else:
                    A.append(line.a)
                A.append(top_intersect)
                B.append(bot_intersect)

            elif top_intersect:
                top_n += 1
                if not inside:
                    A.append(line.a)
                A.append(top_intersect)
                inside = not inside

            elif bot_intersect:
                bot_n += 1
                if not inside:
                    B.append(line.a)
                B.append(bot_intersect)
                inside = not inside
            elif not inside:
                # outside, so append depending on which side of field
                if line.a.y < field_top:
                    A.append(line.a)
                else:
                    B.append(line.a)              
        
        # don't return if less than three points or intersected more than twice
        if top_n != 2 or len(A) < 3:
            A = []
        if bot_n != 2 or len(B) < 3:
            B = []
        elif A == []:
            return [B, A] # flip em
        return [A, B]
    
    def __repr__(self):
        return f"{NAMES[self.id]} at {self.centroid}"

class Game:
    """Game class implementing Tetris with rigid tetrominos
    
    METHODS
    -------
    - run() - The main game loop
    - update() - Update current tetromino with player input + gravity
    - physics() - Update the physics sizes of all tetrominos + boundary checks
    - collision() - Check for collisions among tetrominos by polygon intersection + collision response
    """

    def __init__(self):
        pg.init()
        self.font1 = pg.font.SysFont('NewTimesRoman', 100)
        self.font2 = pg.font.SysFont('NewTimesRoman', 40)
        self.screen = pg.display.set_mode((W, H))
        pg.display.set_caption("Rigid Tetris")
        self.clock = pg.time.Clock()

        self.fields = [Shape(-1, (0, h)) for h in range(0, H, SIZE)]
        self.reset()

    def reset(self):
        self.bag = []
        self.score = 0
        self.tetrominos : List[Tetromino] = []  # Keeps track of dead tetrominos
        self.fragments : List[Fragment] = []  # Keeps track of fragments - different physics
        self.t = 10  # Frame counter
        piece=self.sample_bag()
        self.current = Tetromino(piece=piece, pos=SPAWNS[piece])

    def new_tetromino(self):
        # Add tetromino to list of dead tetrominos
        self.tetrominos.append(self.current)  # Delete them
        if self.t < 2:  # Game over
            self.reset()
            return      
        
        self.clear_lines()
        piece=self.sample_bag()
        self.current = Tetromino(piece=piece, pos=SPAWNS[piece])
        self.t = 0

        # check if any lines are full
        # self.score += self.clear_lines
    
    def sample_bag(self):
        """Return a list of tetrominos in the bag."""
        if self.bag == []:
            self.bag = [0, 1, 2, 3, 4, 5, 6]
            random.shuffle(self.bag)
        
        return self.bag.pop()
        
    def clear_line(self, field, intersecting: List[Shape]):
        """Clear a single line by clearing intersection with line. Returns True if any tetromino died of starvation."""
        for shape in intersecting:
            if isinstance(shape, Tetromino):
                kek = shape.cut(field)
                self.fragment_tetromino(shape, kek)
                if shape in self.tetrominos:
                    self.tetrominos.remove(shape)
            elif isinstance(shape, Fragment):
                if shape in self.fragments:
                    self.fragments.remove(shape)
            else:
                raise TypeError("Shape is not a Tetromino or Fragment")
    
    def sweep_field(self, ray, tetrominos: List[Tetromino]):
        """Sweep a field with a ray and return the total_length and intersecting tetrominos.
        Assumes tetrominos are sorted by y-coordinate."""
        length = 0.0
        intersected = []
        for t in tetrominos:
            if t.top > ray.a.y:
                return length, intersected  # Cut short if ray is above tetromino
            last_intersection = V2(0, 0)
            inside = False
            for line in t.lines:
                # compute intersection with ray
                intersection = line._seg_intersect(ray)
                if intersection:
                    if inside:
                        length += abs(intersection.x - last_intersection.x)
                    inside = not inside
                    last_intersection = intersection
            if last_intersection:
                intersected.append(t)

        return length, intersected

    def clear_lines(self):
        """Check if any lines are full and clear them. Returns the number of lines cleared."""
        # TODO: Preparea a query for each field
        # Ray cast from right to left to find intersections with lines
        # and if the length of intersection is equal to the length of the line, clear it
        # They ray could intersect multple times, but meh. Stop after two for each tetromino
        if self.tetrominos == []:
            return 0

        ts = sorted(self.tetrominos + self.fragments, key=lambda x: x.top)
        ray = Line(V2(0, -SIZE//2), V2(W, -SIZE//2)) # start above screen
        i = 0 # index of highest tetromino (lowest y)
        for field in self.fields:
            ray.translate(V2(0, SIZE))
            t = ts[i] # tetromino
            if t.top > field.bot: # no more pieces in this field
                continue
            for j in range(i, len(ts)): # Set new starting tetriminoe
                t = ts[j]
                if t.bot > field.top:
                    break
                i = j 

            # Sweep through the field and determine if it is full
            length, intersecting = self.sweep_field(ray, ts[i:])
            if length > CLEAR_TRESH: # 8 * SIZE here
                self.clear_line(field, intersecting)
                self.score += 1
    
    def fragment_tetromino(self, tetromino: Tetromino, fragment_corners: list):
        """Convert the provied corners into a list of fragments"""
        for corners in fragment_corners:
            frag = Fragment(tetromino.id, corners, tetromino.vel, tetromino.omega)
            if frag.valid: # area too small or corners empty
                self.fragments.append(frag)

    
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
                    self.current = Tetromino(T, pos=event.pos)

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
        
        for frag in self.fragments:
            frag.physics_step()
        
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
        
        # Draw fragments
        for frag in self.fragments:
            frag.draw(self.screen)

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
        self.current.draw_bounds(self.screen)
        
        for t in self.tetrominos:
            t.draw(self.screen)
            t.draw_bounds(self.screen)
        
        for f in self.fragments:
            f.draw(self.screen)

        color = (255, 0, 0, 20)
        for f in self.fields:
            gfx.aapolygon(self.screen, f.corners, color)
            gfx.filled_polygon(self.screen, f.corners, color)

        if flip:
            pg.display.flip()

    """Collision methods"""
    def collision(self):  # Swep and prune
        """Collision detection bettween tetriminos and placement check."""
        # Sort the balls by y position
        tetrominos = sorted(self.tetrominos, key=lambda t: t.top)

        # Sweep and prune
        for i, a in enumerate(tetrominos):
            for b in tetrominos[i+1:]:
                if b.top - a.top > SIZE * 4:  # Max distance between tetrominos is longbars height
                    break
                if not a.bounds_intersect(b):
                    continue
                disp_a, disp_b, cunt, normal = a.collide_with(b)
                if disp_a or disp_b:
                    self.collision_response1(a, b, disp_a, disp_b, cunt, normal)

        # Current tetromino placement
        # for other in self.tetrominos:
        #     if self.current.intersect(other):
        #         self.new_tetromino()
        #         break
    
    def collision_response1(self, a: Tetromino, b: Tetromino, disp_a, disp_b, x, y): 
                    #        cunt: V2, normal: V2):
        """Collision response between two tetrominos.
        Args:
            a (Tetromino): First tetromino
            b (Tetromino): Second tetromino
            poe (V2): Point of tetrimino a that intersects with b
            poi (V2): Point of intersection
            normal (V2): Normal of collision"""
        # pg.draw.circle(self.screen, RED, x, 10)
        # pg.draw.line(self.screen, YELLOW, x, x + y, 10)
        # self.pause()
        if disp_a:
            a.translate(disp_a)
        if disp_b:
            b.translate(disp_b)

        a.vel, b.vel = b.vel * WALL_FRIC, a.vel * WALL_FRIC  # No point of intersection, swap velocities (cop out)
        a.omega, b.omega = a.omega * WALL_FRIC, b.omega * WALL_FRIC
        
    
    def collision_response(self, a: Tetromino, b: Tetromino, disp_a, disp_b,
                           cunt: V2, normal: V2):
        """Collision response between two tetrominos.
        Args:
            a (Tetromino): First tetromino
            b (Tetromino): Second tetromino
            poe (V2): Point of tetrimino a that intersects with b
            poi (V2): Point of intersection
            normal (V2): Normal of collision"""
        if disp_a:
            a.translate(disp_a)
        if disp_b:
            b.translate(disp_b)

        # ra = cunt - a.centroid
        # rb = cunt - b.centroid
        # va = a.vel
        # vb = b.vel
        # wa = a.omega
        # wb = b.omega
        # nb = normal.normalize()
        # Ia, Ib = a.moment, b.moment
        # ma, mb = a.mass, b.mass

        # numer = -2 * (va.dot(nb) - vb.dot(nb) + wa * (ra.cross(nb)) - wb * (ra.cross(nb)))
        # denom = ma + mb + (Ia / ra.cross(nb) ** 2) + (Ib / rb.cross(nb) ** 2)

        # J = numer / denom * nb
        # va_ = va + J / ma
        # vb_ = vb - J / mb
        # wa_ = wa + ra.cross(J) / Ia # or wa + J.cross(ra) / Ia
        # wb_ = wb - rb.cross(J) / Ib # or wb - J.cross(rb) / Ib - copilot

        # a.vel, b.vel, a.omega, b.omega = va_, vb_, wa_, wb_
    
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
        # pg.draw.line(self.screen, BLACK, *self.current.lines[0], 2)

        _, field_top, _, field_bot = self.f.bounds()
        top_line = [V2(W, field_top), V2(0, field_top)]
        bot_line = [V2(W, field_bot), V2(0, field_bot)]
        top_intersect, bot_intersect = V2(0, 0), V2(0, 0)
        lines = self.current.lines

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
            if self.f.contains_point(self.current.centroid):
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
        self.current = Tetromino(L, pos=(W // 2, H // 2 + 80), rot = 3 * 91 - 180)
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
        self.draw_ui(f"Rot: {self.current.rot}", (100, 100))
        self.pause()

        # if self.A:
        #     self.current.fragment_into(self.A)

    
    def test_2(self): # Compute length of cut
        self.current.kinematic()
        self.debug(False)
        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)
        pg.draw.line(self.screen, BLACK, *self.current.lines[0], 3)

        _, field_top, _, field_bot = self.f.bounds()
        top_line = [V2(W, field_top), V2(0, field_top)]
        bot_line = [V2(W, field_bot), V2(0, field_bot)]
        top_intersect, bot_intersect = V2(0, 0), V2(0, 0)
        lines = self.current.lines

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
            if self.f.contains_point(self.current.centroid):
                self.draw_ui("Fully contained", (100, 100))
            else:
                self.draw_ui("No intersection", (100, 100))
                return
        
        # ALWAYS APPENDING START OF LINE -----------------------
        # Find where initial line ends (insde or outside)
        if top_intersect and bot_intersect: # both, so outside and two new polygons
            top_n += 1; bot_n += 1
            # pg.draw.line(self.screen, TURQUOISE, bot_intersect, top_intersect, 2)
            total_len += get_len(bot_intersect, top_intersect)
            inside = False
            

            if (line[1] - line[0]).cross(V2(-1, 0)) < 0:
                # self.B.append(line[0])
                for j in range(i+1):                    
                    self.B.append(lines[j][0])
            else:
                for j in range(i+1):                    
                    self.A.append(lines[j][0])
                # self.A.append(line[0])    
            self.A.append(top_intersect)
            self.B.append(bot_intersect)


        elif top_intersect:
            top_n += 1
            inside = (line[1] - line[0]).cross(V2(-1, 0)) > 0
            if inside:
                
                pg.draw.line(self.screen, BLUE, line[1], top_intersect, 2)
                total_len += get_len(line[1], top_intersect)
                for j in range(i+1):                    
                    self.A.append(lines[j][0])
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
                        pass
                        self.A.append(line[0])
                    else:
                        self.B.append(line[0])              
        
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
        kek = self.current.cut(self.f)
        self.fragment_tetromino(self.current, kek)
        self.new_tetromino()
    
    def test_3(self): # Cut testing
        
        pg.display.flip()
        self.debug(False)

        self.update()
        # self.current.kinematic()
        self.physics()
        
        # if self.other:
        #     self.other.kinematic_other()
        #     corners = self.other.corners
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
        self.frag = None
        self.f = self.fields[8]
        # self.A, self.B = self.current.cut(self.f)
        # if self.A:
        #     self.current.fragment_into(self.A, self.B)
    
    def test_4_event(self):
        self.A, self.B = self.current.cut(self.f)
        for a in self.A:
            pg.draw.circle(self.screen, RED, a, 5)
        if self.A:
            self.frag = Fragment(self.current.id, self.A, self.current.vel, self.current.omega)
            if self.frag.valid:
                self.fragments.append(self.frag)

    def test_4(self): # Compute centroid
        
        pg.display.flip()
        self.debug(False)

        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)

        self.current.kinematic()
        self.physics()
        
        # if self.frag:
        #     # self.frag.kinematic_other()
        #     # self.frag.physics_step()
        #     self.frag.draw(self.screen)

        

    def test_5_init(self): # Clear lines
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 1
        ROT_SPEED = 1
        self.current = Tetromino(L, pos=(W // 2, H // 2), rot = 3 * 91)
        # create other shapes to fill the field
        self.tetrominos = []
        # for i in range(10):
        #     rot = random.randint(0, 360)
        #     piece = random.randint(0, 6)
        #     y = random.randint(0, H)
        #     self.tetrominos.append(Tetromino(piece, pos=(i * SIZE * 2, y), rot = rot))

        self.other = None
        self.f = self.fields[8]
        self.ray = [V2(W, H // 2 + SIZE), V2(-W, H // 2+ SIZE)]
        self.LEN = CLEAR_TRESH
    
    def test_5_event(self):
        self.clear_lines()
    
    def test_5(self):  # Clearline - assume all are within field
        self.current.kinematic()
        self.debug(False)
        field_color = (255, 0, 0, 100)
        gfx.aapolygon(self.screen, self.f.corners, field_color)
        gfx.filled_polygon(self.screen, self.f.corners, field_color)


        # compute length of ray that is within the pieces
        # ray will intersect exactly twice with each piece
        ts = sorted(self.tetrominos + [self.current], key=lambda x: x.top)
        # for i, t in enumerate(ts):
        #     self.draw_ui(i, t.centroid)

        def sweep_field(ray, tetrominos: List[Shape]):
            # Recieves all tetro's within or below the field
            total_length = 0.0
            for t in tetrominos:
                if t.top > ray.a.y:
                    return total_length
                last_intersection = V2(0, 0)
                inside = False
                for line in t.lines:
                    # compute intersection with ray
                    intersection = line._seg_intersect(ray)
                    if intersection:
                        if inside:
                            total_length +=  abs(intersection.x - last_intersection.x)
                        inside = not inside
                        last_intersection = intersection
                        pg.draw.circle(self.screen, WHITE, intersection, 5)   
            return total_length
        

        total_total_lenth = 0
        ray = Line(V2(0, -SIZE//2), V2(W, -SIZE//2)) # start above screen
        i = 0 # index of highest tetromino (lowest y)
        for field in self.fields:
            ray.translate(V2(0, SIZE))
            t = ts[i]
            if t.top > field.bot: # no more pieces in this field
                continue
            for j in range(i, len(ts)): # Set new starting tetriminoe
                t = ts[j]
                if t.bot > field.top:
                    break
                i = j 
            length = sweep_field(ray, ts[i:])
            if length:
                total_total_lenth = length
                ray.draw(self.screen, RED)
            
        self.draw_ui(f'len: {round(total_total_lenth, 2)}', (200, 100))
        

                 

        pg.display.flip()

    def test_6_init(self):  # Collision intersect
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 3
        ROT_SPEED = 2
        self.current = Tetromino(L, pos=(W // 2 - 2*SIZE, H // 2), rot = 44)
        self.other = Tetromino(T, pos=(W // 2 + SIZE, H // 2 + SIZE * 3), rot = 4)
        self.current.vel = V2(0, 100)
        self.other.vel = V2(-20, 20)
        self.current.scale(2)
        self.other.scale(2)
        
    
    def test_6_event(self):
        if self.minimal_displacement_a:
            self.current.translate(self.minimal_displacement_a)
        if self.minimal_displacement_b:
            self.other.translate(self.minimal_displacement_b)

    def test_6(self): # Compute centroid
        self.current.kinematic()
        self.other.kinematic_other()
        self.screen.fill(BLACK)

        gfx.aapolygon(self.screen, self.current.corners, self.current.color)
        gfx.filled_polygon(self.screen, self.current.corners, self.current.color)
        gfx.aapolygon(self.screen, self.other.corners, self.other.color)
        gfx.filled_polygon(self.screen, self.other.corners, self.other.color)
        pg.draw.line(self.screen, WHITE, self.current.centroid, self.current.centroid + self.current.vel, 1)
        pg.draw.line(self.screen, WHITE, self.other.centroid, self.other.centroid + self.other.vel, 1)


        # compute intersection - assume only two points of intersection
        pois = []
        lines_crossed = []
        for line2 in self.other.lines1:
            for line1 in self.current.lines1:
                intersection = line1._seg_intersect(line2)
                if intersection:
                    pois.append(intersection)
                    lines_crossed.append((line1, line2))
                    # pg.draw.circle(self.screen, RED, intersection, 10)
                    # self.draw_ui(len(pois), intersection)
                    if len(pois) == 2:
                        break                    
            if len(pois) == 2:
                break


        if len(lines_crossed) != 2:
            pg.display.flip()
            return

        cunt1, cunt2 = V2(0, 0), V2(0, 0)
        # Find contained point by abusing lines appearance in lines_crossed
        # Either all lines are different or one appears twice
        (line_a1, line_b1), (line_a2, line_b2) = lines_crossed  # cross_a of lines and cross_b of lines
        # line_a1, line_b1 = cross_a
        # line_a2, line_b2 = cross_b
        side = Line() # side of interest when resolving later
        # draw_arrow(self.screen, WHITE, b1[0], b1[1], 5)
        # draw_arrow(self.screen, WHITE, b2[0], b2[1], 5)
        if line_a1 == line_a2 or line_b1 == line_b2: # twice appearence => one cunt
            # one cunt must appear at start and end of cross respectively
            if line_a1 == line_a2: # same line, so b point is contained
                side = line_a1
                if line_b1.a == line_b2.b:  # match the cunt
                    cunt2 = line_b1.a
                else:
                    cunt2 = line_b1.b
            else:
                side = line_b1
                if line_a1.a == line_a2.b:  # match the cunt
                    cunt1 = line_a1.a
                else:
                    cunt1 = line_a1.b

        else: # all unique => 2 cunts. can only check cunts
            if line_b1.a == line_b2.b:
                cunt2 = line_b1.a
            else:
                cunt2 = line_b1.b
            if line_a1.a == line_a2.b:  # match the cunt
                    cunt1 = line_a1.a
            else:
                cunt1 = line_a1.b

        # if cunt1:
        #     pg.draw.circle(self.screen, GREEN, cunt1, 2)
        # if cunt2:
        #     pg.draw.circle(self.screen, RED, cunt2, 2)
        
        self.minimal_displacement_a = V2(0, 0)
        self.minimal_displacement_b = V2(0, 0)
        side_a, side_b = Line(), Line()
        cunt = V2(0, 0)
        if cunt1 and cunt2: # much more complicated. Must move both objects
            # I know that the cunt was caused by velocities, so I need 
            # to find the relevant side for both cunts
            cunt_line = Line(cunt1, cunt1 - self.current.vel)
            # cunt_line.draw(self.screen, YELLOW, 5)
            intersect = cunt_line._seg_intersect(line_b1)
            
            if intersect:
                side_b = line_b1
                # side_b.draw(self.screen, RED, 10)
            else:
                intersect = cunt_line._seg_intersect(line_b2)
                if intersect: # if not, other object caused collision!
                    side_b = line_b2
                    # side_b.draw(self.screen, GREEN, 10)
            if side_b:
                self.minimal_displacement_a = intersect - cunt1
                side = side_b
                cunt = cunt2
                
                
                # pg.draw.line(self.screen, YELLOW, intersect, cunt1, 4)
            
            # Other piece
            cunt_line = Line(cunt2, cunt2 - self.other.vel)
            # cunt_line.draw(self.screen, YELLOW, 5)
            intersect = cunt_line._seg_intersect(line_a1)
            
            if intersect:
                side_a = line_a1
                # side_a.draw(self.screen, RED, 10)
            else:
                intersect = cunt_line._seg_intersect(line_a2)
                if intersect:
                    side_a = line_a2
                    # side_a.draw(self.screen, GREEN, 10)
                # pg.draw.line(self.screen, BLUE, intersect, cunt2, 4)
            if side_a:
                self.minimal_displacement_b = intersect - cunt2
                side = side_a
                cunt = cunt1
                
                
            
            # Since I have two, displacement becomre more complicated
            # First check if both even came up with a side to intersect with
            # - this may not occur depending on their velocities
            # For now just pick the one with the highest velocity
            if side_a and side_b:
                v1 = self.current.vel.length_squared()
                v2 = self.other.vel.length_squared()
                if v1 > v2:
                    self.minimal_displacement_b = V2(0, 0)
                    side = side_a
                    side_a.draw(self.screen, YELLOW, 4)
                    cunt = cunt2
                    pg.draw.circle(self.screen, YELLOW, cunt, 19)
                else:
                    self.minimal_displacement_a = V2(0, 0)
                    side = side_b
                    cunt = cunt1
                    side_a.draw(self.screen, WHITE, 4)
                # side_b.draw(self.screen, GREEN, 10) # here
                # side_a.draw(self.screen, RED, 10) # here


            # intersect = cunt_line._seg_intersect(side_1)
        
        elif cunt1:
            cunt = cunt1
            # self.current.vel = V2(20, 100)
            # self.other.vel = V2(-5, 20)

            # Now using the cunts, find minimal displacement to resolve instersection
            # Assuming intersection occurs on side of velocity pointing to
            cunt_line = Line(cunt1, cunt1 - self.current.vel)
            intersect = cunt_line._seg_intersect(side)

            if intersect:
                self.minimal_displacement_a = intersect - cunt1
                # pg.draw.line(self.screen, GREEN, cunt1, intersect, 5)
            else:
                cunt_line = Line(cunt1, cunt1 + self.other.vel)
                intersect = cunt_line._seg_intersect(side)
                self.minimal_displacement_b = cunt1 - intersect
                # pg.draw.line(self.screen, YELLOW, cunt1, intersect, 5)
            # side.draw(self.screen, RED, 10) # here
        
        elif cunt2:
            cunt = cunt2
            # Now using the cunts, find minimal displacement to resolve instersection
            # Assuming intersection occurs on side of velocity pointing to
            cunt_line = Line(cunt2, cunt2 - self.other.vel)
            intersect = cunt_line._seg_intersect(side) # move b                

            if intersect: # Bias towards moving the piece with cunt
                self.minimal_displacement_b = intersect - cunt2
                # cunt_line.draw(self.screen, GREEN, 10)
                # side.draw(self.screen, RED, 10)
                # pg.draw.circle(self.screen, WHITE, intersect, 5)
                # pg.draw.line(self.screen, YELLOW, cunt2, intersect, 5)
            else: # must move other piece then
                pass
                # pg.draw.circle(self.screen, BLUE, cunt2, 4)
                cunt_line = Line(cunt2, cunt2 + self.current.vel)
                # cunt_line.draw(self.screen, GREEN, 10)
                # side.draw(self.screen, RED, 10)
                intersect = cunt_line._seg_intersect(side)
                self.minimal_displacement_a = cunt2 - intersect
                
                # pg.draw.circle(self.screen, WHITE, intersect, 5)
            # side.draw(self.screen, GREEN, 10) # here

        self.test_6_event()


        if cunt1 and cunt2:
            self.draw_ui("bot cunt", (100, 100))
        # if cunt1:
        #     pg.draw.circle(self.screen, GREEN, cunt1, 10)
        # if cunt2:
        #     pg.draw.circle(self.screen, BLUE, cunt1, 10)
        # if side:
        #     side.draw(self.screen, YELLOW, 5)
        #     normal = side.get_normal()
        #     mid = side.get_midpoint()
            # pg.draw.line(self.screen, RED, mid, mid + normal, 4)
        else:
            self.draw_ui("No side", (200, 100))
        # if side_a:
        #     side_a.draw(self.screen, GREEN, 5)
        # if side_b:
        #     side_b.draw(self.screen, BLUE, 5)
        
        pg.draw.circle(self.screen, RED, cunt, 18)

        pg.display.flip()

    def test_7_init(self):
        self.current = Tetromino(O)

    def test_7_event(self):
        pass

    def test_7(self):
        self.current.move()
        

        left, top, right, bot = self.current.bounds  # absolute positions

        self.debug(False)
        

        center = self.current.centroid
        corners = self.current.corners                            
        
        def doit(ra, nb):
            va = self.current.vel
            wa = self.current.omega
            Ia = 100
            ma = 4

            numer = -2 * (va.dot(nb) + wa * (ra.cross(nb)))
            denom = ma + (Ia / ra.cross(nb) ** 2)

            J = numer / denom * nb
            va_ = va + J / ma
            wa_ = wa + ra.cross(J) / Ia # or wa + J.cross(ra) / Ia

            self.current.vel, self.current.omega = va_, wa_
        
        if left < 0: # Wall
            dx = -left
            self.current.translate((dx, 0))
            # self.current.vel.x *= -WALL_FRIC
            # self.current.omega *= - ROT_FRIC
            most = min(corners, key=lambda c: c.x)
            ra = most - center
            nb = V2(1, 0)
            doit(ra, nb)
        
        elif right > W: # Wall
            dx = W - right
            self.current.translate((dx, 0))
            # self.current.vel.x *= -WALL_FRIC
            # self.current.omega *= - ROT_FRIC
            most = max(corners, key=lambda c: c.x)
            ra = most - center
            nb = V2(-1, 0)
            doit(ra, nb)

        if bot > H: # Floor
            dy = H - bot
            self.current.translate((0, dy))
            # self.current.vel.y *= -FLOOR_FRIC             
            # self.current.omega *= - ROT_FRIC 
            most = max(corners, key=lambda c: c.y)
            ra = most - center
            nb = V2(0, -1)
            doit(ra, nb)  

        elif top < - 2 * SIZE: # Ceiling
            dy = - (2 * SIZE + top)
            self.current.translate((0, dy))
            # self.current.vel.y *= -WALL_FRIC  
            # self.current.omega *= - ROT_FRIC   
            most = min(corners, key=lambda c: c.y)
            ra = most - center
            nb = V2(0, 1)
            doit(ra, nb)
        

        self.current.physics_step()
        pg.display.flip()
    
    def test_8_init(self):
        self.current = Tetromino(O)
        self.other = Tetromino(I)
    
    def test_8_event(self):
        self.new_tetromino()
        self.clear_lines()
    
    def test_8(self): # Testing main game without fucking too much 
        self.current.move()
        self.current.physics_step()
        self.debug(False)
        self.current.move()
        self.physics()
        # self.collision()


        pg.display.flip()

DEBUG = False
if __name__ == "__main__":
    game = Game()
    # game.test(8)
    game.run(debug=True)




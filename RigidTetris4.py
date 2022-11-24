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
- Define a polygon including its center point? Since the relative positions between points are invariant. 
- repeat collision checks until no collisions


BUG
- When finding extracting shapes fromt split in cut using geoms, a moot warning is given
- Pieces are accumulating when cut, possible causes:
    - Out of bounds pieces are not being removed
    - Small area check not working properæy - the one liner
    - The cut is not being applied properly

Fuck Shapely
- Define Tetromino with center + exterior coords, where center = coords[0] and corners = coords[1:].
- Assemble all coords in a matrix and use numpy to rotate and translate with transform matrix - how?
- Intersection is done by seg_intersect.
- Cut is done by intersecting ClearLine over piece, with the piece being cut determined by T_CoM > ClearLine_y - SIZE // 2.
- After cutting, fragment areas are defined when computing the moment of inertia I.
- 


NOTE
- Use shapely.ops.transform(func, geom) to map all points in a shape
- Use STR-packed R-tree for collision detection and recreate the tree after each line deletion
- Convert to numpy arrays using np.asarry
- Snapping is a thing
- Use shape.touching to determine when tunneling has been resolved
- Intuitive collision https://fotino.me/2d-parametric-collision-detection/ but computationally heavy

CONSIDER
- Consider scoring based on area covered in line
- Settle pieces after a certain amount of time?
- Keep small tetrimos for cluttering the screen and cool spashing of small bodies

Status
- Boundary collision works great by forcing the piece to stay within the bounds before updating


"""

import pygame as pg
import numpy as np
import random, time
from typing import List, Tuple, NewType
from math import sin, cos, radians
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
AREA = 4 * SIZE ** 2
W, H = SIZE * 10, SIZE * 15
FPS = 60
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
I = [(0, 0), (4, 0), (4, 1), (0, 1)]
L = [(0, 0), (2, 1), (2, 0), (3, 0), (3, 2), (0, 2)]
J = [(0, 1), (1, 0), (1, 1), (3, 1), (3, 2), (0, 2)]
O = [(0, 0), (2, 0), (2, 2), (0, 2)]
S = [(0, 1), (1, 1), (1, 0), (3, 0), (3, 1), (2, 1), (2, 2), (0, 2)]
T = [(0, 1), (1, 1), (1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (0, 2)]
Z = [(0, 0), (2, 0), (2, 1), (3, 1), (3, 2), (1, 2), (1, 1), (0, 1)]
SHAPES = [I, L, J, O, S, T, Z]
I, J, L, O, S, T, Z = range(7)
names = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

# CLEAR_LINE = [(-50, 0), (W+50, 0), (W+50, SIZE), (-50, SIZE)]
CLEAR_LINE = [(0, 0), (W, 0), (W, SIZE), (0, SIZE)]
LINE_AREA = W * SIZE * 0.8  # Controls the ratio of area a line must be covered for it to clear
MIN_AREA = 0.5 * SIZE ** 2  # How small a piece can be before it is considered starved and removed from the game
MOVE_SPEED, ROT_SPEED = 10, 30
FLOOR_FRIC, WALL_FRIC, ROT_FRIC = 0.9, 1, 0.9
ACC = 1
FORCE = 1.4
K = 3
KEK = 0

# helper functions
def seg_intersect(a1: V2, a2: V2, b1: V2, b2: V2):
    # When parallel, seg_intersect should return average of overlapping segments
    db = b2 - b1
    da = a2 - a1
    denom = da.cross(db)
    if denom == 0: # parallel 
        # return midpoint of overlapping segments
        return (a1 + b2) / 2  # also return flag for parallel
    
    d0 = a1 - b1
    ua = db.cross(d0) / denom
    if ua < 0 or ua > 1: # out of range
        return False

    ub = da.cross(d0) / denom
    if ub < 0 or ub > 1: # out of range
        return False

    return a1 + da * ua
def perp(v):
    return V2(-v.y, v.x)
def get_normal(a, b):
    return perp(b - a).normalize()
    

R = 3 # Rotation speed degrees per frame
ROTATION = np.array([[np.cos(np.radians(R)), -np.sin(np.radians(R))], [np.sin(np.radians(R)), np.cos(np.radians(R))]])

class Tetromino():
    """Mainly defined from shapely's Polygon
    This acts as a kinematic body when current, and otherwise is dynamic.
    Transitions from kinematic to dynamic is tentative, but is checked first thing in move()

    METHODS
    -------
    - move() - Moves the tetromino based on player input
    - physics_step() - Updates the tetromino's position and velocity + boundary collision
    - cut() - Cuts the tetromino where it intersects with a line being cleared

    TODO
    - limit calls to shapes.centroid - have another point in polygon for this.
    
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
        self.pos = V2(pos)
        self.vel = V2(0, 50*MOVE_SPEED)
        self.acc = ACC # y component
        self.omega = 0
        self.mass = 1 # Updates when cut

        self.KEK = 0

        # self.inertia = 1
        # self.friction = 0.1
        # self.force = V2(0, 0)
        # self.torque = 0
    
    def kinematic(self): # Used to debug with precise movement
        keys = pg.key.get_pressed()
        
        rotate = (keys[pg.K_e] - keys[pg.K_q]) * ROT_SPEED
        self.shape = affinity.rotate(self.shape, rotate, origin=self.shape.centroid)

        dx = (keys[pg.K_d] - keys[pg.K_a]) * MOVE_SPEED
        dy = (keys[pg.K_s] - keys[pg.K_w]) * MOVE_SPEED
        self.shape = affinity.translate(self.shape, dx, dy)

    def move(self):
        """Move the tetromino by x and y and wall check. Called before update."""
        # if self.vel.y < 0:
        # if self.shape.bounds[3] > H:  # TRANSITION TO DYNAMIC
        #     return True # <------

        keys = pg.key.get_pressed()
        
        if keys[pg.K_e]:  # Rotation
            self.omega += ROT_SPEED
        elif keys[pg.K_q]:
            self.omega += -ROT_SPEED

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
            self.acc = 0
        # event = pg.event.get()
        # if event and event[0].type == pg.KEYDOWN:
        #     if event[0].key == pg.K_g:
        #         if self.acc == 0:
        #             self.acc = 100
        #         else:
        #             self.acc = 0
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
        # self.vel.y += self.acc * dt if not self.boundary_collision() else - self.vel.y
        self.boundary_collision()

        self.vel.y += self.acc * dt
        # self.omega *= ROT_FRIC

        self.shape = affinity.rotate(self.shape, self.omega * dt, origin=self.shape.centroid.coords[0])
        self.shape = affinity.translate(self.shape, *(self.vel * dt))
    
    def boundary_collision(self):
        """Discrete boundary collision detection and response"""
        # Continuous with reflection vector calculated using pygame vector.reflect
        left, top, right, bot = self.shape.bounds  # absolute positions

        if left < 0: # Wall
            dx = -left
            self.shape = affinity.translate(self.shape, dx, 0)
            self.vel.x *= -WALL_FRIC
            self.omega *= -1
        
        elif right > W: # Wall
            dx = W - right
            self.shape = affinity.translate(self.shape, dx, 0)
            self.vel.x *= -WALL_FRIC
            dx = W - right
            self.omega *= -1

        if bot > H: # Floor
            dy = H - bot
            self.shape = affinity.translate(self.shape, 0, dy)
            self.vel.y *= -FLOOR_FRIC    
            self.omega *= -1

        if top < - 2 * SIZE: # Ceiling
            dy = - (2 * SIZE + top)
            self.shape = affinity.translate(self.shape, 0, dy)
            self.vel.y *= -WALL_FRIC     
            self.omega *= -1
    
    def draw(self, screen):
        """Draw the tetromino on the screen."""
        gfx.aapolygon(screen, self.shape.exterior.coords, self.color)
        gfx.filled_polygon(screen, self.shape.exterior.coords, self.color)

        # center in int
        center = tuple(map(int, self.shape.centroid.coords[0]))
        # gfx.filled_circle(screen, *center, 5, WHITE) 

    def intersects1(self, other):
        pass

    def intersects(self, other: shp.Polygon) -> bool:
        """Return True if the tetromino intersects with another tetromino. 
        If no other tetromino is given, check if the tetromino intersects with the clear line."""
        # check if any of the points of the other tetromino are inside the tetromino
        # self.current.shape.touches(self.other.shape)
        return [p for p in self.shape.exterior.coords if other.contains(shp.Point(p))]
        return self.shape.intersects(other.shape)

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
                if key is None or event.key == key:
                    return
                elif event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()

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

    def update(self):
        # Update current kinematics
        if self.current.move(): # calls update too
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

    def debug(self, flip=True):
        self.screen.fill(BLACK)

        # draw SIZExSIZE grid
        for i in range(0, W, SIZE):
            for j in range(0, H, SIZE):
                pg.draw.rect(self.screen, GREY, (i, j, SIZE, SIZE), 1)

        # draw tetrominos
        self.current.draw(self.screen)
        self.draw_debug(self.current.shape)
        
        for t in self.tetrominos:
            t.draw(self.screen)
            self.draw_debug(t.shape)

        if flip:
            pg.display.flip()
    
    def draw_debug(self, shape: shp.Polygon):
        bounds = shape.bounds
        gfx.aapolygon(self.screen, [(bounds[0], bounds[1]), (bounds[2], bounds[1]), (bounds[2], bounds[3]), (bounds[0], bounds[3])], RED)

        for p in shape.exterior.coords:
            pg.draw.circle(self.screen, RED, p, 2)

    """Collision methods"""
    def collision(self):  # Assumes only one point intersects
        """Collision detection bettween tetriminos and placement check."""
        for i, a in enumerate(self.tetrominos):
            for b in self.tetrominos[i+1:]:
                # if a.intersects(b.shape):
                self.collision_response(a, b)

        # Current tetromino placement - delete?
        # for tetro in self.tetrominos:
        #     if self.current.intersects(tetro.shape):
        #         self.new_tetromino()
        #         break
    
    def collision_response(self, a: Tetromino, b: Tetromino):
        """Collision response between two tetrominos."""
        result = self.collision_displacement(a, b, a.vel)
         
        if not result:
            return
        poi, p = result
        try:
            pg.draw.circle(self.screen, RED, poi.coords[0], 5)
            pg.draw.line(self.screen, WHITE, p, poi.coords[0])
            print(poi)
            print(poi.coords[0])
            print(p)
            displacement = V2(p) - V2(poi.coords[0])
            a.shape = affinity.translate(a.shape, -displacement[0], -displacement[1])
            b.shape = affinity.translate(b.shape, displacement[0], displacement[1])
            a.vel, b.vel = b.vel, a.vel  # swap velocities
        except:
            pass
    
    def collision_displacement(self, a: Tetromino, b: Tetromino, normal: V2):
        """Return point of intersection (poi) and point of a confined in b.
        Use result to displace a and b with vector poi - p pointing towards.
        a -> b with vector a.vel
        args: a, b: Tetrominos
              normal: V2 velocity vector of a"""
        # if a.shape.touches(b.shape):
        #     return None
        normal = normal.copy() * 100
        for p in a.shape.exterior.coords:
            if b.shape.contains(shp.Point(p)):
                A = shp.LineString((shp.Point(p), shp.Point(p - normal)))
                poi = b.shape.exterior.intersection(A)
                return poi, p

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
        # raise NotImplementedError("test_1 not implemented")
        self.current = Tetromino(T, None, (W // 2, H // 2))
        self.current.vel.y = 0

        self.other = Tetromino(I, None, (W // 2 + 3 * SIZE, H // 2 - SIZE * 2), 90)
        self.other.vel.y = 0
        global MOVE_SPEED, ROT_SPEED
        MOVE_SPEED = 2
        ROT_SPEED = 2
        self.vel = V2(30,30)
        self.other.vel = V2(-30, 0)

    def test_1_event(self): # test_event()
        if self.displacement:
            # calculate ratio each tetromino must displace to resolve

            # OH NO: This approach uses the dot product to determine ratio, 
            # but then current will always be maximized
            # since displacement always points opposite current.vel
            dis_len = - self.displacement.length() 
            v_len = self.vel.length()
            if v_len > 1:
                a_disp = self.displacement.dot(self.vel) / (v_len * dis_len)
                self.current.shape = affinity.translate(self.current.shape, *(self.displacement * a_disp))

            ov_len = self.other.vel.length()
            if ov_len > 1:
                b_disp = self.displacement.dot(self.other.vel) / (ov_len * dis_len)
                self.other.shape = affinity.translate(self.other.shape, *(self.displacement * b_disp))

    def test_1(self): # test_method
        self.current.kinematic()
        # self.vel = self.vel.rotate(ROT_SPEED / 2)
        
        self.debug(False)
        # self.other.draw(self.screen)
        self.draw_debug(self.other.shape)
        
        
        # collision check, assumes collision occurs with velocities (controls sign of displacement and normal)
        # returns displacement vector and normal vector (or point of intersection and point of a confined in b)
        # When parallel, seg_intersect should return average of overlapping segments
        for p in self.current.shape.exterior.coords:
            if self.other.shape.contains(shp.Point(p)):
                A = V2(p - self.vel), V2(p)  # Line from contained point to current tetromino
                                             # Just need direction of vel, magnitude ~30, but ensure that B will intersecpt 
                # iterate over the other exterior points and create lines and check for intersection
                for a, b in zip(self.other.shape.exterior.coords, self.other.shape.exterior.coords[1:]):
                    B = V2(a), V2(b)
                    if poi := seg_intersect(*A, *B):
                        # point being contained in other
                        pg.draw.circle(self.screen, RED, poi, 5)
                        
                        normal = get_normal(B[1], B[0])  # incorrect sign
                        pg.draw.line(self.screen, WHITE, poi, poi + normal * 30)

                        # resolution displacement                        
                        displacement = V2(poi) - V2(p)
                        pg.draw.line(self.screen, WHITE, p, poi)

        pg.display.flip()

    def test_2_init(self): # moment of inertia
        self.current = Tetromino(L, None, (W // 2, H // 2))
        self.current.vel.y = 0

        
        
            

        for l in L:
            print(V2((l)))
        coords = [V2(coord) for coord in L]
        # coords = [V2(coord) for coord in self.current.shape.exterior.coords]
        cm = V2(0, 0)
        for c in coords:
            cm += c
        cm /= len(coords)
        print(cm)
        return 
        # calcluate total distance from center of mass to each point
        dist = 0
        for c in coords:
            dist += (c - cm).length()
        print(dist)

        self.current = Tetromino(L, None, (W // 2, H // 2))
        self.current.vel.y = 0
        coords = [V2(coord) for coord in self.current.shape.exterior.coords]
        cm = V2(0, 0)
        for coord in coords:
            cm += coord
        cm /= len(coords)

        # calcluate total distance from center of mass to each point
        dist = 0
        for c in coords:
            dist += (c - cm).length()
        print(dist)

        return         

        rho = 1
        def I_right(h, w):
            return rho * (h * w ** 3 / 4 + h ** 3 * w / 12)
        
        




        # compute moment of inertia for polygon with origin at center of mass
        # currently incorrect since I_J != I_K and I_S != I_Z
        # https://fotino.me/moment-of-inertia-algorithm/ # comments assign according to his illustartion
        # return 
        # rho = 0.0000001 # density
        for j in range(7):
            self.current = Tetromino(j, None, (W // 2, H // 2))
            moment = 0
            center = V2(self.current.shape.centroid.coords[0])
            self.coords = [V2(coord) - center for coord in self.current.shape.exterior.coords]
            for i in range(1, len(self.coords) - 2): # first is anchor and last is duplicate
                p1, p2, p3 = self.coords[0], self.coords[i], self.coords[i+1]

                w = p1.distance_to(p2) # width and then split by p2
                w1 = abs((p1 - p2).dot(p3 - p2) / w) # p1 -> p2 
                w2 = abs(w - w1)  # p2 -> p3

                signed_tri_area = (p3 - p1).cross(p2 - p1) / 2 # area
                h = 2 * abs(signed_tri_area) / w # height

                p4 = p2 + ((p1 - p2) * w1 / w) # midpoint of p1 -> p3
                cm1 = (p2 + p3 + p4) / 3 # center of mass
                cm2 = (p1 + p3 + p4) / 3

                I1 = w1 * h * ((h * h / 4) + (w1 * w1 / 12)) * rho # moment of inertia around anchor
                I2 = w2 * h * ((h * h / 4) + (w2 * w2 / 12)) * rho
                m1 = 0.5 * w1 * h * rho # mass
                m2 = 0.5 * w2 * h * rho

                I1cm = I1 - (m1 * cm1.distance_to(p3) ** 2)  # parallel axis theorem
                I2cm = I2 - (m2 * cm2.distance_to(p3) ** 2)

                moment_1 = I1cm + m1 * cm1.length() ** 2 # moment of inertia
                moment_2 = I2cm + m2 * cm2.length() ** 2

                if (p1 - p3).cross(p4 - p3) > 0: # sign
                    moment += moment_1
                else:
                    moment -= moment_1
                if (p4 - p3).cross(p2 - p3) > 0:
                    moment += moment_2
                else:
                    moment -= moment_2
                
                moment = abs(moment)
                
            print(f'I_{names[self.current.piece]} = {moment:.2f}')
        
    
    def test_2_event(self):
        pass

    def test_2(self):
        self.current.kinematic()
        self.debug(False)
        self.draw_debug(self.current.shape)
        center = V2(self.current.shape.centroid.coords[0])
        coords = [V2(coord) for coord in self.current.shape.exterior.coords]

        # draw line from center to each coord
        cm = V2(0, 0)
        for coord in coords[1:]:
            pg.draw.line(self.screen, WHITE, center, coord)
            cm += coord
        cm /= len(coords) - 1
        pg.draw.circle(self.screen, RED, self.centroid, 5)

        # for i in range(1, len(coords) - 2): # first is anchor and last is duplicate
        #     p1, p2, p3 = coords[0], coords[i], coords[i+1]
        #     pg.draw.line(self.screen, WHITE, p1, p2)
        #     pg.draw.line(self.screen, WHITE, p2, p3)
        #     pg.draw.line(self.screen, WHITE, p3, p1)

        # for c in self.coords:
        #     pg.draw.circle(self.screen, RED, c, 10)
        



        pg.display.flip()
    
    
    def test_3_init(self):  # centroids and area
        self.pieces = []
        for j, piece in enumerate(PIECES):
            A = 0
            C = V2(0, 0)
            for i in range(len(piece)-1):
                x = V2(piece[i][0], piece[i+1][0])
                y = V2(piece[i][1], piece[i+1][1])

                cross = x.cross(y)
                C += (x + y) * cross
                A += cross

            A /= 2 
            centroid = C / (6 * A)
            self.pieces.append(Piece(j, centroid, A))

            # print(f'{j}) Piece: {names[j]}, Area: {A}, Centroid: {C / (6 * A)}')
        
    def test_3_event(self):
        pass

    def test_3(self):
        self.debug(False)
        for j, piece in enumerate(self.pieces):
            piece.draw(self.screen)
        
        pg.display.flip()

class Shape():

    def __init__(self, id, pos):
        self.id = id
        self.corners = SHAPES[id]
        self.centroid = np.array((0, 1))
        self.corners -= self.centroid
        self.array = np.concatenate(([self.centroid], self.corners))  # First entree is centroid
        self.color = COLORS[id]

        # self.array *= 1000
        # self.array += (W // 2, H // 2)
    
    def translate(self, vector):
        """Translate shape by vector"""
        self.array += vector
    
    def rotate(self, degrees):
        """Rotate the shape by a given degrees around its center."""
        self.array = np.matmul(self.array, np.array([[cos(radians(degrees)), -sin(radians(degrees))], [sin(radians(degrees)), cos(radians(degrees))]]))
            
    def __iter__(self): # iterate over corners
        return iter(self.array[1:])  # Skip centroid
    
    def __str__(self):
        return f'{np.around(self.array[1:], 2)}'
        # return f'Shape: {names[self.id]}, Centroid: {self.centroid}, Count: {len(self.array)}'
    
    def __repr__(self) -> str:
        return names[self.id]
    
    def draw(self, screen):
        gfx.aapolygon(screen, self.shape, self.color)
        gfx.filled_polygon(screen, self.shape, self.color)
        
    
shapes = [Shape(i, (10, 15)) for i in range(7)]

shape = shapes[0]
print(shape.array)


    
quit()
if __name__ == "__main__":
    game = Game()
    game.test(3)
    game.run(debug=True)
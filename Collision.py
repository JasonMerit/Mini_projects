"""Implementation of Reudicble video https://www.youtube.com/watch?v=eED4bSkYCB8&list=LL&index=2&t=16s"""

import pygame as pg
import random, math
from VectorMath import V
import time 

# Settings
FRAMES = 1000
INIT_COUNT = 400
continuous = True      # Lerping ball position to actual position after colliding with wall
elastic = True          # Moementum and energy conservation
min_trans_dist = True   # Minimum translation distance to avoid sticking
detection = 2           # 0: None, 1: Naive, 2: Sweep and Prune, 3: Uniform Grid Partition, 
                        # 4: KD_Tree, 5: Bounding Volume Hierarchy

# pygame screen and clock
pg.init()
# W, H = 800, 400
W, H = 1200, 600
screen = pg.display.set_mode((W, H))
pg.display.set_caption("Collision")
clock = pg.time.Clock()

# Constants
WHITE, GREY, BLACK, RED, GREEN, BLUE, YELLOW = (255, 255, 255), (128, 128, 128), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)
RAINBOW = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (128, 0, 128), (148, 0, 211)]
FPS = 60
dt = 1 / FPS
K = FPS * 5  # Characteristic magnitude

# Variables
ACC = (0, 0)
FRICTION = 0.99  # Energy loss upon collision
T = 2  # KD Tree depth before terminating
seed = 3
random.seed(None)  


# Create the ball
class Ball:
    def __init__(self, pos, vel, acc, radius, color):
        self.p : V = V(pos)
        self.v = V(vel)
        self.a = V(acc)
        self.r = radius
        self.color = color

        self.r2 = self.m  = self.r ** 2
        self.wall_collision = self.collide_wall_continuous if continuous else self.collide_wall_discrete
        
    
    def __repr__(self) -> str:
        return str(self.p)

    @property
    def x(self):
        return self.p.x
    
    @property
    def y(self):
        return self.p.y
    
    @property
    def left(self):
        return self.p.x - self.r
    
    @property
    def right(self):
        return self.p.x + self.r
    
    @property
    def top(self):
        return self.p.y - self.r
    
    @property
    def bot(self):
        return self.p.y + self.r
    
    @property
    def pos(self):
        return self.p.pos
    
    def collides_with(self, other):
        return self.p.dist_squared(other.p) < (self.r + other.r) ** 2

    def draw(self, screen):
        pg.draw.circle(screen, self.color, tuple(self.p), self.r)

    def move(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.v.x *= 0.9
        if keys[pg.K_RIGHT]:
            self.v.x *= 1.1
        if keys[pg.K_UP]:
            self.v.y *= 1.1
        if keys[pg.K_DOWN]:
            self.v.y *= 0.9

    def collide_wall_continuous(self):
        """Continuous collision detection and response using lerping"""
        if self.p.x - self.r < 0:  # Left wall
            tc = (self.r - self.p.x) / self.v.x
            self.p.x += tc * (self.v.x)
            self.v.x *= -1
        if self.p.x + self.r > W: # Right wall
            tc = (W - self.r - self.p.x) / self.v.x      
            self.p.x += tc * (self.v.x)
            self.v.x *= -1
        if self.p.y - self.r < 0: # Top wall
            tc = (self.r - self.p.y) / self.v.y
            self.p.y += tc * (self.v.y)
            self.v.y *= -1
        if self.p.y + self.r > H: # Bottom wall
            tc = (H - self.r - self.p.y) / self.v.y      
            self.p.y += tc * (self.v.y)
            self.v.y *= -1
    
    def collide_wall_discrete(self):
        """Discrete collision detection and response"""
        if self.p.x - self.r < 0: # Left wall
            self.p.x = self.r
            self.v.x *= -1
        elif self.p.x + self.r > W: # Right wall
            self.p.x = W - self.r
            self.v.x *= -1
        if self.p.y - self.r < 0: # Top wall
            self.p.y = self.r
            self.v.y *= -1
        elif self.p.y + self.r > H: # Bottom wall
            self.p.y = H - self.r
            self.v.y *= -1
    
    def update(self):
        # Particle dynamics
        self.wall_collision()
        self.v += self.a * dt
        self.p += self.v * dt
    
    

class Box():
    """Box contains balls and handles collisions between balls.
    Ball handle wall collisions indepently."""

    def __init__(self, acc, count):
        self.acc = acc
        self.count = count
        self.balls = [Ball]
        self.reset()

        detections = [lambda: None, self.naive, self.sweep_and_prune, self.uniform_grid_partition, self.k_d_tree, self.bounding_volume_hierarchy]
        self.ball_collision_detection = detections[detection]
        self.ball_collision_response = self.elastic_collision if elastic else self.inelastic_collision
        self.collision_displacement = self.minimum_translation_distance if min_trans_dist else lambda: None
        
        # Constants for uniform grid partition
        assert(W % 10 == 0 and H % 10 == 0), "W and H must be divisible by 10"
        self.parts = 10
        self.size = W // self.parts
    
    def ball_colliding(self, a, b): return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 <= (a.r + b.r) ** 2

    def reverse(self):
        for self.ball in self:
            self.ball.v *= -1

    def __iter__(self):
        return iter(self.balls)
    
    def get_balls_attr(self):
        return [(ball.r, ball.color) for ball in self]

    def reset(self):
        self.balls.clear()

        # uniformly space the balls
        axis_count = math.ceil(math.sqrt(self.count))
        Pos = []
        for i in range(axis_count):
            for j in range(axis_count):
                Pos.append(((i + 0.5) * W / axis_count, (j + 0.5) * H / axis_count))

        for i in range(self.count):
            pos = Pos[i]
            vel = random.uniform(-1, 1) * K / 4, random.uniform(-1, 1) * K / 4
            r = random.randint(10, 20)
            self.balls.append(Ball(pos, vel, self.acc, r, random.choice(RAINBOW)))
    
    def update(self):
        # Update the balls
        for ball in self:
            ball.move()
            ball.update()
        # Check for ball collisions
        self.ball_collision_detection()
        
        # Draw the screen
        screen.fill(BLACK)
        for ball in self:
            ball.draw(screen)
        pg.display.update()

    def nudge(self):
        for ball in self:
            ball.v.x += random.randint(-1, 1)
            ball.v.y += random.randint(-1, 1)
    
    """ Ball collision detection algorithms """
    def naive(self):
        """Check for ball collisions"""
        for i in range(len(self.balls)):
            a = self.balls[i]
            for j in range(i+1, len(self.balls)):
                b = self.balls[j]
                if self.ball_colliding(a, b):
                    self.ball_collision_response(a, b)

    def sweep_and_prune(self):
        """Sweep and Prune collision detection algorithm on x-axis"""
        # Sort the balls by x position
        balls = sorted(self.balls, key=lambda ball: ball.x)

        # Sweep and prune
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                if balls[j].x - balls[i].x > balls[i].r + balls[j].r:
                    break
                if self.ball_colliding(balls[i], balls[j]):
                    self.ball_collision_response(balls[i], balls[j])
        
    def uniform_grid_partition(self):
        """Uniform Grid Partition collision detection algorithm"""
        # Parition the screen into a grid
        # Place each ball in touching cells
        # Check for collision between balls in the same cell

        # Create grid and populate with balls
        grid = [[[] for _ in range(self.parts)] for _ in range(self.parts)]
        for ball in self.balls:
            # print(ball.p, size)
            # print(ball.p // size)
            c = ball.p // self.size  # Cell containing center
            if c.y > 0 and c.x > 0 and c.y < self.parts-1 and c.x < self.parts-1:
                grid[c.y][c.x].append(ball)

            # get relative position to nearest intersection {1st, 2nd, 3rd, 4th} quadrant
            n = round(ball.p / self.size) * self.size
            R = ball.p - n
            if R.x > 0:
                quadrant = 4 if R.y > 0 else 1
            else:
                quadrant = 3 if R.y > 0 else 2
            
            # depending on the quadrant, check the 3 cells around the intersection
            both = False
            if quadrant == 1: # 1st quadrant, check left and down
                if c.x > 0 and ball.p.x - ball.r < n.x:
                    grid[c.y][c.x-1].append(ball)
                    both = True
                if c.y < self.parts-1 and ball.p.y + ball.r > n.y:
                    grid[c.y+1][c.x].append(ball)
                    both &= True
                if both: # check 3rd quadrant
                    if ball.p.dist_squared(n) < ball.r2:
                        grid[c.y+1][c.x-1].append(ball)
            elif quadrant == 2: # 2nd quadrant, check right and down
                if c.x < self.parts-1 and ball.p.x + ball.r > n.x:
                    grid[c.y][c.x+1].append(ball)
                    both = True
                if c.y < self.parts-1 and ball.p.y + ball.r > n.y:
                    grid[c.y+1][c.x].append(ball)
                    both &= True
                if both: # check 4th quadrant
                    if ball.p.dist_squared(n) < ball.r2:
                        grid[c.y+1][c.x+1].append(ball)
                        
            elif quadrant == 3: # 3rd quadrant, check right and up
                if c.x < self.parts-1 and ball.p.x + ball.r > n.x:
                    grid[c.y][c.x+1].append(ball)
                    both = True
                if c.y > 0 and ball.p.y - ball.r < n.y:
                    grid[c.y-1][c.x].append(ball)
                    both &= True
                if both: # check 1st quadrant
                    if ball.p.dist_squared(n) < ball.r2:
                        grid[c.y-1][c.x+1].append(ball)
            else:          # 4th quadrant, check left and up
                if c.x > 0 and ball.p.x - ball.r < n.x:
                    grid[c.y][c.x-1].append(ball)
                    both = True
                if c.y > 0 and ball.p.y - ball.r < n.y:
                    grid[c.y-1][c.x].append(ball)
                    both &= True
                if both: # check 2nd quadrant
                    if ball.p.dist_squared(n) < ball.r2:
                        grid[c.y-1][c.x-1].append(ball)

        # Check for collisions wihin each cell
        for row in grid:
            for balls in row:
                if len(balls) < 2:
                    continue
                for i, a in enumerate(balls):
                    for b in balls[i+1:]:
                        if self.ball_colliding(a, b):
                            self.ball_collision_response(a, b)
    
    def k_d_tree(self):

        kd = KDTree(self.balls)
        collections = kd.get_potentials()
        for balls in collections:
            
            for i, a in enumerate(balls):
                for b in balls[i+1:]:
                    if self.ball_colliding(a, b):
                        self.ball_collision_response(a, b)

    def bounding_volume_hierarchy(self):
        """Bounding Volume Hierarchy collision detection algorithm"""
        bvh = BVH(self.balls)
        for a, b in bvh.get_collisions():
            self.ball_collision_response(a, b)

    """ Ball collision response algorithms """
    def elastic_collision(self, a, b):
        """Elastic collision between two balls"""
        # Calculate relative velocity
        vab = b.v - a.v

        # Calculate relative position
        rab = b.p - a.p

        # Calculate magnitude of impulse
        j = (2 * a.m * b.m) / (a.m + b.m) * vab.dot(rab) / rab.norm()

        # Apply impulse
        a.v += rab.unit() * j / a.m
        b.v -= rab.unit() * j / b.m
        
        # Friction
        a.v *= 0.99
        b.v *= 0.99
        self.collision_displacement(a, b)
    
    def inelastic_collision(self, a, b):
        """Inelastic collision between two balls"""
        a.v, b.v = b.v, a.v
        self.collision_displacement(a, b)

    def minimum_translation_distance(self, a, b):
        # Minimum Translation Distance (MTD) collision response
        delta = a.p - b.p
        dist = delta.norm()
        mtd = delta * (a.r + b.r - dist) / dist

        # resolve intersection
        a.p += mtd * (a.m / (a.m + b.m))
        b.p -= mtd * (b.m / (a.m + b.m))


        


class KDTree:
    def __init__(self, balls, depth=0):
        self.depth = depth
        self.axis = depth % 2
        self.balls = balls
        self.left = None
        self.right = None
        self.ball = None
        self.D = ["Vertical", "Horizontal"]

        # terminating condition
        if self.depth < T:
            self.build()
    
    def build(self):
        if len(self.balls) < 2:
            return
        
        # sort balls by axis
        balls = sorted(self.balls, key=lambda ball: ball.p[self.axis])
        med = len(balls) // 2

        # save median and split balls into two groups
        self.ball = balls[med]
        self.left = KDTree(balls[:med], self.depth + 1)
        self.right = KDTree(balls[med+1:], self.depth + 1)
       
    def get_potentials(self):
        potentials = []
        def traverse(tree):
            if tree.left:
                traverse(tree.left)
                traverse(tree.right)
            else:
                if len(tree.balls) > 1:
                    potentials.append(tree.balls)

        traverse(self)
        return potentials


class BVH:
    "Skewed to the right"

    def __init__(self, balls, parent=None, rect=None, depth=0):
        self.balls = balls
        self.parent = parent
        self.rect: pg.Rect = rect
        self.depth = depth
        self.ball : Ball = None
        self.left = None
        self.right = None

        self.build_tree(balls, depth % 2)
    
    def build_tree(self, balls, axis):
        if len(balls) == 1:
            self.ball = balls[0]
            return
        
        balls = sorted(balls, key=lambda ball: ball.p[axis])
        mid = len(balls) // 2

        # encompass each groups with a single rectangle
        # Check if either group is singular for easier rect calculation
        Ab1, Ab2 = balls[0], balls[mid-1]
        Bb1, Bb2 = balls[mid], balls[-1]

        # singular groups
        if Bb1 == Bb2:
            Ax, Ay, Aw, Ah = Ab1.left, Ab1.top, Ab1.r * 2, Ab1.r * 2
            Bx, By, Bw, Bh = Bb1.left, Bb1.top, Bb1.r * 2, Bb1.r * 2
        # B contains two balls
        elif Ab1 == Ab2:
            Ax, Ay, Aw, Ah = Ab1.left, Ab1.top, Ab1.r * 2, Ab1.r * 2
            
            if axis == 0:
                Bx = Bb1.left
                By = min(ball.top for ball in balls[mid:])
                Bw = Bb2.right - Bx
                Bh = max(ball.bot for ball in balls[mid:]) - By
            else:
                Bx = min(ball.left for ball in balls[mid:])
                By = Bb1.top
                Bw = max(ball.right for ball in balls[mid:]) - Bx
                Bh = Bb2.bot - By
        # determine rect dimensions
        else:
            if axis == 0:
                Ax = Ab1.left
                Ay = min(ball.top for ball in balls[:mid])
                Aw = Ab2.right - Ax
                Ah = max(ball.bot for ball in balls[:mid]) - Ay

                Bx = Bb1.left
                By = min(ball.top for ball in balls[mid:])
                Bw = Bb2.right - Bx
                Bh = max(ball.bot for ball in balls[mid:]) - By
            else:
                Ax = min(ball.left for ball in balls[:mid])
                Ay = Ab1.top
                Aw = max(ball.right for ball in balls[:mid]) - Ax
                Ah = Ab2.bot - Ay

                Bx = min(ball.left for ball in balls[mid:])
                By = Bb1.top
                Bw = max(ball.right for ball in balls[mid:]) - Bx
                Bh = Bb2.bot - By
        
        left_rect = pg.Rect(Ax, Ay, Aw, Ah)
        right_rect = pg.Rect(Bx, By, Bw, Bh)

        self.left = BVH(balls[:mid], self, left_rect, self.depth+1)
        self.right = BVH(balls[mid:], self, right_rect, self.depth+1)
  
    def get_collisions(self):
        yield from self.left.intersects_with(self.right)
    
    # def bigger_than(self, rect: pg.Rect):
    #     return self.rect.width * self.rect.height > rect.width * rect.height
    
    def intersects_with(self, other: 'BVH'):
        """Recursively call from get_collisions"""
        # Check own children
        if self.left:
            yield from self.left.intersects_with(self.right)
        if other.left:
            yield from other.left.intersects_with(other.right)

        # Return if rects not intersecting
        if not self.rect.colliderect(other.rect):
            return 
        
        if self.ball and other.ball:
            if self.ball.collides_with(other.ball):
                yield (self.ball, other.ball)
            return
        
        if other.ball and self.ball is None:
            yield from self.left.intersects_with(other)
            yield from self.right.intersects_with(other)
            return 
        
        if self.ball and other.ball is None:
            yield from other.left.intersects_with(self)
            yield from other.right.intersects_with(self)
            return 
        
        # Both this and other have children
        yield from self.left.intersects_with(other.left)
        yield from self.left.intersects_with(other.right)
        yield from self.right.intersects_with(other.left)
        yield from self.right.intersects_with(other.right)
    

def compute_render(frames: int):
    """Pre-render the balls for the animation"""
    print("Pre-rendering...")
    t0 = time.time()
    box = Box(ACC, INIT_COUNT)
    attr = box.get_balls_attr()
    rendering = []
    for _ in range(frames):
        frame = []
        box.ball_collision_detection()

        for ball in box:
            ball.update()
            frame.append(ball.pos)
        rendering.append(frame)
    
    print(f"Render time: {time.time() - t0:.2f}s")
    return rendering, attr

def play_render(render, attr):
    """Play the pre-rendered animation"""
    print("Playing...")
    t0 = time.time()

    for frame in render:
        screen.fill(BLACK)
        for pos, (r, c) in zip(frame, attr):
            pg.draw.circle(screen, c, pos, r)
        pg.display.flip()
        process_events(pg.event.get())
        clock.tick(FPS)
    print(f"Play time: {time.time() - t0:.2f}s")
    

def process_events(events, box=None):
    for event in events:
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()
            if event.key == pg.K_p:
                # pause
                while True:
                    for event in pg.event.get():
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_p:
                                # unpause
                                return
                        elif event.type == pg.QUIT:
                            pg.quit()
                            quit()
            
            if box:
                if event.key == pg.K_r:
                    box.reset()
                elif event.key == pg.K_SPACE:
                    box.nudge()
                elif event.key == pg.K_f:                
                    box.reverse()
                elif event.key == pg.K_c:
                    global continuous
                    continuous = not continuous

def main():
    box = Box(ACC, INIT_COUNT)
    while True:
        clock.tick(FPS)
        process_events(pg.event.get(), box)
        box.update()

if __name__ == "__main__":
    if not FRAMES:
        main()
    else:
        render, attr = compute_render(FRAMES)
        play_render(render, attr)

    
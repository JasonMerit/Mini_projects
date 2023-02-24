import pygame as pg
import numpy as np
import random
from math import atan2

"""
FEATURES:
    - Random polygon generation (RPG) Growth and space partioning
    - Triangulation of simple polygons (ear-clipping)
    - Three-coloring of simple polygons 

CONCEPTS:
    - Convex vertex: Interior angle of polygon < 180 degrees
    - Convex hull: The smallest convex region enclosing a specified group of points. 

ASSUMPTIONS:
    - Polygon is simple (no self-intersections)
    - Polygon is counter-clockwise (marked *C where this is assumed)    

SOURCES:
    - Random simple polygon: https://observablehq.com/@tarte0/generate-random-simple-polygon
    - More random random simple polygon: 
    - Ear-clipping: https://www.youtube.com/watch?v=QAdfkylpYwc&ab_channel=Two-BitCoding
    - Art gallery problem (nlogn) and 3 coloring and y-monotone (sweepline algorithm): https://www.youtube.com/watch?v=pmVn5KylI1Q&ab_channel=AlgorithmsLab
    - Linear time algorithm Chazelle: linear-poly-tri.pdf under downloads

OVER THE TOP IDEAS:
    - Make sick animations that zooms in the convex hull when partitioning, where the line becomes the bottom of screen. 

"""

WHITE, BLACK, GREY = (200, 200, 200), (50, 50, 50), (128, 128, 128)
RED, GREEN, BLUE = (200, 20, 20), (100, 200, 20), (0, 100, 200)
YELLOW, PURPLE, CYAN = (200, 200, 0), (200, 0, 200), (0, 200, 200)
def random_color(): return random.randint(60, 255), random.randint(60, 255), random.randint(60, 255)

POLYGON = [[343, 342], [204, 367], [426, 513], [504, 289], [584, 520], [659, 355], [467, 198], [407, 307], [258, 182]]

class Display():

    W, H = 800, 600
    frames = []
    frame = -1
    def __init__(self) -> None:
        pg.init()
        pg.display.set_caption("Polygon Triangulation - [0]")
        self.screen = pg.display.set_mode((self.W, self.H))        
        pg.font.init()
        self.font = pg.font.SysFont('Comic Sans MS', 30)
    
    def wipe(self):
        self.screen.fill(BLACK)
        self.update()
    
    def next(self):
        if self.frame == len(self.frames)-1: return
        self.frame += 1
        self.screen.blit(self.frames[self.frame], (0, 0))
        self.update(False)
    
    def back(self):
        if self.frame == 0: return
        self.frame -= 1
        self.screen.blit(self.frames[self.frame], (0, 0))
        self.update(False)
    
    def first(self):
        self.frame = 0
        self.screen.blit(self.frames[self.frame], (0, 0))
        self.update(False)
    
    def last(self):
        self.frame = len(self.frames)-1
        self.screen.blit(self.frames[self.frame], (0, 0))
        self.update(False)
    
    def update(self, new_frame=True):
        pg.display.update()
        if new_frame:
            self.frames.append(self.screen.copy())
            self.frame += 1
            step()
        pg.display.set_caption(f"Polygon Triangulation - [{self.frame}]")

    def draw_polygon(self, points, color=None, label=False):
        if color is None:
            color = random.choice([RED, GREEN, BLUE])
        pg.draw.polygon(self.screen, color, points)

        if label:# Draw indices of points
            for i, point in enumerate(points):
                text = self.font.render(str(i), False, RED)
                self.screen.blit(text, point)
        self.update()
    
    def draw_line(self, p1, p2, color=RED, width=3, head=False):
        pg.draw.line(self.screen, color, p1, p2, width)
        
        if head:
            angle = atan2(p1[1] - p2[1], p1[0] - p2[0])
            k = width * 5
            pg.draw.polygon(self.screen, color, ((p2[0] + k * np.cos(angle - np.pi / 6), p2[1] + k * np.sin(angle - np.pi / 6)),
                                                (p2[0] + k * np.cos(angle + np.pi / 6), p2[1] + k * np.sin(angle + np.pi / 6)),
                                                p2))
                                            
        self.update()
    
    def draw_points(self, points, color=None, radius=5, label=False):
        if color is None:
            color = random_color()
        for i, point in enumerate(points):
            pg.draw.circle(self.screen, color, point, radius)
            if label:
                text = self.font.render(str(i), False, color)
                self.screen.blit(text, point)
        self.update()
    
    def draw_path(self, points, color=RED):
        for i in range(len(points) - 1):
            self.draw_line(points[i], points[i + 1], color=color, width=2, head=True)
        self.update()
    
    def draw_text(self, text, pos, color=RED):
        text = self.font.render(text, False, color)
        self.screen.blit(text, pos)
        self.update()

class Polygon():

    def create_polygon(self, N, algorithm=2):
        """0: Random until true, 1: Angle sorting, 2: Space partitioning"""
        return [self.random_polygon, self.random_simple_polygon, self.space_partitioning][algorithm](N)        

    def is_left(self, a, b, p):  # Or determinant of [a, b, p]
        """Return True if p is left of the line a -> b"""
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < 0
    
    def sample_line_point(self, a, b):
        """Return a random point on the line a -> b"""
        display.draw_line(a, b, GREEN, head=True)
        k = random.random()
        return (a[0] + k * (b[0] - a[0]), a[1] + k * (b[1] - a[1]))

    def partition(self, points, was_left=True):
        """
        Partition points into two sets.
        The line partition is defined by tail -> head, where tail is sampled from the 
        prior line partition (first and last points) and head = s'
        While partitioning head is removed and added once returning as left + [head] + right.
        Note that tail is not an actual point in the polygon, but a point on the line partition, so is not included in return.
        Note again that tail is needed in the next partition, so must be included in the start and end of left and right respectively.
        How will the distinction be made when removing? A was_left flag?
        Given the flag, [head] is removed from either end accordingly. 
        It will be tricky to ensure consistent ordering of points in the polygon.
        """
        
        if len(points) <= 4:
            return points
            display.draw_points(points, label=True)
        # display.draw_points(points, RED)
        # 1) Pick random point
        head = random.choice(points[1:-1])

        # 2) Pick random point on line and connect to sp
        tail = self.sample_line_point(points[0], points[-1])
        # display.draw_line(tail, head, RED, head = True)

        # 3) Partition points into two sets divided by the line sp -> sl
        subsets = {1: [], 0: []}
        [subsets[self.is_left(tail, head, p)].append(p) for p in points]
        left, right = subsets.values()
        # left.append(head)
        # display.draw_path(left, CYAN)
        # display.draw_points(left, BLUE)
        # display.draw_path(left, color=GREEN)
        # display.draw_path(right, color=BLUE)
        # display.draw_path(right, YELLOW)

        # 4) Recursively partition the two subsets
        return self.partition(left) + self.partition(right)

    def space_partitioning(self, N, min_x=50, max_x=750, min_y=50, max_y=550):
        points = [(random.randint(min_x, max_x), random.randint(min_y, max_y)) for _ in range(N)]
        display.draw_points(points, WHITE, label=True)

        # pick two random unique elements
        tail, head = random.sample(points, 2)
        display.draw_line(tail, head, WHITE, head=True)

        # Partition the remaining points into two sets divided by the line tail -> head
        subsets = {1: [], 0: []}
        [subsets[self.is_left(tail, head, p)].append(p) for p in points]
        left, right = subsets.values()
        left.append(head)
        left.insert(0, tail)
        # display.draw_path(left)
        # return []
        # display.draw_points(right)
        return list(set(self.partition(left) + self.partition(right, False)))



    # Get the angle of the vector p to origin
    def get_angle(self, p): return atan2(p[1], p[0])

    def random_simple_polygon(self, N=3, min_x=50, max_x=750, min_y=50, max_y=550):
        """Create simple counter-clockwise polygon with N vertices"""
        points = [(random.randint(min_x, max_x), random.randint(min_y, max_y)) for _ in range(N)]
        mean_point = np.mean(points, axis=0)

        points = [(p[0] - mean_point[0], p[1] - mean_point[1]) for p in points]
        points = sorted(points, key=self.get_angle)
        points = [(p[0] + mean_point[0], p[1] + mean_point[1]) for p in points]
        
        # assert self.is_simple(points), "Polygon is not simple"
        return points[::-1]  # reverse to get counter-clockwise
        
    def random_polygon(self, N=3, min_x=50, max_x=750, min_y=50, max_y=550):
        points = [(random.randint(min_x, max_x), random.randint(min_y, max_y)) for _ in range(N)]

        # return points
        while not self.is_simple(points):
            points = [(random.randint(min_x, max_x), random.randint(min_y, max_y)) for _ in range(N)]

        # TODO: Check if the polygon is counter-clockwise
        if not self.is_counter_clockwise(points):
            points = points[::-1]
        return np.array(points)
    
    def is_counter_clockwise(self, points):
        return True
    
    def is_simple(self, points):
        # Check if the polygon is simple (no self-intersections)
        N = len(points)
        for i in range(N):
            for j in range(i+1, N):
                if i == 0 and j == N-1:
                    continue
                if self.intersect(points[i], points[(i+1)%N], points[j], points[(j+1)%N]):
                    return False
        return True

    def ccw(self, p1, p2, p3):
        # Check if p3 is on the left of the line p1-p2
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        return (y3-y1)*(x2-x1) > (y2-y1)*(x3-x1)

    def intersect(self, p1, p2, p3, p4):
        # Check if the line p1-p2 intersects with the line p3-p4
        return self.ccw(p1, p3, p4) != self.ccw(p2, p3, p4) and self.ccw(p1, p2, p3) != self.ccw(p1, p2, p4)

# the determinant of the matrix [p1, p2, p3]
def det(a, b, c): return (b[0] - a[0]) * (c[1] - b[1]) - (c[0] - b[0]) * (b[1] - a[1])

def is_ear(polygon, i):
    # Assumes convex vertex i
    N = len(polygon)
    p1, p2, p3 = polygon[i-1], polygon[i], polygon[(i+1)%N]
    for j in range(N):
        if j == i-1 or j == i or j == (i+1)%N: # skip p1, p2, p3
            continue
        # check if triangle p1, p2, p3 contains polygon[j]
        if det(p1, p2, polygon[j]) < 0 and det(p2, p3, polygon[j]) < 0 and det(p3, p1, polygon[j]) < 0: # *C for < 0
            return False
    return True

def identify_vertices(polygon):
    convex, reflex= [], []
    N = len(polygon)
    for i in range(N):
        p1, p2, p3 = polygon[i-1], polygon[i], polygon[(i+1)%N]
        if det(p1, p2, p3) > 0:  # *C
            reflex.append(i)
        else:
            convex.append(i)
    
    ears = [ear for ear in convex if is_ear(polygon, ear)]

    x = 10
    display.draw_text("Convex: " + str(convex), (x, 10))
    txt = "Ears:     " + str(ears)
    display.draw_text(txt, (x, 40))
    # txt = "Reflex:  " + str(reflex)

    return convex, reflex, ears

def is_convex(polygon, i):
    p1, p2, p3 = polygon[i-1], polygon[i], polygon[(i+1)%len(polygon)]
    return det(p1, p2, p3) < 0  # *C

def ear_clipping(polygon: list):
    # Iterate over all vertices
    # Determine if vertex is convex and ear
    # If so, remove vertex and add triangle
    triangles = []
    n = len(polygon)
    i = 0
    while n > 3:
        if is_convex(polygon, i) and is_ear(polygon, i):
            triangles.append([polygon[i-1], polygon[i], polygon[(i+1)%n]])
            polygon.pop(i)
            n = len(polygon)
        i = (i+1)%n

    triangles.append(polygon)
    return triangles
    

def main():
    display.wipe()

    # 0) Generate random polygon    
    polygon = POLYGON
    polygon = Polygon.create_polygon(8, 1)
    # print(polygon)
    # print(list(set(polygon)))
    # display.draw_path(polygon, YELLOW)
    # display.draw_points(polygon, WHITE, label=True)
    display.draw_polygon(polygon, CYAN)
    pg.display.update()
    # return
    # 1) Identify vertices from start
    identify_vertices(polygon)

    triangles = []
    # 2.1) Triangulate with ear clipping
    triangles = ear_clipping(polygon)

    # 2.2) Tringulate in log(n) time

    # 2.3) Triangulate in n time

    # 3) Draw triangles
    for t in triangles:
        # display.draw_line(t[0], t[-1], RED)
        display.draw_polygon(t)
    pg.display.update()

def update_fps(delta):
    global FPS
    FPS += delta

def step():
    process_input()
    clock.tick(FPS)

def pause():
    while True:
        event = pg.event.wait()
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                quit()
            if event.key == pg.K_p:
                return

def process_input():
    global FPS
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                quit()
            if event.key == pg.K_p:
                pause()
            if event.key == pg.K_SPACE:
                main()
            if event.key == pg.K_DOWN:
                if FPS < 2: return
                update_fps(-1)
            elif event.key == pg.K_UP:
                update_fps(1)
            
            # Frame navigation
            if event.key == pg.K_LEFT:
                display.first() if pg.key.get_mods() & pg.KMOD_SHIFT else display.back()
            elif event.key == pg.K_RIGHT:
                display.last() if pg.key.get_mods() & pg.KMOD_SHIFT else display.next()

        
        if event.type == pg.MOUSEBUTTONDOWN:
            print(event.pos)

if __name__ == "__main__":
    random.seed(1435235) # 3
    FPS = 5
    N = 10
    display = Display()
    Polygon = Polygon()
    
    clock = pg.time.Clock()
    
    main()
    while True:
        process_input()
import pygame as pg
import numpy as np
import random
from math import atan2

"""
Assumptions:
    - Polygon is simple
    - Polygon is counter-clockwise (not enforced) (Clockwise with POLYGON following YT)

SOURCES:
    - Random simple polygon: https://observablehq.com/@tarte0/generate-random-simple-polygon
    - Ear-clipping: https://www.youtube.com/watch?v=QAdfkylpYwc&ab_channel=Two-BitCoding
    - Art gallery problem (nlogn): https://www.youtube.com/watch?v=pmVn5KylI1Q&ab_channel=AlgorithmsLab
    - Linear time algorithm Chazelle: linear-poly-tri.pdf under downloads

"""

WHITE, BLACK, GREY = (200, 200, 200), (50, 50, 50), (128, 128, 128)
RED, GREEN, BLUE = (200, 0, 0), (0, 200, 0), (0, 0, 200)
YELLOW, PURPLE, CYAN = (200, 200, 0), (200, 0, 200), (0, 200, 200)
POLYGON = np.array([[258, 182],
                    [407, 307],
                    [467, 198],
                    [659, 355],
                    [584, 520],
                    [504, 289],
                    [426, 513],
                    [204, 367],
                    [343, 342]])
POLYGON = POLYGON[::-1]                
                    
class Display():

    W, H = 800, 600
    def __init__(self) -> None:
        pg.init()
        pg.display.set_caption("Polygon Triangulation")
        self.screen = pg.display.set_mode((self.W, self.H))        
        pg.font.init()
        self.font = pg.font.SysFont('Comic Sans MS', 30)
    
    def wipe(self):
        self.screen.fill(BLACK)
    
    def draw_polygon(self, points, color=None, with_index=False):
        if color is None:
            color = random.choice([RED, GREEN, BLUE])
        pg.draw.polygon(self.screen, color, points)

        if with_index:# Draw indices of points
            for i, point in enumerate(points):
                text = self.font.render(str(i), False, RED)
                self.screen.blit(text, point)
        pg.display.update()
    
    def draw_line(self, p1, p2, color, width=2):
        pg.draw.line(self.screen, color, p1, p2, width)
        pg.display.update()
    
    def draw_points(self, points, color=WHITE, radius=5, label=False):
        for i, point in enumerate(points):
            pg.draw.circle(self.screen, color, point, radius)
            if label:
                text = self.font.render(str(i), False, RED)
                self.screen.blit(text, point)
        pg.display.update()
    
    def draw_text(self, text, pos, color=RED):
        text = self.font.render(text, False, color)
        self.screen.blit(text, pos)
        pg.display.update()

class Polygon():
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
        if det(p1, p2, polygon[j]) > 0 and det(p2, p3, polygon[j]) > 0 and det(p3, p1, polygon[j]) > 0:
            return False
    return True

def identify_vertices(polygon):
    convex, reflex= [], []
    N = len(polygon)
    for i in range(N):
        p1, p2, p3 = polygon[i-1], polygon[i], polygon[(i+1)%N]
        # v1 = p2 - p1
        # v2 = p3 - p2
        # if np.linalg.det([v1, v2]) < 0:  # Clockwise
        if det(p1, p2, p3) > 0:  # Counter-clockwise
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
    # p1, p2, p3 = triangle
    # v1 = p2 - p1
    # v2 = p3 - p2
    # return np.linalg.det([v1, v2]) > 0  # Clockwise
    return det(p1, p2, p3) > 0  # Clockwise

def ear_clipping(polygon, render=False):
    # Iterate over all vertices
    # Determine if vertex is convex and ear
    # If so, remove vertex and add triangle
    triangles = []
    # vertex = polygon
    # for i in range(N):
    i = 0
    polygon = np.array(polygon)
    while len(polygon) > 3:
        if is_convex(polygon, i) and is_ear(polygon, i):
            print(i)
            triangle = [polygon[i-1], polygon[i], polygon[(i+1)%N]]            
            triangles.append(triangle)
            polygon = np.delete(polygon, i, axis=0)  # Gross
            # polygon.pop(i)

            if render:
                display.draw_polygon(triangle)
                clock.tick(FPS)
            
        i = (i+1)%len(polygon)
    if render:
        display.draw_polygon(polygon)
    triangles.append(polygon)

    return triangles
    

def main():
    display.wipe()
    clock.tick(FPS)
    
    polygon = POLYGON
    
    # Reverse order
    # polygon = Polygon.random_simple_polygon(N)
    triangles = []
    # polygon = polygon[::-1]
    
    display.draw_polygon(polygon, WHITE, True)

    # 1) Identify vertices from start
    convex, reflex, ears = identify_vertices(polygon)

    # 2.1) Triangulate with ear clipping
    # triangles = ear_clipping(polygon)

    # 2.2) Tringulate in log(n) time

    # 2.3) Triangulate in n time

    # 3) Draw triangles
    for t in triangles:
        display.draw_line(t[0], t[-1], RED)
        # display.draw_polygon(t)
        clock.tick(FPS)
    pg.display.update()


if __name__ == "__main__":
    random.seed(39442222189) # 3
    display = Display()
    Polygon = Polygon()
    
    clock = pg.time.Clock()
    FPS = 2

    N = 10
    ORIGIN = np.array([display.W/2, display.H/2])
    

    main()
    keks = []
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                
                if event.key == pg.K_SPACE:
                    main()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                keks.append(list(event.pos))
                print(np.array(keks))
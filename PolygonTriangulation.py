import pygame as pg
import numpy as np
import random

"""
Assumptions:
    - Polygon is simple
    - Polygon is counter-clockwise (not enforced) (Clockwise with POLYGON following YT)

SOURCES:
    - https://www.youtube.com/watch?v=QAdfkylpYwc&ab_channel=Two-BitCoding

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
                    
 
 


class Display():

    def __init__(self) -> None:
        pg.init()
        pg.display.set_caption("Polygon Triangulation")
        self.screen = pg.display.set_mode((800, 600))
        self.screen.fill(BLACK)
        pg.font.init()
        self.font = pg.font.SysFont('Comic Sans MS', 30)
    
    def draw_polygon(self, points, color=None, with_index=False):
        if color is None:
            color = random.choice([RED, GREEN, BLUE])
        pg.draw.polygon(self.screen, color, points)

        if with_index:# Draw indices of points
            for i, point in enumerate(points):
                text = self.font.render(str(i), False, RED)
                self.screen.blit(text, point)
        pg.display.update()
    
    def draw_line(self, p1, p2, color):
        pg.draw.line(self.screen, color, p1, p2, 4)
        pg.display.update()

class Polygon():
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
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        return self.ccw(p1, p3, p4) != self.ccw(p2, p3, p4) and self.ccw(p1, p2, p3) != self.ccw(p1, p2, p4)

def det(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) - (c[0] - b[0]) * (b[1] - a[1])

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
        v1 = p2 - p1
        v2 = p3 - p2
        if np.linalg.det([v1, v2]) < 0:  # Clockwise
            reflex.append(i)
        else:
            convex.append(i)
    
    ears = [ear for ear in convex if is_ear(polygon, ear)]

    txt = "Convex: " + str(convex)
    text = display.font.render(txt, False, RED)
    display.screen.blit(text, (50, 50))
    txt = "Reflex: " + str(reflex)
    text = display.font.render(txt, False, RED)
    display.screen.blit(text, (50, 100))
    txt = "Ears: " + str(ears)
    text = display.font.render(txt, False, RED)
    display.screen.blit(text, (50, 150))

    return convex, reflex, ears

def is_convex(polygon, i):
    p1, p2, p3 = polygon[i-1], polygon[i], polygon[(i+1)%len(polygon)]
    # p1, p2, p3 = triangle
    v1 = p2 - p1
    v2 = p3 - p2
    return np.linalg.det([v1, v2]) > 0  # Clockwise

def triangulate(polygon):
    # Iterate over all vertices
    # Determine if vertex is convex and ear
    # If so, remove vertex and add triangle

    triangles = []
    N = len(polygon)
    # vertex = polygon
    # for i in range(N):
    i = 0
    while len(polygon) > 3:
        if is_convex(polygon, i) and is_ear(polygon, i):
            # Draw triangle
            triangle = [polygon[i-1], polygon[i], polygon[(i+1)%N]]
            display.draw_polygon(triangle)
            # display.draw_line(triangle[0], triangle[-1], RED)
            polygon = np.delete(polygon, i, axis=0)  # Gross
            triangles.append(triangle)
        i = (i+1)%len(polygon)
    triangles.append(polygon)
    display.draw_polygon(polygon, YELLOW)
    

def main():
    clock.tick(FPS)
    polygon = POLYGON#Polygon.random_polygon(6)
    display.draw_polygon(polygon, WHITE, True)

    # identify vertices from start
    # convex, reflex, ears = identify_vertices(polygon)

    # triangulate
    triangulate(polygon)
    pg.display.update()


if __name__ == "__main__":
    random.seed(3)
    display = Display()
    Polygon = Polygon()
    clock = pg.time.Clock()
    FPS = 2
    

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
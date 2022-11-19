import numpy as np
from typing import List, Tuple

class Vec():
    """A 2D vector class."""
    def __init__(self, x, y=None) -> None:
        if y is None:
            self.x, self.y = x
        else:
            self.x, self.y = x, y
    
    def __repr__(self) -> str:
        return f"Vec({self.x}, {self.y})"
    
    @property
    def t(self) -> Tuple[int, int]:
        return self.x, self.y
    
    def draw(self, color: Tuple[int, int, int], radius: int = 5) -> None:
        """Draw a circle at the vector's position."""
        pg.draw.circle(screen, color, self.t, radius)
    
    def dot(self, other: 'Vec') -> float:
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vec') -> float:
        return self.x * other.y - self.y * other.x
    
    def rotate(self, degr: float) -> 'Vec':
        """Rotate the vector by degr degrees."""
        rad = radians(degr)
        self.x = self.x * cos(rad) - self.y * sin(rad)
        self.y = self.x * sin(rad) + self.y * cos(rad)
    
    def rotate_around(self, point: 'Vec', degr: float) -> 'Vec':
        """Rotate the vector around point by degr degrees."""
        rad = - radians(degr)
        x, y = self.x - point.x, self.y - point.y
        self.x = x * cos(rad) - y * sin(rad) + point.x
        self.y = x * sin(rad) + y * cos(rad) + point.y

    def __add__(self, other) -> 'Vec':
        if isinstance(other, tuple):
            return Vec(self.x + other[0], self.y + other[1])
        return Vec(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vec') -> 'Vec':
        if isinstance(other, tuple):
            return Vec(self.x - other[0], self.y - other[1])
        return Vec(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other: float) -> 'Vec':
        return Vec(self.x * other, self.y * other)
    
    def __rmul__(self, other: float) -> 'Vec':
        return Vec(self.x * other, self.y * other)

class Line():
    """A line class."""
    
    def __init__(self, start: Vec, end: Vec) -> None:
        self.start, self.end = start, end
    
    def __repr__(self) -> str:
        return f"Line({self.start}, {self.end})"
    
    def draw(self, color, width: int = 2) -> None:
        """Draw the line on the screen."""
        pg.draw.line(screen, color, self.start.t, self.end.t, width)
    
    def intersects(self, other: "Line") -> bool:
        """Check if the line intersects with another line."""
        # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        p = self.start
        r = self.end - self.start
        q = other.start
        s = other.end - other.start
        if r.cross(s) == 0:
            return False
        t = (q - p).cross(s) / r.cross(s)
        u = (q - p).cross(r) / r.cross(s)
        return 0 <= t <= 1 and 0 <= u <= 1

    def intersection(self, other: "Line") -> Vec:
        """Return the intersection point of the line and another line."""
        # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        p = self.start
        r = self.end - self.start
        q = other.start
        s = other.end - other.start
        t = (q - p).cross(s) / r.cross(s)
        return p + r * t

class Block():
    """Rectangle that can rotate. 
    Defined by two vector sides and their shared origin.
    ----->
    |
    |
    |"""
    def __init__(self, x, y, w, h):
        """x, y define top left corner."""
        self.x, self.y = x, y
        self.w, self.h = w, h

        self.a, self.b = Vec(x + w, y), Vec(x, y)
        self.c, self.d = Vec(x, y + h), Vec(x + w, y + h)
        self.lines = [Line(self.a, self.b), Line(self.b, self.c), Line(self.c, self.d), Line(self.d, self.a)]

        self.surf_og = pg.Surface((w, h))
        self.surf_og.set_colorkey(BLACK)
        self.surf_og.fill(WHITE)

        self.surf = self.surf_og.copy()
        self.surf.set_colorkey(BLACK)
        self.rect = self.surf.get_rect()
        self.rect.center = (x+w//2, y+h//2)

        self.angle = 0

    def __repr__(self) -> str:
        return f"Block({self.x}, {self.y}, {self.w}, {self.h})"

    def rotate(self, degr: float) -> None:
        old_center = self.rect.center
        self.angle = (self.angle + degr) % 360
        new_surf = pg.transform.rotate(self.surf_og, self.angle)
        self.rect = new_surf.get_rect()
        self.rect.center = old_center
        self.surf = new_surf

        point = Vec(old_center[0], old_center[1])
        self.a.rotate_around(point, degr)
        self.b.rotate_around(point, degr)
        self.c.rotate_around(point, degr)
        self.d.rotate_around(point, degr)
    
    def rotate_around(self, point: Vec, degr: float) -> None:
        old_center = self.rect.center
        self.angle = (self.angle + degr) % 360
        # new_surf = pg.transform.rotate(self.surf_og, self.angle)
        new_surf = pg.transform.rotozoom(self.surf_og, self.angle, 1)
        rotated_offset = Vec(new_surf.get_rect().center) - Vec(self.surf_og.get_rect().center)

        self.rect = new_surf.get_rect(center=(point+rotated_offset).t)
        # self.rect.center = old_center
        self.surf = new_surf

        self.a.rotate_around(point, degr)
        self.b.rotate_around(point, degr)
        self.c.rotate_around(point, degr)
        self.d.rotate_around(point, degr)
    
    def intersects(self, other: 'Block' = None):
        """Check if intersects with other block."""
        intersect = []
        for line in self.lines:
            for line2 in other.lines:
                if line.intersects(line2):
                    intersect.append((line, line2))
        return intersect
    
    def translate(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.center = (self.x + self.w/2, self.y + self.h/2)

        self.a += Vec(dx, dy)
        self.b += Vec(dx, dy)
        self.c += Vec(dx, dy)
        self.d += Vec(dx, dy)
        self.lines = [Line(self.a, self.b), Line(self.b, self.c), Line(self.c, self.d), Line(self.d, self.a)]

    def test(self, other):
        """Check if the rectangle intersects with another rectangle."""
        intersect = self.intersects(other)
        if intersect:
            for line, line2 in intersect:
                line.draw(RED)
                line2.draw(RED)
                point = line.intersection(line2)
                point.draw(RED, 5)

    def draw(self):
        screen.blit(self.surf, self.rect)
        for line in self.lines:
            line.draw(GREEN)
        # pg.draw.rect(screen, RED, self.rect, 2)

        

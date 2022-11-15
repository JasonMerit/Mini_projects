<<<<<<< Updated upstream
import numpy as np
import psutil

print(psutil.sensors_temperatures())
=======
class Vec2D():
    """Helper class for flipping coordinates and basic arithmetic.
    pygame draws by v=(x, y) and numpy indexes by p=(y, x)."""

    def __init__(self, x, y=0):
        if type(x) != tuple:
            self.x, self.y = x, y
        else:
            self.x, self.y = x[0], x[1]

    @property
    def v(self):
        return self.x, self.y

    @property
    def p(self):
        return self.y, self.x

    @property
    def sum(self):
        return self.x + self.y

    def __repr__(self):
        return f'Vec2D({self.x}, {self.y})'

    def __add__(self, o):
        return Vec2D(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        return Vec2D(self.x - o.x, self.y - o.y)

    def __mul__(self, k):
        return Vec2D(k * self.x, k * self.y)

    def __rmul__(self, k):
        return self.__mul__(k)

    def __abs__(self):
        return Vec2D(abs(self.x), abs(self.y))

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y

    def __iter__(self):
        for i in [self.x, self.y]:
            yield i

    def __hash__(self):
        return hash((self.x, self.y))

vec = Vec2D(3, 4)

print(vec.sum)
print(vec.p)
print(vec.v)
print(vec.x)
print(vec + vec)
print(vec*2)
print(2*vec)
>>>>>>> Stashed changes

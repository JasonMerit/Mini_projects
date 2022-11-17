"""Implement vector math functions wih tuples."""
from math import floor

class V:
    """2D vector class."""
    def __init__(self, vector: tuple):
        self._x, self._y = vector
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
    
    @property
    def pos(self):
        return self._x, self._y
    
    def dot(self, other):
        # assert(isinstance(other, V)), "other must be a vector"
        return self._x * other._x + self._y * other._y
    
    def dist(self, other):
        return (self - other).norm()
    
    def dist_squared(self, other):
        return (self - other).norm_squared()
    
    def norm(self):
        """Return the norm of the vector."""
        return self.norm_squared() ** 0.5
    
    def norm_squared(self):
        return self._x ** 2 + self._y ** 2
    
    def unit(self):
        """Return the unit vector of the vector."""
        return self / self.norm()
    
    def __getitem__(self, index):
        return (self._x, self._y)[index]
    
    def __repr__(self):
        return f"V({self._x}, {self._y})"
    
    def __add__(self, other):
        return V((self._x + other._x, self._y + other._y))
    
    def __sub__(self, other):
        return V((self._x - other._x, self._y - other._y))
    
    def __mul__(self, k):
        # assert(isinstance(k, (int, float))), "k must be a number"
        return V((self._x * k, self._y * k))
    
    def __rmul__(self, k):        
        return self * k
    
    def __truediv__(self, k):
        # assert(isinstance(k, (int, float))), "k must be a number"
        return V((self._x / k, self._y / k))
    
    def __floordiv__(self, k):
        # assert(isinstance(k, (int, float))), "k must be a number"
        return V((int(self._x // k), int(self._y // k)))
    
    def __round__(self):
        return V((round(self._x), round(self._y)))
    
    def __floor__(self):
        return V((int(self._x), int(self._y)))
    
    def __abs__(self):
        return V((abs(self._x), abs(self._y)))
    
    def __mod__(self, k):
        # assert(isinstance(k, (int, float))), "k must be a number"
        return V((self._x % k, self._y % k))
    
    def __tuple__(self):
        return (self._x, self._y)

if __name__ == "__main__":
    p1 = V((1.0, 2.))
    p2 = V((-3.0, 4.0))
    v1 = V((-2.0, 4.0))
    v2 = V((1.0, 3.0))
    # print(v1.norm_squared() + v2.norm_squared())
    a = (v1 - v2).dot(p1 - p2) / (p1 - p2).norm_squared()
    b = (v2 - v1).dot(p2 - p1) / (p2 - p1).norm_squared()
    print(a, b)
    # print(a.norm_squared() + b.norm_squared())
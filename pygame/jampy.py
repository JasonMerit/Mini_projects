"""Script replecating numpy for use in pygbag that only takes native libraries."""


def ones(size):
    jarray = Jarray(size)
    jarray._ones(size)
    return jarray

def zeros(size):
    jarray = Jarray(size)
    jarray._zeros(size)
    return jarray

class Jarray():
    def __init__(self, size):
        self.size = size
    
    def _ones(self, size):
        if len(size) == 1:
            return [1] * size[0]
        self.array = [self._ones(size[1:]) for _ in range(size[0])]

    def _zeros(self, size):
        if len(size) == 1:
            return [0] * size[0]
        self.array = [self._zeros(size[1:]) for _ in range(size[0])]
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.array[key]
        elif isinstance(key, tuple):
            return self.array[key[0]][key[1]]
        else:
            raise TypeError(f"Jarray.__getitem__ key must be int or tuple, not {type(key)}")
    
    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.array[key] = value
        elif isinstance(key, tuple):
            self.array[key[0]][key[1]] = value
        else:
            raise TypeError(f"Jarray.__setitem__ key must be int or tuple, not {type(key)}")
    
    def __repr__(self):
        if len(self.size) == 1:
            return str(self.array)
        string = ""
        for row in self.array:
            string += str(row) + '\n'
        return string[:-1]


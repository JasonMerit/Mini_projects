"""Script replecating numpy for use in pygbag that only takes native libraries."""
int8 = int
sum_standard = sum

def array(array):
    return jdarray(array)

def ones(shape, dtype=None):
    array = jdarray(shape)
    array._build(shape, 1)
    return array

def zeros(shape, dtype=None):
    array = jdarray(shape)
    array._build(shape, 0)
    return array

def all(array):
    if isinstance(array[0], list):  # 2d
        for row in array:
            for item in row:
                if not item:
                    return False
    else:  # 1d
        for item in array:
            if not item:
                return False
    return True

def any(array):
    if isinstance(array[0], list):  # 2d
        for row in array:
            for item in row:
                if item:
                    return True
    else:  # 1d
        for item in array:
            if item:
                return True
    return False

def sum(array, axis=None):
    return array.sum(axis)

def _where(array):
    return [(i, j) for i, row in enumerate(array) for j, item in enumerate(row) if item]

def where(array):
    """ Returns two lists of indices of non-zero elements.
    Use _where instead to get a list of tuples."""
    if isinstance(array[0], int):  # 1d
        return jdarray([i for i, item in enumerate(array) if item]), None # dtype from np
    
    rows, cols = [], []
    for i, row in enumerate(array):
        for j, item in enumerate(row):
            if item:
                rows.append(i)
                cols.append(j)
    return jdarray(rows), jdarray(cols)

def nonzero(array):
    return where(array)

def unique(array, axis):
    """Returns a list of unique rows or columns"""
    if axis == 0:
        return jdarray([array[i] for i in range(len(array)) if array[i] not in array[:i]])
    elif axis == 1:
        raise NotImplementedError("unique axis 1 not implemented, due to numpy's being weird")
    else:
        raise ValueError(f"unique axis must be 0 or 1, not {axis}")

def array_equal(array1, array2): # TODO: Test
    if isinstance(array1[0], list):  # 2d
        for i, row in enumerate(array1):
            for j, item in enumerate(row):
                if item != array2[i][j]:
                    return False
    else:  # 1d
        for i, item in enumerate(array1):
            if item != array2[i]:
                return False
    return True

class jdarray():
    """A ndarray clone that supports only 2d arrays, but a few places are written to support more dimensions.
    1d array is implemented too, for list > int stuff"""

    def __init__(self, shape):
        """If shape, remember to call _ones or _zeros. Otherwise giving a list works fine."""
        if isinstance(shape, int):
            self.shape = (shape,)
        elif isinstance(shape, tuple):
            self.shape = shape

        elif isinstance(shape, list):  # Broken 'shape' name
            array = shape
            if array == []:
                self.shape = (0,)
                self.array = []
            elif isinstance(array[0], list):
                self.shape = (len(array), len(array[0]))
                self.array = [jdarray(row) for row in array]
            elif isinstance(array[0], tuple):  # Weird, but used when defining tiles to be shuffled [(0, 0), (0, 1), ...]
                self.shape = (len(array), len(array[0]))
                self.array = [jdarray(list(row)) for row in array]

            elif isinstance(array, list):  # 1d
                self.shape = (len(array), )
                self.array = array
            else:
                raise TypeError(f"jdarray.__init__ shape must be int, tuple or list, not {type(shape)}")
        else:
            raise TypeError(f"jdarray.__init__ shape must be int, tuple or list, not {type(shape)}")
    
    def copy(self):
        # return jdarray([list(row) for row in self.array])
        copy = jdarray(self.shape)
        copy.array = [row for row in self.array]
        return copy
    
    def sum(self, axis=None):
        if axis is None:  
            if isinstance(self.array[0], int):
                return sum_standard(self.array) # 1d
            return sum_standard([sum_standard(row) for row in self.array])
        elif axis == 0:
            # return [sum_standard(row) for row in zip(*self.array)]
            return jdarray([sum_standard(row) for row in zip(*self.array)])
        elif axis == 1:
            # return [sum_standard(row) for row in self.array]
            return jdarray([sum_standard(row) for row in self.array])
    
    def _build(self, shape, value=0):
        if isinstance(shape, int):
            self.array = [value] * shape

        elif len(shape) == 1:
            return jdarray([value] * shape[0])
        else:
            self.array = [self._build(shape[1:], value) for _ in range(shape[0])]
    
    @property
    def T(self):
        return jdarray([list(row) for row in zip(*self.array)])
    
    def all(self, axis=None):
        if axis is None:
            return all(self.array)
        
        elif axis == 0:
            return jdarray([all(row) for row in zip(*self.array)])
        elif axis == 1:
            return jdarray([all(row) for row in self.array])


    def __getitem__(self, key):
        if isinstance(key, int):
            return self.array[key]
        
        elif isinstance(key, tuple):
            # print('tuple')
            # if isinstance(key[0], jdarray):
            #     if len(key) > 2:
            #         raise IndexError(f"jdarray.__getitem__ key {key} is out of range")
            #     return jdarray([self.array[i] for i in key[0].array])[key[1]]

            if len(key) > len(self.shape):
                raise IndexError(f"jdarray.__getitem__ key {key} is out of range")
            return self.array[key[0]][key[1]]

        elif isinstance(key, slice):
            # print('slice')
            return jdarray(self.array[key])
        
        elif isinstance(key, jdarray):
            # print('jdarray')
            if len(key.shape) == 1:
                return jdarray([self.array[i] for i in key.array])
            return [self.array[i][j] for i, row in enumerate(key.array) for j, b in enumerate(row) if b]

        else:
            raise TypeError(f"jdarray.__getitem__ key must be int or tuple, not {type(key)}")
    
    def __setitem__(self, key, value):
        if isinstance(key, int):  # 1d
            # print('int')
            self.array[key] = value

        elif isinstance(key, tuple):
            # print('tuple')
            if len(key) > len(self.shape):
                raise IndexError(f"jdarray.__getitem__ key {key} is has too many dimensions")
            
            if isinstance(key[0], jdarray):
                # print('jdarray [0]')
                if isinstance(key[1], jdarray):
                    # print('jdarray [0] jdarray value')
                    for k, v in zip(key[0], value):
                        self.array[k][key[1]] = v
                else:
                    for k in key[0]:
                        self.array[k][key[1]] = value

            elif isinstance(key[1], jdarray):
                if isinstance(value, jdarray):
                    # print('jdarray [1] jdarray value')
                    for k, v in zip(key[1], value):
                        self.array[key[0]][k] = v
                else:
                    # print('jdarray [1]')
                    for k in key[1]:
                        self.array[key[0]][k] = value
            else:
                self.array[key[0]][key[1]] = value
        # else:
        #     raise TypeError(f"jdarray.__setitem__ key must be int or tuple, not {key, type(key)}")
        
    def __len__(self):
        return len(self.array)
    
    def __iter__(self):
        return iter(self.array)
    
    def __contains__(self, item):
        if self.array == []:
            return False
        if isinstance(self.array[0], int):  # 1d
            return item in self.array
        
        # 2d
        if isinstance(item, int):
            for row in self.array:
                if item in row:
                    return True
        else:
            for row in self.array:
                if item == row:
                    return True
        return False
    
    def __hash__(self):
        return hash(tuple([item for row in self.array for item in row]))
    
    def __mul__(self, integer):
        if isinstance(integer, int):
            result = jdarray(self.shape)
            result.array = self._mul(self.array, integer)
            return result
        else:
            raise TypeError(f"jdarray.__mul__ integer must be int, not {type(integer)}")
    
    def _mul(self, array, integer):
        if isinstance(array[0], int):  # No more nests
            return [integer * element for element in array]
        return [jdarray(self._mul(entree, integer)) for entree in array]
    
    def __floordiv__(self, integer):
        if isinstance(integer, int):
            result = jdarray(self.shape)
            result.array = self._floordiv(self.array, integer)
            return result
        else:
            raise TypeError(f"jdarray.__floordiv__ integer must be int, not {type(integer)}")
    
    def _floordiv(self, array, integer):
        if isinstance(array[0], int):
            return [element // integer for element in array]
        return [jdarray(self._floordiv(entree, integer)) for entree in array]
    
    def __repr__(self):
        if len(self.shape) == 1:
            return f'array({str(self.array)})'
        string = "["
        for row in self.array:
            string += str(row.array) + '\n '
        return string[:-2] + "]"
    
    def __add__(self, other):
        if isinstance(other, int):
            result = jdarray(self.shape)
            result.array = self._add(self.array, other)
            return result
        else:
            raise TypeError(f"jdarray.__add__ other must be int, not {type(other)}")
    
    def _add(self, array, other):
        if isinstance(array[0], int):
            return [element + other for element in array]
        return [self._add(entree, other) for entree in array]

    def __eq__(self, other):
        """Double function, checks if equal array or returns bool list of equalities to int"""
        if isinstance(other, int): # Get bool list of equalities
            result = jdarray(self.shape)
            result.array = self._eq(self.array, other)
            return result
        elif isinstance(other, jdarray):  # Check if equal
            return self.array == other.array
        else:
            raise TypeError(f"jdarray.__eq__ other must be int, not {type(other)}")
    
    def _eq(self, array, other):
        # assert(not isinstance(array, np.int32)), "array is np.int32"
        # print("type", type(array))
        # print("array", array)
        if isinstance(array[0], int):
            return [element == other for element in array]
        return jdarray([self._eq(entree, other) for entree in array])

    def __ne__(self, other):
        if isinstance(other, int):
            array = self._ne(self.array, other)
            result = jdarray(self.shape)
            result.array = array
            return result
        else:
            raise TypeError(f"jdarray.__ne__ other must be int, not {type(other)}")
    
    def _ne(self, array, other):
        if isinstance(array[0], int):
            return [element != other for element in array]
        return [self._ne(entree, other) for entree in array]
    
    def __gt__(self, other):  # 
        if isinstance(other, int):
            array = self._gt(self.array, other)
            result = jdarray(self.shape)
            result.array = array
            return result
        else:
            raise TypeError(f"jdarray.__gt__ other must be int, not {type(other)}")
    
    def _gt(self, array, other):
        if isinstance(array[0], int):
            return [element > other for element in array]
        return [self._gt(entree, other) for entree in array]
    
    def __lt__(self, other):
        if isinstance(other, int):
            array = self._lt(self.array, other)
            result = jdarray(self.shape)
            result.array = array
            return result
        else:
            raise TypeError(f"jdarray.__lt__ other must be int, not {type(other)}")
        
    def _lt(self, array, other):
        if isinstance(array[0], int):
            return [element < other for element in array]
        return [self._lt(entree, other) for entree in array]

from random import randint, shuffle, seed

class Random():
    
    def randint(self, lower, upper=0):
        if upper == 0:
            return randint(0, lower-1)
        return randint(lower, upper-1)
    
    def shuffle(self, array):
        shuffle(array)
        return array
    
    def seed(self, s):
        seed(s)
        
random = Random()
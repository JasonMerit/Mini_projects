from VectorMath import V
import VectorMath
import pygame as pg
import math
import random
import numpy as np
from random import randint

class Tree():

    def __init__(self, root, left, right):
        self.root = root
        self.left = left
        self.right = right
    
    def __repr__(self) -> str:
        return str((self.left, self.root, self.right))
    
    def get_even(self):
        if self.root == None:
            return 

        if isinstance(self.left, int):
            if self.left % 2 == 0:
                yield self.left
                print("lol")
        else:
            yield from self.left.get_even()

        if isinstance(self.right, int):
            if self.right % 2 == 0:
                yield self.right
                print("lol")
        else:
            yield from self.right.get_even()
    
    def larger_than(self, n):
        if isinstance(self.left, int):
            if self.left > n:
                yield self.left
        else:
            yield from self.left.larger_than(n)

        if isinstance(self.right, int):
            if self.right > n:
                yield self.right
        else:
            yield from self.right.larger_than(n)
        

A = np.random.randint(0, 10, 10)
print(A)
print(sorted(A))
kek()
quit()

tree = Tree(0, Tree(None, 4, 5), Tree(6, 10, 8))
for k in tree.get_even():
    print(k)

def lol(i):
    return i + 1

def kek():
    for i in range(10):
        yield lol(i)

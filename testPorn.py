from pygame.math import Vector2 as V2
from math import *

import pygame_sdl2
pygame_sdl2.import_as_pygame()


import numpy as np

A = [0, 1, 2, 3]
if all([x == 0 for x in A]):
    print("All zero")
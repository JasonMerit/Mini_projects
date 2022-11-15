"""Simulate quantum particle as a wave funciton in a barrier potential."""

import pygame as pg
import numpy as np
import sys
import math
import time
import random
import os

# Set up pygame
pg.init()
pg.font.init()
pg.display.set_caption('Quantum Particle in a Barrier')
screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()

# Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Set up the fonts
font = pg.font.SysFont('Arial', 20)

# Set up the constants
FPS = 60

# Set up the variables

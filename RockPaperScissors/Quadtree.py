import quads
import random

tree = quads.QuadTree((0, 0), 100, 100, 6)
# get boudning box of tree
for _ in range(1000):
    tree.insert((random.uniform(-50, 50), random.uniform(-50, 50)))

# quads.visualize(tree)

# import configparser
# config = configparser.ConfigParser()
# config.read('RockPaperScissors/config.ini')
# from glob import glob

# # print(glob('RockPaperScissors/*'))
# def do():
#     return config['DEFAULT']['COUNT']
# print(do())

import pygame as pg
print(pg.Vector2(0.1, 1))
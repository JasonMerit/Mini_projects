import pygame as pg
import numpy as np



dic = {"Wein" : 10, "Fred" : 12, "Jay": 4}


def go1(x):
    k = 2
    dic = {}
    def go2(y):
        dic[y + k] = 3
    go2(x)
    print(dic)

print(go1(3))


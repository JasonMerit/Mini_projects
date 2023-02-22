import math
import random
from random import randint

w, h = 100, 7
xmin, xmax = 0, w-1

random.seed(1)


def rand_cell():
    x = randint(xmin, xmax)
    return x


X = 20
print(f"bomb: {X}")
warmer = True
same = False
was_outside = False

last = 2  
positions = [last]

cut = math.ceil((xmax + xmin) / 2)
leapping_right = last < cut


for i in range(10 ):

    x = xmax - last if leapping_right else xmin + xmax - last
    if x < 0:
        print("OUTSIDE")
        print(f"{last} -> {xmax}\n")
        last = xmax
        # last = xmax
        continue
    if x == last: # special case
        x -= 1
    if x == X:
        print("BOMB FOUND")
        quit()
    
    last_dst = abs(last - X)
    dst = abs(x - X)
    warmer = last_dst > dst
    same = last_dst == dst

    if same:
        print("SAME")
        print(last, x)
    
    cut = math.ceil((xmax + xmin) / 2)
    leapping_right = last < cut
    if warmer:
        if leapping_right:
            xmin = cut
        else:
            xmax = cut
    else:
        if leapping_right:
            xmax = cut
        else:
            xmin = cut
    direction = f"{last} -> {x}" if leapping_right else f"{x} <- {last}"
    print(direction)
    print(f"WARMER: {warmer}")
    print(f"[{xmin}, {xmax}]")
    print()

    positions.append(x)
    last = x
    leapping_right = last < cut

print(positions)



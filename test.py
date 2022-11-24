from pygame import Vector2 as V2
from random import randint
import numpy as np
import time
from math import pow

start = time.time()

A = np.arange(8).reshape((4,-1))
print(A)
# A[1:, :] = [0, 0]
# A = np.delete(A, slice(1, 0), axis=0)
# A = np.insert(A, 1, [3, 3], axis=0)
# A[1] = [0, 0]
A = np.power([3, 4], 2)
print(A)


# remove middle two elements

# replace middle two points
max = 5
start = 2
i = start + 1
while i != start:
    print(i)
    i = (i + 1) % max






# collision reponse
# ra = V2(3, 4)
# rb = V2(5, 6)
# va = V2(1, 1)
# vb = V2(-1, 0.5)
# wa = -5
# wb = 3
# nb = V2(1, 0.2).normalize()
# Ia = Ib = 1
# ma = mb = 1
# print(f'va: {va}, vb: {vb}, wa: {wa}, wb: {wb}')
# numer = -2 * (va.dot(nb) - vb.dot(nb) + wa * (ra.cross(nb)) - wb * (ra.cross(nb)))
# denom = ma + mb + (Ia / ra.cross(nb) ** 2) + (Ib / rb.cross(nb) ** 2)
# print(f'{numer}/{denom} = {numer / denom}')

# J = numer / denom * nb
# va_ = va + J / ma
# vb_ = vb - J / mb
# wa_ = wa + ra.cross(J) / Ia # or wa + J.cross(ra) / Ia
# wb_ = wb - rb.cross(J) / Ib # or wb - J.cross(rb) / Ib - copilot

# print(f'va_ = {va_}, vb_ = {vb_}, wa_ = {wa_}, wb_ = {wb_}')



quit()

L = [(0, 1), (2, 1), (2, 0), (3, 0), (3, 2), (0, 2)]
Cx = 0
Cy = 0
A = 0
for i in range(len(L)-1):
    x1, x2 = L[i][0], L[i+1][0]
    y1, y2 = L[i][1], L[i+1][1]
    print(x1)

    Cx += (x1 + x2) * (x1 * y2 - x2 * y1)
    Cy += (y1 + y2) * (x1 * y2 - x2 * y1)
    A += (x1 * y2 - x2 * y1)

A = 1/2 * A
centroid = V2(Cx, Cy) / (6 * A)
print(A, centroid)
print(3/4, 5/4)
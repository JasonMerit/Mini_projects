import numpy as np

A = [i for i in range(5, 15)]

for i, a in enumerate(A):
    print(i, a)
    for other in A[i+1:]:
        print(other)
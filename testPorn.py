import numpy as np
from typing import List, Tuple

class kek():
    def __init__(self):
        k = 10
    def fragments_into(self):
        return [kek() for i in range(k)]

ke = kek()
A = [1, 3]
A += ke.fragments_into()
print(A)
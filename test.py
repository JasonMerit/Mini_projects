import pyautogui, sys
import numpy as np

A = indices = np.indices((10, 10)).T[:,:,[1, 0]]  # Create indices for extraction later
B = indices = np.indices((10, 10)).T  # Create indices for extraction later
print(A.shape)
print(B.shape)
print(np.array_equal(A, B))

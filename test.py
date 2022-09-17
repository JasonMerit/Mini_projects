import numpy as np
from scipy.ndimage import label, binary_dilation

np.random.seed(0)
W, H = 1, 1
A = np.random.randint(0,10, (H+2, W+2))
print(A)
print(np.max(A))

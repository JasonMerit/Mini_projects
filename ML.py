import numpy as np


# 16.1 AUC
x = np.array([1,0,1,0,1,0,1,0,1,0,0,1,0,0])
y = np.array([1,0,0,0,1,0,0,0,1,0,0,0,0,0])

N = len(x)
actual_P = y.sum()
actual_F = N - actual_P
TP = np.logical_and(x, y).sum()
FP = np.logical_and(x, y==0).sum()
TN = np.logical_and(x==0, y==0).sum()
FN = np.logical_and(x==0, y).sum()

FPR = FP / actual_F  # 0.27
TPR = TP / actual_P  # 1 => all positives are predicted
# So we have the point (0.27, 1), which ...


import numpy as np


# 16.1 AUC
x = np.array([1,0,1,0,1,0,1,0,1,0,0,1,0,0])
y = np.array([1,0,0,0,1,0,0,0,1,0,0,0,0,0])

N = len(x)
actual_P = y.sum()
actual_F = N - actual_P
TP = np.logical_and(x, y)
print(TP)
FP = np.logical_and(x, y==0).sum()
TN = np.logical_and(x==0, y==0).sum()
FN = np.logical_and(x==0, y).sum()

FPR = FP / actual_F  # 0.27
TPR = TP / actual_P  # 1 => all positives are predicted
# So we have the point (0.27, 1), which ...

# LECTURE 9 QUIZ 3
# All for 4 or more gear are predicted positive 
# y = 0 [13 2 2] 
# y = 1 [2 10 3]

actual_N = 13 + 2 + 2
actual_P = 2 + 10 + 3

# TP<x or more geares>
TP2 = 2 + 10 + 3
FP2 = 13 + 2 + 2

TP3 = 10 + 3
FP3 = 2 + 2

TP4 = 3
FP4 = 2

FPR2 = FP2 / actual_N
TPR2 = TP2 / actual_P

FPR3 = FP3 / actual_N
TPR3 = TP3 / actual_P

FPR4 = FP4 / actual_N
TPR4 = TP4 / actual_P
print(FPR2)
print(TPR2)
print(FPR3)
print(TPR3)
print(FPR4)
print(TPR4)
# ALSO COUNT NUMBER OF BREAKS IN PLOT

# Correspinding rlr_validaion
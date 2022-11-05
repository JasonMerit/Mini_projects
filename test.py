import numpy as np

A = [1, 2, 3, 4, 5, 6, 7]
print(np.mean(A))
m = 0
for n, a in enumerate(A):
	m += (a-m)/(n+1)
	print(m)
# 0 <- 1/1
# 1 <- 1 + (2-1)/2
import numpy as np
from sys import exit
np.random.seed(0)

# Compute the eigenvalues of a matrix
A = np.random.randint(0,10,(3,3))  # [5 0 3] [5 0]
								   # [3 7 9] [3 3]
								   # [3 5 2]

def det(A):
	# Keep decomposing until we get a 1x1 matrix
	N = len(A)
	if N == 1:
		return A[0, 0]

	B = np.delete(A, 0, 0)  # Delete first row
	result = 0

	# Decompose by column
	for j in range(N):
		a = A[0, j] 
		if j % 2 == 1: a *= -1 

		result += a * det(np.delete(B, j, 1))

	return result
		

def normalized(A):
	return A / np.linalg.norm(A)
	
def qr(A):
	# Q columns are the orthonormal basis of A
	# R is the linear combination of Q that produces A
	R = np.zeros(A.shape)

	R[0, 0] = np.linalg.norm(A[:, 0])
	q1 = A[:,0] / R[0, 0]

	R[0, 1] = A[:,1] @ q1
	p2 = R[0, 1] * q1
	a2 = A[:,1] - p2
	R[1, 1] = np.linalg.norm(a2)
	q2 = a2 / R[1, 1]

	R[0,2] = A[:,2] @ q1
	R[1,2] = A[:,2] @ q2
	p3 = R[0, 2] * q1 + R[1, 2] * q2
	a3 = A[:,2] - p3
	R[2,2] = np.linalg.norm(a3)
	q3 = a3 / R[2,2]

	Q = np.vstack((q1, q2, q3))
	return Q.transpose(), R

# mine = det(A)
# nps = round(np.linalg.det(A))
# print(mine, "=", nps, mine == nps)
print(A)
Q, R = qr(A)
# print(Q)
# print(R)
# print(R[0, 0] * Q[:, 0])
# print(R[0, 1] * Q[:, 0] + R[1, 1] * Q[:, 1])
# print(R[0, 2] * Q[:, 0] + R[1, 2] * Q[:, 1] + R[2, 2] * Q[:, 2])
mine = np.round(Q @ R)
print(R)
print()
eigpairs = np.linalg.eig(A)
eig, v = eigpairs[0], eigpairs[1]
print(eig)
# print(A @ v[:, 0])
# print(eig[0] * v[:, 0])

# print(np.linalg.qr(A))

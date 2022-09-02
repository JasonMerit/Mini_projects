import numpy as np
from sys import exit
np.random.seed(0)
EPS = 1e-4#1e-17  # Set by np accuracy of eigenvalues

# 0.9733884909175844
# Compute the eigenvalues of a matrix
A = np.random.randint(0,10,(3,3))  # [5 0 3] [5 0]
								   # [3 7 9] [3 3]
								   # [3 5 2]
A = A.astype(float)								  

def det(A):
	A = A.copy()
	# Determinant is the product of the diagonal for an upper triangular matrix
	# Reduce provided matrix with elementary row operations
	# Swapping neighbouring rows causes a sign flip of the determinant

	N, M = A.shape
	if N != M:
		raise Exception("Provided matrix is non-square")

	flip = False
	for i in range(N-1):
		v = A[:, i]
		
		# Find non-zero element
		index = i
		while index < N and v[index] == 0:
			index += 1

		# If 0-column, matrix is singular
		if index == N:
			return 0

		# Swap rows accordingly and flip sign of determinant if odd row swap
		if index != i:
			A[[index, i]] = A[[i, index]]
			if (index - i) % 2 == 0:
				flip != flip

		# Eliminate to upper triangular form by subtracting out the elements under the diagonal
		diag = A[i, i]
		row = A[i, :]

		for j in np.arange(i+1, N):
			if A[j, i] == 0:
				continue
			A[j, :] -= row / diag * A[j, i]

	determinant = np.prod(np.diagonal(A))
	if flip:
		determinant *= -1
	return determinant

def normalized(A):
	return A / np.linalg.norm(A)

def qr(A):
	N = len(A)
	Q = np.empty((N, N))
	R = np.zeros((N, N))

	R[0, 0] = np.linalg.norm(A[:, 0])
	Q[:, 0] = A[:,0] / R[0, 0]

	for i in range(1, N):
		# Fill out neccesary inner products and compute the projection
		p = np.zeros(N)
		for j in range(i):
			q = Q[:, j]
			r = A[:, i] @ q

			R[j, i] = r
			p += r * q

		# Orthogonal element
		a = A[:, i] - p

		# Normalize and insert as basis vector
		R[i, i] = np.linalg.norm(a)
		Q[:, i] = a / R[i, i]

	return Q, R

def is_upper_triangular(A):
	for i in range(len(A)):
		for j in range(i+1, len(A)):
			if abs(A[j, i]) > EPS:
				return False
	return True


def qr_iteration(A):
	# Assumes A invertible 
	# If A is symmetric, V columns are eigenvectors 
	n = 0
	V = np.eye(len(A))  # Accumilated product of Q
	while not is_upper_triangular(A):
		Q, R = qr(A)
		A = R @ Q
		V = V @ Q
		n += 1
	# print("qr_iteration complete after", n, "iterations")
	return A, V
	# return flush_residue(A), flush_residue(V)

def flush_residue(A):
	A[abs(A) < EPS] = 0
	return A

def householder_reduction(A):
	return A

def eig(A):
	A, Q = qr_iteration(A)
	return np.diagonal(A), Q

def is_eig(A, s, V):
	# Checks the relation Av = sv for all eigenpairs
	for i in range(len(A)):
		LFS = A @ V[:, 0]
		RHS = s[0] * V[:, 0]
		
		if not np.allclose(LFS, RHS):
			return False
	return True

def standardize(A):
	# A = np.array([[0.7972, 0.0767, 0.4383, 0.7866, 0.8091], 
	# 			[0.1954, 0.6307, 0.6599, 0.1065, 0.0508]])
	print(np.mean(A, 0))
	A -= np.mean(A, 0)
	print(A)
	# print(det(A))
	A /= np.std(A, 0)
	print(A)
	
# standardize(A)
# exit()


def PCA(A):
	# https://iq.opengenus.org/algorithm-principal-component-analysis-pca/
	Z = A.copy()
	
	# First standardize
	Z -= np.mean(A, 0)
	print(det(Z))
	Z /= np.std(Z, 0)  # Only if importance of features is independent of variance of features???

	# Find and sort eigenpairs of covariance matrix
	Cov = Z.transpose() @ Z
	s, V = np.linalg.eig(Cov)
	# s, V = eig(Z.transpose() @ Z)
	order = np.argsort(s)
	s = s[order[::-1]]
	V = V[:, order[::-1]]

	# Project data onto eigenvector basis
	Z = Z @ V
	# assert(round(det(Z)) != 0)

	return is_eig(Cov, s, V)

	return s
s, V1 = np.linalg.eig(A)
for j in range(20):
	print("----,", j,"----")
	EPS /= 10
	s, V0 = eig(A)
	print(V0[:, 1] @ V1[:, 1])
	# for i in range(len(V0)):
	# 	print(V0[:, i] @ V1[:, i])

# print(eig(A))
exit()

# Test for true eig
# A = np.cov(A)
# print(A)
# S, V = eig(A)
# print(A @ V[:, 0])
# print(S[0] * V[:, 0])
# print(V)
# print(np.linalg.eig(A)[1])		
# print(eig(A)[1])
# print(qr(A)[1])

# exit()

# Testing
n = 100000
N = 2
print("testing for", n, "iterations ...")
for i in range(n):
	A = np.random.randint(0,10,(N, N))
	A = A.astype(float)	

	while abs(det(A)) < 0.01:
		A = np.random.randint(0,10,(2, 2))
		A = A.astype(float)	
	# np.linalg.eig(A) #  13.0 s
	eig(A)

	# q, r = qr(A)

	# if not np.array_equal(A, np.round(q @ r)):
	# 	print(A)
	# 	print(np.round(q @ r))
	# 	print(det(A))
	# 	raise Exception("FAILED")
print("SUCCESS")

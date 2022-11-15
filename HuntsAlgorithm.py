import numpy as np

np.random.seed(42)
D = np.array([[1, 0, 1, 0, 0],
			[1, 0, 1, 0, 0],
			[0, 1, 1, 0, 0],
			[0, 1, 1, 0, 0],
			[1, 0, 1, 0, 0],
			[1, 0, 1, 0, 0],
			[1, 0, 1, 0, 0],
			[1, 0, 1, 0, 0],
			[1, 0, 1, 0, 0],
			[1, 0, 1, 0, 0],
			[0, 0, 0, 0, 1],
			[0, 1, 0, 1, 1],
			[0, 1, 0, 1, 1],
			[0, 1, 0, 1, 1],
			[0, 1, 0, 1, 1]])
largest_count = lambda X: max(m := np.sum(X[:, -1] == 1), len(X)-m)
class_error = lambda X: 1 - largest_count(X) / len(X)
delta = lambda X, c: class_error(X) - (len(X[X[:, c] == 0]) * class_error(X[X[:, c] == 0]) + len(X[X[:, c] == 1]) * class_error(X[X[:, c] == 1])) / len(X)

def hunt(D):
	splits = []

	s = splitting_attr(D)
	splits.append(s)
	A = D[D[:, s] == 0]
	B = D[D[:, s] == 1]
	A = np.delete(A, s, 1)
	B = np.delete(B, s, 1)

	
	
	print(A)
	print(B)
	print(class_error(A))
	print(class_error(B))

def splitting_attr(X):
	if class_error(X) == 0.0: return None
	
	purity_gains = [delta(D, i) for i in range(len(D[0])-1)]
	branching_attr = np.argmax(purity_gains)
	
	return branching_attr


hunt(D)



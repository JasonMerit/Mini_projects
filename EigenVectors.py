import numpy as np
import math, sys

def PCA():
    """Perform Principal Component Analysis on a matrix"""
    A = np.array([[1, 2, 3], [2, 4, 6], [3, 6, 9]])
    Q, R = QR_decomposition(A)
    Q = Q[:, ::-1]
    R = R[::-1, ::-1]
    print("A = {}".format(A))
    print("Q = {}".format(Q))
    print("R = {}".format(R))
    print("Q^T * A = {}".format(np.dot(Q.T, A)))
    print("Q^T * A * R = {}".format(np.dot(np.dot(Q.T, A), R)))

def get_eigen_vectors(A):
    """Get the eigen vectors of a matrix"""
    if A.shape[0] == A.shape[1]:
        return np.linalg.eig(A)[1]
    else:
        raise ValueError("Matrix must be square")

def get_eigen_vectors(A):
    """Get the eigen vectors of a matrix"""
    if A.shape[0] == A.shape[1]:
        return np.linalg.eig(A)[1]
    else:
        raise ValueError("Matrix must be square")

def QR_decomposition(A):
    """Perform QR decomposition on a matrix"""
    if A.shape[0] == A.shape[1]:
        A = A.copy()
        Q = np.eye(A.shape[0])
        for i in range(A.shape[1]):
            v = A[i:, i]
            v[0] += np.sign(v[0]) * np.linalg.norm(v)
            v = v / np.linalg.norm(v)
            A = A.astype('float64')
            A[i:, i:] -= 2 * np.outer(v, np.dot(v, A[i:, i:]))
            Q[i:, :] -= 2 * np.outer(v, np.dot(v, Q[i:, :]))
        return Q, A
    else:
        raise ValueError("Matrix must be square")

def gram_schmidt(A):
    """Perform Gram-Schmidt orthogonalization on a matrix"""
    basis = []
    for i in range(A.shape[1]):
        v = A[:, i]
        for u in basis:
            v = v - np.dot(u, v) * u
        basis.append(v / np.linalg.norm(v))
    return np.array(basis).T

def decomposition(A):
    """Perform a decomposition on a matrix"""
    A = A.copy()
    Q = np.eye(A.shape[0])
    for i in range(A.shape[1]):
        for j in range(i+1, A.shape[0]):
            c = A[i, i] / math.sqrt(A[i, i]**2 + A[j, i]**2)
            s = A[j, i] / math.sqrt(A[i, i]**2 + A[j, i]**2)
            G = np.eye(A.shape[0])
            G[i, i] = c
            G[j, j] = c
            G[i, j] = -s
            G[j, i] = s
            A = np.dot(G, A)
            Q = np.dot(Q, G.T)
    return Q, A

def det(A):
    """Compute the determinant of a matrix"""
    if A.shape[0] == A.shape[1]:
        A = A.copy()
        for i in range(A.shape[1]):
            for j in range(i+1, A.shape[0]):
                c = A[i, i] / math.sqrt(A[i, i]**2 + A[j, i]**2)
                s = A[j, i] / math.sqrt(A[i, i]**2 + A[j, i]**2)
                G = np.eye(A.shape[0])
                G[i, i] = c
                G[j, j] = c
                G[i, j] = -s
                G[j, i] = s
                A = np.dot(G, A)
        return np.prod(np.diag(A))

def householder(A):
    """Perform Householder orthogonalization on a matrix"""
    A = A.copy()
    Q = np.eye(A.shape[0])
    for i in range(A.shape[1]):
        v = A[i:, i]
        v[0] += np.sign(v[0]) * np.linalg.norm(v)
        v = v / np.linalg.norm(v)
        A = A.astype('float64')
        A[i:, i:] -= 2 * np.outer(v, np.dot(v, A[i:, i:]))
        Q[i:, :] -= 2 * np.outer(v, np.dot(v, Q[i:, :]))

def givens(A):
    """Perform Givens orthogonalization on a matrix"""
    if A.shape[0] == A.shape[1]:
        A = A.copy()
        Q = np.eye(A.shape[0])
        for i in range(A.shape[1]):
            for j in range(i+1, A.shape[0]):
                c = A[i, i] / math.sqrt(A[i, i]**2 + A[j, i]**2)
                s = A[j, i] / math.sqrt(A[i, i]**2 + A[j, i]**2)
                G = np.eye(A.shape[0])
                G[i, i] = c
                G[j, j] = c
                G[i, j] = -s
                G[j, i] = s
                A = np.dot(G, A)
                Q = np.dot(Q, G.T)
        return Q, A
    else:
        raise ValueError("Matrix must be square")

def main():
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print("A = {}".format(A))
    print("Eigen vectors of A = {}".format(get_eigen_vectors(A)))
    print("QR decomposition of A = {}".format(QR_decomposition(A)))
    print("Gram-Schmidt orthogonalization of A = {}".format(gram_schmidt(A)))
    print("Householder orthogonalization of A = {}".format(householder(A)))
    print("Givens orthogonalization of A = {}".format(givens(A)))
    print("Determinant of A = {}".format(det(A)))



if __name__ == "__main__":
    main()
import numpy as np
np.random.seed(2)

X = np.random.randint(0, 5, (28, 28))
W = np.random.randint(0, 2, (5, 5))
print(X)
# print(W)
def convolve(X, W, stride = 1, zero_padding = False):
    # Only gives resonable results for proper dimensions
    M = len(W)  # Assumes square filter
    output_dim = np.array(X.shape) - np.array(W.shape) + [1, 1]
    output_dim = np.ceil(output_dim / stride).astype(int)
    if zero_padding:  # Pad zeros and extend output dimensions
        X = np.pad(X, 1)
        output_dim += [2, 2]
    Y = np.zeros(output_dim)
    
    # Move along the input and elementwise multiply and sum up. 
    for j in range(output_dim[0]):
        for i in range(output_dim[1]):
            Y[j, i] = sum(sum(X[j*stride:(j*stride)+M, i*stride:(i*stride)+M] * W))
    return Y.astype(int)

def pool(X, dim = (2, 2), type="max", stride=1):
    # Only gives resonable results for proper dimensions
    M = dim[0]  # Assumes square dim
    output_dim = np.array(X.shape) - np.array(dim) + [1, 1]
    output_dim = np.ceil(output_dim / stride).astype(int)
    Y = np.zeros(output_dim)
    
    # Move along the input and get max 
    for j in range(output_dim[0]):
        for i in range(output_dim[1]):
            Y[j, i] = np.max(X[j*stride:(j*stride)+M, i*stride:(i*stride)+M])
    return Y.astype(int)

# print(pool(X, (2, 2), "max", 2))
Y = convolve(X, W, 1)
print(Y.shape)

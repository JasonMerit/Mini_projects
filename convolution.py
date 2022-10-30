import numpy as np
np.random.seed(2)

X = np.random.randint(0, 5, (12, 12))
W = np.random.randint(0, 2, (3, 3))

# dim_out = floor((dim_in+2*padding-(kernel_size - 1)-1)/stride+1)

print(X)
# print(W)
def convolve(X, W, padding = 0, stride = 1):
    # Only gives resonable results for proper dimensions
    M = len(W)  # Assumes square filter
    dim_out = np.floor((len(X)+2*padding-(len(W) - 1)-1)/stride+1)  # From torch
    print(dim_out)
    output_dim = np.array(X.shape) - np.array(W.shape) + [1, 1]
    print(output_dim / stride)
    output_dim = np.ceil(output_dim / stride).astype(int)
    if padding:  # Pad zeros and extend output dimensions
        X = np.pad(X, 2)
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
Y = convolve(X, W, 2)
print(Y.shape)

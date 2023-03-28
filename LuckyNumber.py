import numpy as np

N = 100_0

samples = np.random.randint(0, N, N)
unique = np.unique(samples)
# print(np.round(len(unique) / N, 3) * 100, '%')  # 63.2 %


# Let x ~ U(0, N) be a random variable
# Let y be the number of unique values in the sample
# Let p(y) be the probability of y unique values in the sample
# Let p(y) = (N choose y) * (1/N)^y * (1 - 1/N)^(N - y)
def choose(n, k):
    return np.math.factorial(n) / (np.math.factorial(k) * np.math.factorial(n - k))
y = [(choose(N, y)) * (1/N)**y * (1 - 1/N)**(N - y) for y in range(N)]
print(np.round(np.sum([y]), 3) * 100, '%')

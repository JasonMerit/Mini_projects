import numpy as np
import matplotlib.pyplot as plt
from sys import exit
# y = (a + N(0, 1)*x + b + N(0, 4)
np.random.seed(0)
a = 10; sigma_a = 2
b = 4; sigma_b = 40

data = np.array([(x, (a + np.random.normal(0, sigma_a)) * x + b + np.random.normal(0, sigma_b)) for x in range(100)])
np.random.shuffle(data)

training, test = data[:75, :], data[75:, :]

w = np.array([10, 4])

def predict(x):
    return w[0] * x + w[1]

def cost():
    cost = 0.0
    for t in test:
        cost += pow(predict(t[0]) - t[1], 2)

    return cost / len(test)
print(cost())

plt.scatter(test[:, 0], test[:, 1], color='b')
y_hat = [predict(i) for i in test[:, 0]]
plt.plot(test[:, 0], y_hat, color='r')
plt.show()



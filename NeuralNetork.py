import numpy as np
sigmoid = lambda x: 1 / (1 + np.exp(-x))

class Neuron:
    
        def __init__(self, weights, bias):
            self.weights = weights
            self.bias = bias
            self.output = 0
            self.delta = 0
    
        def calculate_output(self, inputs):
            self.output = sigmoid(np.dot(self.weights, inputs) + self.bias)
            return self.output
    
        def calculate_delta(self, target_output):
            self.delta = self.output * (1 - self.output) * (target_output - self.output)
            return self.delta
    
        def update_weights(self, inputs, learning_rate):
            for i in range(len(self.weights)):
                self.weights[i] += learning_rate * self.delta * inputs[i]
            self.bias += learning_rate * self.delta
    
        def __repr__(self):
            return "Weights: " + str(self.weights) + " Bias: " + str(self.bias) + " Output: " + str(self.output) + " Delta: " + str(self.delta)

class NeuralNetwork:
        
            def __init__(self, input_size, hidden_size, output_size):
                self.input_size = input_size
                self.hidden_size = hidden_size
                self.output_size = output_size
                self.hidden_layer = []
                self.output_layer = []
                for i in range(hidden_size):
                    weights = np.random.rand(input_size)
                    bias = np.random.rand()
                    self.hidden_layer.append(Neuron(weights, bias))
                for i in range(output_size):
                    weights = np.random.rand(hidden_size)
                    bias = np.random.rand()
                    self.output_layer.append(Neuron(weights, bias))
        
            def feed_forward(self, inputs):
                self.hidden_outputs = []
                for neuron in self.hidden_layer:
                    self.hidden_outputs.append(neuron.calculate_output(inputs))
                output_outputs = []
                for neuron in self.output_layer:
                    output_outputs.append(neuron.calculate_output(self.hidden_outputs))
                return output_outputs
        
            def back_propagation(self, inputs, targets, learning_rate):
                self.feed_forward(inputs)
                for i in range(len(self.output_layer)):
                    self.output_layer[i].calculate_delta(targets[i])
                for i in range(len(self.hidden_layer)):
                    sum = 0
                    for neuron in self.output_layer:
                        sum += neuron.weights[i] * neuron.delta
                    self.hidden_layer[i].calculate_delta(sum)
                for neuron in self.output_layer:
                    neuron.update_weights(self.hidden_outputs, learning_rate)
                for neuron in self.hidden_layer:
                    neuron.update_weights(inputs, learning_rate)
        
            def train(self, inputs, targets, learning_rate):
                self.back_propagation(inputs, targets, learning_rate)
        
            def predict(self, inputs):
                return self.feed_forward(inputs)
        
            def __repr__(self):
                string = "Hidden Layer: " + str(self.hidden_layer) + " Output Layer: " + str(self.output_layer)
                return string
        
if __name__ == "__main__":
    nn = NeuralNetwork(2, 2, 1)
    print(nn)
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([0, 1, 1, 0])
    for i in range(10000):
        for j in range(len(X)):
            nn.train(X[j], [y[j]], 0.1)
    for i in range(len(X)):
        print("X: " + str(X[i]) + " y: " + str(y[i]) + " Prediction: " + str(nn.predict(X[i])))
    print(nn)

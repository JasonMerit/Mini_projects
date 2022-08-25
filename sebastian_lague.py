
import numpy as np
from scipy.stats import qmc
import pygame as pg
import time

from sys import exit

start = time.time()

num_output = 2

# Create data
N = 91
np.random.seed(5)
sampler = qmc.Halton(d=2, scramble=True)
data = np.array(sampler.random(n=N))
# labels = [[0, 1] if x + y < 0.8 else [1, 0] for x, y in data]  # 0 poison, 1 poison
labels = [1 if x + y < 0.8 else 0 for x, y in data]  # 0 poison, 1 poison
# expected_output = [np.zeros(num_output) for i in range(N)]
data = np.c_[data, labels]
# exit()

class Layer():
	num_in = 0
	num_out = 0
	weights = np.array([])
	biases = np.array([])

	def __init__(self, ind, out):
		self.num_in = ind
		self.num_out = out

		self.weights = np.random.normal(0, 1, (out, ind))
		self.biases = np.random.normal(0, 1, out)

	def compute(self, inputs):
		return np.dot(self.weights, inputs) + self.biases

	def node_cost(self, output_activation, expected_output):
		error = output_activation - expected_output
		print(output_activation, "-", expected_output)
		return error * error

# l = Layer(2, 1)
# print(l.compute([10, 2]))

class NeuralNetwork():

	layers = []

	def __init__(self, layer_sizes):
		for i in range(len(layer_sizes) - 1):
			self.layers.append(Layer(layer_sizes[i], layer_sizes[i + 1]))

	def feedforward(self, inputs):
		for layer in self.layers:
			inputs = layer.compute(inputs)
		return sigmoid(inputs)

	def classify(self, inputs):
		outputs = self.feedforward(inputs)
		return np.argmax(outputs)

	def cost(self, data_point):
		print(data_point)
		# @params data_point (x, y, poison, safe)
		outputs = self.feedforward(data_point[0:2])
		output_layer = self.layers[len(self.layers) - 1]
		cost = 0.0

		for i in range(output_layer.num_out):
			cost += output_layer.node_cost(outputs[i], data_point[2])

	def avg_cost(self, data):
		total_cost = 0

		for data_point in data:
			total_cost += self.cost(data_point)

		return total_cost / len(data)


def sigmoid(x):
	return 1/(1+np.exp(-x))


nn = NeuralNetwork([2, 3, num_output])
# print(nn.feedforward([10, 2]))


# exit()


# Hardcoded 2 layer nn
# W = np.array([[0.9, -0.75], [-0.5, 0.8]])
# B = np.array([1, -1])
#
# def classify(point):
# 	a = np.dot(point, W) + B
# 	return 0 if a[0] > a[1] else 1



# exit()

WIDTH, HEIGHT, MARGIN = 500, 500, 40
screen = pg.display.set_mode((WIDTH, HEIGHT))
background = pg.Surface((WIDTH, HEIGHT))
background.set_alpha(200)

BLACK = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (200, 80, 80)
RED_LIGHT = (240, 120, 120)
BLUE = (80, 80, 200)
BLUE_LIGHT = (120, 120, 240)
GREEN = (80, 200, 80)
GREY = (80, 80, 80)
colors = [RED, BLUE]

pg.display.set_caption('NeuralNetwork')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 25)

# buttons = [screen.blit(pg.Rect(5, 5), (300, 200))]

def pixel2point(pixel):
	# x = 0 + (1 - 0) / (WIDTH - 0) * (pixel[0] - 0)
	return (pixel[0] - MARGIN) / WIDTH, - (pixel[1] + MARGIN - HEIGHT) / HEIGHT

def point2pixel(point):
	return point[0] * WIDTH + MARGIN, HEIGHT - MARGIN - point[1] * HEIGHT

def draw():
	screen.fill(BLACK)

	# Draw decision regions
	# for x in range(WIDTH):
	# 	for y in range(HEIGHT):
	# 		point = pixel2point((x, y))
	# 		color = colors[nn.classify(point)]
	# 		background.set_at((x, y), color)
	# screen.blit(background, (0, 0))

	# Draw axis
	pg.draw.line(screen, GREY, (MARGIN, 0), (MARGIN, HEIGHT), 5)
	pg.draw.line(screen, GREY, (0, HEIGHT - MARGIN), (WIDTH, HEIGHT - MARGIN), 5)

	# Draw data
	for x, y, safe in data:
		color = RED_LIGHT if not safe else BLUE_LIGHT
		pg.draw.circle(screen, color, (WIDTH * x + MARGIN, HEIGHT - MARGIN - y * HEIGHT), 5)

	# Compute and draw cost
	cost = nn.avg_cost(data)
	txt = font2.render(str("Cost:", cost), 1, WHITE)
	screen.blit(txt, (60, HEIGHT - 40))


	pg.display.flip()
	print("done drawing")

def process_input():
	while True:
		event = pg.event.wait()

		if event.type == pg.QUIT:
			pg.quit()
			exit()

		elif event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				pg.quit()
				exit()
			if event.key == pg.K_SPACE:
				pass
			elif event.key == pg.K_r:
				print("restart")
				global nn
				nn = NeuralNetwork([2, 3, 2])
				draw()


		elif event.type == pg.MOUSEBUTTONDOWN:
			pos = pg.mouse.get_pos()
			pg.draw.circle(screen, GREEN, pos, 5)
			print(pos, "->", pixel2point(pos))
			# draw()

# (40, 460)

draw()
process_input()



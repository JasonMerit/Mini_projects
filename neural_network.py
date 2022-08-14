
import numpy as np
import pygame as pg
from sys import exit

N = 200
WIDTH, HEIGHT, MARGIN = 1000, 600, 40
np.random.seed(5)
data = np.array([[np.random.uniform(MARGIN + 10, WIDTH - MARGIN - 10), 
				np.random.uniform(MARGIN + 10, HEIGHT - MARGIN - 10)] for i in range(N)])
labels = [1 if x + y < 500 else 0 for x, y in data]

W = np.array([[20, -5], [-40, 5]])


def classify(point):

	a = np.dot(point, W)
	return 1 if a[0] > a[1] else 0


# exit()




k = 2
win = pg.display.set_mode((WIDTH, HEIGHT))
background = pg.Surface((WIDTH / k, HEIGHT / k))
background.set_alpha(200)

BLACK = (40, 40, 40)
WHITE = (255, 255, 255)
RED = (200, 80, 80)
RED_LIGHT = (240, 120, 120)
BLUE = (80, 80, 200)
BLUE_LIGHT = (120, 120, 240)
GREEN = (80, 200, 80)
GREY = (80, 80, 80)
colors = [BLUE, BLACK]

pg.display.set_caption('NeuralNetwork')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

buttons = [win.blit(pg.Rect(5, 5), (300, 200))]

def draw():
	# screen.fill(BLACK)

	# Draw decision regions
	# for x in range(WIDTH):
	# 	for y in range(HEIGHT):
	# 		color = colors[classify(np.array([x, y]))]
	# 		# color = colors[int((x + y) % 2 == 0)]
	# 		background.set_at((x, y), color)
	# win.blit(pg.transform.scale(background, win.get_rect().size), (0, 0))

	# Draw axis
	pg.draw.line(win, GREY, (MARGIN, 0), (MARGIN, HEIGHT), 5)
	pg.draw.line(win, GREY, (0, HEIGHT - MARGIN), (WIDTH, HEIGHT - MARGIN), 5)

	# Draw data points
	for (x, y), l in zip(data, labels):
		color = BLUE_LIGHT if l else RED_LIGHT
		pg.draw.circle(win, color, (x, HEIGHT - y), 5)


	pg.display.flip()
	print("done")

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


		elif event.type == pg.MOUSEBUTTONDOWN:
			pos = pg.mouse.get_pos()
			pg.draw.circle(win, GREEN, pos, 5)
			print([s for s in buttons if s.rect.collidepoint(pos)])

			draw()



draw()
process_input()



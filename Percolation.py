import numpy as np
import pygame as pg
from scipy.ndimage import label
from sys import exit

W, H = 20, 10
p = 0.5
A = np.random.random((H, W))
B = np.random.random((H, W))
# A = A > p
# print(A)

# A, n = label(A, np.ones((3, 3)))
# print(n)
# print(A)


WHITE, GREY, BLACK = (240, 240, 240),  (200, 200, 200), (0, 0, 0)
colors = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (42, 42, 148),  # Blue, Green, Red, d_Blue
        (128, 0 ,0), (42, 148, 148), BLACK, (160, 160, 160)]  			 # d_Red, turqoise, Black, Grey

pg.display.set_caption('Percolation')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

size = 24
offset = size // 2
screen = pg.display.set_mode([W * size, H * size])

def draw():
    screen.fill(BLACK)

    
    
    closed_horiz = A < p
    closed_vert = B < p

    for x in range(W):
        for y in range(H):
            if closed_horiz[y, x]:
                # Horizontal line
                pg.draw.line(screen, WHITE, (x*size, y*size), ((x*size + size, y*size)), 2)
            if closed_vert[y, x]:
                # Vertical line
                pg.draw.line(screen, WHITE, (x*size, y*size), ((x*size, y*size + size)), 2)

    
    pg.display.flip()


def process_input():
    event = pg.event.wait()
    if event.type == pg.QUIT:
        pg.quit()
        exit()

    elif event.type == pg.KEYDOWN:
        if event.key == pg.K_ESCAPE:
            pg.quit()
            exit()
        global p
        if event.key == pg.K_UP:
            p += 0.02
            p = min(p, 1)

        if event.key == pg.K_DOWN:
            p -= 0.02
            p = max(p, 0)
        
        draw() 
        # if event.key == pg.K_r:
        #     reset()

draw()           
while True:    
    process_input()
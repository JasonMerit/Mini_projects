# https://www.youtube.com/watch?v=gYRrGTC7GtA&list=LL&index=1
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from math import cos, sin, tan, pi, tau, pow
import multiprocessing as mp

W, H = 1200, 600
px, py = 200, 300
pa = 3*pi/2
SPEED = 2
OMEGA = 0.05
pdx, pdy = cos(pa)*SPEED, sin(pa)*SPEED
SIZE = 64
P2 = pi/2
P3 = 3*pi/2
DEGREE = pi/180

MAP = [
 [1,1,1,1,1,1,1,1],
 [1,0,1,0,0,0,0,1],
 [1,0,1,0,0,0,0,1],
 [1,0,1,0,0,0,0,1],
 [1,0,0,0,2,0,0,1],
 [1,0,0,0,0,1,0,1],
 [1,0,0,0,0,0,0,1],
 [1,1,1,1,1,1,1,1],	
]

MAP_Y = len(MAP)
MAP_X = len(MAP[0])
MAP_S = MAP_Y * MAP_X


def events():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()

def input1():
    keys = pg.key.get_pressed()
    global px, py
    if keys[pg.K_a]:
        px -= SPEED
    if keys[pg.K_d]:
        px += SPEED
    if keys[pg.K_w]:
        py -= SPEED
    if keys[pg.K_s]:
        py += SPEED

def input():
    keys = pg.key.get_pressed()
    global px, py, pdx, pdy, pa
    if keys[pg.K_a]:
        pa -= OMEGA
        if pa < 0: pa += tau
        pdx = cos(pa)*SPEED
        pdy = sin(pa)*SPEED

    if keys[pg.K_d]:
        pa += OMEGA
        if pa > tau: pa -= tau
        pdx = cos(pa)*SPEED
        pdy = sin(pa)*SPEED
    
    if keys[pg.K_w]:
        px += pdx
        py += pdy

    if keys[pg.K_s]:
        px -= pdx
        py -= pdy
    
    if keys[pg.K_SPACE]:
        print(-tan(pa))

def draw_player():
    glPointSize(8)
    glColor3f(0.1, 1, 0)
    glBegin(GL_POINTS)
    glVertex2i(int(px), int(py))
    glEnd()

    glLineWidth(3)
    glColor(0.1, 1, 0)
    glBegin(GL_LINES)
    glVertex2i(int(px), int(py))
    glVertex2i(int(px + pdx * 6), int(py + pdy * 6))
    glEnd()

def draw_walls():
    for y in range(len(MAP)):
        for x in range(len(MAP[y])):
            color = (1, 1, 1) if MAP[y][x] else (0, 0, 0)
            xo = x * SIZE
            yo = y * SIZE
            glColor3f(*color)
            glBegin(GL_QUADS)
            glVertex(xo+1, yo+1)
            glVertex(xo+1, yo+SIZE-1)
            glVertex(xo+SIZE-1, yo+SIZE-1)
            glVertex(xo+SIZE-1, yo+1)
            glEnd()

def dist(ax, ay, bx, by):
    return pow(bx - ax, 2) + pow(by - ay, 2)

def draw_rays():
    # ra = pa
    ra = pa - DEGREE*30
    if ra < 0: ra += tau
    if ra > tau: ra -= tau
        
    for r in range(60):
        # --- Vertical ---
        dof = 0  # depth of field
        distV = 100000000 # distance to vertical wall
        vx, vy = px, py # coordinates of vertical wall
        Tan = -tan(ra)  # negative tan
        if P2 < ra < P3:
            rx = ((int(px)>>6)<<6) - 0.0001 # looking left (64 multiples)
            ry = (px - rx) * Tan + py
            xo = -SIZE
            yo = - xo * Tan
        elif ra < P2 or ra > P3:
            rx = ((int(px)>>6)<<6) + SIZE # looking right
            ry = (px - rx) * Tan + py
            xo = SIZE
            yo = - xo * Tan
        if ra == P2 or ra == P3:  # looking straight up or down
            rx = px
            ry = py
            dof = 8
        while dof < 8:  # iterate until wall is found
            mx = int(rx)>>6  # map x
            my = int(ry)>>6  # map y
            if 0 <= mx < MAP_X and 0 <= my < MAP_Y and MAP[my][mx]:
                vx = rx
                vy = ry
                distV = dist(px, py, rx, ry)
                valueV = MAP[my][mx]
                dof = 8
            else:  # next line
                rx += xo
                ry += yo
                dof += 1
        
        # --- Horizontal ---
        dof = 0  # depth of field
        distH = 100000000 # distance to horizontal wall
        aTan = -1/tan(ra)
        # Tan = -1/Tan
        if ra > pi:
            ry = ((int(py)>>6)<<6) - 0.0001 # looking up (64 multiples)
            rx = (py - ry) * aTan + px
            yo = -SIZE
            xo = - yo * aTan
        elif ra < pi:
            ry = ((int(py)>>6)<<6) + SIZE # looking down
            rx = (py - ry) * aTan + px
            yo = SIZE
            xo = - yo * aTan
        if ra == 0 or ra == pi:  # looking straight left or right
            rx = px
            ry = py
            dof = 8
        
        while dof < 8:  # iterate until wall is found
            mx = int(rx)>>6  # map x
            my = int(ry)>>6  # map y
            # mp = my * MAP_X + mx  # map position
            # if mp >= 0 and mp < MAP_X*MAP_Y and MAP[my][mx]:  # if wall is found
            if 0 <= mx < MAP_X and 0 <= my < MAP_Y and MAP[my][mx]:
                distH = dist(px, py, rx, ry)
                valueH = MAP[my][mx]
                dof = 8
            else:  # next line
                rx += xo
                ry += yo
                dof += 1
        
        if distV < distH:
            rx = vx
            ry = vy
            distance = distV
            value = valueV
            if value == 1:
                glColor3f(1, 0, 0)
            elif value == 2:
                glColor3f(0, 0, 1)
        else:
            distance = distH
            value = valueH
            if value == 1:
                glColor3f(0.7, 0, 0)
            elif value == 2:
                glColor3f(0, 0, 0.7)
        
        # draw ray
        glLineWidth(4)
        glBegin(GL_LINES)
        glVertex2i(int(px), int(py))
        glVertex2i(int(rx), int(ry))
        glEnd()

        # --- Draw 3d walls ---
        
        # fix fisheye
        ca = pa - ra  
        if ca < 0: ca += tau
        if ca > tau: ca -= tau
        distance *= cos(ca)

        k = 10240
        lineH = int(MAP_S * k // distance) # height of line
        if lineH > k: lineH = k
        # lineO = int((k >> b-1) - lineH >> 1)  # line offset
        lineO = int((3*H // 4) - lineH >> 1)  # line offset
        t = 7
        glLineWidth(t)
        # glColor3f(*color)
        glBegin(GL_LINES)
        k = W >> 1
        glVertex2i(r*t+k, lineO)
        glVertex2i(r*t+k, lineH + lineO)
        glEnd()
        

        ra += DEGREE
        if ra < 0: ra += tau
        if ra > tau: ra -= tau
        

def display():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glClearColor(0.3,0.3,0.3,0)
    draw_walls()
    draw_rays()
    draw_player()
    pg.display.flip()


def main():
    pg.init()
    pg.display.set_mode((W,H), pg.DOUBLEBUF|pg.OPENGL)
    pg.display.set_caption("RayCast")
    gluOrtho2D(0, W, H, 0)
    clock = pg.time.Clock()

    while True:
        events()
        input()
        display()
        clock.tick(60)
        

if __name__ == "__main__":
    main()
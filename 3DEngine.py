import pygame as pg
import numpy as np
import os
from random import randrange
from OpenGL.GL import *
from OpenGL.GLU import *

SPEED = 1
MOVE_SPEED = 0.1
NUM_CUBES = 15
R_RANGE = 10
ROT_MAT = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
ROTATION_SPEED = 0.05
FPS = 60

verticies = np.array([
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, -1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, -1, 1],
    [-1, 1, 1]
    ])

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )

colors = (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (0,1,0),
    (1,1,1),
    (0,1,1),
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (1,0,0),
    (1,1,1),
    (0,1,1),
    )

ground_surfaces = (0,1,2,3)

ground_vertices = (
    (-10,-0.6,50),
    (10,-0.6,50),
    (-10,-0.6,-300),
    (10,-0.6,-300),
    )

def Cube(verticies):
    glBegin(GL_QUADS)
    for surf in surfaces:
        for i, vertex in enumerate(surf):
            glColor3fv(colors[i])
            glVertex3fv(verticies[vertex])
    glEnd()
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

def Ground():
    glBegin(GL_QUADS)
    for vertex in ground_vertices:
        glColor3fv((0,1,0))
        glVertex3fv(vertex)
    glEnd()

def set_vertices(max_distance, min_distance=-20, camera_x=0, camera_y=0):
    
    # x_value_change = randrange(-R_RANGE,R_RANGE)
    x_value_change = randrange(-camera_x-R_RANGE,-camera_x+R_RANGE)
    y_value_change = randrange(-camera_y-R_RANGE,-camera_y+R_RANGE)
    z_value_change = randrange(-max_distance, min_distance, 1)

    new_vertices = []

    for vert in verticies:
        new_vert = []

        new_x = vert[0] + x_value_change
        new_y = vert[1] + y_value_change
        new_z = vert[2] + z_value_change

        new_vert.append(new_x)
        new_vert.append(new_y)
        new_vert.append(new_z)

        new_vertices.append(new_vert)

    return new_vertices

def events():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()
        
            if event.key == pg.K_SPACE:
                return "space"
        
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                glTranslatef(0,0,1.0)
            if event.button == 5:
                glTranslatef(0,0,-1.0)

def input():
    keys = pg.key.get_pressed()
    dx, dy = 0, 0
    if keys[pg.K_LEFT]:
        dx = MOVE_SPEED
    if keys[pg.K_RIGHT]:
        dx = -MOVE_SPEED
    if keys[pg.K_UP]:
        dy = -MOVE_SPEED
    if keys[pg.K_DOWN]:
        dy = MOVE_SPEED
    return dx, dy
        
def main():
    pg.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (120, 30)
    display = (800,600)
    pg.display.set_mode(display, pg.DOUBLEBUF|pg.OPENGL)    
    clock = pg.time.Clock()

    max_distance = 100
    cubes = [set_vertices(max_distance) for _ in range(NUM_CUBES)]
    cubes.sort(key=lambda x: x[0][2])

    gluPerspective(45, (display[0]/display[1]), 0.1, max_distance)  # FOV, aspect ratio, near clipping plane, far clipping plane
    glTranslatef(0, 0, -60)  

    cur_x, cur_y = 0, 0

    while True:
        key = events()
        dx, dy = input()
        cur_x += dx
        cur_y += dy
        glTranslate(dx,dy,SPEED)
        x = glGetDoublev(GL_MODELVIEW_MATRIX)
        camera_z = x[3][2]


        if key == "space":
            cubes.append(set_vertices(max_distance))
            print(len(cubes))

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1,0.1,0.1,1)
        # Ground()
        unsorted = False
        for i, cube in enumerate(cubes):
            # rotate the cube around the y axis         
            # cube = cube @ np.array([[np.cos(ROTATION_SPEED), 0, np.sin(ROTATION_SPEED)], [0, 1, 0], [-np.sin(ROTATION_SPEED), 0, np.cos(ROTATION_SPEED)]])
            # rotate the cube around the z axis
            # rot_speed = ROTATION_SPEED if i%2 == 0 else -ROTATION_SPEED
            # first translate the cube to the origin, then rotate, then translate back
            if camera_z < cube[0][2]:
                new_max_distance = -int(camera_z - max_distance*2)
                cube = set_vertices(new_max_distance, int(camera_z-max_distance), int(cur_x), int(cur_y))
                unsorted = True
            Cube(cube)
            cubes[i] = cube
            
        if unsorted:
            cubes.sort(key=lambda x: x[0][2])
        pg.display.flip()
        clock.tick(FPS)
        pg.display.set_caption(f"3D Engine - FPS: {clock.get_fps():.2f}")
        


if __name__ == '__main__':
    main()
import pygame as pg

# Initialize the game engine
pg.init()

# Set the width and height of the screen
screen_width = 800
screen_height = 600
screen = pg.display.set_mode([screen_width, screen_height])

# Set the background color
bg_color = (255, 255, 255)

# Define the vertices of the faces of the box
# The order of the vertices is important!
front_face = [(100, 100), (200, 100), (200, 200), (100, 200)]
top_face = [(100, 100), (200, 100), (150, 50)]
right_face = [(200, 100), (200, 200), (150, 150)]
left_face = [(100, 100), (100, 200), (150, 150)]
bottom_face = [(100, 200), (200, 200), (150, 150)]

# Draw the faces of the box
pg.draw.polygon(screen, (255, 0, 0), front_face)
pg.draw.polygon(screen, (0, 255, 0), top_face)
pg.draw.polygon(screen, (0, 0, 255), right_face)
pg.draw.polygon(screen, (255, 255, 0), left_face)
pg.draw.polygon(screen, (0, 255, 255), bottom_face)

# Update the screen
pg.display.flip()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                quit()
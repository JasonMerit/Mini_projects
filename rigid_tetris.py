import pygame as pg, pymunk as pm

pg.init()
W, H = 800, 600
screen = pg.display.set_mode((W, H))
clock = pg.time.Clock()
FPS = 60
BLACK, GREY, WHITE = (0, 0, 0), (100, 100, 100), (255, 255, 255)
SIZE = 30

# create space
space = pm.Space()
space.gravity = 0, 500
tetrimino_surf = pg.Surface((SIZE, SIZE))
tetriminos = []

def create_tetrimino(x, y):
    """Create tetrimino."""
    body = pm.Body(1, 100, body_type=pm.Body.DYNAMIC)
    body.position = x, y
    shape = pm.Poly.create_box(body, (SIZE, SIZE))  # For collision
    space.add(body, shape)
    return shape

def draw_tetriminos(tetriminos):
    """Draw tetrimino."""
    for tetrimino in tetriminos:
        x, y = int(tetrimino.body.position.x), int(tetrimino.body.position.y)
        rect = tetrimino_surf.get_rect(center=(x, y))
        screen.blit(tetrimino_surf, rect)

def static_floor():
    """Create static floor."""
    body = pm.Body(body_type=pm.Body.STATIC)
    body.position = W // 2, H-200
    shape = pm.Segment(body, (-W // 2, 0), (W // 2, 0), 0)
    space.add(body, shape)
    return shape

def draw_floor(floor):
    """Draw floor."""
    x, y = int(floor.body.position.x), int(floor.body.position.y)
    pg.draw.line(screen, BLACK, (x - W // 2, y), (x + W // 2, y), 1)
    
tetriminos.append(create_tetrimino(100, 100))
floor = static_floor()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()
            elif event.key == pg.K_SPACE:
                tetriminos.append(create_tetrimino(100, 100))
    
    screen.fill(GREY)
    draw_tetriminos(tetriminos)
    draw_floor(floor)
    space.step(0.02)
    pg.display.update()
    clock.tick(FPS)
import pygame as pg, pymunk as pm

pg.init()
W, H = 800, 600
screen = pg.display.set_mode((W, H))
clock = pg.time.Clock()
FPS = 60
BLACK, GREY, WHITE = (0, 0, 0), (100, 100, 100), (255, 255, 255)
SIZE = 30

# create space
space = pm.Space()
space.gravity = 0, 500
tetrimino_surf = pg.Surface((SIZE, SIZE))
tetriminos = []

def create_tetrimino(x, y):
    """Create tetrimino."""
    body = pm.Body(1, 100, body_type=pm.Body.DYNAMIC)
    body.position = x, y
    shape = pm.Poly.create_box(body, (SIZE, SIZE))  # For collision
    space.add(body, shape)
    return shape

def draw_tetriminos(tetriminos):
    """Draw tetrimino."""
    for tetrimino in tetriminos:
        x, y = int(tetrimino.body.position.x), int(tetrimino.body.position.y)
        rect = tetrimino_surf.get_rect(center=(x, y))
        screen.blit(tetrimino_surf, rect)

def static_floor():
    """Create static floor."""
    body = pm.Body(body_type=pm.Body.STATIC)
    body.position = W // 2, H-200
    shape = pm.Segment(body, (-W // 2, 0), (W // 2, 0), 0)
    space.add(body, shape)
    return shape

def draw_floor(floor):
    """Draw floor."""
    x, y = int(floor.body.position.x), int(floor.body.position.y)
    pg.draw.line(screen, BLACK, (x - W // 2, y), (x + W // 2, y), 1)
    
tetriminos.append(create_tetrimino(100, 100))
floor = static_floor()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()
            elif event.key == pg.K_SPACE:
                tetriminos.append(create_tetrimino(100, 100))
    
    screen.fill(GREY)
    draw_tetriminos(tetriminos)
    draw_floor(floor)
    space.step(0.02)
    pg.display.update()
    clock.tick(FPS)

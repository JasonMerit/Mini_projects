import pygame as pg
import pymunk as pm
from pygame import Vector2 as Vec2
import pymunk.pygame_util
import math


"""Notes
- pymunk has rects defined from their center, while pygame for upper left corner
- dynamic body with its shape without mass will return NaN after step call
- tunneling is a problem, but can be solved by increasing the number of iterations
- I import pygames Vector2 as Vec2, and remember that Vec2d is a pymunk vector with d at the end
- pymunk vec2d can be added to a list
"""
pg.init()

W, H = 800, 600
screen = pg.display.set_mode((W, H))
pg.display.set_caption("Physics with Tim")

BLACK, GREY, WHITE = (0, 0, 0), (100, 100, 100), (255, 255, 255)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)

IMPULSE = 10



def draw(screen, balls, walls, line=None, struct=None, pendulum=None, space=None):
    screen.fill(GREY)

    if space:
        bodies = space.bodies
        for body in bodies:
            # for shape in body.shapes:
            pg.draw.circle(screen, RED, body.position, 10)
        pg.display.flip()
        return

    for b in balls:        
        p = (int(b.body.position.x), int(b.body.position.y))
        r =  int(b.radius)
        pg.draw.line(screen, RED, p, p + b.body.velocity // 2, 2) # draw velocity vector
        pg.draw.circle(screen, b.color, p, r)   # ball
        pg.draw.line(screen, GREEN, p, p + b.body.rotation_vector * r, 2) # rotation marker

    for w in walls:  # TODO only draw once, and update insides of walls only
        p = w.body.position - w.size // 2
        pg.draw.rect(screen, BLACK, pg.Rect(p, w.size))
    
    if line:
        pg.draw.line(screen, BLUE, *line, 2)
    
    if struct:
        for s in struct:
            p = s.body.position - s.size // 2
            pg.draw.rect(screen, s.color, pg.Rect(p, s.size))
    
    if pendulum:
        line, circle, joint = pendulum  # Line connecting circle to joint
        # p_circ = circle.body.position
        # p_joint = joint.a.position

        a = line.a
        b = line.b
        c = circle.body.position
        d = joint.a.position
        e = joint.b.position
        # pg.draw.line(screen, BLUE, a, b, 2)
        # pg.draw.circle(screen, BLUE, c, 20)
        # pg.draw.circle(screen, BLUE, d, 20)
        # pg.draw.circle(screen, BLUE, e, 20)
        pg.draw.line(screen, RED, d, e, 2)
        # pg.draw.line(screen, BLUE, c, d, 2)
        # pg.draw.line(screen, BLUE, c, e, 2)
        # pg.draw.line(screen, BLUE, d, e, 2)


        # Circle
        # pg.draw.circle(screen, RED, p_circ, int(circle.radius))

        # Center of rotation
        # pg.draw.circle(screen, BLUE, p_joint, int(circle.radius))

        # Draw connecting line
        # pg.draw.line(screen, BLACK, p_circ, p_joint, 2)


    pg.display.update()

def create_boundaries(space, width, height):
    """Create boundaries of width 20"""
    # pymunk rects are defined from their center
    rects = [
        [(width//2, height - 10), (width, 20)],  # Bottom
        [(width//2, 10), (width, 20)],          # Top
        [(10, height//2), (20, height)],        # Left
        [(width - 10, height//2), (20, height)] # Right
    ]

    walls = []
    for pos, size in rects:
        # body = pm.Body(10, 1)
        body = pm.Body(body_type=pm.Body.STATIC)
        body.position = pos
        shape = pm.Poly.create_box(body, size)
        shape.size = Vec2(size)
        space.add(body, shape)
        shape.elasticity = 0.4
        shape.friction = 0.5
        walls.append(shape)

    return walls
    
def create_structure(space, width, height):
    BROWN = (100, 50, 0)
    rects = [
        # [(400, height - 120-10), (40, 200), BROWN, 10],
        [(700, height - 120-10), (40, 200), BROWN, 10],
        [(550+50, height - 240-40), (340, 40), BROWN, 10]
    ]
    
    struct = []
    for pos, size, color, mass in rects:
        body = pm.Body()
        body.position = pos
        shape = pm.Poly.create_box(body, size)
        shape.size = Vec2(size)
        shape.mass = mass
        shape.color = color
        shape.elasticity = 0.4
        shape.friction = 0.5
        space.add(body, shape)
        struct.append(shape)
    return struct

def create_pendulum(space):
    rotation_center_body = pm.Body(body_type=pm.Body.STATIC)
    rotation_center_body.position = (500, 180)

    body = pm.Body()
    body.position = rotation_center_body.position# + [100, -20]
    line = pm.Segment(body, (0, 0), body.position, 1)
    # line = pm.Segment(body, (0, 0), (255, 0), 1)  
    circle = pm.Circle(body, 6, body.position)
    # circle = pm.Circle(body, 20, (255, 0))
    line.friction=1
    circle.friction=1
    line.mass=8
    circle.mass = 30
    circle.elasticity = 0.9
    rotation_center_joint = pm.PinJoint(body, rotation_center_body, (0, 0), (0, 0))  # Center of both
    space.add(body, line, circle, rotation_center_joint)
    return line, circle, rotation_center_joint



def create_ball(space, pos, radii=50, mass=1, color=BLACK):
    body = pm.Body(body_type=pm.Body.STATIC)
    # body = pm.Body()
    
    body.position = pos
    shape = pm.Circle(body, radii)
    shape.mass = mass  # REMEMBER THIS LINE
    shape.elasticity = 0.9
    shape.friction = 0.4
    shape.color = color
    space.add(body, shape)
    return shape



def run(screen, W, H):
    run = True
    clock = pg.time.Clock()
    fps = 60
    dt = 1 / fps

    space = pm.Space()
    space.gravity = 0, 500
    walls = create_boundaries(space, W, H) # walls are first 4 elements in space.shapes
    # struct = create_structure(space, W, H)
    struct = None
    pendulum = create_pendulum(space)

    # ball = create_ball(space, (W // 2, 50), 50, 1)
    balls = []
    pressed_pos = None
    ball = None
    while run:
        line = None
        if ball and pressed_pos:
            line = [pressed_pos, pg.mouse.get_pos()]
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break

            if event.type == pg.MOUSEBUTTONDOWN:
                if not ball:
                    pressed_pos = event.pos
                    ball = create_ball(space, pressed_pos, 50, 1)
                    balls = [ball]
                elif pressed_pos:
                    ball.body.body_type = pm.Body.DYNAMIC
                    angle = math.atan2(pressed_pos[1] - event.pos[1], pressed_pos[0] - event.pos[0])
                    dist = Vec2(pressed_pos).distance_to(event.pos) * IMPULSE
                    force = math.cos(angle) * dist, math.sin(angle) * dist
                    ball.body.apply_impulse_at_local_point(force, (0, 0))
                    pressed_pos = None
                    
                else:
                    space.remove(ball.body, ball)
                    balls.clear()
                    ball = None
                    pressed_pos = None
                if ball:
                        assert(not math.isnan(ball.body.position.x)), f'ball.body.position.x is {ball.body.position.x}'

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run = False
                elif event.key == pg.K_SPACE:
                    ball = create_ball(space, (W // 2, 50), 50, 1)                
                    balls.append(ball)
                elif event.key == pg.K_r:
                    ball = None; pressed_pos = None
                    k = len(walls)
                    space.remove(*space.bodies[k:], *space.shapes[k:])  # walls are first four elements
                    struct = create_structure(space, W, H)
                    pendulum = create_pendulum(space)
                    balls.clear()
            if ball:
                assert(not math.isnan(ball.body.position.x)), f'ball.body.position.x is {ball.body.position.x}'
        draw(screen, balls, walls, line, struct, pendulum, space)
        # steps = 100
        # for _ in range(steps): # move simulation forward 0.1 seconds:
        #     space.step(dt / steps)
        step_dt = 1 / 250.0
        x = 0
        while x < dt:
            x += step_dt
            space.step(step_dt)

        # space.step(dt)
        clock.tick(fps)
        
    pg.quit()

if __name__ == "__main__":
    run(screen, W, H)

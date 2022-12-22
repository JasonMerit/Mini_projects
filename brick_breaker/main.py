import pygame as pg
from pygame.math import Vector2 as V2
from typing import List
# import time
from random import randint, choice, seed, random
from math import sqrt, sin, cos, tan, radians, pi

"""
TOOD:
- Spinning wall bounce adds to velocity, but should velocity add to spin?
  It seems that if radial_speed > lin_speed, then spin is reduced otherwise
  spin is increased opposite sign of friction or same sign velocity component.
- Add lives to ball and have them start by default at 2, so that ball shooting starts hitting floor.
- Go slower when holding l_shift when aiming
- Baseclass called Entity that is inherited by Brick, Trick, and Power
- Add touch capability and export to android
- Don'r allow y velocity to be 0

Power ups:
- Flipping x-velocity
- Ghosting
- Paddle for short duration

Optimizations:
- define BRICK_HALF = BRICK_SIZE // 2, used when drawing
- update and draw in same loop - ok, since entities and balls do not interact with themselves
- draw specific entity instead of all entities when updating

Bugs:
- Odd corner collisions rarely occur
"""

pg.init()
pg.font.init()
seed(30)

# W, H = 200, 130
W, H = 400, 510
HUD_OFFSET = 50
CHANGE_SPEED = 0.5
MOVE_SPEED = 2

# colors and font
WHITE, GREY, BLACK_, BLACK = (255, 255, 255), (100, 100, 100), (15, 15, 15), (0, 0, 0)
RED, GREEN, BLUE = (255, 50, 50), (0, 255, 0), (100, 100, 255)
YELLOW, CYAN, MAGENTA = (255, 255, 0), (0, 255, 255), (255, 0, 255)
BROWN, ORANGE, PURPLE = (108, 44, 0), (255, 128, 0), (174, 0, 174)
BEIGE, PINK, TURQUOISE = (255, 255, 128), (255, 128, 255), (128, 255, 255)
EGG, LIME, TEAL = (255, 255, 192), (128, 255, 128), (0, 128, 128)
COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, BEIGE, PINK, EGG, LIME]
FONT = pg.font.Font("brick_breaker/munro.ttf", 30)
BRICK_FONT = pg.font.Font("brick_breaker/munro.ttf", 25)

BALL_COUNT = 1
RADIUS = 8
SPIN_THRESH = 10
MAX_SPEED = 200
MAX_OMEGA = 500
ROT_FRIC = 0.6
WALL_FRIC = 0.9

BRICKS_PER_ROW = 7
BRICK_SIZE = W // BRICKS_PER_ROW #60
BRICK_HITS = 1000
BRICK_PCT = 0.3
TRICK_PCT = 0.3

# create 4 triangles oriented in 4 directions

            
    

POWER_SIZE = BRICK_SIZE // 2
POWER_PCT = 0.1
POWERS = ['+1'] #ghost, 'flip', 'paddle'
POWER_COLORS = {'+1': WHITE, 'ghost': GREEN, 'flip': BLUE, 'paddle': YELLOW}


ZERO, RIGHT, UP, LEFT, DOWN = V2(0, 0), V2(1, 0), V2(0, -1), V2(-1, 0), V2(0, 1)
RIGHT_UP, RIGHT_DOWN, LEFT_DOWN, LEFT_UP = V2(1, -1), V2(1, 1), V2(-1, 1), V2(-1, -1)
DIRS = [(0, 0), (0, -1), (-1, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Prioritize non diagonal directions
KEK = None
KEK_ = 0


# screens
screen = pg.display.set_mode((W, H + HUD_OFFSET))
pg.display.set_caption("Brick Breaker")

hud_screen = pg.Surface((W, HUD_OFFSET))
hud_rect = hud_screen.get_rect()
hud_rect.top = H

dynamic_screen = pg.Surface((W, H))
dynamic_screen_rect = dynamic_screen.get_rect()
dynamic_screen.set_colorkey(BLACK)  # important to let ball screen be transparent

static_screen = pg.Surface((W, H))
static_screen_rect = static_screen.get_rect()

# phsyics
clock = pg.time.Clock()
FPS = 60
GRAVITY = V2(0, 0)

def show(text):
    print(text)
    # 1st draw object
    if isinstance(text, float):
        text = round(text, 2)
    text = FONT.render(f' {text}', True, WHITE)
    text_rect = text.get_rect()
    text_rect.left = hud_rect.left
    text_rect.centery = hud_rect.centery
    
    # 2nd fill screen where last object was and blit new object
    screen.fill(BROWN, (0, H, W // 2 - 20, HUD_OFFSET))  # <-- 20 from radius of ball count
    screen.blit(text, text_rect)  # <-- only update where drawn
    pg.display.update(hud_rect)  # <-- also update hud_rect area

def show_ball_count(count: int):
    text = FONT.render(str(count), True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = hud_rect.center

    screen.fill(BROWN, text_rect)
    pg.draw.circle(screen, BLACK, text_rect.center, 20)
    
    screen.blit(text, text_rect)
    pg.display.update(text_rect)

def blit_screens():
    """Blit all screens to main screen"""
    screen.blit(static_screen, (0, 0))
    screen.blit(dynamic_screen, (0, 0))

class Ball():
    def __init__(self, pos, velocity, omega, radius, color, lives=1):
        self.pos = V2(pos)
        self.vel = V2(velocity)
        
        self.thickness = radius // 8  # thickness of the blue plus

        self.omega = omega
        self.angle = 0
        self.spinning = True

        self.radius = radius
        self.color = color
        self.lives = lives
    
    @property
    def rect(self):
        """Bounding rectangle"""
        return pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, 2 * self.radius, 2 * self.radius)
    
    @property
    def bounds(self):
        """Return left, right, top, bottom bounds of the ball"""
        return self.pos.x - self.radius, self.pos.x + self.radius, self.pos.y - self.radius, self.pos.y + self.radius

    def draw(self):
        pg.draw.circle(dynamic_screen, self.color, self.pos, self.radius)

        # blue plus
        if self.spinning:
            dx = self.radius * cos(radians(self.angle))
            dy = self.radius * sin(radians(self.angle))
            pg.draw.line(dynamic_screen, BLACK_, self.pos - (dx, dy), self.pos + (dx, dy), self.thickness)
            pg.draw.line(dynamic_screen, BLACK_, self.pos + (-dy, dx), self.pos + (dy, -dx), self.thickness)

        # and bounds
        # pg.draw.rect(dynamic_screen, RED, self.rect, 1)

    def update(self, dt):
        """Update ball position and velocity. Return True if ball hit floor"""
        if self.wall_bounce():
            self.lives -= 1
            if self.lives == 0:
                return True
        self.pos += self.vel * dt
        if self.spinning:
            self.angle += self.omega * dt
            self.angle %= 360
    
    def kinematic(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.pos.x -= 1
        if keys[pg.K_RIGHT]:
            self.pos.x += 1
        if keys[pg.K_UP]:
            self.pos.y -= 1
        if keys[pg.K_DOWN]:
            self.pos.y += 1
        if keys[pg.K_RSHIFT]:
            self.angle -= 1
        if keys[pg.K_END]:
            self.angle += 1
            
    def wall_bounce1(self):
        """Continuous collision detection and response using lerping"""
        if self.pos.x - self.radius < 0:  # Left wall
            tc = (self.radius - self.pos.x) / self.vel.x
            self.pos.x += tc * (self.vel.x)
            self.vel.x *= -1
        if self.pos.x + self.radius > W: # Right wall
            tc = (W - self.radius - self.pos.x) / self.vel.x      
            self.pos.x += tc * (self.vel.x)
            self.vel.x *= -1
        if self.pos.y - self.radius < 0: # Top wall
            tc = (self.radius - self.pos.y) / self.vel.y
            self.pos.y += tc * (self.vel.y)
            self.vel.y *= -1
        if self.pos.y + self.radius > H: # Bottom wall
            tc = (H - self.radius - self.pos.y) / self.vel.y      
            self.pos.y += tc * (self.vel.y)
            self.vel.y *= -1

    def wall_bounce2(self):
        """Spinning collision detection and response"""
        # https://www.youtube.com/watch?v=Tb19Y_PR7jk&t=307s
        if self.pos.x - self.radius < 0: # Left wall
            self.pos.x = self.radius
            # self.omega += (1 - WALL_FRIC) * self.vel.x / self.radius
            self.vel.x *= -WALL_FRIC
            if self.spinning:
                self.vel.y += (1 - ROT_FRIC) * self.omega * self.radius * dt
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH
        elif self.pos.x + self.radius > W: # Right wall
            self.pos.x = W - self.radius
            self.vel.x *= -WALL_FRIC
            if self.spinning:
                self.vel.y -= (1 - ROT_FRIC) * self.omega * self.radius * dt
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH
        if self.pos.y - self.radius < 0: # Top wall
            self.pos.y = self.radius
            # self.omega += (1 - WALL_FRIC) * self.vel.x * 10
            self.vel.y *= -WALL_FRIC
            if self.spinning:
                self.vel.x -= (1 - ROT_FRIC) * self.omega * self.radius * dt  # flip sign because hitting top flips friction direction
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH
        elif self.pos.y + self.radius > H: # Bottom wall
            self.pos.y = H - self.radius
            # self.omega -= (1 - WALL_FRIC) * self.vel.x * 10
            self.vel.y *= -WALL_FRIC
            if self.spinning:
                self.vel.x += (1 - ROT_FRIC) * self.omega * self.radius * dt
                self.omega *= -ROT_FRIC
                # self.spinning = not abs(self.omega) < SPIN_THRESH

    def wall_bounce(self):
        """Discrete collision detection and response. Return True if ball hit floor"""
        if self.pos.x < self.radius: # Left wall
            self.pos.x = self.radius
            self.vel.x *= -1
        elif self.pos.x + self.radius > W: # Right wall
            self.pos.x = W - self.radius
            self.vel.x *= -1
        if self.pos.y < self.radius: # Top wall
            self.pos.y = self.radius
            self.vel.y *= -1
        elif self.pos.y + self.radius > H: # Bottom wall
            self.pos.y = H - self.radius
            self.vel.y *= -1
            return True
    
    def __repr__(self):
        return f"Ball(x={self.pos.x})"

class Entity():
    def __init__(self, indices, size=BRICK_SIZE):
        self.j, self.i = indices  # for grid lookup
        self._pos = V2(self.i, self.j) * BRICK_SIZE  # flipped
        self.size = size

        offset = (BRICK_SIZE - self.size) / 2
        self.offset = V2(offset, offset)
        self.rect = pg.Rect(self._pos + self.offset, (size, size))
        self.left, self.right = self._pos.x, self._pos.x + self.size
        self.top, self.bot = self._pos.y, self._pos.y + self.size
    
    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos: V2):
        self._pos = pos
        self.rect.topleft = pos + self.offset
        self.left, self.right = pos.x, pos.x + self.size
        self.top, self.bot = pos.y, pos.y + self.size
    
    def draw(self):
        raise NotImplementedError
    
    def __repr__(self) -> str:
        return f'Entity{(self.j, self.i)}'

class Brick(Entity):
    def __init__(self, indices, color, hits=BRICK_HITS):
        super().__init__(indices, BRICK_SIZE)
        self.color = color
        self.hits = hits
    
    def draw(self):
        pg.draw.rect(static_screen, self.color, self.rect)        
        # pg.draw.rect(static_screen, GREY, (self._pos.x, self._pos.y + self.size.y - 5, self.size.x, 3))
        pg.draw.rect(static_screen, BLACK, self.rect, 3)
        
        text = BRICK_FONT.render(str(self.hits), True, BLACK)
        static_screen.blit(text, self._pos + (BRICK_SIZE // 2 - text.get_width() // 2, BRICK_SIZE // 2 - text.get_height() // 2))

        # draw bounding box
        pg.draw.rect(static_screen, RED, self.rect, 1)

    def collide(self, ball: Ball, heading: V2):
        """Check if ball is colliding with brick from heading. Return collision depth and normal"""
        if heading in [LEFT, RIGHT, UP, DOWN]:
            # check if this side intersects with ball boundary
            if heading == LEFT:  # ball is moving left so side is right
                depth = ball.radius + self.right - ball.pos.x
                if depth > 0 and self.right < ball.pos.x + ball.radius:                      
                    return depth, -heading
            elif heading == RIGHT:
                depth = ball.pos.x + ball.radius - self.left
                if depth > 0 and self.left > ball.pos.x - ball.radius:
                    return depth, -heading
            elif heading == UP:
                depth = ball.radius + self.bot - ball.pos.y
                if depth > 0 and self.bot < ball.pos.y + ball.radius:
                    return depth, -heading
            elif heading == DOWN:
                depth = ball.pos.y + ball.radius - self.top
                if depth > 0 and self.top > ball.pos.y - ball.radius:
                    return depth, -heading

        elif heading in [LEFT_UP, RIGHT_UP, LEFT_DOWN, RIGHT_DOWN]:
            # check if corner is contained by ball
            corner = self.pos + (BRICK_SIZE * (heading.x < 0), BRICK_SIZE * (heading.y < 0))
            
            if (depth := ball.radius - (corner - ball.pos).length()) > 0:
                # determine closest side
                # normal = V2(0, -heading.y) if abs(corner.x - ball.pos.x) < abs(corner.y - ball.pos.y) else V2(-heading.x, 0)
                normal = -heading  # reflects the velocity vector
                return depth, normal

    def hit(self, value):
        self.hits -= value
        if self.hits <= 0:
            self.hits = 0
            return True

class Trick(Brick):
    """Brick, but triangled"""

    def __init__(self, indices, color, hits=BRICK_HITS, orientation=0):
        super().__init__(indices, color, hits)
        self.trick = orientation
    
    @property
    def points(self):
        orientations = [[self.rect.topleft, self.rect.bottomleft, self.rect.topright],
                        [self.rect.topright, self.rect.topleft, self.rect.bottomright],
                        [self.rect.bottomright, self.rect.topright, self.rect.bottomleft],
                        [self.rect.bottomleft, self.rect.bottomright, self.rect.topleft]]
        return orientations[self.trick]
    
    @property
    def defining_corner(self):
        return self.points[0]
    
    def draw(self):
        """Draw triangle"""
        pg.draw.polygon(static_screen, self.color, self.points)
        pg.draw.polygon(static_screen, BLACK, self.points, 3)

        # draw hits offset towards defining corner
        text = BRICK_FONT.render(str(self.hits), True, BLACK)
        offset = V2(self.defining_corner) - self.rect.center
        static_screen.blit(text, self.rect.center + offset // 2 - V2(text.get_width() // 2, text.get_height() // 2))

        # draw bounding box
        pg.draw.rect(static_screen, RED, self.rect, 1)

    def collide(self, ball: Ball, heading: V2):
        """Check if ball is colliding with brick from heading. Return collision depth and normal"""
        # 1) bounding box
        # 2) Horizontal/vertical sides
        # 3) Sloped sides
        global KEK

        if not self.rect.colliderect(ball.rect): 
            KEK = None
            # show("NONE")
            return

        x, y = self.defining_corner
        start, end = V2(self.points[1]), V2(self.points[2])
        v = end - start
        length = v.length()
        dot = (ball.pos - start).dot(v) / length ** 2
        closest = start + dot * v  # Assume closest point is on the line segment, because of grid lookup
        # KEK = closest
        dist = (closest - ball.pos).length()
        if dist < ball.radius:
            normal = V2(-v.y, v.x).normalize()
            # normal = - heading
            depth = ball.radius - dist
            KEK = depth, normal
            # show("SLOPE")
            return ball.radius - dist, normal

        dist = abs(ball.pos.y - y)
        if dist < ball.radius:
            # normal = UP if ball.pos.y < y else DOWN
            depth = ball.radius - dist
            normal = -heading
            KEK = depth, normal
            # show("HORIZONTAL")
            return ball.radius - dist, normal
        
        dist = abs(ball.pos.x - x)
        if dist < ball.radius:
            # normal = LEFT if ball.pos.x < x else RIGHT
            normal = -heading
            depth = ball.radius - dist
            KEK = depth, normal
            # show("VERTICAL")
            return ball.radius - dist, normal

        
        # if not heading == ZERO: return # ignore if ball is not contained in brick
        # check if ball is colliding with any of the triangle's straight sides
        
class Power(Entity):
    def __init__(self, indices, power_type: str):
        super().__init__(indices, size=POWER_SIZE)
        self.type = power_type
        self.color = POWER_COLORS[power_type]
    
    def draw(self):
        # draw power up as a ball circle encircled by a white circle
        pg.draw.circle(static_screen, self.color, self._pos + (self.size, self.size), RADIUS)
        pg.draw.circle(static_screen, WHITE, self._pos + (self.size, self.size), self.size // 2, 2)

        # draw bounding box
        pg.draw.rect(static_screen, RED, self.rect, 1)

class Player():
    def __init__(self):
        self.pos = V2(W // 2, H - RADIUS)
        self.a = 90

        self.speed = MOVE_SPEED
        self.omega = 1
    
    def play(self):        
        self.cast_ray()
        self.draw()
        return self.input()
    
    def input(self):
        """Aim and shoot ball"""
        keys = pg.key.get_pressed()
        # go slower if holding shift
        
        if keys[pg.K_a]: 
            x = self.pos.x - self.speed
            x = max(x, 1)
            self.pos.x = x
        if keys[pg.K_d]: 
            x = self.pos.x + self.speed
            x = min(x, W - 1)
            self.pos.x = x
        if keys[pg.K_e]: 
            self.a += self.omega
            self.a = min(self.a, 170)
        if keys[pg.K_q]: 
            self.a -= self.omega
            self.a = max(self.a, 10)
        if keys[pg.K_SPACE]:
            return self.ray
        if keys[pg.K_ESCAPE]:
            pg.quit()
            quit()
        
        # touch screen
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LSHIFT:
                    self.speed = MOVE_SPEED // 2
                    self.omega = 0.5
            elif event.type == pg.KEYUP:
                if event.key == pg.K_LSHIFT:
                    self.speed = MOVE_SPEED
                    self.omega = 1

    def draw(self):
        dynamic_screen.fill(BLACK)
        
        pg.draw.line(dynamic_screen, WHITE, self.pos, self.pos + self.ray * 100, 3)
        pg.draw.circle(dynamic_screen, GREEN, self.pos, 10)

        blit_screens()        
        pg.display.update(dynamic_screen_rect)
    
    def cast_ray(self):
        """Cast ray from player to ball and return brick hit"""
        self.ray = V2(-1, 0).rotate(self.a)
        
        
class Game():
    """Game class
    Call draw_static() whenever bricks are updated.
    Use show() to display text on screen.
    Grid has redunant first row left empty for easier indexing and posiitoning."""     
    
    @property
    def ball_count(self):
        return self._ball_count
    
    @ball_count.setter
    def ball_count(self, value):
        self._ball_count = value
        show_ball_count(self._ball_count)

    """Game functions"""
    def reset(self):
        self.score = 0
        self.level = 1
        self.ball = None       
        self.balls : List[Ball] = []
        
        self.bricks : List[Brick] = []
        self.powers : List[Power] = []
        empty_row = [None] * BRICKS_PER_ROW
        self.grid : List[List[Brick]] = [empty_row.copy() for _ in range(BRICKS_PER_ROW+1)]

        # randomly fill screen with bricks and powers
        for j in range(1, BRICKS_PER_ROW+1):
            for i in range(BRICKS_PER_ROW):
                if random() < BRICK_PCT:
                    if random() < TRICK_PCT:
                        brick = Trick((j, i), choice(COLORS), self.level, randint(0, 3))
                    else:
                        brick = Brick((j, i), choice(COLORS), self.level)
                    self.bricks.append(brick)
                    self.grid[j][i] = brick
                elif random() < POWER_PCT:
                    power = Power((j, i), choice(POWERS))
                    self.powers.append(power)
                    self.grid[j][i] = power

        self.draw_static()
        self.malthe = Player()
        self.floor_x = W // 2  # x position malthe is reset to
        self.floor_x_last = self.floor_x
        self.fps = FPS
        self.dt = 1 / FPS

        hud_screen.fill(BROWN)
        screen.blit(hud_screen, (0, H))
        self.ball_count = BALL_COUNT
        pg.display.update(hud_rect)
        
    def run(self):
        """Main game loop covering player aiming, shooting and ball movement"""
        # Three loops:
        # 1) Aim player
        # 2) Shoot balls
        # 3) Wait until all balls are gone

        while True:
            
            # 1) let player aim              
            while True:
                if ray := self.malthe.play(): 
                    
                    break
                self.events()
                clock.tick(self.fps)
            
            
            # 2) Shoot ball in intervals
            t = 0            
            ball_count = self._ball_count
            while ball_count:
                if t % 10 == 0:
                    self.balls.append(Ball(self.malthe.pos, ray * 500, 0, RADIUS, RED))
                    ball_count -= 1
                pg.draw.line(dynamic_screen, WHITE, self.malthe.pos, self.malthe.pos + self.malthe.ray * 100, 3)
                pg.draw.circle(dynamic_screen, GREEN, self.malthe.pos, 10)
                self.update()
                self.events()
                self.draw_dynamic()
                clock.tick(self.fps)
                t += 1
            
            # 3) Balls are flying around
            while self.balls:
                self.update()
                self.events()
                self.draw_dynamic()
                clock.tick(self.fps)
            
            # Prepare for next round
            self.malthe.pos.x = self.floor_x
            self.floor_x_last = self.floor_x
            # self.floor_x = W // 2 # reset to floor_x last?
            self.malthe.a = 90
            self.balls.clear()
            if self.scroll():
                self.game_over()
            # else:
            #     show("")

    def update(self):
        """Update ball positions and check for collisions.
        Update floor_x to firs floor touch."""
        for ball in self.balls:
            if ball.update(self.dt):
                self.balls.remove(ball)
                if self.floor_x == self.floor_x_last:
                    self.floor_x = ball.pos.x
            else:
                self.entity_collide(ball)
    
    def events(self):        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print(event.pos)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                if event.key == pg.K_r:
                    self.reset()
                if event.key == pg.K_s:
                    self.dt *= CHANGE_SPEED
                    self.fps *= CHANGE_SPEED
                if event.key == pg.K_RETURN:
                    # show("HAWLEAWE")
                    self.scroll()
                if event.key == pg.K_BACKSPACE:
                    self.recall_balls()
            
            if event.type == pg.KEYUP:
                if event.key == pg.K_s:
                    self.dt /= CHANGE_SPEED
                    self.fps /= CHANGE_SPEED

    def draw_dynamic(self):
        dynamic_screen.fill(BLACK)
        if self.ball:
            self.ball.draw()
        for ball in self.balls:
            ball.draw()
        
        blit_screens()
        pg.display.update()
    
    def draw_static(self):
        static_screen.fill(BLACK)
        for brick in self.bricks:
            brick.draw()
        for power in self.powers:
            power.draw()
  
    def game_over(self):
        pass
        # show("Game over")
    
    def recall_balls(self):
        """Recall all balls to player"""
        self.balls.clear()

    """Entity functions"""
    def pos2grid(self, pos):
        x, y = pos // BRICK_SIZE
        return (int(y), int(x))

    def entity_collide(self, ball: Ball):
        j, i = self.pos2grid(ball.pos)
        
        # check power up
        if 0 <= j < len(self.grid) and 0 <= i< len(self.grid[0]):
            if type(power := self.grid[j][i]) == Power and power.rect.colliderect(ball.rect):
                self.powers.remove(power)
                self.grid[j][i] = None
                
                self.draw_static()
                self.collect_power(power)

        # check neighbors
        for di, dj in DIRS:
            if 0 <= j + dj < len(self.grid) and 0 <= i + di < len(self.grid[0]):
                entity = self.grid[j + dj][i + di]

                if isinstance(entity, Brick) and (result := entity.collide(ball, V2(di, dj))): # COLLISION!
                    # alter ball position and velocity
                    depth, normal = result
                    ball.pos += depth * normal
                    # if normal.x == 0:  # vertical collision
                    #     ball.vel.y *= -1
                    # elif normal.y == 0:  # horizontal collision
                    #     ball.vel.x *= -1
                    # else:  # diagonal collision, so we need to split the velocity
                    if ball.vel.y != 0 and ball.vel.x != 0 or di == dj == 0:  # later only for diagonal collision
                        ball.vel = ball.vel.reflect(normal)
                    else:
                        ball.vel = - ball.vel.project(V2(di, dj))

                    # update brick
                    destroyed = entity.hit(1)
                    if destroyed:
                        self.remove_entity(entity)  
                    self.draw_static()                  

    def remove_entity(self, entity: Entity):
        # self.score += 1
        self.grid[entity.j][entity.i] = None
        list = self.bricks if isinstance(entity, Brick) else self.powers
        list.remove(entity)

    def collect_power(self, power):
        if power.type == "+1":
            self.ball_count += 1

    def scroll(self):
        """Scroll entities down one row and add new row at top.
        Return True if game over."""
        self.level += 1

        # scroll entities down
        for row in self.grid[1:-1]: # skip first and last row
            for entity in row:
                if entity is None: continue
                entity.pos += V2(0, BRICK_SIZE)
                entity.j += 1

        # add new bricks and insert to second entree of list
        brick_added = False
        row = [None] * BRICKS_PER_ROW
        for i in range(BRICKS_PER_ROW):
            if random() < BRICK_PCT:
                if random() < TRICK_PCT:
                    brick = Trick((1, i), choice(COLORS), self.level, randint(0, 3))
                else:
                    brick = Brick((1, i), choice(COLORS), self.level)
                row[i] = brick
                self.bricks.append(brick)
                brick_added = True
            elif random() < POWER_PCT:
                power = Power((1, i), "+1")
                self.powers.append(power)
                row[i] = power

        # ensure at least one brick in row
        if not brick_added:
            i = randint(0, BRICKS_PER_ROW - 1)
            row[i] = Brick((1, i), choice(COLORS), hits=self.level)
            self.bricks.append(row[i])
        
        # ensure not filled with bricks
        if all(isinstance(e, Brick) for e in row):
            row[randint(0, BRICKS_PER_ROW - 1)] = None
        self.grid.insert(1, row)
        
        # delete bricks that are out of bounds
        game_over = False
        for entity in self.grid[-1]:
            if entity is None: continue
            list = self.bricks if isinstance(entity, Brick) else self.powers
            list.remove(entity)
            game_over = True
        self.grid.pop()

        # draw bricks
        self.draw_static()

        return game_over


    """Test methods"""
    def test(self, i=None):
        if i is None: return
        method = getattr(self, f"test{i}")
        method()
    
    def test0(self):  # Collision test
        self.ball = Ball((W // 2, H // 2), (0,0), 0, RADIUS, RED)

        self.bricks : List[Brick] = []
        empty_row = [None] * BRICKS_PER_ROW
        self.grid : List[List[Brick]] = [empty_row.copy() for _ in range(BRICKS_PER_ROW)]
        j, i = 3, 3
        brick = Brick((j, i), choice(COLORS))
        self.bricks.append(brick)
        self.grid[j][i] = brick     

        self.draw_static()   

        while True:
            self.ball.kinematic()
            self.entity_collide(self.ball)
            self.events()

            dynamic_screen.fill(BLACK)
            self.ball.draw()
            blit_screens()
            pg.display.update()

            clock.tick(self.fps)
    
    def test1(self):  # Wntities test
        self.ball = Ball((W // 2, H // 2), (0,0), 0, RADIUS, RED)

        self.bricks : List[Brick] = []
        self.powers : List[Power] = []
        empty_row = [None] * BRICKS_PER_ROW
        self.grid : List[List[Brick]] = [empty_row.copy() for _ in range(BRICKS_PER_ROW)]
        j, i = 3, 3

        # trick = Brick((j, i), choice(COLORS))
        trick0 = Trick((j, i), choice(COLORS), orientation=3)
        self.bricks.append(trick0)
        self.grid[j][i] = trick0

        # trick1 = Trick((j, i+2), choice(COLORS), orientation=1)
        # self.bricks.append(trick1)
        # self.grid[j][i] = trick1

        # trick2 = Trick((j, i+1), choice(COLORS), orientation=2)
        # self.bricks.append(trick2)
        # self.grid[j][i] = trick2

        # trick3 = Trick((j, i-1), choice(COLORS), orientation=3)
        # self.bricks.append(trick3)
        # self.grid[j][i] = trick3

        # power = Power((j, i), "+1")
        # self.powers.append(power)
        # self.grid[j][i] = power

        # j -= 1
        # brick = Brick((j, i), choice(COLORS))
        # self.bricks.append(brick)
        # self.grid[j][i] = brick
        # j += 1

        # i -= 1
        # brick = Brick((j, i), choice(COLORS))
        # self.bricks.append(brick)
        # self.grid[j][i] = brick

        # i += 2
        # brick = Brick((j, i), choice(COLORS))
        # self.bricks.append(brick)
        # self.grid[j][i] = brick

        self.draw_static()   

        while True:
            self.ball.kinematic()
            self.entity_collide(self.ball)
            self.events()
            dynamic_screen.fill(BLACK)
            self.ball.draw()
            
            if KEK:
                depth, normal = KEK
                normal = normal * 100
                pg.draw.line(dynamic_screen, GREEN, self.ball.pos, self.ball.pos + normal, 5)
            # draw bounding box of ball
            pg.draw.rect(dynamic_screen, RED, self.ball.rect, 1)
            blit_screens()
            pg.display.update()

            clock.tick(self.fps)

if __name__ == "__main__":
    game = Game()
    game.reset()
    # game.test(1)
    game.run()



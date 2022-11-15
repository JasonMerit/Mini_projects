"""Implementation of Reudicble video https://www.youtube.com/watch?v=eED4bSkYCB8&list=LL&index=2&t=16s"""

import pygame as pg
import random
import psutil

# Initialize pg
pg.init()

# Create the screen
W, H = 800, 400
win = pg.display.set_mode((W, H))
pg.display.set_caption("Collision")

# Constants
WHITE, GREY, BLACK, RED, GREEN, BLUE, YELLOW = (255, 255, 255), (128, 128, 128), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)
RAINBOW = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
FPS = 60
INIT_COUNT = 10
dt = 1 / FPS

# Settings
continuous = True  
elastic = False
random.seed(3)  

# Variables
critical_temp = 80.0

# Create the clock
clock = pg.time.Clock()

# Create the ball
class Ball:
    def __init__(self, pos, vel, acc, radius, color):
        self.x, self.y = pos
        self.dx, self.dy = vel
        self.ax, self.ay = acc
        self.r = radius
        self.color = color

    def draw(self, win):
        pg.draw.circle(win, self.color, (self.x, self.y), self.r)

    def move(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and self.x > self.r:
            self.dx *= 0.9
        if keys[pg.K_RIGHT] and self.x < W - self.r:
            self.dx *= 1.1
        if keys[pg.K_UP] and self.y > self.r:
            self.dy *= 1.1
        if keys[pg.K_DOWN] and self.y < H - self.r:
            self.dy *= 0.9

    def collide(self):
        # Wall collision detection
        if continuous:
            # Continuous collision detection using lerping
            if self.x - self.r < 0:  # Left wall
                tc = (self.r - self.x) / self.dx
                self.x += tc * (self.dx)
                self.dx *= -1
            if self.x + self.r > W: # Right wall
                tc = (W - self.r - self.x) / self.dx      
                self.x += tc * (self.dx)
                self.dx *= -1
            if self.y - self.r < 0: # Top wall
                tc = (self.r - self.y) / self.dy
                self.y += tc * (self.dy)
                self.dy *= -1
            if self.y + self.r > H: # Bottom wall
                tc = (H - self.r - self.y) / self.dy      
                self.y += tc * (self.dy)
                self.dy *= -1
            return 

        if self.x - self.r < 0:
            self.x = self.r
            self.dx *= -1
        if self.x + self.r > W:
            self.x = W - self.r
            self.dx *= -1
        if self.y - self.r < 0:
            self.y = self.r
            self.dy *= -1
        if self.y + self.r > H:
            self.y = H - self.r
            self.dy *= -1
    
    def update(self):
        # Particle dynamics
        self.dx += self.ax * dt
        self.dy += self.ay * dt
        self.x += self.dx
        self.y += self.dy
        self.move()
        self.collide()

class Box():

    def __init__(self, acc, count):
        self.acc = acc
        self.count = count
        self.balls = []
        self.reset()

        self.ball_colliding = lambda a, b: (a.x - b.x) ** 2 + (a.y - b.y) ** 2 <= (a.r + b.r) ** 2

    def reverse(self):
        for self.ball in self.balls:
            self.ball.dx *= -1
            self.ball.dy *= -1

    def reset(self):
        self.balls.clear()
        for _ in range(self.count):
            pos = random.randint(0, W), random.randint(0, H)
            vel = random.randint(-5, 5), random.randint(-5, 5)
            r = random.randint(10, 20)
            self.balls.append(Ball(pos, vel, self.acc, r, random.choice(RAINBOW)))
    
    def update(self):
        # Update the balls
        for ball in self.balls:
            ball.update()

        # Check for ball collisions
        self.ball_collision()

        # Draw the screen
        win.fill(BLACK)
        for ball in self.balls:
            ball.draw(win)
        pg.display.update()


    def ball_collision(self):
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                if self.ball_colliding(self.balls[i], self.balls[j]):  
                    # Elastic collision with conservation of momentum and energy
                    # https://en.wikipedia.org/wiki/Elastic_collision#Two-dimensional_collision_with_two_moving_objects
                    a, b = self.balls[i], self.balls[j]
                    if elastic:
                        
                        continue

                    # still elastic collision but with conservation of energy only
                    a.dx, b.dx = b.dx, a.dx
                    a.dy, b.dy = b.dy, a.dy
    
    def nudge(self):
        for ball in self.balls:
            ball.dx += random.randint(-1, 1)
            ball.dy += random.randint(-1, 1)

def process_events():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return True
            elif event.key == pg.K_r:
                box.reset()
            elif event.key == pg.K_SPACE:
                box.nudge()
            elif event.key == pg.K_f:                
                box.reverse()
            elif event.key == pg.K_c:
                global continuous
                continuous = not continuous

if __name__ == "__main__":
    # Create the balls
    box = Box((0, 10), INIT_COUNT)

    # Main loop
    done = False
    while not done:
        clock.tick(FPS)

        # Stop if overheat
        # if psutil.sensors_temperatures()['coretemp'][0].current > critical_temp:
        #     break
        done = process_events()
        box.update()

    pg.quit()
"""Implementation of Reudicble video https://www.youtube.com/watch?v=eED4bSkYCB8&list=LL&index=2&t=16s"""

import pygame as pg
import random
from VectorMath import V
import psutil

# Initialize pg
pg.init()

# pygame window and clock
W, H = 800, 400
win = pg.display.set_mode((W, H))
pg.display.set_caption("Collision")
clock = pg.time.Clock()

# Constants
WHITE, GREY, BLACK, RED, GREEN, BLUE, YELLOW = (255, 255, 255), (128, 128, 128), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)
RAINBOW = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
FPS = 60
K = FPS * 5  # Characteristic magnitude
INIT_COUNT = 10
ACC = (0, 0)
dt = 1 / FPS

# Settings
continuous = True  # Lerping ball position to actual position after colliding with wall
elastic = True     # Moementum and energy conservation
detections = ["None", "Sweep and Prune", "Bounding Volume Hierarchy"]
detection = 1
random.seed(3)  

# Variables
critical_temp = 80.0


# Create the ball
class Ball:
    def __init__(self, pos, vel, acc, radius, color):
        self.p = V(pos)
        self.v = V(vel)
        self.a = V(acc)
        self.r = radius
        self.color = color

        self.m = self.r ** 2

    def draw(self, win):
        pg.draw.circle(win, self.color, tuple(self.p), self.r)

    def move(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.v.x *= 0.9
        if keys[pg.K_RIGHT]:
            self.v.x *= 1.1
        if keys[pg.K_UP]:
            self.v.y *= 1.1
        if keys[pg.K_DOWN]:
            self.v.y *= 0.9

    def collide(self):
        # Wall collision detection
        if continuous:
            # Continuous collision detection and response using lerping
            if self.p.x - self.r < 0:  # Left wall
                tc = (self.r - self.p.x) / self.v.x
                self.p.x += tc * (self.v.x)
                self.v.x *= -1
            if self.p.x + self.r > W: # Right wall
                tc = (W - self.r - self.p.x) / self.v.x      
                self.p.x += tc * (self.v.x)
                self.v.x *= -1
            if self.p.y - self.r < 0: # Top wall
                tc = (self.r - self.p.y) / self.v.y
                self.p.y += tc * (self.v.y)
                self.v.y *= -1
            if self.p.y + self.r > H: # Bottom wall
                tc = (H - self.r - self.p.y) / self.v.y      
                self.p.y += tc * (self.v.y)
                self.v.y *= -1
            return 

        if self.p.x - self.r < 0: # Left wall
            self.p.x = self.r
            self.v.x *= -1
        if self.p.x + self.r > W: # Right wall
            self.p.x = W - self.r
            self.v.x *= -1
        if self.p.y - self.r < 0: # Top wall
            self.p.y = self.r
            self.v.y *= -1
        if self.p.y + self.r > H: # Bottom wall
            self.p.y = H - self.r
            self.v.y *= -1
    
    def update(self):
        # Particle dynamics
        self.move()
        self.collide()
        
        self.v += self.a * dt
        self.p += self.v * dt

class Box():

    def __init__(self, acc, count):
        self.acc = acc
        self.count = count
        self.balls = []
        self.reset()

        self.ball_colliding = lambda a, b: (a.p.x - b.p.x) ** 2 + (a.p.y - b.p.y) ** 2 <= (a.r + b.r) ** 2

    def reverse(self):
        for self.ball in self.balls:
            self.ball.v *= -1

    def reset(self):
        self.balls.clear()
        for i in range(1, self.count+1):
            pos = i * W / self.count, random.randint(0, H)
            vel = random.uniform(-1, 1) * K, random.uniform(-1, 1) * K
            r = random.randint(10, 20)
            self.balls.append(Ball(pos, vel, self.acc, r, random.choice(RAINBOW)))
    
    def update(self):
        # Update the balls
        for ball in self.balls:
            ball.update()

        # Check for ball collisions
        self.ball_collision_detection()

        # Draw the screen
        win.fill(BLACK)
        for ball in self.balls:
            ball.draw(win)
        pg.display.update()

    def sweep_and_prune(self):
        # Sort the balls by x position
        self.balls.sort(key=lambda ball: ball.p.x)

        # Sweep and prune
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                if self.balls[j].p.x - self.balls[i].p.x > self.balls[i].r + self.balls[j].r:
                    break
                if self.ball_colliding(self.balls[i], self.balls[j]):
                    self.ball_collision_response(self.balls[i], self.balls[j])

    def ball_collision_detection(self):
        self.sweep_and_prune()
        # for i in range(len(self.balls)):
        #     for j in range(i + 1, len(self.balls)):
        #         if detection == 0:
        #             if self.ball_colliding(self.balls[i], self.balls[j]):  
        #                 self.collide_balls(self.balls[i], self.balls[j])
        #         elif detection == 1:
        #             if self.sweep_and_prune(self.balls[i], self.balls[j]):
        #                 self.collide_balls(self.balls[i], self.balls[j])
    
    def ball_collision_response(self, a, b):
        # Elastic collision with conservation of momentum and energy
        # https://en.wikipedia.org/wiki/Elastic_collision#Two-dimensional_collision_with_two_moving_objects
        if elastic:
            ratio = 2 / (a.m + b.m)  * (a.v - b.v).dot(a.p - b.p)  /  (a.p - b.p).norm_squared()
            v1 = b.m * ratio * (a.p - b.p)
            v2 = a.m * ratio * (b.p - a.p)
            a.v -= v1
            b.v -= v2
            return

        # still elastic collision but with conservation of energy only
        a.v, b.v = b.v, a.v
    
    def nudge(self):
        for ball in self.balls:
            ball.v.x += random.randint(-1, 1)
            ball.v.y += random.randint(-1, 1)

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
    box = Box(ACC, INIT_COUNT)

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
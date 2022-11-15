import pygame as pg
from math import sin, cos
import random

# colors
BLUE, RED, YELLOW, GREEN, WHITE = (0, 0, 255), (255, 0, 0), (255, 255, 0), (0, 255, 0), (255, 255, 255)
COLORS = [BLUE, RED, YELLOW, GREEN, WHITE]

pg.init()

class Boid():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.speed = 1
        self.vx = 0
        self.vy = 0

        self.size = 5
    
    def move(self, x, y, xv, yv):
        # Move the boid towards (x, y) and velocity towards (xv, yv)
        self.x += (x - self.x) * 0.01
        self.y += (y - self.y) * 0.01
        self.vx += (xv - self.vx) * 0.01
        self.vy += (yv - self.vy) * 0.01

        self.x += self.vx; self.y += self.vy

        # Limit the speed
        if self.vx > self.speed: self.vx = self.speed
        if self.vy > self.speed: self.vy = self.speed
        if self.vx < -self.speed: self.vx = -self.speed
        if self.vy < -self.speed: self.vy = -self.speed


class Boids():
    def __init__(self, width, height, count):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.screen.fill((0, 0, 0))
        self.boids = []
        for i in range(count):
            x, y = random.randint(0, width), random.randint(0, height)
            self.boids.append(Boid(x, y, COLORS[i % len(COLORS)]))

    def draw(self):
        for boid in self.boids:
            pg.draw.circle(self.screen, boid.color, (int(boid.x), int(boid.y)), boid.size)
        pg.display.flip()
    
    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                elif event == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        return
                
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))
            self.draw()
            cx = 0; cy = 0
            axv = 0; ayv = 0
            for boid in self.boids:
                # Cohesion
                cx += boid.x; cy += boid.y

                # Alignment
                axv += boid.vx; ayv += boid.vy

                # Separation
                for boid2 in self.boids:
                    if boid != boid2:
                        if abs(boid.x - boid2.x) < 50 and abs(boid.y - boid2.y) < 50:
<<<<<<< Updated upstream
                            boid.vx -= boid.x - boid2.x
                            boid.vy -= boid.y - boid2.y
=======
                            boid.vx += boid.x - boid2.x
                            boid.vy += boid.y - boid2.y
>>>>>>> Stashed changes

            cx /= len(self.boids); cy /= len(self.boids)
            axv /= len(self.boids); ayv /= len(self.boids)
            for boid in self.boids:
                boid.move(cx, cy, axv, ayv)
    
if __name__ == "__main__":
    boids = Boids(640, 480, 20)
    boids.run()



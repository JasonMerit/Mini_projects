import pygame as pg
import numpy as np
from random import randint

# ---------- Visualizing --------
size = 24
W = 10; H = 15
screen = pg.display.set_mode([W * size, H * size])
pg.display.set_caption('Balls')
pg.font.init()
font1 = pg.font.SysFont("comicsans", 40)
font2 = pg.font.SysFont("comicsans", 15)

# ---------- Constants --------
WHITE, GREY, BLACK = (255, 255, 255),  (200, 200, 200), (0, 0, 0)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
COUNT = 50
COOLING = 0.9999
HEATING = 1.5
EPS = 1e-6

class Ball:
    def __init__(self, x, y, dx, dy, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.r = 4

    def draw(self):
        pg.draw.circle(screen, self.color, (self.x, self.y), self.r)

    def move(self):
        self.x += self.dx
        self.y += self.dy

        self.collide_wall()
        self.collide_mouse(pg.mouse.get_pos())

        print(self.get_temperature() * 255 / (temp + EPS))
        self.color = (self.get_temperature() * 255 / (temp + EPS), 0, 0)

    def collide(self, other):
        if (self.x - other.x)**2 + (self.y - other.y)**2 < (self.r + other.r)**2:
            self.reverse()
            other.reverse()
    
    def collide_wall(self):
        if self.x < self.r or self.x > W * size - self.r:
            self.dx *= -1
        if self.y < self.r or self.y > H * size - self.r:
            self.dy *= -1
    
    def collide_mouse(self, mouse_pos):
        if (self.x - mouse_pos[0])**2 + (self.y - mouse_pos[1])**2 < self.r**2:
            self.dx *= -1
            self.dy *= -1
    
    def ellipse(self):
        return pg.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)
    
    def get_energy(self):
        return 0.5 * self.r**2 * (self.dx**2 + self.dy**2)
    
    def get_momentum(self):
        return self.r**2 * (self.dx + self.dy)
    
    def get_kinetic_energy(self):
        return 0.5 * self.r**2 * (self.dx**2 + self.dy**2)
    
    def get_potential_energy(self):
        return 0
    
    def get_temperature(self):
        return self.get_kinetic_energy() / (1.5 * self.r**2)
    
    def get_pressure(self):
        return self.get_temperature() / (self.r**2)
    
    def get_volume(self):
        return 4/3 * np.pi * self.r**3
    
    def get_mass(self):
        return self.r**2
    
    def get_speed(self):
        return np.sqrt(self.dx**2 + self.dy**2)
    
    def get_speed_vector(self):
        return np.array([self.dx, self.dy])
    
    def get_position_vector(self):
        return np.array([self.x, self.y])
    
    def get_velocity_vector(self):
        return np.array([self.dx, self.dy])
    
    def get_velocity(self):
        return np.sqrt(self.dx**2 + self.dy**2)
    
    def get_velocity_vector(self):
        return np.array([self.dx, self.dy])
    
    def reverse(self):
        self.dx *= -1
        self.dy *= -1
    
    def __str__(self):
        return "Ball at ({}, {}) with velocity ({}, {})".format(self.x, self.y, self.dx, self.dy)
    
    def __repr__(self):
        return self.__str__()
    

balls = []
temp = 0
def reset():
    global temp
    balls.clear()
    for i in range(COUNT):
        x = randint(0, W * size)
        y = randint(0, H * size)
        dx = randint(-5, 5)
        dy = randint(-5, 5)
        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        ball = Ball(x, y, dx, dy, color)
        balls.append(ball)
        temp += ball.get_temperature()
    temp /= COUNT
    


def draw():
    global temp
    screen.fill(GREY)

    temp = 0
    for ball in balls:
        ball.draw()
        temp += ball.get_temperature()
    temp /= len(balls)
    
    text = font1.render("Balls: {}".format(len(balls)), 1, BLACK)
    screen.blit(text, (W * size - text.get_width() - 10, 10))
    text = font2.render("Press R to reset", 1, BLACK)
    screen.blit(text, (W * size - text.get_width() - 10, 60))
    text = font2.render("Press ESC to quit", 1, BLACK)
    screen.blit(text, (W * size - text.get_width() - 10, 80))
    text = font2.render("Click to reverse velocity", 1, BLACK)
    screen.blit(text, (W * size - text.get_width() - 10, 100))
    text = font2.render("Temperature: {:.2f}".format(temp), 1, BLACK)
    screen.blit(text, (W * size - text.get_width() - 10, 120))

    pg.display.flip()

def move():
    
    for ball in balls:
        ball.move()
        for other in balls:
            if ball is not other:
                ball.collide(other)
        
        # cooldown balls
        if ball.get_speed() > 0:
            ball.dx *= COOLING
            ball.dy *= COOLING


def main():
    clock = pg.time.Clock()
    while True:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    return
                if event.key == pg.K_r:
                    reset()
            if event.type == pg.MOUSEBUTTONDOWN:
                for ball in balls:
                    ball.reverse()
                    # raise temperature
                    ball.dx *= HEATING
                    ball.dy *= HEATING

        move()
        draw()

if __name__ == '__main__':
    reset()
    main()





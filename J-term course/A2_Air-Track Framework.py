import pygame as pg
from typing import List
import math

BLACK, GREY, WHITE = (0, 0, 0), (100, 100, 100), (255, 255, 255)
RED, GREEN, BLUE, YELLOW, ORANGE = (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)

class GameWindow:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))

    def set_caption(self, caption):
        pg.display.set_caption(caption)
    
    def erase(self):
        self.screen.fill(BLACK)
    
class Detroit:
    def __init__(self, dimensions, x, speed, color):
        self.dimensions = dimensions
        self._x = x
        self.speed = speed
        self.color = color

        self.rect = pg.Rect(self.x, H // 2, *self.dimensions)
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
        self.rect.x = value
    
    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.rect)

class AirTrack:
    def __init__(self):
        self.cars : List[Detroit] = []
        self.env = Environment(W, 5)
    
    def update(self, dt):
        for car in self.cars:
            dx = car.speed * dt
            car.x += self.env.meters_to_pixels(dx)
    
    def make_cars(self, demo):
        if demo == 1:
            car1 = Detroit((50, 100), W // 2, 1, RED)
            car2 = Detroit((50, 100), 0, 2, BLUE)
        elif demo == 2:
            car1 = Detroit((50, 100), W, -2, RED)
            car2 = Detroit((50, 100), 0, 2, BLUE)
        
        self.cars = [car1, car2]
            
    
    def draw(self, screen):
        for car in self.cars:            
            car.draw(screen)

class Environment:
    def __init__(self, pixels, meters):
        self.pix2met = meters / pixels
        self.met2pix = pixels / meters
    
    def pixels_to_meters(self, pixels):
        return pixels * self.pix2met
    
    def meters_to_pixels(self, meters):
        return math.ceil(meters * self.met2pix)



def demo(demo=1):
    if not demo in range(1, 3):
        return 
    print(f"Demo {demo} selected.")
    
    track = AirTrack()
    track.make_cars(demo)
            
    return track
    
        


pg.init()
W, H = 800, 600
dt = 0.01
window = GameWindow(W, H)
window.set_caption("Air Track")
track = demo(1)
print("Select demo (1-2):")

running = True
while running:
    window.erase()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            runing = False
            break
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                break
            if event.key == pg.K_1:
                track = demo(1)
            elif event.key == pg.K_2:
                track = demo(2)
    if track:
        track.update(dt)
        track.draw(window.screen)
    pg.display.flip()


    
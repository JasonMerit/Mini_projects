import pygame 
import random
import math
import time

class Player:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = 5
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.hitbox = (self.x, self.y, self.width, self.height)
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)
    
    def move(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.x > self.vel:
            self.x -= self.vel
            self.left = True
            self.right = False
            self.up = False
            self.down = False
        elif keys[pygame.K_RIGHT] and self.x < 800 - self.width - self.vel:
            self.x += self.vel
            self.left = False
            self.right = True
            self.up = False
            self.down = False
        elif keys[pygame.K_UP] and self.y > self.vel:
            self.y -= self.vel
            self.left = False
            self.right = False
            self.up = True
            self.down = False
        elif keys[pygame.K_DOWN] and self.y < 600 - self.height - self.vel:
            self.y += self.vel
            self.left = False
            self.right = False
            self.up = False
            self.down = True
        else:
            self.left = False
            self.right = False
            self.up = False
            self.down = False

class Obtacle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = 5
        self.hitbox = (self.x, self.y, self.width, self.height)
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

class Map:
    pass



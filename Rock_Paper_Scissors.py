from typing import Iterator
import pygame as pg
from pygame.math import Vector2
import random


class Player(pg.sprite.Sprite):
    prey_pos = None
    predator_pos = None

    def __init__(self, type, id, size=100, pos=None):
        super().__init__()
        self.id = f'{type[0]}{id}'
        self.type = type
        self.image = pg.image.load(f'Images/{type}.png')
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()

        self.rect.center = pos if pos else (random.randint(0, w - self.image.get_width()), random.randint(0, h - self.image.get_height()))
        self.crumb = Vector2(self.rect.center)
    
    def __repr__(self):
        return f"{self.id} at {self.rect.center}"
    
    def __str__(self):
        return f"{self.id} at {self.rect.center}"

    @property
    def pos(self):
        return Vector2(self.rect.center)
    
    def update(self):
        # t = self.prey_pos + Vector2(random.randint(-5, 5), random.randint(-5, 5))
        # get distance to prey and predator
        prey_dist = (self.prey_pos - Vector2(self.rect.center)).length_squared()
        predator_dist = (self.predator_pos - Vector2(self.rect.center)).length_squared()

        target = self.prey_pos if prey_dist < predator_dist else self.predator_pos
        p = Vector2(self.rect.center)
        try:
            v = (target - p).normalize()
        except ValueError:
            pg.draw.circle(SCREEN, (0, 0, 0), self.rect.center, 10)
            pg.display.flip()
            pause()
            raise ValueError(f"target: {target}, p: {p}")
            
        self.rect.center += v #* 5
            

            # self.rect.x += random.randint(-5, 5)
            # self.rect.y += random.randint(-5, 5)
        # clamp x,y to stay on screen
        self.rect.x = max(0, min(w - self.image.get_width(), self.rect.x))
        self.rect.y = max(0, min(h - self.image.get_height(), self.rect.y))
    
    def collide(self, other):
        return self.rect.colliderect(other.rect)
    
    def kill(self):
        # respawn at random location
        self.rect.x = random.randint(0, w - self.image.get_width())
        self.rect.y = random.randint(0, h - self.image.get_height())
    
    def lay_crumb(self):
        """Just for debugging"""
        self.crumb = Vector2(self.rect.center)
        return self.crumb

class Team(pg.sprite.Group):
    prey_team = None  # type: Team
    predator_team = None
    com = Vector2(0, 0)
    
    def __repr__(self):
        return f"Team of {len(self)} {self.sprites()[0].type}s"

    def collide(self):
        for player in self:
            for prey in self.prey_team:
                if player.collide(prey):
                    prey.kill()
                    player.prey_pos = min(self.prey_team, key=lambda prey: (prey.pos - Vector2(player.pos)).length_squared()).pos
                    # what about killing multiple prey?


    def set_teams(self, prey_team, predator_team):
        self.prey_team = prey_team
        self.predator_team = predator_team
    
    def update_targets(self):
        for player in self:
            player.prey_pos = min(self.prey_team, key=lambda prey: (prey.pos - Vector2(player.pos)).length_squared()).pos
            player.predator_pos = min(self.predator_team, key=lambda predator: (predator.pos - Vector2(player.pos)).length_squared()).pos
    
    def lay_crumbs(self):
        com = Vector2(0, 0)
        for player in self:
            com += player.lay_crumb()
        self.com /= len(self)
    
    def draw_crumbs(self, surface):
        color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)][['Rock', 'Paper', 'Scissors'].index(self.sprites()[0].type)]
        for player in self:
            pg.draw.circle(surface, color, player.crumb, 5)
    
    

clock = pg.time.Clock()
pg.init()
GREY = (178, 178, 178)
w = 1000
h = 650
SCREEN = pg.display.set_mode((w, h))
SCREEN.fill((GREY))

def process_events():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                quit()
        # elif event.type == lay_crumb:
        #     for team in (rocks, papers, scissors):
        #         team.lay_crumbs()
        #         team.update_targets()

def pause():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    quit()
                elif event.key == pg.K_SPACE:
                    return
            
COUNT = 3
ROCK, PAPER, SCISSORS = range(3)
rocks = Team([Player('Rock', i, 50) for i in range(COUNT)])
papers = Team([Player('Paper', i, 50) for i in range(COUNT)])
scissors = Team([Player('Scissors', i, 50) for i in range(COUNT)])
rocks.set_teams(scissors, papers)
papers.set_teams(rocks, scissors)
scissors.set_teams(papers, rocks)

lay_crumb = pg.USEREVENT + 1
pg.time.set_timer(lay_crumb, 1000)

# targets
rocks.update_targets()
papers.update_targets()
scissors.update_targets()

while True:
    process_events()

    SCREEN.fill((GREY))
    for team in (rocks, papers, scissors):
        # team.lay_crumbs()
        # team.update_targets()
        team.update()
        team.collide()
        team.draw(SCREEN)
        team.draw_crumbs(SCREEN)

    pg.display.flip()
    clock.tick(30)

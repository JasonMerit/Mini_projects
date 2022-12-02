"""Implement same functionality as paint"""

import pygame as pg
from pygame import gfxdraw as gfx, Vector2 as V2
import numpy as np
from typing import List, Tuple, NewType

W, H = 800, 600
FPS = 30
BLACK, GREY, WHITE = (0, 0, 0), (100, 100, 100), (255, 255, 255)
ORANGE, YELLOW, PURPLE = (255, 128, 0), (255, 255, 0), (255, 0, 255)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
COLORS = [RED, GREEN, BLUE, ORANGE, YELLOW, PURPLE]

NUMBERS = [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6]


class Line():
    def __init__(self, start: V2, end: V2, color, width):
        self.start = V2(start)
        self.end = V2(end)
        self.color = color
        self.width = width

    def draw(self, screen: pg.Surface):
        pg.draw.line(screen, self.color, self.start, self.end, self.width)
    
    def update(self, end_pos: V2):
        self.end = end_pos
    
    def move(self, offset: V2):
        self.start += offset
        self.end += offset
    
    def cut(self, clipped_line):
        """Cut this by part of it"""
        # Three cases: 
        # 1) clipped_line is fully
        if clipped_line.start == self.start and clipped_line.end == self.end:
            return []

        # 2) clipped_line is partially containing start/end
        if clipped_line.start == self.start:
            return [Line(clipped_line.end, self.end, self.color, self.width)]
        if clipped_line.end == self.end:
            return [Line(self.start, clipped_line.start, self.color, self.width)]
        
        # 3) cut on either end
        return [Line(self.start, clipped_line.start, self.color, self.width), Line(clipped_line.end, self.end, self.color, self.width)]
            
        

    def __repr__(self) -> str:
        return f"Line({self.start}, {self.end}, {self.color}, {self.width})"

class Circle():
    def __init__(self, center: V2, radius: int, color=WHITE, width=0):
        self.center = V2(center)
        self.radius = radius
        self.color = color
        self.width = width

    def draw(self, screen: pg.Surface):
        if self.width == 0:
            gfx.filled_circle(screen, int(self.center.x), int(self.center.y), self.radius, self.color)
        else:
            pg.draw.circle(screen, self.color, self.center, self.radius, self.width)

    def __repr__(self) -> str:
        return f"Circle({self.center}, {self.radius}, {self.color}, {self.width})"

class Rect():
    def __init__(self, topleft: V2, size: V2, color, width):
        self.topleft = topleft
        self.size = size
        self.color = color
        self.width = width

    def draw(self, screen: pg.Surface):
        pg.draw.rect(screen, self.color, pg.Rect(self.topleft, self.size), self.width)
        # gfx.box(screen, pg.Rect(self.topleft, self.size), self.color)

    def __repr__(self) -> str:
        return f"Rect({self.topleft}, {self.size}, {self.color}, {self.width})"

class Polygon():
    def __init__(self, points: List[V2], color, width):
        self.points = points
        self.color = color
        self.width = width

    def draw(self, screen: pg.Surface):
        pg.draw.polygon(screen, self.color, self.points, self.width)

    def __repr__(self) -> str:
        return f"Polygon({self.points}, {self.color}, {self.width})"



class Paint():
    def __init__(self):
        self.screen = pg.display.set_mode((W, H))
        pg.display.set_caption("Paint")
        self.clock = pg.time.Clock()
        pg.font.init()
        self.font = pg.font.SysFont("Arial", 20)
        self.running = True
        self.color = WHITE
        self.width = 10
        self.shapes = []
        self.shape = None
        self.option = 0
        self.shape_inits = [
            lambda pos: Line(pos, pos, self.color, self.width),
            lambda pos: Circle(pos, 0, self.color, self.width),
            lambda pos: Rect(pos, (0, 0), self.color, self.width),
        ]
        self.shape_updates = [
            lambda shape, pos: setattr(shape, "end", pos),
            lambda shape, pos: setattr(shape, "radius", V2(shape.center).distance_to(pos)),
            lambda shape, pos: setattr(shape, "size", V2(pos) - shape.topleft)
        ]
        
        self.tool = 0
        self.tools = [
            self.select
        ]

        self.shapes.append(Line(V2(400, 200), V2(700, 200), RED, 10))
        # self.shapes.append(Circle(V2(400, 200), 10))
        self.draw()
        self.select()


    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.draw()
        
        

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: quit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.make_shape(event.pos)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_r:
                    self.shapes.clear()
                if event.key == pg.K_s:
                    self.save()
                if event.key in NUMBERS:
                    self.option = NUMBERS.index(event.key)
                if event.key == pg.K_m:
                    self.select()
    
    def make_shape(self, pos):
        painting = True
        shape = self.shape_inits[self.option](pos)
        while painting:
            self.clock.tick(FPS)
            self.draw(shape)
            for event in pg.event.get():
                if event.type == pg.QUIT: quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: quit()
                if event.type == pg.MOUSEMOTION:
                    self.shape_updates[self.option](shape, event.pos)
                if event.type == pg.MOUSEBUTTONUP:
                    painting = False
                    self.shapes.append(shape)
                    self.shape = None
                    break
    
    def select(self):
        """Select a rect area to move"""

        # First click - place the rect
        starting = True
        while starting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT: quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos = event.pos
                    starting = False
                    break
        
        # Second click - increase the rect size
        selecting = True
        while selecting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT: quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: quit()
                if event.type == pg.MOUSEMOTION:
                    self.draw(flip=False)
                    rect = pg.draw.rect(self.screen, WHITE, pg.Rect(pos, V2(event.pos) - V2(pos)), 1)
                    pg.display.flip()
                if event.type == pg.MOUSEBUTTONUP:
                    selecting = False
                    # Find the shapes that are being clipped
                    clipped = []
                    for shape in self.shapes:
                        if isinstance(shape, Line):
                            if rect.collidepoint(shape.start) or rect.collidepoint(shape.end):
                                clipped.append(shape)
                        # elif isinstance(shape, Circle):
                        #     if rect.collidepoint(shape.center):
                        #         clipped.append(shape)
                        # elif isinstance(shape, Rect):
                        #     if rect.colliderect(pg.Rect(shape.topleft, shape.size)):
                        #         clipped.append(shape)
                    line = clipped[0]
                    self.shapes.remove(line)

                    # Clip them
                    clipped_line = Line(*rect.clipline(line.start, line.end), line.color, line.width)
                    rest_of_line = line.cut(clipped_line)
                    self.shapes += rest_of_line
                    # self.shapes.append(rest_of_line)
                    # self.shapes.append(Line(*clipped_line, RED, 10))
                    # self.shapes.append(Circle(clipped_line[1], 10))
                    # self.shapes = [shape for shape in self.shapes if not self.shape_in_rect(shape, pg.Rect(pos, event.pos))]
                    break
        
        # Motion - cut and move the selection
        moving = True
        while moving:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT: quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: quit()
                if event.type == pg.MOUSEMOTION:
                    self.draw(flip=False)
                    rect.move_ip(event.rel)
                    clipped_line.move(event.rel)
                    pg.draw.rect(self.screen, WHITE, rect, 1)
                    clipped_line.draw(self.screen)
                    pg.display.flip()
                if event.type == pg.MOUSEBUTTONUP:
                    moving = False
                    self.shapes.append(clipped_line)
                    break
    
    def shape_in_rect(self, shape, rect):
        if isinstance(shape, Line):
            return self.line_in_rect(shape, rect)
    
    def line_in_rect(self, line: Line, rect: pg.Rect):
        return rect.collidepoint(line.start) and rect.collidepoint(line.end)

    def draw(self, shape=None, flip=True):
        self.screen.fill(BLACK)

        # Number of shapes
        text = self.font.render(f"{len(self.shapes)}", True, WHITE)
        self.screen.blit(text, (10, 10))

        for s in self.shapes:
            s.draw(self.screen)
        if shape:
            shape.draw(self.screen)
        if flip:
            pg.display.flip()
    
    def save(self):
        pg.image.save(self.screen, "image.png")
    

if __name__ == "__main__":
    app = Paint()
    app.run()
    pg.quit()


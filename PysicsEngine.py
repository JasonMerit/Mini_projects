import pygame as pg

W, H = 800, 600
FPS = 60
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
BLACK, GREY, WHITE = (0, 0, 0), (100, 100, 100), (255, 255, 255)
ORANGE, YELLOW, PURPLE = (255, 128, 0), (255, 255, 0), (255, 0, 255)
COLORS = [RED, GREEN, BLUE, ORANGE, YELLOW, PURPLE] 

class V2():

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return V2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return V2(self.x - other.x, self.y - other.y)
    
    def __neg__(self):
        return V2(-self.x, -self.y)
    
    def __mul__(self, other):
        return V2(self.x * other, self.y * other)
    
    def __div__(self, other):
        return V2(self.x / other, self.y / other)
    
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def cross(self, other):
        return self.x * other.y - self.y * other.x
    
    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def normalize(self):
        return self / self.length()
    
    def draw_point(self, pos, color=WHITE, size=5):
        pg.draw.circle(self.screen, color, pos, 5)
    

class Game():

    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode((W, H))
        self.clock = pg.time.Clock()
    
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()
    
    def update(self):
        pass

    def draw(self):
        self.screen.fill(BLACK)
        pg.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()


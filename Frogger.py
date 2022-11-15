import pygame as pg

# pygame init
pg.font.init()


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
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)
    
    def move(self):
        keys = pg.key.get_pressed()
        
        if keys[pg.K_LEFT] and self.x > self.vel:
            self.x -= self.vel
            self.left = True
            self.right = False
            self.up = False
            self.down = False
        elif keys[pg.K_RIGHT] and self.x < 800 - self.width - self.vel:
            self.x += self.vel
            self.left = False
            self.right = True
            self.up = False
            self.down = False
        elif keys[pg.K_UP] and self.y > self.vel:
            self.y -= self.vel
            self.left = False
            self.right = False
            self.up = True
            self.down = False
        elif keys[pg.K_DOWN] and self.y < 600 - self.height - self.vel:
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

class Car:

    def __init__(self, x, y, width, height, color, vel):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = vel
        self.hitbox = (self.x, self.y, self.width, self.height)
    
    def move(self):
        self.x += self.vel
    
    def draw(self, win):
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        # self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)
    
    def collide(self, player):
        if player.hitbox[0] < self.hitbox[0] + self.hitbox[2] and player.hitbox[0] + player.hitbox[2] > self.hitbox[0]:
            if player.hitbox[1] < self.hitbox[1] + self.hitbox[3] and player.hitbox[1] + player.hitbox[3] > self.hitbox[1]:
                return True
        return False
    
class Log:

    def __init__(self, x, y, width, height, color, vel):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = vel
        self.hitbox = (self.x, self.y, self.width, self.height)
    
    def move(self):
        self.x += self.vel
    
    def draw(self, win):
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        # self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)
    
    def collide(self, player):
        if player.hitbox[0] < self.hitbox[0] + self.hitbox[2] and player.hitbox[0] + player.hitbox[2] > self.hitbox[0]:
            if player.hitbox[1] < self.hitbox[1] + self.hitbox[3] and player.hitbox[1] + player.hitbox[3] > self.hitbox[1]:
                return True
        return False

class Game:
    def __init__(self):
        self.win = pg.display.set_mode((800, 600))
        pg.display.set_caption("Frogger")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont('comicsans', 30, True)
        self.run = True
        self.reset()
    
    def reset(self):
        self.map = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        self.player = Player(400, 550, 30, 30, (0, 255, 0))
        self.cars = [Car(0, 500, 100, 30, (255, 0, 0), 2),
                    Car(0, 450, 100, 30, (255, 0, 0), 2),
                    Car(0, 400, 100, 30, (255, 0, 0), 2),
                    Car(0, 350, 100, 30, (255, 0, 0), 2),
                    Car(700, 500, 100, 30, (255, 0, 0), -2),
                    Car(700, 450, 100, 30, (255, 0, 0), -2),
                    Car(700, 400, 100, 30, (255, 0, 0), -2),
                    Car(700, 350, 100, 30, (255, 0, 0), -2)]
        self.logs = [Log(0, 300, 100, 30, (255, 255, 255), 2),
                    Log(0, 250, 100, 30, (255, 255, 255), 2),
                    Log(0, 200, 100, 30, (255, 255, 255), 2),
                    Log(0, 150, 100, 30, (255, 255, 255), 2)]
        self.score = 0
    
    def draw_window(self):
        self.win.fill((0, 0, 0))
        self.player.draw(self.win)
        for car in self.cars:
            car.draw(self.win)
        for log in self.logs:
            log.draw(self.win)
        text = self.font.render('Score: ' + str(self.score), 1, (255, 255, 255))
        self.win.blit(text, (700, 10))
        pg.display.update()
    
    def main(self):
        while self.run:
            self.clock.tick(30)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.run = False
            self.player.move()
            for car in self.cars:
                car.move()
                if car.collide(self.player):
                    self.player.x = 400
                    self.player.y = 550
                    self.score -= 1
            for log in self.logs:
                log.move()
                if log.collide(self.player):
                    self.player.x += log.vel
            self.draw_window()
        pg.quit()

if __name__ == "__main__":
    game = Game()
    game.main()


import pygame as pg

pg.init()

class MandelBrot():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.screen.fill((0, 0, 0))

    def draw(self, max_iter=100):
        for x in range(self.width):
            for y in range(self.height):
                z = complex(0, 0)
                c = complex(x / self.width * 3.5 - 2.5, y / self.height * 2 - 1)
                for i in range(max_iter):
                    z = z * z + c
                    if abs(z) > 2:
                        break
                self.screen.set_at((x, y), (i % 4 * 64, i % 8 * 32, i % 16 * 16))
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

if __name__ == "__main__":
    mandelbrot = MandelBrot(640, 480)
    mandelbrot.draw()
    mandelbrot.run()    

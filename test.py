import random

import pygame as pg
from pygame.math import Vector2


# A simple sprite, just to have something moving on the screen.
class Ball(pg.sprite.Sprite):

    def __init__(self, screen_rect):
        super().__init__()
        radius = random.randrange(5, 31)
        self.image = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        pg.draw.circle(self.image, pg.Color('dodgerblue1'), (radius, radius), radius)
        pg.draw.circle(self.image, pg.Color('dodgerblue3'), (radius, radius), radius-2)
        self.rect = self.image.get_rect(center=screen_rect.center)
        self.vel = Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.pos = Vector2(self.rect.center)
        self.screen_rect = screen_rect
        self.lifetime = 350

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

        self.lifetime -= 1
        if not self.screen_rect.contains(self.rect) or self.lifetime <= 0:
            self.kill()


def main():
    screen = pg.display.set_mode((800, 600))
    screen.fill((20, 40, 70))
    pg.display.update()
    screen_rect = screen.get_rect()
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()
    # Pass this rect to `pg.display.update` to update only this area.
    update_rect = pg.Rect(100, 150, 500, 400)

    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        all_sprites.add(Ball(screen_rect))
        all_sprites.update()

        screen.fill((20, 50, 90))
        all_sprites.draw(screen)

        # Update only the area that we specified with the `update_rect`.
        pg.display.update(update_rect)
        clock.tick(60)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()
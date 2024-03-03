# # # """
# # # TODO
# # # 1) 
# # # - Play around with code to see how it works
# # # - Update draw ball method to take a ball object
# # # - Create a ball class that collides with the walls
# # # """

# # import pygame as pg

# # # class Display():
# # #     """Manage the display of the game"""
# # #     BLACK, GREY, WHITE = (33, 33, 33), (128, 128, 128), (211, 211, 211)

# # #     def __init__(self, width, height):
# # #         pg.init()
# # #         self.width = width
# # #         self.height = height
# # #         self.screen = pg.display.set_mode((self.width, self.height))
    
# # #     def draw_ball(self, x, y, radius=10, color=WHITE):
# # #         # TODO: Update this method to take a ball object
# # #         self.screen.fill(self.BLACK)
# #         pg.draw.circle(self.screen, color, (x, y), radius)
# # #         pg.display.update()

# class Ball():
#     # TODO: Create a ball class
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y

#     def move(self):
#         self.x += 1
#         self.y += 1
    
#     def draw(self, screen):
#         pg.draw.circle(screen, (211, 211, 211), (self.x, self.y), 10)
    
# def process_input():
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             quit()
        
#         if event.type == pg.KEYDOWN:
#             if event.key == pg.K_ESCAPE:
#                 quit()

# # # if __name__ == "__main__":
# # #     FPS = 60
# # #     display = Display(800, 600)
# #     clock = pg.time.Clock()

# # #     balls = [Ball(400, 300) for _ in range(10)]
# #     while True:
#         for ball in balls:
#             ball.move()
# #         process_input()
# # #         display.draw_ball(ball.x, ball.y)
# #         clock.tick(FPS)


# x, y = 0, 0

# def move(x, y):
#     x+=1

#     return x, y

# move()
# print(x)

import random
index = 0
length = 4
for _ in range(10):

    index = (index + 1) % length
    print(index)
import pygame as pg
from Tetris import Tetris, Display

pg.init()
pg.font.init()
pg.display.set_caption('Tetris')
SCREEN = pg.display.set_mode([1200, 760])
BLACK = (34, 34, 34)
SCREEN.fill(BLACK)
TXT_FONT = pg.font.SysFont("comicsans", 20)
STAT_FONT = pg.font.SysFont("comicsans", 35)
CELL_SIZE = 30
CELL_SIZE_2 = 3 * CELL_SIZE
N = 1



def process_events():
    global FPS
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                quit()
            if event.key in [pg.K_RIGHT, pg.K_d]:
                return "right"
            if event.key in [pg.K_LEFT, pg.K_a]:
                return "left"
            if event.key in [pg.K_UP, pg.K_w]:
                return "up"
            if event.key in [pg.K_DOWN, pg.K_s]:
                return "drop"
            if event.key == pg.K_q:
                return "lotate"
            elif event.key == pg.K_e:
                return "rotate"
            elif event.key == pg.K_SPACE:
                return "slam"
            elif event.key == pg.K_o:
                global RENDER
                RENDER = not RENDER
            elif event.key == pg.K_2:
                FPS += 1
            elif event.key == pg.K_1:
                FPS -= 1
            # elif event.key == pg.K_LSHIFT:
            #     return "shift"
            elif event.key == pg.K_r:
                env.reset()
            elif event.key == pg.K_p:
                pause()

def pause():
    while True:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_ESCAPE, pg.K_q]:
                    quit()
                elif event.key == pg.K_p:
                    return
                    


clock = pg.time.Clock() 
Range = range(N)
agents = []
anchors = []
envs = []
for i in Range:
    env = Tetris(False, Display())
    env.reset()
    agents.append(Agent(env, 0))
    anchors.append(50 + 400 * i)
    envs.append(env)

# time related stuff
FPS = 40
RENDER = True
# time_screen = pg.Surface((200, 50))
# t0 = pg.time.get_ticks()

while True:

    process_events()
    # if not action:
    #     action = "drop"
    i = 0
    for _ in Range:
        if agents[i].step():
            pass
        #     # remove agent from list
        #     agents.pop(i)
        #     i -= 1

        # if env.step(action):
        #     pause()
        if RENDER:
            SCREEN.blit(envs[i].render(), (anchors[i], CELL_SIZE_2))
            pg.display.update()
        i += 1
    
    # draw time
    # time_screen.fill(BLACK)
    # text = TXT_FONT.render("Play time: " + str(round((pg.time.get_ticks() - t0) / 1000, 2)), 1, (255, 255, 255))
    # time_screen.blit(text, (10, 10))
    # SCREEN.blit(time_screen, (0, 0))

    # update SCREEN
    # pg.display.update()
    clock.tick(FPS)
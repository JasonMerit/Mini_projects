PLAYER = False
DISPLAY = True
MAZE_GENERATOR = 5
SOLVER = 1
SCREEN_SIZE = 570
SIZE = 30
assert(SCREEN_SIZE % SIZE == 0), f"bad screen size / size ratio: {SCREEN_SIZE, SIZE}" 
START, GOAL = (0, 0), (SIZE-1, SIZE-1)
FPS = 300

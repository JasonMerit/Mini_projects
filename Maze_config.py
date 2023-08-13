PLAYER = False
DISPLAY = True
MAZE_GENERATOR = 1  # 0 : stack, 1 : eller, 2 : wilson, 3 : kruskal, 4 : prim, 5 : hunt and kill
SOLVER = 1
SCREEN_SIZE = 630
SIZE = 30 #SCREEN_SIZE // 2 # 570
assert(SCREEN_SIZE % SIZE == 0), f"bad screen size / size ratio: {SCREEN_SIZE, SIZE}" 
START, GOAL = (0, 0), (SIZE-1, SIZE-1)
FPS = 300

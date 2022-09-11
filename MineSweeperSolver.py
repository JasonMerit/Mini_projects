import numpy as np
from MineSweeperGame import MineSweeper
from scipy.ndimage import label, binary_dilation

W, H = 40, 30
MS = MineSweeper(W, H, 150)
# MS = MineSweeper(W, H, W*H*33//160)

dir_x = [1, 1, 0,-1,-1,-1, 0, 1]
dir_y = [0,-1,-1,-1, 0, 1, 1, 1]

# MS.left_click(MS.guess())

def basic_flagging():
    # Number = #Hidden - Number satisfied, so all touching mines
    # - Mark hidden and flagged to 1 else 0
    # - np.roll in all directions and sum up
    # - if np.roll result = square number, then flag
    A = (MS.player < 0).astype(int)
    kernel = np.zeros((H+2, W+2), dtype=int)
    Y = kernel.copy()
    kernel[1:-1, 1:-1] = A

    # Offset kernel and +1 for every A in all directions
    for y, x in zip(dir_x, dir_y):
        temp = np.roll(kernel, x, axis=0)  # Roll x-direction
        Y += np.roll(temp, y, axis=1) 	   # Roll y_direction

    Y = Y[1:-1, 1:-1]
    # print("Y", Y)
    # print(MS.player)
    A = (Y == MS.player)#.astype(int)  # All 
    A = np.logical_and(A, MS.player)#.astype(int)  # All satistied numbers
    A = binary_dilation(A, np.ones((3, 3)))  
    # print(A.astype(int))
    flagged = np.nonzero(MS.player + 3 == A)#.astype(int)
    for point in zip(*flagged):
        MS.right_click(point)


    

def basic_sweeping():
    # Number = #Flagged - Number satisfied, so, all touching empty
    pass

def step():
    basic_flagging()

# step()

while True:
    if MS.process_input():
        step()
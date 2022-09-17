from itertools import count
import numpy as np
from MineSweeperGame import MineSweeper
from scipy.ndimage import label, binary_dilation

W, H = 15, 20
MS = MineSweeper(W, H, 30)
# MS = MineSweeper(W, H, W*H*33//160)

dir_x = [1, 1, 0,-1,-1,-1, 0, 1]
dir_y = [0,-1,-1,-1, 0, 1, 1, 1]

# MS.left_click(MS.guess())

def count_touching(A):
    # @Params: A : 2d array of squares we wish to count as touching, e.g. flagged would be MS.player == -1 
    kernel = np.zeros((H+2, W+2), dtype=int)  # Kernel that shifts in all directions
    Y = kernel.copy()                         # 2d list where counting is made
    # A = MS.player < 0                         # Squares satisfying condition are counted
    kernel[1:-1, 1:-1] = A

    # Offset kernel and +1 for every A in all directions
    for y, x in zip(dir_x, dir_y):
        temp = np.roll(kernel, y, axis=0)  # Roll y-direction
        Y += np.roll(temp, x, axis=1) 	   # Roll x_direction

    return Y[1:-1, 1:-1]

def basic_flagging():
    # Number = #Hidden - Number satisfied, so all touching mines
    non_numbered_touching = count_touching(MS.player < 0)
    # print(non_numbered_touching)
    A = (non_numbered_touching == MS.player)#.astype(int)  # All 
    A = np.logical_and(A, MS.player)#.astype(int)  # All satisfied numbers
    A = binary_dilation(A, np.ones((3, 3)))  
    # print(A.astype(int))
    flagged = np.nonzero(MS.player + 3 == A)#.astype(int)   # +3 due to not caring about 0?
    return flagged
    


def basic_sweeping():
    # Number = #Flagged - Number satisfied, so, all touching empty
    num_touching_flags = count_touching(MS.player == -1)
    satisfied_numbered = num_touching_flags == MS.player
    dilated = binary_dilation(satisfied_numbered, np.ones((3, 3)))  # Dilate satisfied numbered to get toucing
    edge = np.logical_xor(dilated, satisfied_numbered)  # Substract satisfied, to get edge of dilation
    sweep = np.logical_and(edge, MS.player == -2)  # Sweep adjacent hiddens to satisfied
    return np.nonzero(sweep)

def get_hidden(point):
    pass

def set_difference():
    num_touching_flags = count_touching(MS.player == -1)
    unsatisfied_numbered = MS.player - num_touching_flags
    unsatisfied_numbered[unsatisfied_numbered <= 0] = 0


    # Find horizontal with difference > 0
    Y = np.roll(unsatisfied_numbered, -1, axis=1)     # Roll x-direction
    Y -= unsatisfied_numbered
    # Y = Y[1:-1, 1:-1]
    print(Y)
    print(np.logical_and(unsatisfied_numbered, Y != 0).astype(int))
    #look at index to the right of a nonzero, only include those where index to right is a unsatisfied number
    # Y += np.roll(temp, 1, axis=1) 	   # Roll y_direction

    
    return [], []

def psuedo_flagging(point_pair):
    # Find 1:2 and 0:1 and allocate 1/2 as psuedo flagged
    pass

def step(move):
    if move == 1:
        flagged = basic_flagging()
        for point in zip(*flagged):
            MS.right_click(point)
    elif move == 2:
        sweeped = basic_sweeping()
        for point in zip(*sweeped):
            MS.left_click(point)
    elif move == 3:
        sweeped, flagged = set_difference()
        for point in zip(*sweeped):
            MS.left_click(point)
        for point in zip(*flagged):
            MS.right_click(point)

    # mines = basic_sweeping()
    # for point in zip(*mines):
    #     MS.left_click(point)

# step()

# MS.sweep((17, 4))
# for i in range(4):
#     step(1)
#     step(2)
# step(3)
while True:
    move = MS.process_input()
    if not move:
        continue
    step(move)
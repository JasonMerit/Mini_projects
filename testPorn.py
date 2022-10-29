import numpy as np

import _thread

def input_thread(a_list):
    raw_input()             # use input() in Python3
    a_list.append(True)
    
def do_stuff():
    a_list = []
    _thread.start_new_thread(input_thread, (a_list,))
    while not a_list:
        print("kek")

A = [[1, 2], [3, 4]]
print(A[0:2])
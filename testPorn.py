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

k = lambda x: (x - 1) % 4
for i in range(4):
    print(k(i))
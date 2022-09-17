import csv
import numpy as np
from MineSweeperGame import MineSweeper

mines = []
history = []

def extract_data():
    global mines
    with open('last_mines.csv', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            mines.append(row)
    mines = np.array(mines, dtype=int)

    with open('last_moves.csv', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            history.append(row)


extract_data()
MS = MineSweeper(mines=mines)

while True:
    if MS.process_input():
        pass
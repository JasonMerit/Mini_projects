import pygame as pg

# ---------- Constants --------
WHITE, GREY, BLACK = (255, 255, 255),  (200, 200, 200), (0, 0, 0)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)

# ---------- pg initialization --------
pg.init()
pg.font.init()
font = pg.font.SysFont('Comic Sans MS', 30)
clock = pg.time.Clock()

# ---------- Variables --------
running = True
size = 10
W, H = 50, 50
font = pg.font.SysFont("comicsans", 40)

# ---------- Helper Functions --------

# ---------- Classes --------
class Sudoku():
    def __init__(self, grid):
        self.grid = grid

    def draw_grid(self):
        # fill the background
        screen.fill(WHITE)
        k = 5.5
        
        # draw lines
        for i in range(10):
            if i % 3 == 0:
                thick = 4
            else:
                thick = 1
            pg.draw.line(screen, BLACK, (0, i * size * k), (W * size * k, i * size * k), thick)
            pg.draw.line(screen, BLACK, (i * size * k, 0), (i * size * k, H * size * k), thick)

        # draw numbers
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] != 0:
                    text = font.render(str(self.grid[i][j]), True, BLACK)
                    screen.blit(text, (j * size * k + 15, i * size * k + 10))

        pg.display.flip()


    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None

    def valid(self, num, pos):
        # Check row
        for i in range(9):
            if self.grid[pos[0]][i] == num and pos[1] != i:
                return False

        # Check column
        for i in range(9):
            if self.grid[i][pos[1]] == num and pos[0] != i:
                return False

        # Check box
        box_x = pos[1] // 3
        box_y = pos[0] // 3

        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if self.grid[i][j] == num and (i, j) != pos:
                    return False

        return True

    def solve(self):
        find = self.find_empty()
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if self.valid(i, (row, col)):
                self.grid[row][col] = i
                self.draw_grid()
                clock.tick(4)
                

                if self.solve():
                    return True

                self.grid[row][col] = 0

        return False

# ---------- Main Program --------
def main():
    global running
    pg.display.set_caption("Sudoku Solver")
    

    grid = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]

    sudoku = Sudoku(grid)
    sudoku.draw_grid()
    sudoku.solve()
    clock.tick(1)
    sudoku.draw_grid()

    while running:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False

    pg.quit()

if __name__ == "__main__":
    screen = pg.display.set_mode((W * size, H * size))
    main()
import pygame as pg
import time

class Display():

    WHITE, BLACK, GREY = (200, 200, 200), (50, 50, 50), (128, 128, 128)
    RED, GREEN, BLUE = (200, 20, 20), (100, 200, 20), (0, 100, 200)
    YELLOW, PURPLE, CYAN = (200, 200, 0), (200, 0, 200), (0, 200, 200)
    COLORS = [BLACK, CYAN, YELLOW]

    pg.font.init()
    # bold calibri font
    font = pg.font.SysFont("calibri", 50, True)

    size = 100
    offset = size // 2 + 1
    cursor_size = 15

    def __init__(self, board, pos):
        self.dim = len(board)
        self.SIZE = self.size * self.dim

        self.screen = pg.display.set_mode((self.SIZE, self.SIZE))
        pg.display.set_caption("10 Puzzle")

        self.screen_board = pg.Surface((self.SIZE, self.SIZE))
        self.screen_cursor = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        self.screen_cursor.set_colorkey(self.GREEN)

        self.update(board, pos)

    def update(self, board, pos):
        self.draw_board(board)
        self.draw_cursor(pos)

    def draw_board(self, board):
        self.screen_board.fill(self.GREY)

        for i in range(self.dim):
            for j in range(self.dim):
                x, y = i * self.size + 1, j * self.size + 1
                color = self.COLORS[board[j][i]]
                pg.draw.rect(self.screen_board, color, (x, y, self.size - 2, self.size - 2))
        self.screen.blit(self.screen_board, (0, 0))
        pg.display.update()
    
    def draw_cursor(self, pos):
        x, y = pos
        self.screen_cursor.fill(self.GREEN)
        pg.draw.circle(self.screen_cursor, self.WHITE, (x * self.size + self.offset, y * self.size + self.offset), self.cursor_size)
        
        self.screen.blit(self.screen_board, (0, 0))  # Draw board to erase cursor
        self.screen.blit(self.screen_cursor, (0, 0))
        pg.display.update()
    
    def congrats(self):
        # self.screen.fill(self.WHITE)
        
        text = self.font.render("Complete!", 1, self.BLACK)
        self.screen.blit(text, (self.SIZE // 2 - text.get_width() // 2, 3 * self.SIZE // 8 - text.get_height() // 2))
        pg.display.update()

class Game():
    def __init__(self, dim):
        self.dim = dim
        self.goal = dim // 2 + dim  # Used to check if puzzle is complete

        self.board = [[1 for _ in range(dim)] for _ in range(dim)]
        self.pos = [0, 0]

        self.display = Display(self.board, self.pos)
    
    def reset(self):
        self.board = [[1 for _ in range(self.dim)] for _ in range(self.dim)]
        self.pos = [0, 0]
        self.display.update(self.board, self.pos)

    def run(self):
        while True:
            self.process_input()
    
    def process_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    quit()
                
                if event.key == pg.K_UP:
                    self.move("up")
                elif event.key == pg.K_DOWN:
                    self.move("down")
                elif event.key == pg.K_LEFT:
                    self.move("left")
                elif event.key == pg.K_RIGHT:
                    self.move("right")

                if event.key == pg.K_SPACE:
                    self.action()
    
    def move(self, direction):
        if direction == "up":
            if self.pos[1] == 0:
                self.pos[1] = self.dim - 1
            else: 
                self.pos[1] -= 1
        elif direction == "down":
            if self.pos[1] == self.dim - 1:
                self.pos[1] = 0
            else:
                self.pos[1] += 1
        elif direction == "left":
            if self.pos[0] == 0:
                self.pos[0] = self.dim - 1
            else:
                self.pos[0] -= 1
        elif direction == "right":
            if self.pos[0] == self.dim - 1:
                self.pos[0] = 0
            else:
                self.pos[0] += 1
        
        self.display.draw_cursor(self.pos)
    
    def action(self):
        x, y = self.pos
        self.board[y][x] = (self.board[y][x] + 1) % 3
        self.display.update(self.board, self.pos)

        self.is_full()
    
    def is_full(self):
        for row in self.board:
            if 0 in row:
                return
            
        self.is_complete()
    
    def is_complete(self):
        """Resets if the following rules are satisfied:
        - All rows are different.
        - All columns are different.
        - Each row and column have equal number of non-zero entrees.

        This is done smart by checking if the sum of each row and column is equal to the goal.
        """

        for row in self.board:
            if sum(row) != self.goal:
                return
        
        for i in range(self.dim):
            col = [self.board[j][i] for j in range(self.dim)]
            if sum(col) != self.goal:
                return
        
        self.win()
    
    def win(self):
        self.display.congrats()
        time.sleep(2)
        self.reset()


if __name__ == "__main__":
    game = Game(4)
    game.run()


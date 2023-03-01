# Tetris game

import pygame
import numpy as np
import random

dic = {"Z": 1, "I": 2, "J": 5, "T": 7, "L": 9, "S": 14, "O": 19}
#random.seed(dic["I"])


class Piece():
    """
    Piece class representing a tetromino.
    """

    S = np.array([[[0, 0, 0],
                   [0, 1, 1],
                   [1, 1, 0]],
                  [[0, 1, 0],
                   [0, 1, 1],
                   [0, 0, 1]]])

    Z = np.array([[[0, 0, 0],
                   [1, 1, 0],
                   [0, 1, 1]],
                  [[0, 0, 1],
                   [0, 1, 1],
                   [0, 1, 0]]])

    T = np.array([[[0, 0, 0],
                   [1, 1, 1],
                   [0, 1, 0]],
                  [[0, 1, 0],
                   [1, 1, 0],
                   [0, 1, 0]],
                  [[0, 1, 0],
                   [1, 1, 1],
                   [0, 0, 0]],
                  [[0, 1, 0],
                   [0, 1, 1],
                   [0, 1, 0]]])

    L = np.array([[[0, 0, 0],
                   [1, 1, 1],
                   [1, 0, 0]],
                  [[1, 1, 0],
                   [0, 1, 0],
                   [0, 1, 0]],
                  [[0, 0, 1],
                   [1, 1, 1],
                   [0, 0, 0]],
                  [[0, 1, 0],
                   [0, 1, 0],
                   [0, 1, 1]]])

    J = np.array([[[0, 0, 0],
                   [1, 1, 1],
                   [0, 0, 1]],
                  [[0, 1, 0],
                   [0, 1, 0],
                   [1, 1, 0]],
                  [[1, 0, 0],
                   [1, 1, 1],
                   [0, 0, 0]],
                  [[0, 1, 1],
                   [0, 1, 0],
                   [0, 1, 0]]])

    O = np.array([[[0, 0, 0, 0],
                   [0, 1, 1, 0],
                   [0, 1, 1, 0],
                   [0, 0, 0, 0]]])

    I = np.array([[[0, 0, 0, 0],
                   [0, 0, 0, 0],
                   [1, 1, 1, 1],
                   [0, 0, 0, 0]],
                  [[0, 0, 1, 0],
                   [0, 0, 1, 0],
                   [0, 0, 1, 0],
                   [0, 0, 1, 0]]])

    shapes = [S, Z, T, L,
              J, O, I]
    shape_colors = [(0, 255, 0), (255, 0, 0), (128, 0, 128), (255, 165, 0),
                    (0, 0, 255), (255, 255, 0), (0, 255, 255)]

    def __init__(self):
        """
        Initialize the object positioned at the top of board
        :param teromino: shape of piece (int)
        :return: None
        """
        self.rotation = 0
        self.tetromino = random.randint(0, 6)
        self.shape = self.shapes[self.tetromino][self.rotation]
        self.color = self.shape_colors[self.tetromino]
        # Spawn position depends on tetromino
        self.y = 1 if self.tetromino < 6 else 0
        self.x = 7 if self.tetromino < 5 else 6



    def rotate(self, clockwise=True):
        """
        Rotates piece in either direction
        :param clockwise: Rotates clockwise if true else counter-clockwise (bool)
        :return: None
        """
        dir = 1 if clockwise else -1
        num_rotations = len(self.shapes[self.tetromino])
        self.rotation = (self.rotation + dir) % num_rotations
        self.shape = self.shapes[self.tetromino][self.rotation]

    def change(self):
        """
        Change current piece to another piece (for debugging)
        :return: None
        """
        num_pieces = len(self.shapes)
        self.tetromino = (self.tetromino + 1) % num_pieces
        self.rotation = 0
        self.shape = self.shapes[self.tetromino][self.rotation]
        self.color = self.shape_colors[self.tetromino]

def new_board():
    board = np.zeros([22, 10])
    wall = np.ones([22, 2])
    floor = np.ones([2, 15])
    board = np.c_[np.ones(22), wall, board, wall]
    board = np.vstack((board, floor))
    return board

class Tetris():
    """
    Tetris class acting as enviroment.
    The game data is represented using a matrix representing the board,
    and piece objects. The board is extended out of view for easy collision
    detection, as such occationally the a submatrix is constructed.
    """

    # Rendering Dimensions
    screen_size = 600
    cell_size = 25
    height = 20
    width = 10
    top_left_y = screen_size / 2 - height * cell_size / 2
    top_left_x = screen_size / 2 - width * cell_size / 2
    offset = 100

    # Colors
    black = (34, 34, 34)
    grey = (184, 184, 184)
    pygame.font.init()  # init font
    TXT_FONT = pygame.font.SysFont("comicsans", 25)
    STAT_FONT = pygame.font.SysFont("comicsans", 35)

    def __init__(self, state=None):
        pygame.init()
        self.reward = 0
        self.score = 0
        self.board = new_board()
        self.piece = Piece()
        self.next_piece = Piece()
        self.shift_piece = None
        self.shifted = False
        
        self.pieces_placed = 0

        self.screen = pygame.display.set_mode([self.screen_size, self.screen_size])
        pygame.display.set_caption('Tetris')
        self.background = pygame.Surface(self.screen.get_size())

    def step(self, action):
        """
        Applies the given action in the environment.
        It works by taking the action and redoing if the piece ends up
        in an invalid configuration.
        :param action: Action given to environment (String)
        :return: None
        """

        if action == "left":
            self.piece.x -= 1
            if not self.valid_position():
                self.piece.x += 1
        elif action == "right":
            self.piece.x += 1
            if not self.valid_position():
                self.piece.x -= 1
        elif action == "down":
            self.piece.y += 1
            if not self.valid_position():
                self.piece.y -= 1
                self.new_piece()
        elif action == "up":
            self.piece.y -= 1
            if not self.valid_position():
                self.piece.y += 1
        elif action == "rotate":
            self.piece.rotate()
            if not self.valid_position():
                self.piece.rotate(False)
        elif action == "lotate":
                self.piece.rotate(False)
                if not self.valid_position():
                    self.piece.rotate(True)
        elif action == "drop":
            while self.valid_position():
                self.piece.y += 1
            self.piece.y -= 1
            self.new_piece()
        elif action == "change":
            self.piece.change()
        elif action == "shift" and not self.shifted:
            self.shifted = True
            if self.shift_piece:
                temp = self.piece
                self.shift_piece.x, self.shift_piece.y = self.piece.x, self.piece.y
                self.piece = self.shift_piece
                self.shift_piece = temp
                # BUG Collides with wall
            else:
                self.shift_piece = self.piece
                self.piece = Piece()

    def valid_position(self):
        """
        Returns whether the current position is valid.
        Assumes piece is positioned inside board.
        """
        # Get area of board that the shape covers
        x, y = self.piece.x, self.piece.y
        size = len(self.piece.shape)
        sub_board = self.board[y:y + size, x:x + size]

        # Check for collision by summing and checking for 2
        collision_matrix = self.piece.shape + sub_board

        return not np.any(collision_matrix == 2)

    def drop(self):
        """
        Drop the piece one unit down.
        :return: None
        """
        self.piece.y += 1
        if not self.valid_position():
            self.piece.y -= 1
            self.new_piece()

    def new_piece(self):
        """
        Registers current piece into board, creates new piece and
        determines if game over
        :return: None
        """
        self.pieces_placed += 1
        
        # Find coordinates the current piece inhabits
        indices = np.where(self.piece.shape == 1)
        a, b = indices[0], indices[1]
        a, b = a + self.piece.y, b + self.piece.x
        coords = zip(a, b)

        # Change the board accordingly
        for c in coords:
            self.board[c] = 1

        # Get new piece and clear possible lines
        self.piece = self.next_piece
        self.next_piece = Piece()
        self.clear_lines()

        # Check for game over by overlapping spawn piece
        if not self.valid_position(): # Add training bool
            self.pieces_placed = 0
            self.reset()

        self.shifted = False

    def clear_lines(self):
        """
        Check and clear lines if rows are full
        :return: None
        """
        # Get visual part of board
        grid = self.board[2:22, 3:13]
        idx = np.array([], dtype=int)

        # Find complete rows in reverse order
        for r in reversed(range(len(grid))):  # Count rows to remove in reverse order
            if grid[r].all():
                idx = np.append(idx, r)

        # Now clear the rows
        for c in idx:
            grid = np.delete(grid, c, 0)  # Remove the cleared row
            grid = np.vstack((np.zeros(10), grid))  # Add an empty row on top
            idx += 1  # Shift remaining clear rows a line down

        # Add final result to board
        self.board[2:22, 3:13] = grid


    def render(self):
        """
        Renders game by drawing the board and pieces.
        :return: None
        """

        # Clear the screen
        self.screen.fill(self.black)

        # Get and draw grid
        grid = self.board[2:22, 3:13]
        background = (self.top_left_x - 1,
                      self.top_left_y - 1,
                      self.width * self.cell_size + 1,
                      self.height * self.cell_size + 1)
        pygame.draw.rect(self.screen, self.grey, background)

        for i in range(self.width):
            for j in range(self.height):
                val = grid[j, i]
                color = self.grey if val != 0 else self.black
                square = (self.top_left_x + self.cell_size * i,
                          self.top_left_y + self.cell_size * j,
                          self.cell_size - 1, self.cell_size - 1)
                pygame.draw.rect(self.screen, color, square)

        # Draw piece
        size = len(self.piece.shape[0])
        for i in range(size):
            for j in range(size):
                if self.piece.shape[i, j] == 0:
                    continue
                square = (self.top_left_x + self.cell_size * (self.piece.x + j - 3),  # POSITION HERE
                          self.top_left_y + self.cell_size * (self.piece.y + i - 2),
                          self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.piece.color, square)

        # Draw "pieces placed"
        label = self.TXT_FONT.render("Pieces Placed",1,(255,255,255))
        self.screen.blit(label, (self.screen_size - label.get_width() - 25, 120))

        # Draw lines cleared
        label = self.STAT_FONT.render(str(self.pieces_placed),1,(255,255,255))
        self.screen.blit(label, (self.screen_size - label.get_width() - 70, 150))
        
        # Draw next piece
        size = len(self.next_piece.shape[0])
        for i in range(size):
            for j in range(size):
                if self.next_piece.shape[i, j] == 0:
                    continue
                square = (470 + self.cell_size * j,
                          100 + self.cell_size * i,
                          self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.next_piece.color, square)

        # Draw shift_piece
        if self.shift_piece:
            size = len(self.shift_piece.shape[0])
            for i in range(size):
                for j in range(size):
                    if self.shift_piece.shape[i, j] == 0:
                        continue
                    square = (50 + self.cell_size * j,
                              100 + self.cell_size * i,
                              self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, self.shift_piece.color, square)


        # text = self.scorefont.render("{:}".format(self.score), True, (0,0,0))
        # self.screen.blit(text, (790-text.get_width(), 10))

        # Display
        pygame.display.flip()

    def reset(self):
        """
        Resets game by creating new board and pieces
        :return: None
        """
        self.board = new_board()
        self.piece = Piece()
        self.next_piece = Piece()
        self.shift_piece = None

    def close(self):
        """
        Close down the game
        :return: None
        """
        pygame.quit()

    def get_state(self):
        """
        Returns all relevant information
        :return: None
        """
        return self.board


# Initialize the environment
env = Tetris()
env.reset()
board = env.get_state()

# Definitions and default settings
run = True
action_taken = False
slow = True
runai = False
render = True
done = False
drop_time = 0
drop_speed = 0.06
dos = 0
dos_lag = 0

clock = pygame.time.Clock()

while run:
    clock.tick(40)
    drop_time += clock.get_rawtime()  # Time since last iteration (ms)
    dos += clock.get_rawtime()
    dos_lag += clock.get_rawtime()

    if drop_time / 1000 > drop_speed:  # Drop piece
        drop_time = 0
        env.drop()

    # Process game events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            dos_lag = 0
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                run = False
            if event.key == pygame.K_RIGHT:
                action, action_taken = "right", True
            if event.key == pygame.K_LEFT:
                action, action_taken = "left", True
            if event.key == pygame.K_UP:
                action, action_taken = "up", True
            if event.key == pygame.K_DOWN:
                action, action_taken = "down", True
            if event.key == pygame.K_z:
                action, action_taken = "lotate", True
            elif event.key == pygame.K_x:
                action, action_taken = "rotate", True
            elif event.key == pygame.K_SPACE:
                action, action_taken = "drop", True
            # elif event.key == pygame.K_e:
            #     action, action_taken = "change", True
            elif event.key == pygame.K_LSHIFT:
                action, action_taken = "shift", True
            elif event.key == pygame.K_r:
                env.reset()
            elif event.key == pygame.K_p:
                pause = True
                while pause:
                    clock.tick(40)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        if event.type == pygame.KEYDOWN:
                            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                                pygame.quit()
                                quit()
                            elif event.key == pygame.K_p:
                                pause = False
    if dos_lag / 1000 > 0.05 and dos / 1000 > 0.005:
        dos = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            action, action_taken = "right", True
        elif keys[pygame.K_LEFT]:
            action, action_taken = "left", True
        if keys[pygame.K_DOWN]:
            action, action_taken = "down", True
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            break

    # AI controller
    if runai:
        pass

    # Human controller
    else:
        if action_taken:
            env.step(action)
            action_taken = False

    if render:
        env.render()

env.close()

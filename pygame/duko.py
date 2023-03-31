"""


TODO:
- Create proper starting configuration
- Press 1-2-3-4-5 for choosing dimension size (4, 6, 8, 10, 12)
- Fix cell offset
- Add outline to font (write a congrats surface)
- Aestetics
    - Cursor outline
    - Shadowed locks on fixed cells upon press

"""

import sys, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
from pygame import gfxdraw
import numpy as np
import random, time

class Display():

    WHITE, BLACK, GREY = (244, 244, 244), (22, 22, 22), (52, 52, 52)
    RED, GREEN, BLUE = (200, 20, 20), (100, 200, 20), (255, 100, 0)
    ORANGE, YELLOW, PURPLE = (0, 156, 255), (255, 255, 0), (128, 0, 255)
    COLORS = [GREY, ORANGE, BLUE]
    SHADES = [None, (0, 130, 220), (220, 50, 0)]

    pg.font.init()
    # bold calibri font
    font_big = pg.font.SysFont("calibri", 50, True)
    font_med = pg.font.SysFont("calibri", 30, True)

    size = 100
    cursor_size = 15

    def __init__(self, board):
        self.dim = len(board)
        self.SIZE = self.size * self.dim

        self.screen = pg.display.set_mode((self.SIZE, self.SIZE))
        pg.display.set_caption("10 Puzzle")

        self.screen_board = pg.Surface((self.SIZE, self.SIZE))
        self.screen_cursor = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)

        self.surf_cursor, self.surf_cells = self.create_surfaces()

        self.reset(board, (0, 0))
    
    def create_surfaces(self):
        size = np.array([self.size, self.size])
        offset =  size // 2

        cursor = pg.Surface(size, pg.SRCALPHA) 
        gfxdraw.aacircle(cursor, *offset, self.cursor_size + 2, self.BLACK)
        gfxdraw.filled_circle(cursor, *offset, self.cursor_size + 2, self.BLACK)
        gfxdraw.aacircle(cursor, *offset, self.cursor_size, self.WHITE)
        gfxdraw.filled_circle(cursor, *offset, self.cursor_size, self.WHITE)

        cells = []
        cell_rect = (0, 0, self.size - 2, self.size - 2)
        w = self.size - 10
        h = self.size // 12
        shade_horiz = (self.size // 2 - w // 2, self.size - h - 5, w, h)
        shade_verti = (h - 5, self.size // 2 - w // 2, h, w)

        for i in range(3):
            cell = pg.Surface(size, pg.SRCALPHA)
            pg.draw.rect(cell, self.COLORS[i], cell_rect, border_radius=3)
            
            # Shades
            if i > 0:
                pg.draw.rect(cell, self.SHADES[i], shade_horiz)
                pg.draw.rect(cell, self.SHADES[i], shade_verti)
            cells.append(cell)

        return cursor, cells

    def reset(self, board, pos):
        self._draw_board(board)
        self.update_cell(np.array(pos))
        self.draw_cursor(np.array(pos))
    
    def update_cell(self, pos, color=None):
        """Update cell at pos with color"""
        pos = np.array(pos)
        
        if color != None:
            self._draw_cell(pos, color)

        # self.draw_cursor(pos)

        pg.display.update()

    def _draw_board(self, board):
        self.screen_board.fill(self.BLACK)

        for i in range(self.dim):
            for j in range(self.dim):
                x, y = i * self.size + 1, j * self.size + 1
                self.screen_board.blit(self.surf_cells[board[j][i]], (x, y))

        self.screen.blit(self.screen_board, (0, 0))
    
    def _draw_cell(self, pos, color):
        x, y = pos * self.size + 1
        self.screen_board.blit(self.surf_cells[color], (x, y))
        self.screen.blit(self.screen_board, (0, 0))
    
    def draw_cursor(self, pos: np.array):
        pos *= self.size

        self.screen_cursor.fill((0, 0, 0,0))
        self.screen_cursor.blit(self.surf_cursor, pos)

        self.screen.blit(self.screen_board, (0, 0))  # Draw board to erase cursor
        self.screen.blit(self.screen_cursor, (0, 0))
        pg.display.update()
        
    
    def outline_text(self, string, color, outline_color, x, y):
        text = self.font_big.render(string, 1, color)
        text_outline = self.font_big.render(string, 1, outline_color)
        self.screen.blit(text_outline, (x - 2, y))
        self.screen.blit(text_outline, (x + 2, y))
        self.screen.blit(text_outline, (x, y - 2))
        self.screen.blit(text_outline, (x, y + 2))
        self.screen.blit(text, (x, y))
    
    def congrats(self):
        text = self.font_big.render("Complete!", 1, self.WHITE)
        self.outline_text("Complete!", self.WHITE, self.BLACK, self.SIZE // 2 - text.get_width() // 2, self.SIZE // 2 - text.get_height() // 2)

        # Press space to continue
        text = self.font_med.render("Press space to continue", 1, self.WHITE)
        self.screen.blit(text, (self.SIZE // 2 - text.get_width() // 2, 5 * self.SIZE // 8 - text.get_height() // 2))
        pg.display.update()

class Duko():
    pos = [0, 0]

    def __init__(self, dim, render=True):
        self.dim = dim

        goal = dim // 2 + dim  # Used to check if puzzle is complete
        self.goal = np.ones(self.dim, dtype=np.int8) * goal

        self.board_init, self.fixed = self._generate_board()

        self.board = self.board_init.copy()
        self.display = Display(self.board) if render else None
            
    def reset(self):
        """Reset board and cursor to initial state"""
        self.board = self.board_init.copy()
        self.pos = [0, 0]
        if self.display:
            self.display.reset(self.board, self.pos)
    
    def _generate_board(self):
        """Generate a board with a unique solution"""
        # board_init = np.array([[0 for _ in range(dim)] for _ in range(dim)], dtype=np.int8)
        board = np.array([[0, 0, 0, 0], [0, 1, 0, 1], [0, 0, 2, 0], [0, 1, 0, 0]], dtype=np.int8)
        fixed = list(zip(*np.nonzero(board.T))) # Transpose to get x, y
        
        return board, fixed
        

    def run(self):
        if not self.display:
            raise Exception("Can't run without rendering")
        
        while True:
            self.process_input()
    
    def process_input(self):
        """Process input from keyboard.
        - Up, down, left, right to move cursor
        - Space to toggle cell
        - Escape to quit
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    quit()
                
                if event.key == pg.K_r:
                    self.reset()

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
        
        if self.display:
            self.display.draw_cursor(np.array(self.pos))
    
    def action(self):
        """Toggle cell at cursor position"""
        
        if tuple(self.pos) in self.fixed:
            return # TODO: Draw shadowed locks on fixed cells
        
        x, y = self.pos
        self.board[y, x] = (self.board[y, x] + 1) % 3
        self.display.update_cell(self.pos, self.board[y, x])
        self.display.draw_cursor(np.array(self.pos))

        if self.is_complete():
            self.win()
    
    def is_complete(self):
        """Returns true if the puzzle is complete:
        - Each row and column have equal number of non-zero entrees.
        - All rows and columns are different.
        """
        A = self.board

        # Check if all rows and columns have equal number of non-zero entrees
        if 0 in A \
            or not np.all(np.sum(A, axis=0) == self.goal) \
            or not np.all(np.sum(A, axis=1) == self.goal):
            return False

        # Check if all rows and columns are different
        for i in range(self.dim):
            for j in range(i, self.dim):
                if i != j:
                    if np.all(A[i] == A[j]) or np.all(A[:, i] == A[:, j]):
                        return False
        return True
        
    def win(self):
        """Congratulate player and wait for space to be pressed"""
        if self.display:
            self.display.congrats()

        # Wait until space is pressed   
        while True:
            event = pg.event.wait()
            if event.type == pg.QUIT:
                quit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    quit()

                if event.key == pg.K_SPACE:
                    self.reset()
                    return

# ---------- Reinforcement learning ----------------------- #
from gym import spaces, Env

class EnvironmentDuko(Env):
    DT = 0.04
    def __init__(self, game):
        self.game = game
        dim = game.dim
        self.action_space = spaces.Box(low=np.array([0, 0, 1]), high=np.array([dim-1, dim-1, 2]), shape=(3,), dtype=int)
        self.observation_space = spaces.Box(low=0, high=2, shape=(dim,dim), dtype=np.int8)
        self.reward_range = (0, 1)
    
    def reset(self):
        self.game.reset()
        return self.game.board

    def reset_to(self, board):
        self.game.board = board
        return self.game.board
    
    def step(self, action):
        if action not in self.action_space:
            raise Exception(f"Invalid action: {action}")
        
        x, y, a = action
        self.game.board[y, x] = a
        done = self.game.is_complete()
        self.render(*action)
        return self.game.board, int(done), done
    
    def render(self, x, y, a):
        if self.game.display:
            self.game.display.update_cell(np.array([x, y]), a)
            
            self.game.process_input()
            time.sleep(self.DT)
    
    def random_action(self):
        x, y, a = self.action_space.sample()
        while (x, y) in self.game.fixed:
            x, y, a = self.action_space.sample()
        
        return np.array([x, y, a])

    def is_done(self):
        return self.game.is_complete()

    def close(self):
        pass

class Agent():
    def __init__(self, env: Env):
        self.env = env

    def policy(self, state):
        """Returns a random action"""
        return self.env.random_action()
    
    def episode(self):
        total_steps = 0
        # total_reward = 0
        state = self.env.reset()
        while True:
            action = self.policy(state)
            state, r, done = self.env.step(action)  # TODO: Doesn't work properly
            total_steps += 1
            # total_reward += r
            if done:
                print(f"Complete after {total_steps} steps!")
                break

class Test():
    """Test the game and agent based on the board configurations in duko_configs.npz.
    The first board in the file is a boolean array indicating if the board is complete."""

    def __init__(self, game):
        self.env = EnvironmentDuko(game)
        self.agent = Agent(self.env)

        loaded = np.load("duko_configs.npz")
        self.board_configs = [np.array(board) for board in loaded.values()]
        self.complete = self.board_configs.pop(0)
    
    def test_all(self):
        self.test_is_complete()
        self.test_agent()
    
    def test_is_complete(self):
        for i, board in enumerate(self.board_configs):
            self.env.reset_to(board)
            done = self.complete[i]
            assert(self.env.is_done() ==  done), f"Board {i} is {['NOT complete', 'complete'][done]}!\n{board}"
    
    def test_agent(self):
        for i, board in enumerate(self.board_configs):
            self.env.reset_to(board)
            done = self.complete[i]
            if done:
                print(f"Board {i} is complete!")
                continue

            self.agent.board = board
            print(f"Testing board {i}...")
            self.agent.episode()
            assert(self.env.is_done()), f"Board {i} is NOT complete!\n{board}"


if __name__ == "__main__":
    try:
        setting = sys.argv[1]
        if setting == "test":
            game = Duko(4, render=False)
            test = Test(game)
            test.test_all()
        elif setting == "agent":
            game = Duko(4, render=True)
            env = EnvironmentDuko(game)
            agent = Agent(env)
            agent.episode()
        else:
            print("Invalid setting. Use 'test' or 'agent'.")   

    except IndexError:
        game = Duko(4, render=True)
        game.run()



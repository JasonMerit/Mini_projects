import os
import time
import keyboard
def clear(): os.system('cls')
def snooze(s): time.sleep(s)


class Snake:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.body = [(0, 0)]
        self.direction = 'right'
        self.alive = True
    
    def play(self):
        while self.alive:
            self.get_user_input()
            self.move()
            self.check_collision()
            self.draw()
            snooze(0.1)
    
    def get_user_input(self):
        if keyboard.is_pressed('right'):
            self.change_direction('right')
        elif keyboard.is_pressed('left'):
            self.change_direction('left')
        elif keyboard.is_pressed('up'):
            self.change_direction('up')
        elif keyboard.is_pressed('down'):
            self.change_direction('down')
        elif keyboard.is_pressed('esc'):
            self.alive = False

    def move(self):
        if self.direction == 'right':
            self.x += 1
        elif self.direction == 'left':
            self.x -= 1
        elif self.direction == 'up':
            self.y -= 1
        elif self.direction == 'down':
            self.y += 1
        self.body.append((self.x, self.y))
        self.body.pop(0)

    def draw(self):
        clear()
        for y in range(20):
            for x in range(20):
                if (x, y) in self.body:
                    print('O', end='')
                else:
                    print(' ', end='')
            print()
        print(f'Score: {len(self.body)}')
        print(f'Direction: {self.direction}')

    def change_direction(self, direction):
        if direction == 'right' and self.direction != 'left':
            self.direction = 'right'
        elif direction == 'left' and self.direction != 'right':
            self.direction = 'left'
        elif direction == 'up' and self.direction != 'down':
            self.direction = 'up'
        elif direction == 'down' and self.direction != 'up':
            self.direction = 'down'

    def check_collision(self):
        if self.x < 0 or self.x > 19 or self.y < 0 or self.y > 19:
            self.alive = False
        for x, y in self.body[:-1]:
            if self.x == x and self.y == y:
                self.alive = False

def main():
    snake = Snake()
    clear()
    print('SnakeCMD')
    print('Press any key to start')
    input('>')
    clear()
    snake.play()
    print('Game Over')
    


if __name__ == '__main__':
    main()
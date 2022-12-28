"""Using pydirectinput to automate the game DinoChrome

- Can't hold down keys"""

import pydirectinput as pdi
import pyautogui as gui
from time import sleep
from PIL import ImageGrab
from playsound import playsound
from pygame import mixer

lowest = 100000
sound = "DinoChrome/ping.mp3"

def dist_to_cacti(left, top, color, width=150):
    global lowest
    # colors = []
    # offset = 330
    offset = 500
    y = top+45
    x = left + offset
    # top += 100
    # px = ImageGrab.grab().load()
    px = ImageGrab.grab(bbox=(x, y, x+width, y+1)).load()
    for i in range(width):
        if px[i, 0] == color:
            # playsound(sound)
            
            # print(x + i)
            return x + i
            # screen = ImageGrab.grab()
            # for i in range(x-5, x+15):
            #     for j in range(y-5, y+5):
            #         screen.putpixel((i, j), (255,0, 0))
            # screen.show()
            break
    
    # for y in range(top, top+40):
    # for x in range(left-width, left):
    # if px[x, y] == color:
    #     if x < lowest:
    #         lowest = x
    #     print(x)
    #     return x
    #         colors.append(px[x, y])
    # return colors

def is_game_over(game_over_reg):
    """Check if the game is over"""
    gui.locateOnScreen('DinoChrome/game_over.png', confidence=0.2, grayscale=True, region=game_over_reg)

def jump(play_sound=False):
    """Jump"""
    # if play_sound:
    #     playsound(sound)
    pdi.press('space')

def main():
    """Main function"""
    FPS = 10
    dt = 1 / FPS 
    GREEN = (64, 144, 22)
    JUMP_THRESHOLD = 340

    # Get the position of the game after tabing out
    gui.hotkey('alt', 'tab')
    sleep(0.1)
    # game_over_reg = gui.locateOnScreen('DinoChrome/dino_dead.png', confidence=0.5, grayscale=True)
    game_over_reg = gui.locateOnScreen('DinoChrome/game_over.png', confidence=0.7, grayscale=True)
    if game_over_reg is None:
        print("> Game over not found")
        return

    pdi.press('space') # start the game
    dino = gui.locateOnScreen('DinoChrome/dino.png', confidence=0.5, grayscale=True)
    if dino is None:
        print("> Dino not found")
        return 
    # set mouse position to game
    
    left, top = dino.left, dino.top

    game_over = False
    distances = []
    while not game_over:
        dist = dist_to_cacti(left, top, GREEN)
        if dist and (distances == [] or dist - distances[-1] > 50): 
            distances.append(dist)
            print(dist)
            print(len(distances))
            # print(dist)
        if distances:
            distances = [x-20 for x in distances]
            if distances[0] < 500:
                distances.pop(0)
                jump(True)
                
            # if dist < 420:
            #     playsound(sound)
                # gui.press('space')
            # else:
                # print("too far")
                # while dist > 370:
                #     dist -= 50
                #     print(dist)
                    # if gui.locateOnScreen('DinoChrome/game_over.png', confidence=0.2, grayscale=True, region=game_over_reg):
                    #     print("died while waiting to jump")
                    #     gui.hotkey('alt', 'tab')
                    #     return
                #     sleep(0.1)
                # playsound(sound)
                # print("jump")
                # gui.press('space')
        
        game_over = gui.locateOnScreen('DinoChrome/game_over.png', confidence=0.2, grayscale=True, region=game_over_reg)
        # sleep(dt)
    
    gui.hotkey('alt', 'tab')

if __name__ == '__main__':
    try:
        main()
    except:
        gui.hotkey('alt', 'tab')
        raise 



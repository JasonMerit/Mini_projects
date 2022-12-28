import pydirectinput as pdi
import pyautogui as gui
from time import sleep
from PIL import ImageGrab, ImageOps
from playsound import playsound
from pygame import mixer
from time import sleep, time
sound = "DinoChrome/ping.mp3"
start = time()
playsound(sound)
# sleep(0.5)


# mixer.init()
# mixer.music.load(sound)
# mixer.music.play()


# image = ImageGrab.grab()
# for i in range(10):
#     for j in range(10):
#         image.putpixel((i, j), (255,0, 0))
# # image.putpixel((30,60), (255,0, 0))
# image.show()
print(f"Time: {time() - start} seconds")
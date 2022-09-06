import pyautogui
import numpy as np
import cv2
from sys import exit

SIZE = 24
W, H = 24, 16
corner2grid = np.array([30, 88])

BLUE = [255, 0, 0]
GREEN = [0, 123, 0]
RED = [0, 0, 255]
DARK_BLUE = [123, 0, 0]
colors = [BLUE, GREEN, RED, DARK_BLUE]  # Add by screen shotting color and putting in (remember not RGB but BGR)

def alt_tab():
	pyautogui.keyDown("altleft")
	pyautogui.press("tab")
	pyautogui.keyUp("altleft")


def screenshot(reg=None):
	if reg:
		image = pyautogui.screenshot(region=reg)
	else:
		image = pyautogui.screenshot()
	
	return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def save_image(image, name):
	cv2.imwrite("images/" + name + ".png", image)

def show_image(image):
	if isinstance(image, str):
		image = cv2.imread(path, 0)

	cv2.imshow('output', image)
	cv2.waitKey(0)

def detect_corner():
	template = cv2.imread('images/upper_left.png', 0)
	image = screenshot()
	image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

	result = cv2.matchTemplate(template, image, cv2.TM_SQDIFF_NORMED)
	_,_,mnLoc,_ = cv2.minMaxLoc(result)
	
	return mnLoc

def grab_square_number(square):
	y, x = square
	reg = (offset[0] + x * SIZE, offset[1] + y * SIZE, 3,3)
	image = screenshot(reg).reshape((9, -1))
	# print(image)
	
	# Match pixels with colors
	for pixel in image:
		for i, color in enumerate(colors):
			if all(color == pixel):
				# print(i+1)
				return i + 1

	# print(image[0][0])
	# show_image(image)

def grab_grid():
	G = np.zeros((H, W))

	for i in range(W):
		for j in range(H):
			G[j, i] = grab_square_number((j, i))

	print(G)



# print(pyautogui.position())
# show_image("images/upper_left.png")


alt_tab()
corner = np.array(detect_corner())
offset = corner + corner2grid
# grab_square_color((0, 0))  # BLUE
# grab_square_color((1, 1))  # GREEN
# grab_square_color((3, 5))  # RED
# grab_square_number((2, 0))  # DARK BLUE

grab_grid()
alt_tab()
exit()


alt_tab()

upper_left_reg = (302, 150, 25, 25)
screenshot(upper_left_reg)


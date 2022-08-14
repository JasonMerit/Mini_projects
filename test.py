
import random as rng
import itertools
# import numpy as np
# from sys import exit
# from collections import defaultdict
# import copy

# grid = [[rng.randint(1, 9) if rng.random() < 0.5 else 0 for j in range(9)] for i in range(9)]
# grid = [[1 for j in range(9)] for i in range(9)]
# txt = "12"
# print(len(txt))

# for x, y in p:
# 	print(x, y)


def get_bracket_permutations(s):
	I = [i for i in range(len(s)) if s[i] in ["+", "-"]] # Occurences of either + or -
	if len(I) == 3:
		return [s]

	A = [s]
	for i in I:
		A.append(s[:i-1] + "(" + s[i-1:i+2] + ")" + s[i+2:])

	if len(I) > 1:
		a, b = I

		# Depending on relative positions amongst + and -
		if b - a > 2:
			A.append(s[:a-1] + "(" + s[a-1:a+2] + ")" + s[a+2:b-1] + "(" + s[b-1:b+2] + ")" + s[b+2:])
		else:
			A.append(s[:a-1] + "(" + s[a-1:b+2] + ")" + s[b+2:])

	return A

s = "9*8+2+5"
print(get_bracket_permutations(s))
nums = [1, 1, 1, 1]
print(len(list(itertools.permutations(nums))))

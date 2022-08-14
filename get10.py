import operator
import random
import itertools
import sys


op_dict = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}
ops = ["+", "-", "/"]


def read(txt):
	# Return primitives
	try: # Int
		return int(txt)
	except ValueError:
		# Cut off brackets
		if txt[0] == "(" and txt[-1] == ")":  # In brackets
			if txt.find(")") > txt[1:].find("("):  # Total encompassing
				return read(txt[1:-1])
	
	indices = [i for i in range(len(txt)) if txt[i] in ["+", "-"]] # Occurences of either + or -
	while indices:
		i = indices.pop()
		l, r = txt[0:i], txt[i+1:]

		# Continue if operator is enclosed in brackets 
		# - not enclosed if equal start and end brackets to the left (or right)
		if l.count("(") == l.count(")"):# and r.count("(") == r.count(")"):
			return read(l), txt[i], read(r)

	indices = [i for i in range(len(txt)) if txt[i] in ["/"]]
	if indices:
		i = indices[-1]
		op = txt[i]
		return read(txt[0:i]), op, read(txt[i+1:])

def compute(x):
	# Return primitive
	if isinstance(x, int):
		return x

	l, op, r = x

	# Check for division by zero
	den = compute(r)
	if op == "/" and den == 0:
		return False
	return op_dict[op](compute(l), den)

def get_bracket_permutations(s):
	I = [i for i in range(len(s)) if s[i] in ["+", "-"]] # Occurences of either + or -
	if len(I) == 3:
		return [s]

	A = [s]
	for i in I:  # redundancy by commititive law
		A.append(s[:i-1] + "(" + s[i-1:i+2] + ")" + s[i+2:])

	if len(I) > 1:
		a, b = I

		# Depending on relative positions amongst + and -
		if b - a > 2:
			A.append(s[:a-1] + "(" + s[a-1:a+2] + ")" + s[a+2:b-1] + "(" + s[b-1:b+2] + ")" + s[b+2:])
		else:
			A.append(s[:a-1] + "(" + s[a-1:b+2] + ")" + s[b+2:])

	return A


def go(nums):
	# Each permutation of numbers / operators / brackets - 3840 combinations
	# kek = 0
	p = len(ops)
	for A in list(itertools.permutations(nums)): # 4! = 24
		for i in range(p): # 4
			for j in range(p): # 4
				for k in range(p): # 4
					equation = str(A[0]) + ops[i] + str(A[1]) + ops[j] + str(A[2]) + ops[k] + str(A[3])
					for eq in get_bracket_permutations(equation): # avg 2.5
						# kek += 1
						r = read(eq)
						result = compute(r)
						if result == 10:
							print(eq, "=", int(result))
							# print(kek, "-")
							return True
	# print(kek)
	return False



A = [9,8,2,5]
# r = read("(1+3)*(2+8)")
# print(r)
# sys.exit()


n = 0
F = []
k = 10
for a in range(k):
	for b in range(k):
		for c in range(k):
			for d in range(k):
				n += 1
				A = [a, b, c, d]
				# if sum(A) < 10:
				# 	continue
				if not go(A): 
					F.append(A)
				# else:
				# 	print(A)
				# 	sys.exit()
for f in F:
	print(f)
print("fail ratio:", len(F), "/", n, "times")
# fail ratio: 2062 / 10000 times
# [Finished in 290.3s]

# fail ratio: 3532 / 10000 times
# [Finished in 214.5s] - no multiplication





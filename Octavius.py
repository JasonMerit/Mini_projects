import sys


def go(n):
	return 1 if n == 1 else "{0} {1}".format(n, go(n//2)) if n % 2 == 0 else "{0} {1}".format(n, go(n*3+1))



n = sys.stdin.readline()
sys.stdout.write(go(n))	

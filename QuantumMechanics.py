"""Solve shrinkage of a quantum dot in a magnetic field."""
from __future__ import division
from visual import *
from visual.graph import *
from visual.controls import *
from visual.filedialog import *

from math import *
from numpy import *

# Constants
hbar = 1.0546e-34
e = 1.6022e-19
m = 9.1094e-31
kB = 1.3806e-23
T = 300
kT = kB*T
gamma = 2.21e5
muB = 9.274e-24
mu0 = 4*pi*1e-7
e0 = 8.854e-12
h = 6.626e-34
hbar = h/(2*pi)
e = 1.602e-19
m = 9.109e-31
kB = 1.381e-23

# Parameters
N = 1000
L = 1e-9
dx = L/N
x = arange(-L/2, L/2, dx)
V0 = 0.5
B = 0.1
mu = 0.1
t = 0
dt = 1e-15
tmax = 1e-12
n = 0
nmax = int(tmax/dt)
E = zeros(N)
psi = zeros(N, complex)
psi = exp(-(x/L)**2)

# Graphs

gdisplay(x=0, y=0, width=600, height=600, title='Wavefunction',
            xtitle='x', ytitle='psi', xmax=L/2, xmin=-L/2, ymax=1.2, ymin=-1.2)
psiPlot = gcurve(color=color.red)
gdisplay(x=0, y=600, width=600, height=600, title='Energy',
            xtitle='x', ytitle='E', xmax=L/2, xmin=-L/2, ymax=1.2, ymin=-1.2)


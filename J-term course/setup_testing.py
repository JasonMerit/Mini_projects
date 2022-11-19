import sys

print sys.version

try:
    from PodSixNet.Connection import connection, ConnectionListener
except ImportError:
    print "Not OK: Can't find PodSixNet" 
else:
    print "OK:  found PodSixNet module."

try:
    from pgu import gui
except ImportError:
    print "Not OK: Can't find pgu" 
else:
    print "OK:  found pgu module."

try:
    import pygame
except ImportError:
    print "Not OK: Can't find pygame" 
else:
    print "OK:  found pygame."

try:
    from Box2D import *
except ImportError:
    print "Not OK: Can't find Box2D" 
else:
    print "OK:  found Box2D."


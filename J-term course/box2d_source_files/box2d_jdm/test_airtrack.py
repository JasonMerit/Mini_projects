#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# C++ version Copyright (c) 2006-2007 Erin Catto http://www.box2d.org
# Python version Copyright (c) 2010 kne / sirkne at gmail dot com
# 
# Implemented using the pybox2d SWIG interface for Box2D (pybox2d.googlecode.com)
# 
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

from framework import *

class BodyTypes(Framework):
    name="Body Types"
    description="Change body type keys: (d) dynamic, (s) static, (k) kinematic"
    speed = 3 # platform speed
    def __init__(self):
        super(BodyTypes, self).__init__()


        # The ground
        ground = self.world.CreateBody(
                    shapes=b2EdgeShape(vertices=[(-20,0),(20,0)]) 
                )

        # The attachment
        self.attachment=self.world.CreateDynamicBody(
                    position=(0,3), 
                    fixtures=b2FixtureDef(shape=b2PolygonShape(box=(0.5,2)), density=2.0),
                )

        # The platform
        fixture=b2FixtureDef(
                shape=b2PolygonShape(box=(4,0.5)), 
                density=2,
                friction=0.6,
                )
               
        self.platform=self.world.CreateDynamicBody(
                    position=(0,5), 
                    fixtures=fixture,
                )
        
        # The joints joining the attachment/platform and ground/platform
        self.world.CreateRevoluteJoint(
                bodyA=self.attachment,
                bodyB=self.platform,
                anchor=(0,5),
                maxMotorTorque=50,
                enableMotor=True
            )

        self.world.CreatePrismaticJoint(
                bodyA=ground,
                bodyB=self.platform,
                anchor=(0,5),
                axis=(1,0),
                maxMotorForce = 1000,
                enableMotor = True,
                lowerTranslation = -10,
                upperTranslation = 10,
                enableLimit = True 
            )

        # And the payload that initially sits upon the platform
        # Reusing the fixture we previously defined above
        fixture.shape.box = (0.75, 0.75)
        self.payload=self.world.CreateDynamicBody(
                    position=(0,8), 
                    fixtures=fixture,
                )

    def Keyboard(self, key):
        if key==Keys.K_d:
            self.platform.type=b2_dynamicBody
        elif key==Keys.K_s:
            self.platform.type=b2_staticBody
        elif key==Keys.K_k:
            self.platform.type=b2_kinematicBody
            self.platform.linearVelocity=(-self.speed, 0)
            self.platform.angularVelocity=0
        elif key == Keys.K_n:
            main(Airtrack)
        elif key == Keys.K_m:
            main(BodyTypes)

    def Step(self, settings):
        super(BodyTypes, self).Step(settings)

        if self.platform.type==b2_kinematicBody:
            p = self.platform.transform.position
            v = self.platform.linearVelocity
            if ((p.x < -10 and v.x < 0) or (p.x > 10 and v.x > 0)):
                v.x = -v.x
                self.platform.linearVelocity = v


                
                
class Airtrack(Framework):
    """You can use this class as an outline for your tests.

    """
    name = "Airtrack" # Name of the class to display
    description="The description text goes here"
    def __init__(self):
        """ 
        Initialize all of your objects here.
        Be sure to call the Framework's initializer first.
        """
        super(Airtrack, self).__init__()

        # Have some component of gravity along the track.
        self.world.gravity = (-2.0, -10.0)
        
        # Zoom in a bit.
        self.viewZoom = 31
        
        # Initialize all of the objects    

        # The track   
        ground = self.world.CreateStaticBody(
                    position=(0,0),
                    shapes=[b2EdgeShape(vertices=[(-10,0), (10,0)]),
                            b2PolygonShape(box=(0.2, 1, (-10, 1), 0)),
                            b2PolygonShape(box=(0.2, 1, (10, 1), 0))]
                )        
        
        # The cars
        x = -4
        for j in range(5):
            x += 2.5
            vx = j + 2
            vx = 0
            self.AddCar(self.world, x, vx, width=1, height=.2, my_restitution=1.00)        
        
    
    def AddCar(self, theWorld, x=0, vx=0, width=1, height=1, my_restitution=1.00):
        
        # Create a dynamic body
        # Bullet=True will turn on better collision detection (to avoid tunneling).
        dynamic_body = theWorld.CreateDynamicBody(position=b2Vec2(x, height), angle=0, bullet=False, linearVelocity=b2Vec2(vx, 0))
        
        # And add a box fixture onto it (with a nonzero density, so it will move)
        dynamic_body.CreatePolygonFixture(box=(width, height), density=1, friction=0.00, restitution=my_restitution)
        
        
    def Keyboard(self, key):
        """
        The key is from Keys.K_*
        (e.g., if key == Keys.K_z: ... )
        """
        
        # This restarts the demo. Probably overlays an instance. Just kill the command window to 
        # cleanup everything...
        if key == Keys.K_n:
            main(Airtrack)
        elif key == Keys.K_m:
            main(BodyTypes)

    def Step(self, settings):
        """Called upon every step.
        You should always call
         -> super(Your_Test_Class, self).Step(settings)
        at the beginning or end of your function.

        If placed at the beginning, it will cause the actual physics step to happen first.
        If placed at the end, it will cause the physics step to happen after your code.
        """

        super(Airtrack, self).Step(settings)

        # do stuff

        # Placed after the physics step, it will draw on top of physics objects
        self.Print("*** Base your own testbeds on me! ***")

    def ShapeDestroyed(self, shape):
        """
        Callback indicating 'shape' has been destroyed.
        """
        pass

    def JointDestroyed(self, joint):
        """
        The joint passed in was removed.
        """
        pass

    # More functions can be changed to allow for contact monitoring and such.
    # See the other testbed examples for more information.

if __name__=="__main__":
    main(Airtrack)


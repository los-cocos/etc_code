"""
A script to demo a defect in RectMapCollider, initial report by Netanel at
https://groups.google.com/forum/#!topic/cocos-discuss/a494vcH-u3I

The defect is that the player gets stuck at some positions, and it was confirmed
for cocos master Aug 1, 2015 (292ae676) and cocos-0.6.3-release, see cocos #248

The package 'blinker' (available from pipy) is needed to run this script

Further investigation shows that this happens when both of this concur
        1. the player actively pushes against a blocking surface
        2. player rect alligns with the grid tile. 

changes from the OP bugdemo code:
        lines irrelevant to the bug removed
        
        changed player controls
        
        added a view to show the potentially colliding cells that RectMapCollider
        will consider (sin as red rectangle overlapping the player)

        player pic edited to make visible the actual player boundary
        
Controlling the player:
        use left-right for horizontal move, must keep pressing to move
        use up-down to move vertical; a press adds/substracts up to y-velocity

Demoing the bug:
        1. move to touch the left wall.
        2. release 'left' key
        3. move up and down, this works
        4. keep pressed the 'left' key, and try to move down: player gets stuck
           at some alineations 

scene
	background
	scroller=ScrollingManager
		tilemap <- load(...)['map0']
		layer=Game (a ScrollableLayer)
			sprite
			particles
		potential collisions view, ShowCollision


"""

from __future__ import division, print_function
from cocos.particle_systems import *
from cocos.particle import Color
from cocos.text import Label
from cocos.tiles import load, RectMapLayer
from cocos.mapcolliders import RectMapWithPropsCollider
from cocos.layer import Layer, ColorLayer, ScrollingManager, ScrollableLayer
from cocos.sprite import Sprite
from cocos.actions import *
from cocos.scene import Scene
from cocos.director import director
from pyglet.window import key
from pyglet.window.key import symbol_string, KeyStateHandler
from menu import GameMenu

import blinker

director.init(width=1920, height=480, autoscale = True, resizable = True)

Map = load("mapmaking.tmx")
scroller = ScrollingManager()
tilemap = Map['map0']
assert tilemap.origin_x == 0 
assert tilemap.origin_y == 0 

			
class Background(ColorLayer):
    def __init__(self):
        super(Background, self).__init__(65,120,255,255)


class ShowCollision(ScrollableLayer):
    """
    A layer to show the cells a RectMapCollider considers potentially
    colliding with the 'new' rect.

    Use with CustomRectMapCollider so the event of interest is published
    """
    def __init__(self):
        super(ShowCollision, self).__init__()
        self.collision_view = []
        for i in range(10):
                self.collision_view.append(ColorLayer(255, 0, 0, 255, width=64, height=64))
        for e in self.collision_view:
            self.add(e)
        signal = blinker.signal("collider cells")
        signal.connect(self.on_collision_changed)

    def on_collision_changed(self, sender, payload=None):
        for cell, view in zip(payload, self.collision_view):
            view.position = (cell.i * 64, cell.j * 64)
            view.opacity = 140
        for i in range(len(payload), len(self.collision_view)):
            self.collision_view[i].opacity = 0
                

class Game(ScrollableLayer):
    is_event_handler = True
    
    def __init__(self):
        super(Game, self).__init__()
        
        self.score = 0
                
        # Add player
        self.sprite = Sprite('magic.png')
        self.sprite.position = 320, 240
        self.sprite.direction = "right"
        self.sprite.dx = 0
        self.sprite.dy = 0
        self.add(self.sprite, z=1)

        # A list of balls
        self.balls = set()
        
        # Teleportation counter
        self.teleportation = 0
                
        self.sprite.jump = 0

                
    def on_key_press(self, inp, modifers):
        
        if symbol_string(inp) == "LEFT":
            self.sprite.dx -= 3
            print("press left, dx:", self.sprite.dx)

        
        if symbol_string(inp) == "RIGHT":
            self.sprite.dx += 3
            print("press right, dx:", self.sprite.dx)

        if symbol_string(inp) == "UP":
            self.sprite.dy += 3
            if self.sprite.dy > 6:
                                self.sprite.dy = 6
            print("press up, dy:", self.sprite.dy)

        
        if symbol_string(inp) == "DOWN":
            self.sprite.dy -= 3
            if self.sprite.dy < -6:
                                self.sprite.dy = -6
            print("press down, dy:", self.sprite.dy)
            
                    
    def on_key_release(self, inp, modifers):
        if symbol_string(inp) == "LEFT":
            self.sprite.dx = 0
            print("release left, dx:", self.sprite.dx)
        if symbol_string(inp) == "RIGHT":
            self.sprite.dx = 0
            print("release right, dx:", self.sprite.dx)

class SpyCollider(RectMapWithPropsCollider):
    """
    Same as RectMapWithPropsCollider, except it publishes which cells will be considered
    for collision.

    Usage:
        # istantiate
        a = SpyCollider()
        # set the behavior for velocity change on collision with
        # a.on_bump_handler = a.on_bump_slide
        # add the signal we want to emit
        a.signal = blinker.signal("collider cells")
        # use as stock RectMapCollider
        # catch the signal with something like ShowCollision
    """
    def collide_map(self, maplayer, last, new, vx, vy):
        """collide_map en dos pasadas; """
        objects = maplayer.get_in_region(*(new.bottomleft + new.topright))
        self.signal.send(payload=objects)
        return super(SpyCollider, self).collide_map(maplayer, last, new, vx, vy)


layer = Game()
collider = SpyCollider()
collider.on_bump_handler = collider.on_bump_slide
collider.signal = blinker.signal("collider cells")
#collider = RectMapCollider()

# WARN: this was hacked for bugdemo purposes only; don't use in real code:
#       lots of globals
#       position delta must use dt, else unpredictable view velocity 
def update(dt):
	""" Update game"""
	last = layer.sprite.get_rect()
	new = last.copy()
	new.x += layer.sprite.dx
	new.y += layer.sprite.dy
	# dont care about velocity, pass 0, 0
	collider.collide_map(tilemap, last, new, 0.0, 0.0)
	layer.sprite.position = new.center
	scroller.set_focus(*new.center)

# Schedule Updates
layer.schedule(update)

# Add map to scroller
scroller.add(tilemap)

#Create Scene
scene = Scene()

# Create and add background
background = Background()
scene.add(background)

#Add main layer to scroller
scroller.add(layer)
scroller.add(ShowCollision())

# Add scroller to scene
scene.add(scroller)

# Game menu configuration
menu = GameMenu(scene)
menuScene = Scene()
menuScene.add(menu)

director.run(menuScene)

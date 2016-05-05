from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "s, q"
tags = "TmxObjectMapCollider, collide_map"

from math import sin, cos, radians

import pyglet
from pyglet.window import key

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer
from cocos import mapcolliders
from cocos.mapcolliders import TmxObjectMapCollider


class Ball(cocos.sprite.Sprite):
    def __init__(self, position, velocity, fn_collision_handler):
        super(Ball, self).__init__("circle6.png", color=(255, 0, 255))
        self.opacity = 128
        self.position = position
        self.velocity = velocity
        self.fn_collision_handler = fn_collision_handler
        self.schedule(self.step)

    def step(self, dt):
        vx, vy = self.velocity
        dx = vx * dt
        dy = vy * dt
        last = self.get_rect()
        new = last.copy()
        new.x += dx
        new.y += dy
        self.velocity = self.fn_collision_handler(last, new, vx, vy)
        self.position = new.center

class Actors(cocos.layer.ScrollableLayer):
    is_event_handler = True
    def __init__(self, fn_collision_handler):
        super(Actors, self).__init__()
        self.fn_collision_handler = fn_collision_handler
        self.num_balls = 0

    def add_ball(self):
        k = self.num_balls
        vx = cos(radians(k * 3)) * 600.0
        vy = sin(radians(k * 3)) * 600.0
        b = Ball((300, 300), (vx, vy), self.fn_collision_handler) 
        self.add(b)
        self.num_balls += 1
        print("balls:", self.num_balls)
        
    def on_key_press(self, key, modifier):
        if key == pyglet.window.key.SPACE:
            self.add_ball()
        if key == pyglet.window.key.Z:
            scale = platformer_scene.scale
            scale = 0.25 if scale == 1.0 else 1.0
            platformer_scene.scale = scale

description = """
Shows how to use a TmxMapCollider to control collision between actors and the terrain.
Use SPACE to add a ball
Use Z to togglt scale
"""


def main():
    global keyboard, walls, scroller, platformer_scene
    from cocos.director import director
    director.init(width=800, height=600, autoscale=False)

    print(description)

    # add the tilemap and the player sprite layer to a scrolling manager
    scroller = layer.ScrollingManager()
    walls = tiles.load('tmx_collision.tmx')['walls']
    assert isinstance(walls, tiles.TmxObjectLayer)
    scroller.add(walls, z=0)

    # make the function to handle collision between actors and walls
    mapcollider = TmxObjectMapCollider()
    mapcollider.on_bump_handler = mapcollider.on_bump_bounce
    fn_collision_handler = mapcolliders.make_collision_handler(mapcollider, walls)

    # make the function to set visual focus at position
    fn_set_focus = scroller.set_focus
    
    scroller.add(Actors(fn_collision_handler), z=1)

    # set the player start using the object with the 'player_start' property
    player_start = walls.find_cells(player_start=True)[0]

    # extract the player_start, which is not a wall
    walls.objects.remove(player_start)

    # construct the scene with a background layer color and the scrolling layers
    platformer_scene = cocos.scene.Scene()
    platformer_scene.add(layer.ColorLayer(100, 120, 150, 255), z=0)
    platformer_scene.add(scroller, z=1)
    platformer_scene.scale = 0.75

    # set focus 
    scroller.set_focus(300, 300)

    # track keyboard presses
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    # run the scene
    director.run(platformer_scene)


if __name__ == '__main__':
    main()

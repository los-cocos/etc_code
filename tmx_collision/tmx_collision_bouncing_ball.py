from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "s, q"
tags = "TmxObjectMapCollider, collide_map"

import pyglet
from pyglet.window import key

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer
from cocos import mapcolliders
from cocos.mapcolliders import TmxObjectMapCollider


class Ball(cocos.sprite.Sprite):
    def __init__(self, position, velocity, fn_collision_handler, fn_set_focus, color):
        super(Ball, self).__init__("circle6.png", color=color)
        self.opacity = 128
        self.position = position
        self.velocity = velocity
        self.fn_collision_handler = fn_collision_handler
        self.fn_set_focus = fn_set_focus
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
        self.fn_set_focus(*self.position)


description = """
Shows how to use a TmxMapCollider to control collision between actors and the terrain.
Use Left-Right arrows and space to control.
Use D to show cell / tile info
"""


def main():
    global keyboard, walls, scroller
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
    
    # create a layer to put the player in
    actors_layer = layer.ScrollableLayer()
    ball = Ball((300, 300), (600, 600), fn_collision_handler, fn_set_focus, (255, 0, 255)) 
    actors_layer.add(ball)

    scroller.add(actors_layer, z=1)

    # set the player start using the object with the 'player_start' property
    player_start = walls.find_cells(player_start=True)[0]
    ball.position = player_start.center

    # set focus so the player is in view
    scroller.set_focus(*ball.position)

    # extract the player_start, which is not a wall
    walls.objects.remove(player_start)

    # construct the scene with a background layer color and the scrolling layers
    platformer_scene = cocos.scene.Scene()
    platformer_scene.add(layer.ColorLayer(100, 120, 150, 255), z=0)
    platformer_scene.add(scroller, z=1)

    # track keyboard presses
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)

    # run the scene
    director.run(platformer_scene)


if __name__ == '__main__':
    main()

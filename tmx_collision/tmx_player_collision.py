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
from cocos import tiles, actions, layer, mapcolliders


class PlatformerController2(actions.Action):
    on_ground = True
    MOVE_SPEED = 300
    JUMP_SPEED = 600
    GRAVITY = -1200

    def start(self):
        self.target.velocity = (0, 0)

    def step(self, dt):
        global keyboard, scroller
        vx, vy = self.target.velocity

        # using the player controls, gravity and other acceleration influences
        # update the velocity
        vx = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * self.MOVE_SPEED
        vy += self.GRAVITY * dt
        if self.on_ground and keyboard[key.SPACE]:
            vy = self.JUMP_SPEED

        # with the updated velocity calculate the (tentative) displacement
        dx = vx * dt
        dy = vy * dt

        # get the player's current bounding rectangle
        last = self.target.get_rect()

        # build the tentative displaced rect
        new = last.copy()
        new.x += dx
        new.y += dy

        # account for hitting obstacles, it will adjust new and vx, vy
        self.target.velocity = self.target.collision_handler(last, new, vx, vy)

        # update on_ground status
        self.on_ground = (new.y == last.y)

        # update player position; player position is anchored at the center of the image rect
        self.target.position = new.center

        # move the scrolling view to center on the player
        scroller.set_focus(*new.center)

description = """
Shows how to use a TmxMapCollider to control collision between actors and TmxObjects.
Use Left-Right arrows and space to control.
Use D to show cell / tile info
"""


def main():
    global keyboard, walls, scroller
    from cocos.director import director
    director.init(width=800, height=600, autoscale=False)

    print(description)
    # create the scrolling manager that will hold all game entities
    scroller = layer.ScrollingManager()

    # load the map layer of interest and add to the level
    walls = tiles.load('tmx_collision.tmx')['walls']
    assert isinstance(walls, tiles.TmxObjectLayer)
    scroller.add(walls, z=0)

    # create a layer to put the player in; it will care for player scroll
    player_layer = layer.ScrollableLayer()

    # NOTE: the anchor for this sprite is in the CENTER (the cocos default)
    # which means all positioning must be done using the center of its rect
    player = cocos.sprite.Sprite('witch-standing.png')
    player_layer.add(player)
    player.do(PlatformerController2())
    scroller.add(player_layer, z=1)

    # set the player start using the object with the 'player_start' property
    player_start = walls.find_cells(player_start=True)[0]

    # for convenience the player start was give the same dimensions as player,
    # so put player.center over player start center
    player.position = player_start.center

    # set focus so the player is in view
    scroller.set_focus(*player.position)

    # extract the player_start, which is not a wall
    walls.objects.remove(player_start)

    # give a collision handler to the player
    mapcollider = mapcolliders.TmxObjectMapCollider()
    mapcollider.on_bump_handler = mapcollider.on_bump_slide
    player.collision_handler = mapcolliders.make_collision_handler(mapcollider, walls)

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

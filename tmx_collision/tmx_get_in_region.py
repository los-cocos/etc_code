from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

testinfo = "s, q"
tags = "TmxObjectLayer, get_in_region"

import pyglet
from pyglet.window import key

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer


class DriveCar(actions.Driver):
    def step(self, dt):
        # handle input and move the car
        self.target.rotation += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        self.target.acceleration = (keyboard[key.UP] - keyboard[key.DOWN]) * 400
        if keyboard[key.SPACE]: self.target.speed = 0
        super(DriveCar, self).step(dt)
        scroller.set_focus(self.target.x, self.target.y)

        # update wall colors
        rect = self.target.get_rect()
        overlapped = self.walls.get_in_region(rect.left, rect.bottom, rect.right, rect.top)
        for obj in self.walls.objects:
            color = (255, 0, 0) if obj in overlapped else (255, 255, 255)
            if obj in self.walls._sprites:
                self.walls._sprites[obj].color = color
                

description = """
TmxObjectLayer.get_in_region() test - move actor with arrows,
objects overlapped by the car will tint red
"""

def main():
    global keyboard, walls, scroller
    from cocos.director import director
    director.init(width=800, height=600, autoscale=False)

    print(description)

    car_layer = layer.ScrollableLayer()
    car = cocos.sprite.Sprite('car.png')
    car_layer.add(car)
    car.position = (200, 100)
    car.max_forward_speed = 200
    car.max_reverse_speed = -100
    worker_action = car.do(DriveCar())

    # add the map and the player sprite layer to a scrolling manager
    scroller = layer.ScrollingManager()
    walls = tiles.load('tmx_collision.tmx')['walls']
    assert isinstance(walls, tiles.TmxObjectLayer)
    worker_action.walls = walls
    scroller.add(walls, z=0)
    scroller.add(car_layer, z=1)

    player_start = walls.find_cells(player_start=True)[0]

    # extract the player_start, which is not a wall
    walls.objects.remove(player_start)

    # give car access to the walls so it can change colors
    car.walls = walls

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

#!/usr/bin/env python3
# -*-coding:utf-8 -*

import cocos
from cocos.text import HTMLLabel
from cocos.director import director

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super(TestLayer, self).__init__()

        x, y = director.get_window_size()

        self.text = HTMLLabel("""<center><font color=white size=4>
Image here --><img src="grossini.png"><-- here.</font></center>""", 
            (100, y//2))
        self.add(self.text)

def main():
    director.init()
    test_layer = TestLayer()
    main_scene = cocos.scene.Scene(test_layer)
    director.run(main_scene)

if __name__ == '__main__':
    main()
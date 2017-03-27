#snippet 1: crash with traceback
import cocos
cocos.director.director.init()
sp = cocos.sprite.Sprite("Untitled.png")
tmx_data = cocos.tiles.load_tmx("untitled.tmx")


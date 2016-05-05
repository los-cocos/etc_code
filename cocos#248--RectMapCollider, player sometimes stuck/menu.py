from cocos.director import director
from cocos.menu import Menu, CENTER, MenuItem, shake, shake_back
from cocos.scene import Scene
from pyglet.app import exit

class GameMenu(Menu):
	def __init__(self, gameScene):

		super(GameMenu, self).__init__("Theodorism")

		self.menu_valign = CENTER
		self.menu_halign = CENTER

		self.gameScene = gameScene
		
		menu_items = [

			(MenuItem("Play", self.play_game)),
			(MenuItem("Settings", self.settings)),
			(MenuItem("Credits", self.credits_game)),
			(MenuItem("Exit", self.on_quit))
		]

		self.create_menu(menu_items)


	def play_game(self):
		director.replace(self.gameScene)

		

	# Now for the volume up functionality
	def settings(self):
		pass

	# And the exact opposite for volume down
	def credits_game(self):
		pass

	def on_quit(self):
		exit()




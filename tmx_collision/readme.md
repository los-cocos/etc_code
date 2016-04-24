scripts to explore and test TmxObjectMapCollider api

works with cocos from branch tmx_collision

- tmx_get_in_region : tests TmxObjectLayer.get_in_region() new implementation
- tmx_player_collision.py : a test_platformer.py translation from tiles to tmx objects, uses the Drive style controller. Exercises TmxObjectMapCollider with the mode 'slide' 
- tmx_collision_bouncing_ball.py : a classic bounce ball script, uses the classic ball.step(dt) to update actor. Exercises TmxObjectMapCollider with the mode 'bounce'; change 'bounce' to 'stick' to see stick mode in action.

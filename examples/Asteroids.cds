{
  "type": "stack",
  "handlers": {},
  "properties": {
    "can_save": false,
    "author": "",
    "info": ""
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\n\ntry_again.hide()\nasteroid.hide()\nisGameOver = False",
        "on_show_card": "self.send_message(\"start\")",
        "on_key_press": "# Respond to these keys once per press, on KeyDown\nif key_name == \"Space\" and not isGameOver:\n   self.send_message(\"shoot\")\nelif key_name == \"Return\" and isGameOver:\n   self.send_message(\"start\")",
        "on_key_hold": "if not isGameOver:\n   # Respond to these keys continuously while pressed\n   if key_name == \"Left\":\n      ship.rotation -= 180*elapsed_time\n   elif key_name == \"Right\":\n      ship.rotation += 180*elapsed_time\n   \n   elif key_name == \"Up\":\n      ship.speed += rotate_point((0, 450*elapsed_time), ship.rotation)\n      play_sound(\"puff.wav\")",
        "on_mouse_press": "if is_using_touch_screen():\n   if not isGameOver:\n      if not ship.is_touching_point(mouse_pos):\n         ship.rotation = angle_from_points(ship.center, mouse_pos)\n         self.send_message(\"shoot\")\n   else:\n      self.send_message(\"start\")\n",
        "on_message": "if message == \"start\":\n   # Delete all asteroids\n   for c in card.children.copy():\n      if c.name.startswith(\"asteroid_\"):\n         c.delete()\n   \n   # Set up the first asteroid, as a clone of the original, hidden one\n   ast = asteroid.clone()\n   if randint(0, 1):\n      ast.position = (100,randint(50, card.size.height-100))\n   else:\n      ast.position = (randint(50, card.size.width-100),100)\n   \n   ast.speed += (randint(-100,100), randint(-100,100))\n   ast.show()\n   numAsteroids = 1\n   isGameOver = False\n   ship.rotation = 0\n   ship.center = card.center\n   try_again.hide()\n\nelif message == \"shoot\":\n   # Create shot\n   shot = card.add_oval(\"shot\",\n      center=(ship.center+rotate_point((0, 50), ship.rotation)),\n      size=(10,10),\n      fill_color='red',\n      speed=ship.speed+rotate_point((0, 150), ship.rotation))\n   # Delete after 2 seconds\n   run_after_delay(2, shot.delete)\n   # recoil the ship\n   ship.speed -= rotate_point((0, 3), ship.rotation)\n\nelif message == \"gameOver\":\n   # Stop the ship\n   ship.speed = (0,0)\n   \n   # Stop all asteroids, and Delete shots\n   for c in card.children.copy():\n      if c.name.startswith(\"asteroid_\"):\n         c.speed = (0, 0)\n      if c.name.startswith(\"shot\"):\n         c.delete()\n   isGameOver = True\n   try_again.show()\n",
        "on_resize": "try_again.center = [card.center.x, card.size.height-40]"
      },
      "properties": {
        "name": "card_1",
        "size": [
          800,
          800
        ],
        "fill_color": "#000000",
        "can_resize": true
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {
            "on_message": "if message == \"hit\":\n   # Then split in half\n   angle = randint(0, 360)\n   dSpeed = randint(10, 30)\n   # Create 2 new asteroids\n   ratio1 = randint(35, 50)/100.0\n   ratio2 = 1.1-ratio1\n   \n   child.hide()  # Just hide the shot, since it will be Deleted within a couple seconds\n   \n   if self.size.width * ratio1 >= 12:\n      sub1 = self.clone(size=self.size*ratio1)\n      sub1.speed += rotate_point((0, dSpeed/ratio1), angle)\n      numAsteroids += 1\n   if self.size.width * ratio2 >= 12:\n      sub2 = self.clone(size=self.size*ratio2)\n      sub2.speed -= rotate_point((0, dSpeed/ratio2), angle)\n      numAsteroids += 1\n   \n   self.delete()  # Delete this asteroid\n   numAsteroids -= 1\n",
            "on_periodic": "if not self.is_visible:\n   return\n\n# Wrap this asteroid around the edges of the card\nif self.center.y <= 0 and self.speed.y < 0:\n   # Off the Bottom edge\n   self.center = [self.center.x, card.size.height]\nelif self.center.y >= card.size.height and self.speed.y > 0:\n   # Off the Top edge\n   self.center = [self.center.x, 0]\nelif self.center.x <= 0 and self.speed.x < 0:\n   # Off the Left edge\n   self.center = [card.size.width, self.center.y]\nelif self.center.x >= card.size.width and self.speed.x > 0:\n   # Off the Right edge\n   self.center = [0, self.center.y]\n\n# Did any shot objects touch me?\nhits = []\nfor child in card.children:\n   if child.name.startswith(\"shot\") and child.is_visible:\n      d = distance(self.center, child.center)\n      if d <= self.size.width/2 + child.size.width/2:\n         self.send_message(\"hit\")\n         if numAsteroids == 0:\n            card.send_message(\"gameOver\")\n"
          },
          "properties": {
            "name": "asteroid",
            "size": [
              80,
              80
            ],
            "position": [
              96.0,
              625.0
            ],
            "originalSize": [
              69,
              69
            ],
            "pen_color": "#000000CC",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#DEE2DBCC"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              69.0,
              69.0
            ]
          ]
        },
        {
          "type": "image",
          "handlers": {
            "on_periodic": "# Only move if we're not isGameOver / gameOver\nif not isGameOver:\n   # Respond to these keys continuously while pressed\n   if is_mouse_pressed() and is_using_touch_screen() and self.is_touching_point(get_mouse_pos()):\n      ship.speed += rotate_point((0, 450*elapsed_time), ship.rotation)\n      play_sound(\"puff.wav\")\n\n   if is_key_pressed(\"Up\"):\n      self.file = \"ship-on.png\"\n   else:\n      ship.file = \"ship-off.png\"\n\n   # Wrap the ship around the edges of the card\n   if ship.center.y <= 0 and ship.speed.y < 0:\n      # Off the Bottom edge\n      ship.center = [self.center.x, card.size.height]\n   elif ship.center.y >= card.size.height and ship.speed.y > 0:\n      # Off the Top edge\n      ship.center = [self.center.x, 0]\n   elif ship.center.x <= 0 and ship.speed.x < 0:\n      # Off the Left edge\n      ship.center = [card.size.width, self.center.y]\n   elif ship.center.x >= card.size.width and ship.speed.x > 0:\n      # Off the Right edge\n      ship.center = [0, self.center.y]\n\n   # Did we collide with any asteroid?\n   for child in card.children:\n      # Check the asteroid clones, but not the original, hidden asteroid\n      if child.name.startswith(\"asteroid_\"):\n         d = distance(self.center, child.center)\n         if d <= 30 + child.size.width/2:\n            card.send_message(\"gameOver\")\n            break\n"
          },
          "properties": {
            "name": "ship",
            "size": [
              114,
              114
            ],
            "position": [
              319.0,
              391.0
            ],
            "file": "ship-off.png",
            "fit": "Center",
            "rotation": 0.0,
            "xFlipped": false,
            "yFlipped": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "try_again",
            "size": [
              400,
              35
            ],
            "position": [
              185.0,
              756.0
            ],
            "text": "Press Return to Play Again",
            "alignment": "Center",
            "text_color": "white",
            "font": "Default",
            "font_size": 18,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 9,
  "CardStock_stack_version": "0.99.6"
}
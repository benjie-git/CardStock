{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      800,
      800
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\nfrom math import radians, sin, cos\n\n# rotate point by angle in degrees around (0,0)\ndef rotate(point, angle):\n   angle = radians(angle)\n   px, py = point\n   return [-(cos(angle) * px - sin(angle) * py),\n           sin(angle) * px + cos(angle) * py]\n\ntry_again.Hide()\nasteroid.Hide()\nisGameOver = False\n\nself.SendMessage(\"start\")\n",
        "OnKeyDown": "# Respond to these keys once per press, on KeyDown\nif keyName == \"Space\" and isGameOver == False:\n   shot = card.AddOval(\"shot\",\n      center=(ship.center+rotate((0, 60), ship.rotation)),\n      size=(10,10),\n      fillColor='red',\n      speed=ship.speed+rotate((0, 150), ship.rotation))\n   ship.speed -= rotate((0, 3), ship.rotation)\n   RunAfterDelay(2, shot.Delete)\n\nelif keyName == \"Return\" and isGameOver == True:\n      isGameOver = False\n      ship.rotation = 0\n      ship.center = card.center\n      ast = asteroid.Clone()\n      ast.position = (100,100)\n      ast.speed += (randint(-100,100), randint(-100,100))\n      ast.Show()\n      numAsteroids = 1\n      try_again.Hide()\n",
        "OnMessage": "if message == \"start\":\n   # Set up the first asteroid, as a clone of the original, hidden one\n   ast = asteroid.Clone()\n   ast.position = (100,100)\n   ast.speed += (randint(-100,100), randint(-100,100))\n   ast.Show()\n   numAsteroids = 1\n\nelif message == \"gameOver\":\n   # Stop the ship\n   ship.speed = (0,0)\n   \n   # Delete all asteroids and shots\n   for c in card.children.copy():\n      if c.name.startswith(\"asteroid_\") or c.name.startswith(\"shot\"):\n         c.Delete()\n   isGameOver = True\n   try_again.Show()\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#000000"
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {
            "OnIdle": "if not self.visible:\n   return\n\n# Wrap this asteroid around the edges of the card\nif self.center.y <= 0 and self.speed.y < 0:\n   # Off the Top edge\n   self.center = [self.center.x, card.size.y]\nelif self.center.y >= card.size.height and self.speed.y > 0:\n   # Off the Bottom edge\n   self.center = [self.center.x, 0]\nelif self.center.x <= 0 and self.speed.x < 0:\n   # Off the Left edge\n   self.center = [card.size.x, self.center.y]\nelif self.center.x >= card.size.width and self.speed.x > 0:\n   # Off the Right edge\n   self.center = [0, self.center.y]\n\n# Did any shot objects touch me?\nfor child in card.children:\n   if child.name.startswith(\"shot\") and child.visible:\n      if child.IsTouching(self):\n         # Then split in half\n         angle = randint(0, 360)\n         dSpeed = randint(20, 30)\n         # Create 2 new asteroids\n         ratio1 = randint(35, 50)/100.0\n         ratio2 = 1.1-ratio1\n         if self.size.width * ratio1 >= 12:\n            sub1 = self.Clone(size=self.size*ratio1)\n            sub1.speed = self.speed + rotate((0, dSpeed/ratio1), angle)\n            numAsteroids += 1\n         if self.size.width * ratio2 >= 12:\n            sub2 = self.Clone(size=self.size*ratio2)\n            sub2.speed = self.speed + rotate((0, dSpeed/ratio2), angle)\n            numAsteroids += 1\n         child.Hide()  # Just hide the shot, since it will be Deleted within a couple seconds\n         self.Delete()  # Delete this asteroid\n         numAsteroids -= 1\n         \n         if numAsteroids == 0:\n            card.SendMessage(\"gameOver\")\n"
          },
          "properties": {
            "name": "asteroid",
            "size": [
              80,
              80
            ],
            "position": [
              100.0,
              631.0
            ],
            "originalSize": [
              69,
              69
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "#cdd0c8"
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "try_again",
            "size": [
              800,
              35
            ],
            "position": [
              0.0,
              756.0
            ],
            "text": "Press Return to Play Again",
            "alignment": "Center",
            "textColor": "white",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "# Only move if we're not isGameOver / gameOver\nif isGameOver == False:\n   \n   # Respond to these keys continuously while pressed\n   if IsKeyPressed(\"Left\"):\n      self.rotation -= 5\n   if IsKeyPressed(\"Right\"):\n      self.rotation += 5\n   \n   if IsKeyPressed(\"Up\"):\n      self.speed += rotate((0, 15), self.rotation)\n      self.file = \"ship-on.png\"\n      SoundPlay(\"puff.wav\")\n   else:\n      self.file = \"ship-off.png\"\n\n   # Wrap the ship around the edges of the card\n   if ship.center.y <= 0 and ship.speed.y < 0:\n      # Off the Bottom edge\n      ship.center = [self.center.x, card.size.y]\n   elif ship.center.y >= card.size.height and ship.speed.y > 0:\n      # Off the Top edge\n      ship.center = [self.center.x, 0]\n   elif ship.center.x <= 0 and ship.speed.x < 0:\n      # Off the Left edge\n      ship.center = [card.size.x, self.center.y]\n   elif ship.center.x >= card.size.width and ship.speed.x > 0:\n      # Off the Right edge\n      ship.center = [0, self.center.y]\n\n   # Did we collide with any asteroid?\n   for child in card.children:\n      # Check the asteroid clones, but not the original, hidden asteroid\n      if child.name.startswith(\"asteroid_\"):\n         if self.IsTouchingPoint(child.center):\n            card.SendMessage(\"gameOver\")\n            break\n"
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
            "rotation": 0,
            "xFlipped": false,
            "yFlipped": false
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.8.12"
}
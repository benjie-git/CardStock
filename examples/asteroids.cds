{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      800,
      800
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\nfrom math import radians, sin, cos\n\n# rotate point by angle in degrees around (0,0)\ndef rotate(point, angle):\n   angle = radians(angle)\n   px, py = point\n   return [-(cos(angle) * px - sin(angle) * py),\n           sin(angle) * px + cos(angle) * py]\n\ntry_again.Hide()\nasteroid.Hide()\nisGameOver = False\n\nself.SendMessage(\"start\")\n",
        "OnKeyDown": "# Respond to these keys once per press, on KeyDown\nif keyName == \"Space\" and not isGameOver:\n   # Create shot\n   shot = card.AddOval(\"shot\",\n      center=(ship.center+rotate((0, 50), ship.rotation)),\n      size=(10,10),\n      fillColor='red',\n      speed=ship.speed+rotate((0, 150), ship.rotation))\n   # Delete after 2 seconds\n   RunAfterDelay(2, shot.Delete)\n   # recoil the ship\n   ship.speed -= rotate((0, 3), ship.rotation)\n\nelif keyName == \"Return\" and isGameOver:\n   self.SendMessage(\"start\")",
        "OnKeyHold": "if not isGameOver:\n   # Respond to these keys continuously while pressed\n   if keyName == \"Left\":\n      ship.rotation -= 5\n   if keyName == \"Right\":\n      ship.rotation += 5\n   \n   if keyName == \"Up\":\n      ship.speed += rotate((0, 15), ship.rotation)\n      PlaySound(\"puff.wav\")\n",
        "OnResize": "try_again.center = [card.center.x, card.size.height-40]",
        "OnMessage": "if message == \"start\":\n   # Delete all asteroids\n   for c in card.children.copy():\n      if c.name.startswith(\"asteroid_\"):\n         c.Delete()\n   \n   # Set up the first asteroid, as a clone of the original, hidden one\n   ast = asteroid.Clone()\n   if randint(0, 1):\n      ast.position = (100,randint(50, card.size.height-100))\n   else:\n      ast.position = (randint(50, card.size.width-100),100)\n   \n   ast.speed += (randint(-100,100), randint(-100,100))\n   ast.Show()\n   numAsteroids = 1\n   isGameOver = False\n   ship.rotation = 0\n   ship.center = card.center\n   try_again.Hide()\n\n\nelif message == \"gameOver\":\n   # Stop the ship\n   ship.speed = (0,0)\n   \n   # Stop all asteroids, and Delete shots\n   for c in card.children.copy():\n      if c.name.startswith(\"asteroid_\"):\n         c.speed = (0, 0)\n      if c.name.startswith(\"shot\"):\n         c.Delete()\n   isGameOver = True\n   try_again.Show()\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#000000"
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {
            "OnMessage": "if message == \"hit\":\n   # Then split in half\n   angle = randint(0, 360)\n   dSpeed = randint(10, 30)\n   # Create 2 new asteroids\n   ratio1 = randint(35, 50)/100.0\n   ratio2 = 1.1-ratio1\n   if self.size.width * ratio1 >= 12:\n      sub1 = self.Clone(size=self.size*ratio1)\n      sub1.speed += rotate((0, dSpeed/ratio1), angle)\n      numAsteroids += 1\n   if self.size.width * ratio2 >= 12:\n      sub2 = self.Clone(size=self.size*ratio2)\n      sub2.speed -= rotate((0, dSpeed/ratio2), angle)\n      numAsteroids += 1\n   \n   child.Hide()  # Just hide the shot, since it will be Deleted within a couple seconds\n   self.Delete()  # Delete this asteroid\n   numAsteroids -= 1\n",
            "OnPeriodic": "if not self.visible:\n   return\n\n# Wrap this asteroid around the edges of the card\nif self.center.y <= 0 and self.speed.y < 0:\n   # Off the Bottom edge\n   self.center = [self.center.x, card.size.y]\nelif self.center.y >= card.size.height and self.speed.y > 0:\n   # Off the Top edge\n   self.center = [self.center.x, 0]\nelif self.center.x <= 0 and self.speed.x < 0:\n   # Off the Left edge\n   self.center = [card.size.x, self.center.y]\nelif self.center.x >= card.size.width and self.speed.x > 0:\n   # Off the Right edge\n   self.center = [0, self.center.y]\n\n# Did any shot objects touch me?\nfor child in card.children:\n   if child.name.startswith(\"shot\") and child.visible:\n      if child.IsTouching(self):\n         self.SendMessage(\"hit\")\n         if numAsteroids == 0:\n            card.SendMessage(\"gameOver\")\n"
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
            "penColor": "#000000CC",
            "penThickness": 4,
            "fillColor": "#DEE2DBCC"
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
              400,
              35
            ],
            "position": [
              185.0,
              756.0
            ],
            "text": "Press Return to Play Again",
            "alignment": "Center",
            "textColor": "white",
            "font": "Default",
            "fontSize": 18,
            "autoShrink": true
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnPeriodic": "# Only move if we're not isGameOver / gameOver\nif not isGameOver:\n   if IsKeyPressed(\"Up\"):\n      self.file = \"ship-on.png\"\n   else:\n      ship.file = \"ship-off.png\"\n\n   # Wrap the ship around the edges of the card\n   if ship.center.y <= 0 and ship.speed.y < 0:\n      # Off the Bottom edge\n      ship.center = [self.center.x, card.size.y]\n   elif ship.center.y >= card.size.height and ship.speed.y > 0:\n      # Off the Top edge\n      ship.center = [self.center.x, 0]\n   elif ship.center.x <= 0 and ship.speed.x < 0:\n      # Off the Left edge\n      ship.center = [card.size.x, self.center.y]\n   elif ship.center.x >= card.size.width and ship.speed.x > 0:\n      # Off the Right edge\n      ship.center = [0, self.center.y]\n\n   # Did we collide with any asteroid?\n   for child in card.children:\n      # Check the asteroid clones, but not the original, hidden asteroid\n      if child.name.startswith(\"asteroid_\"):\n         d = Distance(self.center, child.center)\n         if d <= 30 + child.size.width/2:\n            card.SendMessage(\"gameOver\")\n            break\n"
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
  "CardStock_stack_version": "0.9.7"
}
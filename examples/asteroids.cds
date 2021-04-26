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
        "OnSetup": "from random import randint\nimport math\n\nasteroid.Hide()\n\nast = asteroid.Clone()\nast.position = (100,100)\nast.speed += (randint(-100,100), randint(-100,100))\nast.Show()\n\nnumAsteroids = 1\n",
        "OnKeyDown": "if keyName == \"Space\" and hit == False:\n   shot = card.AddOval(\"shot\",\n      size=(10,10),\n      center=(ship.center+rotate((0, 60), ship.rotation)),\n      speed=ship.speed+rotate((0, 100), ship.rotation))\n   RunAfterDelay(2, shot.Delete)\n\nelif keyName == \"Space\" and hit == True:\n      hit = False\n      ship.rotation = 0\n      ship.center = card.center\n      ast = asteroid.Clone()\n      ast.position = (100,100)\n      ast.speed += (randint(-100,100), randint(-100,100))\n      ast.Show()\n      try_again.Hide()\n",
        "OnMessage": "if message == \"gameOver\":\n   ship.speed = (0,0)\n   for c in card.children.copy():\n      if c.name.startswith(\"asteroid_\") or c.name.startswith(\"shot\"):\n         c.Delete()\n   hit = True\n   try_again.Show()\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#000000"
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {
            "OnIdle": "if self.center.y <= 0 and self.speed.y < 0:\n   # Off the Top edge\n   self.center = [self.center.x, card.size.y]\nelif self.center.y >= card.size.height and self.speed.y > 0:\n   # Off the Bottom edge\n   self.center = [self.center.x, 0]\nelif self.center.x <= 0 and self.speed.x < 0:\n   # Off the Left edge\n   self.center = [card.size.x, self.center.y]\nelif self.center.x >= card.size.width and self.speed.x > 0:\n   # Off the Right edge\n   self.center = [0, self.center.y]\n\nfor child in card.children:\n   if child.name.startswith(\"shot\") and child.visible:\n      if child.IsTouching(self):\n         angle = randint(0, 360)\n         dSpeed = randint(30, 100)\n         if self.size.width > 20:\n            sub1 = self.Clone(size=self.size/2)\n            sub2 = self.Clone(size=self.size/2)\n            sub1.speed += rotate((0, dSpeed), angle)\n            sub2.speed -= rotate((0, dSpeed), angle)\n            numAsteroids += 2\n         child.Hide()\n         self.Delete()\n         numAsteroids -= 1\n         \n         if numAsteroids == 0:\n            card.SendMessage(\"gameOver\")\n"
          },
          "properties": {
            "name": "asteroid",
            "size": [
              69,
              69
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
            "penThickness": 0,
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
              416,
              43
            ],
            "position": [
              159.0,
              741.0
            ],
            "text": "Press Space to Play Again",
            "alignment": "Center",
            "textColor": "white",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnSetup": "try_again.Hide()\n\nhit = False\n\ndef rotate(list, angle):\n   angle = math.radians(angle)\n   px, py = list\n   return [-(math.cos(angle) * px - math.sin(angle) * py),\n           math.sin(angle) * px + math.cos(angle) * py]\n",
            "OnIdle": "if hit == False:\n   if IsKeyPressed(\"Left\"):\n      self.rotation -= 5\n   if IsKeyPressed(\"Right\"):\n      self.rotation += 5\n      \n   if IsKeyPressed(\"Up\"):\n      self.speed += rotate((0, 15), self.rotation)\n      self.file = \"ship-on.png\"\n      SoundPlay(\"puff.wav\")\n   else:\n      self.file = \"ship-off.png\"\n\n   if ship.center.y <= 0 and ship.speed.y < 0:\n      # Off the Bottom edge\n      ship.center = [self.center.x, card.size.y]\n   elif ship.center.y >= card.size.height and ship.speed.y > 0:\n      # Off the Top edge\n      ship.center = [self.center.x, 0]\n   elif ship.center.x <= 0 and ship.speed.x < 0:\n      # Off the Left edge\n      ship.center = [card.size.x, self.center.y]\n   elif ship.center.x >= card.size.width and ship.speed.x > 0:\n      # Off the Right edge\n      ship.center = [0, self.center.y]\n\n   for child in card.children:\n      if child.name.startswith(\"asteroid_\"):\n         if self.IsTouchingPoint(child.center):\n            card.SendMessage(\"gameOver\")\n            break\n"
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
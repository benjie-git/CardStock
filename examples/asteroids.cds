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
      "handlers": {},
      "properties": {
        "name": "card_1",
        "bgColor": "#000000"
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {
            "OnIdle": "if asteroid.center.y <= 0 and asteroid.speed.y < 0:\n   # Off the Top edge\n   asteroid.center = [asteroid.center.x, card.size.y]\nelif asteroid.center.y >= card.size.height and asteroid.speed.y > 0:\n   # Off the Bottom edge\n   asteroid.center = [asteroid.center.x, 0]\nelif asteroid.center.x <= 0 and asteroid.speed.x < 0:\n   # Off the Left edge\n   asteroid.center = [card.size.x, asteroid.center.y]\nelif asteroid.center.x >= card.size.width and asteroid.speed.x > 0:\n   # Off the Right edge\n   asteroid.center = [0, asteroid.center.y]\n"
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
            "OnSetup": "import math\nfrom random import randint\n\ntry_again.Hide()\n\nhit = False\nasteroid.speed += (randint(-100,100), randint(-100,100))\n\ndef rotate(list, angle):\n   angle = math.radians(angle)\n   px, py = list\n   return [-(math.cos(angle) * px - math.sin(angle) * py),\n           math.sin(angle) * px + math.cos(angle) * py]\n",
            "OnIdle": "if hit == False:\n   if IsKeyPressed(\"Left\"):\n      self.rotation -= 5\n   if IsKeyPressed(\"Right\"):\n      self.rotation += 5\n      \n   if IsKeyPressed(\"Up\"):\n      self.speed += rotate((0, 15), self.rotation)\n      self.file = \"ship-on.png\"\n      SoundPlay(\"puff.wav\")\n   else:\n      self.file = \"ship-off.png\"\n\n   if ship.center.y <= 0 and ship.speed.y < 0:\n      # Off the Bottom edge\n      ship.center = [self.center.x, card.size.y]\n   elif ship.center.y >= card.size.height and ship.speed.y > 0:\n      # Off the Top edge\n      ship.center = [self.center.x, 0]\n   elif ship.center.x <= 0 and ship.speed.x < 0:\n      # Off the Left edge\n      ship.center = [card.size.x, self.center.y]\n   elif ship.center.x >= card.size.width and ship.speed.x > 0:\n      # Off the Right edge\n      ship.center = [0, self.center.y]\n\n   if ship.IsTouchingPoint(asteroid.center):\n      asteroid.speed = (0,0)\n      ship.speed = (0,0)\n      hit = True\n      try_again.Show()\nelse:\n   if IsKeyPressed(\"Space\"):\n      hit = False\n      ship.rotation = 0\n      ship.position = (295, 295)\n      asteroid.position = (100,100)\n      asteroid.speed += (randint(-100,100), randint(-100,100))\n      try_again.Hide()\n"
          },
          "properties": {
            "name": "ship",
            "size": [
              114,
              114
            ],
            "position": [
              295.0,
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
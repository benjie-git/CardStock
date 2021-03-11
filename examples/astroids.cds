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
          "type": "image",
          "handlers": {
            "OnSetup": "import math\n\ndef rotate(list, angle):\n   angle = math.radians(angle)\n   px, py = list\n   return [math.cos(angle) * px - math.sin(angle) * py,\n           math.sin(angle) * px + math.cos(angle) * py]\n",
            "OnIdle": "if IsKeyPressed(\"Left\"):\n   self.rotation -= 5\nif IsKeyPressed(\"Right\"):\n   self.rotation += 5\n   \nif IsKeyPressed(\"Up\"):\n   self.speed += rotate((0, -15), self.rotation)\n   self.file = \"ship-on.png\"\n   PlaySound(\"puff.wav\")\nelse:\n   self.file = \"ship-off.png\"\n\nif ship.center.y <= 0 and ship.speed.y < 0:\n   # Off the Top edge\n   ship.center = [self.center.x, card.size.y]\nelif ship.center.y >= card.size.height and ship.speed.y > 0:\n   # Off the Bottom edge\n   ship.center = [self.center.x, 0]\nelif ship.center.x <= 0 and ship.speed.x < 0:\n   # Off the Left edge\n   ship.center = [card.size.x, self.center.y]\nelif ship.center.x >= card.size.width and ship.speed.x > 0:\n   # Off the Right edge\n   ship.center = [0, self.center.y]\n"
          },
          "properties": {
            "name": "ship",
            "size": [
              114,
              114
            ],
            "position": [
              293.0,
              295.0
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
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.8.1"
}
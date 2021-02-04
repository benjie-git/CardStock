{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      800,
      800
    ]
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
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "ship",
            "size": [
              160,
              160
            ],
            "position": [
              310.0,
              284.0
            ]
          },
          "childModels": [
            {
              "type": "image",
              "handlers": {
                "OnSetup": "import math\n\ndef rotate(list, angle):\n   angle = math.radians(angle)\n   px, py = list\n   return [math.cos(angle) * px - math.sin(angle) * py,\n           math.sin(angle) * px + math.cos(angle) * py]\n",
                "OnIdle": "if IsKeyPressed(\"Left\"):\n   self.rotation -= 5\nif IsKeyPressed(\"Right\"):\n   self.rotation += 5\nif IsKeyPressed(\"Up\"):\n   self.parent.speed += rotate((0, -15), self.rotation)\n   self.file = \"ship-on.png\"\n   PlaySound(\"puff.wav\")\nelse:\n   self.file = \"ship-off.png\"\n\ncardSize = card.size\n\npos = solid.position\nsize = solid.size\n\nedge = solid.IsTouchingEdge(card)\nif edge == \"Top\" and ship.speed.y < 0:\n   ship.position = [pos.x, cardSize.y-size.y]\nelif edge == \"Bottom\" and ship.speed.y > 0:\n   ship.position = [pos.x, -50]\nelif edge == \"Left\" and ship.speed.x < 0:\n   ship.position = [cardSize.x-size.x, pos.y]\nelif edge == \"Right\" and ship.speed.x > 0:\n   ship.position = [-50, pos.y]\n"
              },
              "properties": {
                "name": "image",
                "size": [
                  160,
                  160
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "file": "ship-off.png",
                "fit": "Center",
                "rotation": 0
              }
            },
            {
              "type": "image",
              "handlers": {},
              "properties": {
                "name": "solid",
                "size": [
                  74,
                  68
                ],
                "position": [
                  43.0,
                  38.0
                ],
                "file": "",
                "fit": "Scale",
                "rotation": 0
              }
            }
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
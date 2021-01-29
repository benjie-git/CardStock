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
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "ship",
            "size": [
              269,
              266
            ],
            "position": [
              146.0,
              105.0
            ]
          },
          "childModels": [
            {
              "type": "image",
              "handlers": {
                "OnSetup": "import math\n\ndef rotate(list, angle):\n   angle = math.radians(angle)\n   px, py = list\n   return [math.cos(angle) * px - math.sin(angle) * py,\n           math.sin(angle) * px + math.cos(angle) * py]\n",
                "OnIdle": "if IsKeyPressed(\"Left\"):\n   self.rotation -= 3\nif IsKeyPressed(\"Right\"):\n   self.rotation += 3\nif IsKeyPressed(\"Up\"):\n   ship.speed += rotate((0, -10), self.rotation)\n\ncardSize = card.size\n\npos = solid.position\nsize = solid.size\n\nedge = solid.IsTouchingEdge(card)\nif edge == \"Top\" and ship.speed.y < 0:\n   ship.position = [pos.x, cardSize.y-size.y]\nelif edge == \"Bottom\" and ship.speed.y > 0:\n   ship.position = [pos.x, -50]\nelif edge == \"Left\" and ship.speed.x < 0:\n   ship.position = [cardSize.x-size.x, pos.y]\nelif edge == \"Right\" and ship.speed.x > 0:\n   ship.position = [-50, pos.y]\n"
              },
              "properties": {
                "name": "image",
                "size": [
                  269,
                  266
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "file": "ship.png",
                "fit": "Center",
                "bgColor": "",
                "rotation": 0
              }
            },
            {
              "type": "oval",
              "handlers": {},
              "properties": {
                "name": "solid",
                "size": [
                  109,
                  109
                ],
                "position": [
                  80.0,
                  72.0
                ],
                "originalSize": [
                  109,
                  109
                ],
                "penColor": "#00000000",
                "penThickness": 1,
                "fillColor": "#00000000"
              },
              "points": [
                [
                  1.0,
                  1.0
                ],
                [
                  108.0,
                  108.0
                ]
              ]
            }
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
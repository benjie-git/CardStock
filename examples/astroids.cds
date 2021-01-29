{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "speed": [
      0,
      0
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "card_1",
        "speed": [
          0,
          0
        ],
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {
            "OnIdle": "if IsKeyPressed(\"Left\"):\n   self.speed -= [1, 0]\nif IsKeyPressed(\"Right\"):\n   self.speed += [1, 0]\nif IsKeyPressed(\"Up\"):\n   self.speed -= [0, 1]\nif IsKeyPressed(\"Down\"):\n   self.speed += [0, 1]\n\ncardSize = card.size\n\npos = self.position\nsize = self.size\n\nedge = self.IsTouchingEdge(card)\nif edge == \"Top\":\n   self.position = [pos.x, cardSize.y-size.y]\nelif edge == \"Bottom\":\n   self.position = [pos.x, 0]\nelif edge == \"Left\":\n   self.position = [cardSize.x-size.x, pos.y]\nelif edge == \"Right\":\n   self.position = [0, pos.y]\n"
          },
          "properties": {
            "name": "guy",
            "size": [
              80,
              77
            ],
            "position": [
              218,
              199
            ],
            "speed": [
              0,
              0
            ],
            "originalSize": [
              80,
              77
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#00FF00"
          },
          "points": [
            [
              1,
              1
            ],
            [
              79,
              76
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
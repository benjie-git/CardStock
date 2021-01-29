{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "pressedKeys = []",
        "OnKeyDown": "if keyName not in pressedKeys:\n   pressedKeys.append(keyName)\n",
        "OnKeyUp": "if keyName in pressedKeys:\n   pressedKeys.remove(keyName)\n",
        "OnIdle": "if \"Left\" in pressedKeys:\n   dx -= 1\nif \"Right\" in pressedKeys:\n   dx += 1\nif \"Up\" in pressedKeys:\n   dy -= 1\nif \"Down\" in pressedKeys:\n   dy += 1\n\nguy.MoveBy([dx,dy])\n\nsize = card.GetSize()\n\nedge = guy.IsTouchingEdge(card)\nguyPos = guy.GetPosition()\nguySize = guy.GetSize()\n\nif edge == \"Top\":\n   guy.SetPosition([guyPos[0], size[1]-guySize[1]])\nelif edge == \"Bottom\":\n   guy.SetPosition([guyPos[0], 0])\nelif edge == \"Left\":\n   guy.SetPosition([size[0]-guySize[0], guyPos[1]])\nelif edge == \"Right\":\n   guy.SetPosition([0, guyPos[1]])\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {
            "OnSetup": "dx = 0\ndy = 0\n"
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
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      519,
      506
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "card_1",
        "bgColor": "#FFFFFF"
      },
      "childModels": [
        {
          "type": "roundrect",
          "handlers": {
            "OnMouseMove": "self.center = mousePos\n",
            "OnMessage": "if message == \"reset\":\n   PlaySound(\"click.wav\")\n   self.position = (10, 10)\nelif message == \"win\":\n   PlaySound(\"yay.wav\")\n   self.position = (10, 10)\n"
          },
          "properties": {
            "name": "ball",
            "size": [
              46,
              47
            ],
            "position": [
              10.0,
              10.0
            ],
            "originalSize": [
              46,
              43
            ],
            "penColor": "black",
            "penThickness": 0,
            "fillColor": "#0A5FFF",
            "cornerRadius": 10
          },
          "points": [
            [
              1,
              1
            ],
            [
              45,
              42
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"win\")\n"
          },
          "properties": {
            "name": "goal",
            "size": [
              20,
              92
            ],
            "position": [
              106.0,
              426.0
            ],
            "originalSize": [
              102,
              24
            ],
            "penColor": "#000000",
            "penThickness": 0,
            "fillColor": "green"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              101.0,
              23.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_1",
            "size": [
              360,
              20
            ],
            "position": [
              88.0,
              412.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_2",
            "size": [
              20,
              86
            ],
            "position": [
              88.0,
              428.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_3",
            "size": [
              196,
              20
            ],
            "position": [
              104.0,
              302.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_4",
            "size": [
              20,
              362
            ],
            "position": [
              90.0,
              -40.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_5",
            "size": [
              196,
              20
            ],
            "position": [
              236.0,
              179.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_6",
            "size": [
              20,
              236
            ],
            "position": [
              428.0,
              179.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_7",
            "size": [
              20,
              117
            ],
            "position": [
              429.0,
              -28.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_8",
            "size": [
              20,
              98
            ],
            "position": [
              236.0,
              99.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnPeriodic": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_9",
            "size": [
              86,
              20
            ],
            "position": [
              351.0,
              69.0
            ],
            "originalSize": [
              211,
              66
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9"
}
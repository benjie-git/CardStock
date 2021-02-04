{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      519,
      506
    ]
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
          "type": "round_rect",
          "handlers": {
            "OnMouseMove": "self.center = mousePos\n",
            "OnMessage": "if message == \"reset\":\n   PlaySound(\"click.wav\")\n   self.center = (30, 465)\nelif message == \"win\":\n   PlaySound(\"yay.wav\")\n   self.center = (30, 465)\n"
          },
          "properties": {
            "name": "ball",
            "size": [
              46,
              47
            ],
            "position": [
              9.0,
              448.0
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
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"win\")\n"
          },
          "properties": {
            "name": "goal",
            "size": [
              103,
              25
            ],
            "position": [
              403.0,
              0.0
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
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall",
            "size": [
              25,
              229
            ],
            "position": [
              92.0,
              284.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_1",
            "size": [
              26,
              185
            ],
            "position": [
              91.0,
              -4.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_2",
            "size": [
              200,
              28
            ],
            "position": [
              91.0,
              178.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_3",
            "size": [
              22,
              129
            ],
            "position": [
              285.0,
              178.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_4",
            "size": [
              224,
              20
            ],
            "position": [
              197.0,
              387.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_5",
            "size": [
              26,
              185
            ],
            "position": [
              394.0,
              -4.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_6",
            "size": [
              30,
              518
            ],
            "position": [
              499.0,
              -8.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_7",
            "size": [
              26,
              185
            ],
            "position": [
              91.0,
              -4.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_8",
            "size": [
              394,
              20
            ],
            "position": [
              112.0,
              489.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_9",
            "size": [
              190,
              28
            ],
            "position": [
              211.0,
              75.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_10",
            "size": [
              21,
              234
            ],
            "position": [
              399.0,
              261.0
            ],
            "originalSize": [
              25,
              229
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "black"
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              23.0,
              227.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
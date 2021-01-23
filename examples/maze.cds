{
  "type": "stack",
  "handlers": {},
  "properties": {
    "name": "",
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
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall",
            "size": [
              20,
              233
            ],
            "position": [
              63,
              273
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"win\")\n"
          },
          "properties": {
            "name": "goal",
            "size": [
              95,
              21
            ],
            "position": [
              406,
              0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "green"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_1",
            "size": [
              20,
              233
            ],
            "position": [
              63,
              -28
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_2",
            "size": [
              20,
              111
            ],
            "position": [
              218,
              84
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_3",
            "size": [
              20,
              233
            ],
            "position": [
              317,
              -23
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_4",
            "size": [
              20,
              387
            ],
            "position": [
              396,
              -3
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_5",
            "size": [
              226,
              20
            ],
            "position": [
              78,
              273
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_6",
            "size": [
              80,
              20
            ],
            "position": [
              158,
              75
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_7",
            "size": [
              158,
              20
            ],
            "position": [
              80,
              185
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_8",
            "size": [
              254,
              20
            ],
            "position": [
              163,
              381
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "round_rect",
          "handlers": {
            "OnMouseMove": "self.SetPosition([mouseX-24, mouseY-24])\n",
            "OnMessage": "if message == \"reset\":\n   PlaySound(\"click.wav\")\n   self.SetPosition((8, 445))\nelif message == \"win\":\n   PlaySound(\"yay.wav\")\n   self.SetPosition((8, 445))\n"
          },
          "properties": {
            "name": "ball",
            "size": [
              46,
              47
            ],
            "position": [
              9,
              448
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
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_9",
            "size": [
              26,
              507
            ],
            "position": [
              500,
              1
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnIdle": "if self.IsTouching(ball):\n   ball.SendMessage(\"reset\")\n"
          },
          "properties": {
            "name": "wall_10",
            "size": [
              429,
              25
            ],
            "position": [
              80,
              487
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black"
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
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
              63.0,
              273.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              406.0,
              0.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "green",
            "rotation": 0
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
              63.0,
              -28.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              218.0,
              84.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              317.0,
              -23.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              396.0,
              -3.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              78.0,
              273.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              158.0,
              75.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              80.0,
              185.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              163.0,
              381.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
          }
        },
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
              500.0,
              1.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
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
              80.0,
              487.0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "black",
            "rotation": 0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
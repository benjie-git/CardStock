{
  "type": "stack",
  "handlers": {},
  "properties": {
    "name": "",
    "size": [
      500,
      500
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
            "OnMouseMove": "self.SetPosition([mouseX-17, mouseY-17])\n",
            "OnMessage": "if message == \"reset\":\n   self.SetPosition((20, 465))\nelif message == \"win\":\n   PlaySound(\"yay.wav\")\n   self.SetPosition((20, 465))\n"
          },
          "properties": {
            "name": "ball",
            "size": [
              34,
              34
            ],
            "position": [
              13,
              450
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "blue"
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
              397,
              -4
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
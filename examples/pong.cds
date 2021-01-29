{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      637,
      715
    ],
    "speed": [
      0,
      0
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n",
        "OnKeyDown": "if keyName == \"Space\":\n   # Only start a game if the ball wasn't already moving\n   if ball.speed.x == 0 and ball.speed.y == 0:\n      ball.SendMessage(\"StartGame\")\n",
        "OnMouseDown": "if ball.speed.x == 0 and ball.speed.y == 0:\n   # Only start a game if the ball wasn't already moving\n  ball.SendMessage(\"StartGame\")\n",
        "OnMouseMove": "# Make the paddle follow the mouse's X position\npaddle.center = [mouseX, paddle.center.y]\n"
      },
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label",
            "size": [
              107,
              42
            ],
            "position": [
              12,
              17
            ],
            "speed": [
              0,
              0
            ],
            "text": "0",
            "alignment": "Left",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": 28
          }
        },
        {
          "type": "oval",
          "handlers": {
            "OnMessage": "if message == \"StartGame\":\n   self.speed.x = randint(10,20)\n   self.speed.y = 30 - self.speed.x\n   self.position = [100,100]\n   score = 0\n   label.text = score\n",
            "OnIdle": "if self.IsTouching(paddle):\n   # Switch vertical sign\n   self.speed.y = -self.speed.y\n   \n   # Speed up or slow down horizontally\n   # based on which side of the paddle\n   # we hit\n   if ball.center.x < paddle.center.x:\n      self.speed.x = self.speed.x - randint(2,6)\n   elif ball.center.x > paddle.center.x:\n      self.speed.x = self.speed.x + randint(2,6)\n   # keep the ball from getting too fast\n   self.speed.x = min(self.speed.x, 30)\n   self.speed.x = max(self.speed.x, -30)\n   \n   score += 1\n   label.text = score\n\nedge = self.IsTouchingEdge(card)\nif edge == \"Top\":\n   self.speed.y = -self.speed.y\nelif edge == \"Left\" or edge == \"Right\":\n   self.speed.x = -self.speed.x\nelif edge == \"Bottom\":\n   # Lose if we hit the bottm of the card\n   self.speed.x = 0\n   self.speed.y = 0\n   label.text = \"Oh no!\"\n"
          },
          "properties": {
            "name": "ball",
            "size": [
              35,
              35
            ],
            "position": [
              86,
              66
            ],
            "speed": [
              0,
              0
            ],
            "originalSize": [
              35,
              35
            ],
            "penColor": "#000000",
            "penThickness": 0,
            "fillColor": "#FF2222"
          },
          "points": [
            [
              2,
              2
            ],
            [
              33.0,
              33
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "paddle",
            "size": [
              237,
              24
            ],
            "position": [
              208,
              646
            ],
            "speed": [
              0,
              0
            ],
            "originalSize": [
              232,
              28
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#0A5FFF"
          },
          "points": [
            [
              1,
              1
            ],
            [
              231,
              27
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
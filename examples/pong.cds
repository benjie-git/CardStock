{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      637,
      715
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n\ndx = 0\ndy = 0",
        "OnKeyDown": "if keyName == \"Space\":\n   # Only start a game if the ball wasn't already moving\n   if dx == 0 and dy == 0:\n      ball.SendMessage(\"StartGame\")\n",
        "OnMouseDown": "if dx == 0 and dy == 0:\n   # Only start a game if the ball wasn't already moving\n  ball.SendMessage(\"StartGame\")\n",
        "OnMouseMove": "# Make the paddle follow the mouse's X position\npaddle.center = [mouseX, paddle.center.y]\n"
      },
      "properties": {
        "name": "card_1",
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
            "OnMessage": "if message == \"StartGame\":\n   dx=randint(10,20)\n   dy=30-dx\n   self.position = [100,100]\n   score = 0\n   label.text = score\n",
            "OnIdle": "self.position += [dx, dy]\n\nif self.IsTouching(paddle):\n   # Switch vertical sign\n   dy = -dy\n   \n   # Speed up or slow down horizontally\n   # based on which side of the paddle\n   # we hit\n   if ball.center.x < paddle.center.x:\n      dx = dx - randint(2,6)\n   elif ball.center.x > paddle.center.x:\n      dx = dx + randint(2,6)\n   # keep the ball from getting too fast\n   dx = min(dx, 30)\n   dx = max(dx, -30)\n   \n   score += 1\n   label.text = score\n\nedge = self.IsTouchingEdge(card)\nif edge == \"Top\":\n   dy = -dy\nelif edge == \"Left\" or edge == \"Right\":\n   dx = -dx\nelif edge == \"Bottom\":\n   # Lose if we hit the bottm of the card\n   dx = 0\n   dy = 0\n   label.text = \"Oh no!\"\n"
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
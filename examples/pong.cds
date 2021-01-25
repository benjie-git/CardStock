{
  "type": "stack",
  "handlers": {
    "OnStackStart": "from random import randint\n\ndx = 0\ndy = 0"
  },
  "properties": {
    "name": "card_1",
    "size": [
      637,
      715
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnKeyDown": "if keyName == \"Space\":\n   # Only start a game if the ball wasn't already moving\n   if dx == 0 and dy == 0:\n      ball.SendMessage(\"StartGame\")\n",
        "OnMouseDown": "if dx == 0 and dy == 0:\n   # Only start a game if the ball wasn't already moving\n  ball.SendMessage(\"StartGame\")\n",
        "OnMouseMove": "# Make the paddle follow the mouse's X position\noldPos = paddle.GetCenter()\npaddle.SetCenter([mouseX, oldPos[1]])\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "paddle",
            "size": [
              226,
              20
            ],
            "position": [
              211,
              655
            ],
            "file": "",
            "fit": "Stretch",
            "bgColor": "Blue"
          }
        },
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
            "OnMessage": "if message == \"StartGame\":\n   dx=randint(10,20)\n   dy=30-dx\n   self.SetPosition([100,100])\n   score = 0\n   label.SetText(score)\n",
            "OnIdle": "self.MoveBy([dx, dy])\n\nif self.IsTouching(paddle):\n   # Switch vertical sign\n   dy = -dy\n   \n   # Speed up or slow down horizontally\n   # based on which side of the paddle\n   # we hit\n   if ball.GetCenter()[0] < paddle.GetCenter()[0]:\n      dx = dx - randint(2,6)\n   elif ball.GetCenter()[0] > paddle.GetCenter()[0]:\n      dx = dx + randint(2,6)\n   # keep the ball from getting too fast\n   dx = min(dx, 30)\n   dx = max(dx, -30)\n   \n   score += 1\n   label.SetText(score)\n\nedge = self.IsTouchingEdge(card)\nif edge == \"Top\":\n   dy = -dy\nelif edge == \"Left\" or edge == \"Right\":\n   dx = -dx\nelif edge == \"Bottom\":\n   # Lose if we hit the bottm of the card\n   dx = 0\n   dy = 0\n   label.SetText(\"Oh no!\")\n"
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
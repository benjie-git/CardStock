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
        "OnKeyDown": "if key == \"Space\":\n   if dx == 0 and dy == 0:\n      ball.SendMessage(\"StartGame\")\n",
        "OnMouseDown": "if dx == 0 and dy == 0:\n  ball.SendMessage(\"StartGame\")\n",
        "OnMouseMove": "oldPos = paddle.GetCenter()\npaddle.SetCenter([mouseX, oldPos[1]])\n"
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
            "OnIdle": "self.MoveBy([dx, dy])\n\nedge = self.IsTouchingEdge(card)\n\nif self.IsTouching(paddle):\n   dy = -dy\n   score += 1\n   label.SetText(score)\n\nif edge == \"Top\":\n   dy = -dy\n\nif edge == \"Left\" or edge == \"Right\":\n   dx = -dx\n\nif edge == \"Bottom\":\n   dx = 0\n   dy = 0\n   label.SetText(\"Oh no!\")\n"
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
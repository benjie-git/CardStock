{
  "type": "stack",
  "handlers": {},
  "properties": {
    "name": "card_1",
    "size": [
      637,
      715
    ],
    "hidden": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "from random import randint\n\ndx = 0\ndy = 0",
        "OnKeyDown": "if key == \"Space\":\n   if dx == 0 and dy == 0:\n      ball.SendMessage(\"StartGame\")\n",
        "OnMouseDown": "if dx == 0 and dy == 0:\n  ball.SendMessage(\"StartGame\")\n",
        "OnMouseMove": "oldPos = paddle.GetPosition()\npaddleSize = paddle.GetSize()\n\npaddle.SetPosition([mouseX-paddleSize[0]/2, oldPos[1]])"
      },
      "properties": {
        "name": "card_1",
        "hidden": false,
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
              194,
              579
            ],
            "hidden": false,
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
            "hidden": false,
            "text": "0",
            "alignment": "Left",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": 28
          }
        },
        {
          "type": "shapes",
          "handlers": {
            "OnMessage": "if message == \"StartGame\":\n   dx=randint(10,20)\n   dy=30-dx\n   self.SetPosition([100,100])\n   score = 0\n   label.SetText(score)\n",
            "OnIdle": "self.MoveBy([dx, dy])\n\nedge = self.IsTouchingEdge(card)\n\nif self.IsTouching(paddle):\n   dy = -dy\n   score += 1\n   label.SetText(score)\n\nif edge == \"Top\":\n   dy = -dy\n\nif edge == \"Left\" or edge == \"Right\":\n   dx = -dx\n\nif edge == \"Bottom\":\n   dx = 0\n   dy = 0\n   label.SetText(\"Oh no!\")\n"
          },
          "properties": {
            "name": "ball",
            "size": [
              36,
              35
            ],
            "position": [
              73,
              93
            ],
            "hidden": false
          },
          "shapes": [
            {
              "type": "oval",
              "penColor": "Red",
              "thickness": 16,
              "points": [
                [
                  10,
                  10
                ],
                [
                  26,
                  25
                ]
              ]
            }
          ]
        }
      ]
    }
  ]
}
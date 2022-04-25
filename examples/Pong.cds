{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      549,
      544
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint",
        "OnKeyDown": "if keyName == \"Space\":\n   ball.SendMessage(\"StartGame\")",
        "OnMouseDown": "ball.SendMessage(\"StartGame\")",
        "OnPeriodic": "# Make the paddle follow the mouse's X position\n# but keep it on-screen.\nx = min(max(GetMousePos().x, 0), card.size.width)\npaddle.center = [x, 40]",
        "OnResize": "# Keep the label at the top, following the window's height\nlabel.position.y = card.size.height - label.size.height - 5"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#EEEEEE"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label",
            "size": [
              107,
              34
            ],
            "position": [
              11.0,
              503.0
            ],
            "text": "0",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18,
            "autoShrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "paddle",
            "size": [
              235,
              22
            ],
            "position": [
              205.0,
              29.0
            ],
            "originalSize": [
              250,
              31
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "rotation": 0.0,
            "fillColor": "#0A5FFF"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              250.0,
              31.0
            ]
          ]
        },
        {
          "type": "oval",
          "handlers": {
            "OnSetup": "# Bounce off of the paddle, and the card's edges\nself.SetBounceObjects([paddle, card])\n\nself.Hide()",
            "OnBounce": "if otherObject == paddle:\n   score += 1\n   label.text = score\n   \n   # Speed up or slow down horizontally\n   # based on which side of the paddle\n   # we hit\n   if ball.center.x < paddle.center.x:\n      self.speed.x -= randint(50,100)\n   elif ball.center.x > paddle.center.x:\n      self.speed.x += randint(50,100)\n   # keep the ball from getting too fast\n   self.speed.x = min(self.speed.x, 500)\n   self.speed.x = max(self.speed.x, -500)\n\nelif otherObject == card and edge == \"Bottom\":\n   # Lose if we hit the bottom of the card\n   self.speed = (0, 0)\n   self.Hide()\n   label.text = \"Oh no!\"",
            "OnMessage": "if message == \"StartGame\":\n   # Only start a game if the ball wasn't already moving\n   if ball.speed.x == 0 and ball.speed.y == 0:\n      self.position = (100, card.size.height-100)\n      self.speed.x = randint(200,400)\n      self.speed.y = self.speed.x - 800\n      self.Show()\n      score = 0\n      label.text = score"
          },
          "properties": {
            "name": "ball",
            "size": [
              30,
              30
            ],
            "position": [
              81.0,
              480.0
            ],
            "originalSize": [
              36,
              36
            ],
            "penColor": "#000000",
            "penThickness": 2,
            "rotation": 0.0,
            "fillColor": "#FB0207"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              36.0,
              36.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9.8"
}
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
        "OnSetup": "from random import randint\n",
        "OnKeyDown": "if keyName == \"Space\":\n   # Only start a game if the ball wasn't already moving\n   if ball.speed.x == 0 and ball.speed.y == 0:\n      ball.SendMessage(\"StartGame\")\n",
        "OnResize": "# Make the paddle follow the window's height\npaddle.center.y = 40\nlabel.position.y = card.size.height - label.size.height",
        "OnMouseDown": "if ball.speed.x == 0 and ball.speed.y == 0:\n   # Only start a game if the ball wasn't already moving\n   ball.SendMessage(\"StartGame\")\n",
        "OnMouseMove": "# Make the paddle follow the mouse's X position\npaddle.center = [mousePos.x, 40]\n"
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
            "fontSize": 18
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
            "OnSetup": "self.Hide()\n",
            "OnMessage": "if message == \"StartGame\":\n   self.speed.x = randint(200,400)\n   self.speed.y = self.speed.x - 800\n   self.position = [50,card.size.height - 80]\n   self.Show()\n   score = 0\n   label.text = score\n",
            "OnIdle": "if self.IsTouching(paddle) and self.speed.y < 0:\n   # We hit the ball with the paddle!\n   # Switch vertical sign and inrease the score\n   self.speed.y = -self.speed.y\n   score += 1\n   label.text = score\n   \n   # Speed up or slow down horizontally\n   # based on which side of the paddle\n   # we hit\n   if ball.center.x < paddle.center.x:\n      self.speed.x -= randint(50,100)\n   elif ball.center.x > paddle.center.x:\n      self.speed.x += randint(50,100)\n   # keep the ball from getting too fast\n   self.speed.x = min(self.speed.x, 500)\n   self.speed.x = max(self.speed.x, -500)\n\n# Bounce if we hit a top or side\nif self.position.y +self.size.height >= card.size.height and self.speed.y > 0:\n   self.speed.y = -self.speed.y\nelif self.position.x <= 0 and self.speed.x < 0:\n   self.speed.x = -self.speed.x\nelif self.position.x + self.size.width >= card.size.width\\\n   and self.speed.x > 0:\n      self.speed.x = -self.speed.x\n\n# Lose if we hit the bottom of the card\nelif self.position.y <= 0 and self.speed.y < 0:\n      self.speed.x = 0\n      self.speed.y = 0\n      self.Hide()\n      label.text = \"Oh no!\"\n"
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
  "CardStock_stack_version": "0.8.12"
}
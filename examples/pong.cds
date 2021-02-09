{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      637,
      715
    ],
    "canSave": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n",
        "OnKeyDown": "if keyName == \"Space\":\n   # Only start a game if the ball wasn't already moving\n   if ball.speed.x == 0 and ball.speed.y == 0:\n      ball.SendMessage(\"StartGame\")\n",
        "OnMouseDown": "if ball.speed.x == 0 and ball.speed.y == 0:\n   # Only start a game if the ball wasn't already moving\n   ball.SendMessage(\"StartGame\")\n",
        "OnMouseMove": "# Make the paddle follow the mouse's X position\npaddle.center.x = mousePos.x\n"
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
              111,
              27
            ],
            "position": [
              1.0,
              1.0
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
              193.0,
              662.0
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
            "OnMessage": "if message == \"StartGame\":\n   self.speed.x = randint(200,400)\n   self.speed.y = 800 - self.speed.x\n   self.position = [50,50]\n   self.Show()\n   score = 0\n   label.text = score\n",
            "OnIdle": "if self.IsTouching(paddle) and self.speed.y > 0:\n   # We hit the ball with the paddle!\n   # Switch vertical sign and inrease the score\n   self.speed.y = -self.speed.y\n   score += 1\n   label.text = score\n   \n   # Speed up or slow down horizontally\n   # based on which side of the paddle\n   # we hit\n   if ball.center.x < paddle.center.x:\n      self.speed.x -= randint(50,100)\n   elif ball.center.x > paddle.center.x:\n      self.speed.x += randint(50,100)\n   # keep the ball from getting too fast\n   self.speed.x = min(self.speed.x, 500)\n   self.speed.x = max(self.speed.x, -500)\n   \nedge = self.IsTouchingEdge(card)\n\n# Bounce if we hit a top or side\nif edge == \"Top\" and self.speed.y < 0:\n   self.speed.y = -self.speed.y\nelif edge == \"Left\" and self.speed.x < 0:\n   self.speed.x = -self.speed.x\nelif edge == \"Right\" and self.speed.x > 0:\n   self.speed.x = -self.speed.x\n\n# Lose if we hit the bottom of the card\nelif edge == \"Bottom\" and self.speed.y > 0:\n   self.speed.x = 0\n   self.speed.y = 0\n   self.Hide()\n   label.text = \"Oh no!\"\n"
          },
          "properties": {
            "name": "ball",
            "size": [
              32,
              32
            ],
            "position": [
              50.0,
              52.0
            ],
            "originalSize": [
              32,
              32
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#FB0207"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              32.0,
              32.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.7"
}
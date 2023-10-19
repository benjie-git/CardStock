{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      549,
      544
    ],
    "can_save": false,
    "can_resize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint",
        "on_key_press": "if key_name == \"Space\":\n   ball.send_message(\"StartGame\")",
        "on_mouse_press": "ball.send_message(\"StartGame\")",
        "on_periodic": "# Make the paddle follow the mouse's X position\n# but keep it on-screen.\nx = min(max(get_mouse_pos().x, 0), card.size.width)\npaddle.center.x = x",
        "on_resize": "# Keep the label at the top, following the window's height\nlabel.position.y = card.size.height - label.size.height - 5"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#D0EBF5"
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
            "text_color": "black",
            "font": "Default",
            "font_size": 18,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
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
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#0A5FFF"
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
            "on_setup": "# Bounce off of the paddle, and the card's edges\nself.set_bounce_objects([paddle, card])\n\nself.hide()",
            "on_bounce": "if other_object == paddle:\n   score += 1\n   label.text = score\n   \n   # Speed up or slow down horizontally\n   # based on which side of the paddle\n   # we hit\n   if ball.center.x < paddle.center.x:\n      self.speed.x -= randint(50,100)\n   elif ball.center.x > paddle.center.x:\n      self.speed.x += randint(50,100)\n   # keep the ball from getting too fast\n   self.speed.x = min(self.speed.x, 500)\n   self.speed.x = max(self.speed.x, -500)\n\nelif other_object == card and edge == \"Bottom\":\n   # Lose if we hit the bottom of the card\n   self.speed = (0, 0)\n   self.hide()\n   label.text = \"Oh no!\"",
            "on_message": "if message == \"StartGame\":\n   # Only start a game if the ball wasn't already moving\n   if ball.speed.x == 0 and ball.speed.y == 0:\n      self.position = (100, card.size.height-100)\n      self.speed.x = randint(200,400)\n      self.speed.y = self.speed.x - 800\n      self.show()\n      score = 0\n      label.text = score"
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
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "red"
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
  "CardStock_stack_format": 7,
  "CardStock_stack_version": "0.99.4"
}
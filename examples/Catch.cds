{
  "type": "stack",
  "handlers": {},
  "properties": {
    "can_save": false,
    "author": "",
    "info": ""
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\n\nscore = 0\n# 3 seconds until the green box (goal) moves\nnextMoveTime = time() + 3",
        "on_key_hold": "# Use arrow keys to move the red box (guy) around\nif key_name == \"Left\" and guy.center.x > 0:\n   guy.center.x -= 8\nelif key_name == \"Right\" and guy.center.x < card.size.width:\n   guy.center.x += 8\nelif key_name == \"Up\" and guy.center.y < card.size.height:\n   guy.center.y += 8\nelif key_name == \"Down\" and guy.center.y > 0:\n   guy.center.y -= 8",
        "on_periodic": "size = card.size\ndidUpdate = False\n\nif guy.is_touching(goal):\n   # Guy caught the goal!\n   score += 1\n   didUpdate = True\n\nif time() >= nextMoveTime:\n   # Time's up, move goal now\n   score -= 1\n   didUpdate = True\n   \nif didUpdate:\n   # we need to move the goal\n   label.text = score\n   goal.left = randint(0,size.width - goal.size.width)\n   goal.bottom = randint(0,size.height- goal.size.height)\n   nextMoveTime = time() + 3"
      },
      "properties": {
        "name": "main",
        "size": [
          598,
          400
        ],
        "fill_color": "white",
        "can_resize": false
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "guy",
            "size": [
              44,
              44
            ],
            "center": [
              311.0,
              262.0
            ],
            "originalSize": [
              41,
              36
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "red"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              40.0,
              35.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "goal",
            "size": [
              118,
              118
            ],
            "center": [
              159.0,
              221.0
            ],
            "originalSize": [
              118,
              118
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "green"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              117.0,
              117.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label",
            "size": [
              75,
              31
            ],
            "center": [
              157.0,
              371.0
            ],
            "text": "0",
            "alignment": "Left",
            "text_color": "blue",
            "font": "Mono",
            "font_size": 18,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              138,
              38
            ],
            "center": [
              92.0,
              369.0
            ],
            "text": "Score:",
            "alignment": "Left",
            "text_color": "black",
            "font": "Mono",
            "font_size": 18,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 10,
  "CardStock_stack_version": "0.99.7"
}
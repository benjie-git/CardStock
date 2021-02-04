{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      598,
      400
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\nscore = 0\nnextMoveTime = Time() + 3\n",
        "OnIdle": "if IsKeyPressed(\"Left\"):\n   guy.position += [-8,0]\nif IsKeyPressed(\"Right\"):\n   guy.position += [8,0]\nif IsKeyPressed(\"Up\"):\n   guy.position += [0,-8]\nif IsKeyPressed(\"Down\"):\n   guy.position += [0,8]\n\nsize = card.size\n\nif guy.IsTouching(goal):\n   score += 1\n   label.text = score\n   goal.position = [randint(0,size.x-80),\\\n      randint(0,size.y-80)]\n   nextMoveTime = Time() + 3\n\nif Time() >= nextMoveTime:\n   score -= 1\n   label.text = score\n   goal.position = [randint(0,size.x-80),\\\n      randint(0,size.y-80)]\n   nextMoveTime = Time() + 3\n"
      },
      "properties": {
        "name": "main",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label",
            "size": [
              65,
              28
            ],
            "position": [
              95.0,
              19.0
            ],
            "text": "0",
            "alignment": "Left",
            "textColor": "blue",
            "font": "Mono",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              69,
              30
            ],
            "position": [
              25.0,
              18.0
            ],
            "text": "Score:",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": "18"
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "guy",
            "size": [
              44,
              44
            ],
            "position": [
              289.0,
              116.0
            ],
            "originalSize": [
              41,
              36
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "red"
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
            "position": [
              100.0,
              120.0
            ],
            "originalSize": [
              118,
              118
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "green"
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
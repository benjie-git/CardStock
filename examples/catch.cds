{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      598,
      400
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n\nscore = 0\nnextMoveTime = Time() + 3\n",
        "OnKeyHold": "if keyName == \"Left\":\n   guy.position.x -= 8\nelif keyName == \"Right\":\n   guy.position.x += 8\nelif keyName == \"Up\":\n   guy.position.y += 8\nelif keyName == \"Down\":\n   guy.position.y -= 8\n",
        "OnPeriodic": "size = card.size\ndidUpdate = False\n\nif guy.IsTouching(goal):\n   score += 1\n   didUpdate = True\n\nif Time() >= nextMoveTime:\n   score -= 1\n   didUpdate = True\n   \nif didUpdate:\n   label.text = score\n   goal.position = [randint(0,size.x-goal.size.width),\\\n      randint(0,size.y-goal.size.height)]\n   nextMoveTime = Time() + 3\n"
      },
      "properties": {
        "name": "main",
        "bgColor": "white"
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
            "position": [
              289.0,
              240.0
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
              162.0
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
            "position": [
              120.0,
              356.0
            ],
            "text": "0",
            "alignment": "Left",
            "textColor": "blue",
            "font": "Mono",
            "fontSize": 18,
            "autoShrink": true
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
            "position": [
              23.0,
              350.0
            ],
            "text": "Score:",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": 18,
            "autoShrink": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9.6"
}
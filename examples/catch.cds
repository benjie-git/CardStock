{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      598,
      400
    ],
    "speed": [
      0,
      0
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
        "speed": [
          0,
          0
        ],
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "goal",
            "size": [
              80,
              80
            ],
            "position": [
              86,
              155
            ],
            "speed": [
              0,
              0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "green"
          }
        },
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "guy",
            "size": [
              38,
              36
            ],
            "position": [
              258,
              105
            ],
            "speed": [
              0,
              0
            ],
            "file": "",
            "fit": "Scale",
            "bgColor": "red"
          }
        },
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
              95,
              19
            ],
            "speed": [
              0,
              0
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
              25,
              18
            ],
            "speed": [
              0,
              0
            ],
            "text": "Score:",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": "18"
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
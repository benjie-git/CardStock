{
  "type": "stack",
  "handlers": {},
  "properties": {
    "name": "",
    "size": [
      598,
      400
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "from random import randint\nscore = 0\npressedKeys = []\nnextMoveTime = Time() + 3\n",
        "OnIdle": "if \"Left\" in pressedKeys:\n   guy.MoveBy([-8,0])\nif \"Right\" in pressedKeys:\n   guy.MoveBy([8,0])\nif \"Up\" in pressedKeys:\n   guy.MoveBy([0,-8])\nif \"Down\" in pressedKeys:\n   guy.MoveBy([0,8])\n\nsize = card.GetSize()\n\nif guy.IsTouching(goal):\n   score += 1\n   label.SetText(score)\n   goal.SetPosition([randint(0,size[0]-80),\\\n      randint(0,size[1]-80)])\n   nextMoveTime = Time() + 3\n\nif Time() >= nextMoveTime:\n   score -= 1\n   label.SetText(score)\n   goal.SetPosition([randint(0,size[0]-80),\\\n      randint(0,size[1]-80)])\n   nextMoveTime = Time() + 3\n      ",
        "OnKeyDown": "if keyName not in pressedKeys:\n   pressedKeys.append(keyName)\n",
        "OnKeyUp": "if keyName in pressedKeys:\n   pressedKeys.remove(keyName)\n"
      },
      "properties": {
        "name": "main",
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
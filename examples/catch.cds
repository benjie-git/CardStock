{
  "type": "stack",
  "handlers": {},
  "properties": {
    "name": "",
    "size": [
      600,
      400
    ],
    "hidden": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "from random import randint\nscore = 0\npressedKeys = []\nnextMoveTime = Time() + 3\n",
        "OnIdle": "if \"Left\" in pressedKeys:\n   guy.MoveBy([-10,0])\nif \"Right\" in pressedKeys:\n   guy.MoveBy([10,0])\nif \"Up\" in pressedKeys:\n   guy.MoveBy([0,-10])\nif \"Down\" in pressedKeys:\n   guy.MoveBy([0,10])\n\nsize = card.GetSize()\n\nif guy.IsTouching(goal):\n   score += 1\n   label.SetText(score)\n   goal.SetPosition([randint(0,size[0]-80),\\\n      randint(0,size[1]-80)])\n   nextMoveTime = Time() + 3\n\nif Time() >= nextMoveTime:\n   score -= 1\n   label.SetText(score)\n   goal.SetPosition([randint(0,size[0]-80),\\\n      randint(0,size[1]-80)])\n   nextMoveTime = Time() + 3\n      ",
        "OnKeyDown": "if key not in pressedKeys:\n   pressedKeys.append(key)\n",
        "OnKeyUp": "if key in pressedKeys:\n   pressedKeys.remove(key)\n"
      },
      "properties": {
        "name": "main",
        "hidden": false,
        "bgColor": "white"
      },
      "shapes": [],
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
            "hidden": false,
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
            "hidden": false,
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
            "hidden": false,
            "text": "0",
            "alignment": "Left",
            "textColor": "red",
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
            "hidden": false,
            "text": "Score:",
            "alignment": "Left",
            "textColor": "red",
            "font": "Mono",
            "fontSize": "18"
          }
        }
      ]
    }
  ]
}
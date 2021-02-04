{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n"
      },
      "properties": {
        "name": "home",
        "bgColor": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"minus\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              226.0
            ],
            "title": "-",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"plus\")"
          },
          "properties": {
            "name": "button_2",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              146.0
            ],
            "title": "+",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"times\")"
          },
          "properties": {
            "name": "button_3",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              306.0
            ],
            "title": "*",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"divide\")"
          },
          "properties": {
            "name": "button_4",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              386.0
            ],
            "title": "/",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              397,
              53
            ],
            "position": [
              54.0,
              40.0
            ],
            "text": "Choose a Math Operation",
            "alignment": "Left",
            "textColor": "red",
            "font": "Helvetica",
            "fontSize": 30
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              182,
              43
            ],
            "position": [
              57.0,
              100.0
            ],
            "text": "To Practice",
            "alignment": "Left",
            "textColor": "red",
            "font": "Helvetica",
            "fontSize": 30
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "label_1.text = randint(0,100)\nlabel_2.text = randint(0,100)\n\nanswer.text = \"\"\nanswer.Focus()\n"
      },
      "properties": {
        "name": "plus",
        "bgColor": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              12.0
            ],
            "title": "Home",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 + num2:\n   lastCardName = \"plus\"\n   GotoCard(\"correct\")\nelse:\n   Alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              202.0
            ],
            "text": "0",
            "alignment": "Right",
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              158.0
            ],
            "text": "+",
            "alignment": "Left",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              159.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              123.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "label_1.text = randint(0,100)\nlabel_2.text = randint(0,100)\n\nanswer.text = \"\"\nanswer.Focus()\n"
      },
      "properties": {
        "name": "minus",
        "bgColor": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              12.0
            ],
            "title": "Home",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 - num2:\n   lastCardName = \"minus\"\n   GotoCard(\"correct\")\nelse:\n   Alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              203.0
            ],
            "text": "0",
            "alignment": "Right",
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              158.0
            ],
            "text": "-",
            "alignment": "Left",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              159.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              123.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "label_1.text = randint(1,13)\nlabel_2.text = randint(0,13)\n\nanswer.text = \"\"\nanswer.Focus()\n"
      },
      "properties": {
        "name": "times",
        "bgColor": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              12.0
            ],
            "title": "Home",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 * num2:\n   lastCardName = \"times\"\n   GotoCard(\"correct\")\nelse:\n   Alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              203.0
            ],
            "text": "0",
            "alignment": "Right",
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              158.0
            ],
            "text": "X",
            "alignment": "Left",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              159.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              123.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "a = randint(1,12)\nb = a * randint(1,12)\nlabel_1.text = b\nlabel_2.text = a\n\nanswer.text = \"\"\nanswer.Focus()\n"
      },
      "properties": {
        "name": "divide",
        "bgColor": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoCard(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              12.0
            ],
            "title": "Home",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 / num2:\n   lastCardName = \"divide\"\n   GotoCard(\"correct\")\nelse:\n   Alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              203.0
            ],
            "text": "0",
            "alignment": "Right",
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              158.0
            ],
            "text": "/",
            "alignment": "Left",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              159.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              60,
              20
            ],
            "position": [
              242.0,
              123.0
            ],
            "text": "0",
            "alignment": "Right",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "PlaySound(\"yay.wav\")\nWait(2)\nGotoCard(lastCardName)\n"
      },
      "properties": {
        "name": "correct",
        "bgColor": "#FFFFDD"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              198,
              49
            ],
            "position": [
              41.0,
              58.0
            ],
            "text": "Good Job!!!",
            "alignment": "Center",
            "textColor": "red",
            "font": "Serif",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              202,
              53
            ],
            "position": [
              38.0,
              117.0
            ],
            "text": "You did it!",
            "alignment": "Center",
            "textColor": "green",
            "font": "Helvetica",
            "fontSize": 35
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
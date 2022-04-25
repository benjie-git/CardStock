{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      597,
      293
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "def UpdateBox():\n   lineStart = line.position.x\n   lineWidth = line.size.width\n   box.position.x = lineStart + (lowerBound-1) * lineWidth/100.0\n   box.size.width = (upperBound-lowerBound+1) * lineWidth/100.0\n\nresetButton.Click()\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#CBE1C4"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              459,
              41
            ],
            "position": [
              69.0,
              5.0
            ],
            "text": "Guess a number from 1 - 100.",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "guess = int(self.text)\n\nif guess == number:\n   title.text = \"Congratulations, you guessed it!\"\n\nelif guess < number:\n   if guess > lowerBound:\n      lowerBound = guess\n   hint.text = \"Higher...\"\n   UpdateBox()\n\nelif guess > number:\n   if guess < upperBound:\n      upperBound = guess\n   hint.text = \"Lower...\"\n   UpdateBox()\n\nself.SelectAll()\n"
          },
          "properties": {
            "name": "field",
            "size": [
              60,
              28
            ],
            "position": [
              230.0,
              55.0
            ],
            "text": "",
            "alignment": "Right",
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "line",
            "size": [
              500,
              20
            ],
            "position": [
              38.0,
              167.0
            ],
            "originalSize": [
              420,
              20
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              420.0,
              15.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              44,
              36
            ],
            "position": [
              17.0,
              208.0
            ],
            "text": "1",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              71,
              32
            ],
            "position": [
              500.0,
              208.0
            ],
            "text": "100",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              20,
              22
            ],
            "position": [
              535.0,
              177.0
            ],
            "originalSize": [
              20,
              22
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              0.0,
              22.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_4",
            "size": [
              20,
              22
            ],
            "position": [
              40.0,
              177.0
            ],
            "originalSize": [
              20,
              22
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              0.0,
              22.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "field.Enter()"
          },
          "properties": {
            "name": "enterButton",
            "size": [
              90,
              30
            ],
            "position": [
              303.0,
              54.0
            ],
            "title": "Enter",
            "border": true
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "box",
            "size": [
              139,
              37
            ],
            "position": [
              178.0,
              155.0
            ],
            "originalSize": [
              139,
              46
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#009400"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              139.0,
              46.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "from random import randint\n\nnumber = randint(1, 100)\nlowerBound = 1\nupperBound = 100\nUpdateBox()\n\ntitle.text = \"Guess a number from 1 - 100.\"\nhint.text = \"\"\n\nfield.text = \"\"\nfield.Focus()\n"
          },
          "properties": {
            "name": "resetButton",
            "size": [
              67,
              40
            ],
            "position": [
              0.0,
              0.0
            ],
            "title": "Reset",
            "border": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "hint",
            "size": [
              115,
              23
            ],
            "position": [
              210.0,
              95.0
            ],
            "text": "",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.7"
}
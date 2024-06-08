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
        "on_show_card": "def UpdateBox():\n    lineStart = line.left\n    lineWidth = line.size.width\n    box.size.width = (upperBound-lowerBound+1) * lineWidth/100.0\n    box.left = lineStart + (lowerBound-1) * lineWidth/100.0\n\nresetButton.click()\n"
      },
      "properties": {
        "name": "card_1",
        "size": [
          597,
          293
        ],
        "fill_color": "#CBE1C4",
        "can_resize": false
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
            "center": [
              298.0,
              267.0
            ],
            "text": "Guess a number from 1 - 100.",
            "alignment": "Center",
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
          "type": "textfield",
          "handlers": {
            "on_text_enter": "try:\n    guess = int(self.text)\nexcept:\n    guess = None\n\nif guess is None:\n    return\n\nif guess == number:\n    title.text = \"Congratulations, you guessed it!\"\n\nelif guess < number:\n    if guess > lowerBound:\n        lowerBound = guess\n    hint.text = \"Higher...\"\n    UpdateBox()\n\nelif guess > number:\n    if guess < upperBound:\n        upperBound = guess\n    hint.text = \"Lower...\"\n    UpdateBox()\n\nself.select_all()\n"
          },
          "properties": {
            "name": "field",
            "size": [
              60,
              28
            ],
            "center": [
              260.0,
              224.0
            ],
            "text": "",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
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
            "center": [
              288.0,
              116.0
            ],
            "originalSize": [
              420,
              20
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
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
            "center": [
              39.0,
              67.0
            ],
            "text": "1",
            "alignment": "Center",
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              71,
              32
            ],
            "center": [
              535.0,
              69.0
            ],
            "text": "100",
            "alignment": "Center",
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
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              20,
              22
            ],
            "center": [
              545.0,
              105.0
            ],
            "originalSize": [
              20,
              22
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              22.0
            ],
            [
              0.0,
              0.0
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
            "center": [
              50.0,
              105.0
            ],
            "originalSize": [
              20,
              22
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              22.0
            ],
            [
              0.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "field.enter()"
          },
          "properties": {
            "name": "enterButton",
            "size": [
              90,
              26
            ],
            "center": [
              348.0,
              224.0
            ],
            "text": "Enter",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
            "center": [
              247.0,
              119.0
            ],
            "originalSize": [
              139,
              46
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#009400"
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
            "on_click": "from random import randint\n\nnumber = randint(1, 100)\nlowerBound = 1\nupperBound = 100\nUpdateBox()\n\ntitle.text = \"Guess a number from 1 - 100.\"\nhint.text = \"\"\n\nfield.text = \"\"\nfield.focus()\n"
          },
          "properties": {
            "name": "resetButton",
            "size": [
              67,
              40
            ],
            "center": [
              33.0,
              273.0
            ],
            "text": "Reset",
            "style": "Borderless",
            "is_selected": false,
            "rotation": 0.0
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
            "center": [
              267.0,
              186.0
            ],
            "text": "",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
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
  "CardStock_stack_format": 11,
  "CardStock_stack_version": "0.99.7"
}
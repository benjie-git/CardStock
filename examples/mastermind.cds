{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n\nindicators = [oval_1, oval_2, oval_3, oval_4, oval_5]\nfields = [field_1, field_2, field_3, field_4, field_5]\nnums = [0, 0, 0, 0, 0]\nnum_guesses = 0\n\ndef reset():\n   global num_guesses\n   \n   for i in range(5):\n      nums[i] = randint(0, 9)\n      indicators[i].fillColor = \"white\"\n      fields[i].text = 0\n   num_guesses = 0\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   fields[0].Focus()\n   fields[0].SelectAll()\n\n\ndef check():\n   global num_guesses\n   \n   num_greens = 0\n   num_guesses += 1\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   \n   for i in range(5):\n      n = nums[i]\n      f = int(fields[i].text)\n      if f == n:\n         indicators[i].fillColor = \"green\"\n         num_greens += 1\n      elif f in nums:\n         indicators[i].fillColor = \"blue\"\n      else:\n         indicators[i].fillColor = \"red\"\n      if num_greens == 5:\n         Alert(f\"You Won in {num_guesses} guesses!\")\n         reset()\n\nreset()\n",
        "OnKeyDown": "if keyName == \"Tab\":\n   for f in fields:\n      if f.hasFocus:\n         f.SelectAll()"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#F0F0F0"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "rect_1",
            "size": [
              472,
              187
            ],
            "position": [
              14.0,
              24.0
            ],
            "originalSize": [
              472,
              187
            ],
            "penColor": "black",
            "penThickness": 2,
            "fillColor": "#E0E0E0"
          },
          "points": [
            [
              0.0,
              187.0
            ],
            [
              472.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
          },
          "properties": {
            "name": "field_1",
            "size": [
              58,
              70
            ],
            "position": [
              57.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_1",
            "size": [
              44,
              44
            ],
            "position": [
              64.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
          },
          "properties": {
            "name": "field_2",
            "size": [
              58,
              70
            ],
            "position": [
              137.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_2",
            "size": [
              44,
              44
            ],
            "position": [
              144.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
          },
          "properties": {
            "name": "field_3",
            "size": [
              58,
              70
            ],
            "position": [
              217.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_3",
            "size": [
              44,
              44
            ],
            "position": [
              224.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
          },
          "properties": {
            "name": "field_4",
            "size": [
              58,
              70
            ],
            "position": [
              297.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_4",
            "size": [
              44,
              44
            ],
            "position": [
              304.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
          },
          "properties": {
            "name": "field_5",
            "size": [
              58,
              70
            ],
            "position": [
              377.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_5",
            "size": [
              44,
              44
            ],
            "position": [
              384.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "check()\nfields[0].Focus()\nfields[0].SelectAll()\n"
          },
          "properties": {
            "name": "guess",
            "size": [
              132,
              28
            ],
            "position": [
              293.0,
              273.0
            ],
            "title": "Guess",
            "border": true
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_6",
            "size": [
              44,
              44
            ],
            "position": [
              32.0,
              156.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "green"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              372,
              32
            ],
            "position": [
              91.0,
              159.0
            ],
            "text": "This number is in the correct spot",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18,
            "autoShrink": true
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_7",
            "size": [
              44,
              44
            ],
            "position": [
              32.0,
              96.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "blue"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              372,
              32
            ],
            "position": [
              91.0,
              99.0
            ],
            "text": "This number is in the wrong spot",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18,
            "autoShrink": true
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_8",
            "size": [
              44,
              44
            ],
            "position": [
              32.0,
              36.0
            ],
            "originalSize": [
              44,
              44
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "red"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              372,
              32
            ],
            "position": [
              91.0,
              39.0
            ],
            "text": "This number is not in the answer",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18,
            "autoShrink": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "num_guesses_label",
            "size": [
              194,
              28
            ],
            "position": [
              262.0,
              241.0
            ],
            "text": "Num Guesses: 0",
            "alignment": "Center",
            "textColor": "#666666",
            "font": "Default",
            "fontSize": 14,
            "autoShrink": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "Alert(\"The goal of Mastermind is to guess the secret 5-digit number.  Enter \"\n\"your guesses for each digit, and click Guess.  Then each digit will be color \"\n\"coded according to whether it is the correct number in the correct spot, \"\n\"a correct number but in the wrong spot, or a wrong digit that's not in the \"\n\"secret number at all.  Then adjust your digits and click Guess again!\")"
          },
          "properties": {
            "name": "help_button",
            "size": [
              55,
              29
            ],
            "position": [
              3.0,
              470.0
            ],
            "title": "Help",
            "border": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9.6"
}
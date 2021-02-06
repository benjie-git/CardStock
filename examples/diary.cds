{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "canSave": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "i = card.index+1\ntotal = stack.numCards\ncardNum.text = str(i) + '/' + str(total)\nfield.Focus()\n"
      },
      "properties": {
        "name": "card_3",
        "bgColor": "#C4ACA9"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              211,
              31
            ],
            "position": [
              140.0,
              8.0
            ],
            "text": "My Diary",
            "alignment": "Center",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 26
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              480,
              450
            ],
            "position": [
              10.0,
              41.0
            ],
            "originalSize": [
              480,
              450
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF"
          },
          "points": [
            [
              2,
              2
            ],
            [
              478,
              448
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "fwdButton",
            "size": [
              53,
              29
            ],
            "position": [
              434.0,
              7.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "backButton",
            "size": [
              53,
              29
            ],
            "position": [
              11.0,
              7.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field",
            "size": [
              473,
              443
            ],
            "position": [
              14.0,
              45.0
            ],
            "text": "card one.12345",
            "alignment": "Left",
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.Clone()\nfield.text = \"\"\n"
          },
          "properties": {
            "name": "addButton",
            "size": [
              44,
              28
            ],
            "position": [
              77.0,
              8.0
            ],
            "title": "Add",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "cardNum",
            "size": [
              57,
              27
            ],
            "position": [
              337.0,
              8.0
            ],
            "text": "1/3",
            "alignment": "Left",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 26
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.Delete()\n"
          },
          "properties": {
            "name": "deleteButton",
            "size": [
              44,
              28
            ],
            "position": [
              132.0,
              8.0
            ],
            "title": "Del",
            "border": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "i = card.index+1\ntotal = stack.numCards\ncardNum.text = str(i) + '/' + str(total)\nfield.Focus()\n"
      },
      "properties": {
        "name": "card_2",
        "bgColor": "#C4ACA9"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              211,
              31
            ],
            "position": [
              140.0,
              8.0
            ],
            "text": "My Diary",
            "alignment": "Center",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 26
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              480,
              450
            ],
            "position": [
              10.0,
              41.0
            ],
            "originalSize": [
              480,
              450
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF"
          },
          "points": [
            [
              2,
              2
            ],
            [
              478,
              448
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "fwdButton",
            "size": [
              53,
              29
            ],
            "position": [
              434.0,
              7.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "backButton",
            "size": [
              53,
              29
            ],
            "position": [
              11.0,
              7.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field",
            "size": [
              473,
              443
            ],
            "position": [
              14.0,
              45.0
            ],
            "text": "",
            "alignment": "Left",
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.Clone()\nfield.text = \"\"\n"
          },
          "properties": {
            "name": "addButton",
            "size": [
              44,
              28
            ],
            "position": [
              77.0,
              8.0
            ],
            "title": "Add",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "cardNum",
            "size": [
              57,
              27
            ],
            "position": [
              337.0,
              8.0
            ],
            "text": "2/3",
            "alignment": "Left",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 26
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.Delete()\n"
          },
          "properties": {
            "name": "deleteButton",
            "size": [
              44,
              28
            ],
            "position": [
              132.0,
              8.0
            ],
            "title": "Del",
            "border": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "i = card.index+1\ntotal = stack.numCards\ncardNum.text = str(i) + '/' + str(total)\nfield.Focus()\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#C4ACA9"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              211,
              31
            ],
            "position": [
              140.0,
              8.0
            ],
            "text": "My Diary",
            "alignment": "Center",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 26
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              480,
              450
            ],
            "position": [
              10.0,
              41.0
            ],
            "originalSize": [
              480,
              450
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF"
          },
          "points": [
            [
              2,
              2
            ],
            [
              478,
              448
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "fwdButton",
            "size": [
              53,
              29
            ],
            "position": [
              434.0,
              7.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "backButton",
            "size": [
              53,
              29
            ],
            "position": [
              11.0,
              7.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field",
            "size": [
              473,
              443
            ],
            "position": [
              14.0,
              45.0
            ],
            "text": "and two.three",
            "alignment": "Left",
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.Clone()\nfield.text = \"\"\n"
          },
          "properties": {
            "name": "addButton",
            "size": [
              44,
              28
            ],
            "position": [
              77.0,
              8.0
            ],
            "title": "Add",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "cardNum",
            "size": [
              57,
              27
            ],
            "position": [
              337.0,
              8.0
            ],
            "text": "3/3",
            "alignment": "Left",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 26
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.Delete()\n"
          },
          "properties": {
            "name": "deleteButton",
            "size": [
              44,
              28
            ],
            "position": [
              132.0,
              8.0
            ],
            "title": "Del",
            "border": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.5"
}
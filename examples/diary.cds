{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "canSave": true,
    "canResize": false
  },
  "cards": [
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
            "name": "header",
            "size": [
              122,
              29
            ],
            "position": [
              190.0,
              8.0
            ],
            "text": "My Diary",
            "alignment": "Center",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 18
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              479,
              411
            ],
            "position": [
              10.0,
              79.0
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
              406
            ],
            "position": [
              14.0,
              83.0
            ],
            "text": "text",
            "alignment": "Left",
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.Clone()\nfield.text = \"\"\ntitle.text = \"Title\"\n"
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
              76,
              26
            ],
            "position": [
              332.0,
              8.0
            ],
            "text": "1/1",
            "alignment": "Right",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 18
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
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              406,
              25
            ],
            "position": [
              41.0,
              48.0
            ],
            "text": "Title",
            "alignment": "Center",
            "editable": true,
            "multiline": false
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.7"
}
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
        "OnShowCard": "i = card.GetCardIndex()+1\ntotal = stack.GetNumCards()\ncardNum.SetText(str(i) + '/' + str(total))"
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
              140,
              8
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
              10,
              41
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
              434,
              7
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
              11,
              7
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field_1",
            "size": [
              470,
              442
            ],
            "position": [
              13,
              43
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
            "OnClick": "card.Clone()"
          },
          "properties": {
            "name": "addButton",
            "size": [
              44,
              28
            ],
            "position": [
              77,
              8
            ],
            "title": "+",
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
              337,
              8
            ],
            "text": "1/1",
            "alignment": "Left",
            "textColor": "black",
            "font": "Serif",
            "fontSize": 26
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
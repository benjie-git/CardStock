{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      269,
      267
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#88D174"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "totalLabel",
            "size": [
              185,
              32
            ],
            "position": [
              42.0,
              26.0
            ],
            "text": "",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 14
          }
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              77,
              77
            ],
            "position": [
              156.0,
              94.0
            ],
            "originalSize": [
              77,
              77
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white",
            "cornerRadius": 8
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              77.0,
              77.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              51,
              50
            ],
            "position": [
              167.0,
              109.0
            ],
            "text": "",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 30
          }
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              77,
              77
            ],
            "position": [
              36.0,
              94.0
            ],
            "originalSize": [
              77,
              77
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white",
            "cornerRadius": 8
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              77.0,
              77.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              51,
              50
            ],
            "position": [
              47.0,
              109.0
            ],
            "text": "",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 30
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "# Roll the dice\na = randint(1,6)\nb = randint(1,6)\nlabel_1.text = a\nlabel_2.text = b\n\n# Show the total\ntotalLabel.text = \"The total is \" + str(a+b)"
          },
          "properties": {
            "name": "roll",
            "size": [
              177,
              24
            ],
            "position": [
              46.0,
              205.0
            ],
            "title": "Roll",
            "border": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9"
}
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      822,
      211
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnMouseMove": "apple.center.x = min(mousePos.x, tube.center.x)\nnext.center.x = max(mousePos.x, tube.center.x)\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#E6E6E6"
      },
      "childModels": [
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "apple",
            "size": [
              157,
              182
            ],
            "position": [
              306.0,
              14.0
            ],
            "file": "apple.png",
            "fit": "Fill",
            "rotation": 0
          }
        },
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "next",
            "size": [
              157,
              182
            ],
            "position": [
              370.0,
              15.0
            ],
            "file": "next.png",
            "fit": "Fill",
            "rotation": 0
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "tube",
            "size": [
              234,
              190
            ],
            "position": [
              299.0,
              13.0
            ],
            "originalSize": [
              234,
              190
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#66FFFF"
          },
          "points": [
            [
              0,
              0
            ],
            [
              233,
              189
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              176,
              34
            ],
            "position": [
              330.0,
              88.0
            ],
            "text": "Magic Tube!",
            "alignment": "Center",
            "textColor": "#074080",
            "font": "Default",
            "fontSize": 20
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.7"
}
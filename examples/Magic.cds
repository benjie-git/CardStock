{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      822,
      211
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnMouseMove": "# The egg can't go further right than the tube's center\negg.center.x = min(mousePos.x, tube.center.x)\n\n# And ship can't go further left than the tube's center\nship.center.x = max(mousePos.x, tube.center.x)\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#E6E6E6"
      },
      "childModels": [
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "egg",
            "size": [
              97,
              120
            ],
            "position": [
              344.0,
              38.0
            ],
            "originalSize": [
              60,
              113
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              60.0,
              113.0
            ]
          ]
        },
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "ship",
            "size": [
              157,
              182
            ],
            "position": [
              371.0,
              17.0
            ],
            "file": "ship-off.png",
            "fit": "Contain",
            "rotation": 0,
            "xFlipped": false,
            "yFlipped": false
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
  "CardStock_stack_version": "0.8.3"
}
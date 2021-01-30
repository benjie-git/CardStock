{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      827,
      260
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnMouseMove": "_,appleY = apple.center\n_,nextY = next.center\ntubeX,_ = tube.center\n\nappleX = mousePos.x\nnextX = mousePos.x\n\nif appleX > tubeX: appleX = tubeX\nif nextX < tubeX: nextX = tubeX\n\napple.center = [appleX, appleY]\nnext.center = [nextX, nextY]\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
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
              302.0,
              37.0
            ],
            "file": "apple.png",
            "fit": "Scale",
            "bgColor": "",
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
              362.0,
              37.0
            ],
            "file": "next.png",
            "fit": "Scale",
            "bgColor": "",
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
              289.0,
              34.0
            ],
            "originalSize": [
              234,
              190
            ],
            "penColor": "#7000E9",
            "penThickness": 1,
            "fillColor": "#871AFF"
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
              226,
              95
            ],
            "position": [
              292.0,
              65.0
            ],
            "text": "Magic!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": 60
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
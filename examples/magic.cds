{
  "type": "stack",
  "handlers": {},
  "properties": {
    "name": "",
    "size": [
      830,
      261
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnMouseMove": "_,appleY = apple.GetCenter()\n_,nextY = next.GetCenter()\ntubeX,_ = tube.GetCenter()\n\nappleX = mouseX\nnextX = mouseX\n\nif appleX > tubeX: appleX = tubeX\nif nextX < tubeX: nextX = tubeX\n\napple.SetCenter([appleX, appleY])\nnext.SetCenter([nextX, nextY])\n"
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
              302,
              37
            ],
            "file": "apple.png",
            "fit": "Scale",
            "bgColor": ""
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
              362,
              37
            ],
            "file": "next.png",
            "fit": "Scale",
            "bgColor": ""
          }
        },
        {
          "type": "shapes",
          "handlers": {},
          "properties": {
            "name": "tube",
            "size": [
              234,
              190
            ],
            "position": [
              289,
              34
            ]
          },
          "shapes": [
            {
              "type": "rect",
              "penColor": "#7000E9",
              "fillColor": "#871AFF",
              "thickness": 1,
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
            }
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
              292,
              65
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
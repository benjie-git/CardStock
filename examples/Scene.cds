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
        "OnSetup": "from random import randint",
        "OnKeyDown": "if keyName == \"N\":\n   night.Click()\nelif keyName == \"D\":\n   day.Click()",
        "OnPeriodic": "o = card.AddOval(\n   size = (10,10),\n   position = (randint(0,490),490),\n   fillColor = 'white',\n   penThickness = 1)\n\no.AnimatePosition(\n   randint(300,450)/100.0,\n   (o.position.x + randint(-20,20), -10),\n   o.Delete)\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#88AAFF"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.StopAnimating()\ncard.AnimateBgColor(1,\"#88AAFF\")\n\ncircle.StopAnimating()\ncircle.AnimateFillColor(1,\"yellow\")"
          },
          "properties": {
            "name": "day",
            "size": [
              124,
              24
            ],
            "position": [
              39.0,
              425.0
            ],
            "title": "Day",
            "border": true
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              143,
              147
            ],
            "position": [
              178.0,
              0.0
            ],
            "originalSize": [
              143,
              147
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "brown"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              143.0,
              147.0
            ]
          ]
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "circle",
            "size": [
              97,
              94
            ],
            "position": [
              386.0,
              373.0
            ],
            "originalSize": [
              97,
              94
            ],
            "penColor": "black",
            "penThickness": 0,
            "fillColor": "yellow"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              97.0,
              94.0
            ]
          ]
        },
        {
          "type": "poly",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              232,
              136
            ],
            "position": [
              136.0,
              148.0
            ],
            "originalSize": [
              232,
              136
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "brown"
          },
          "points": [
            [
              232.0,
              0.0
            ],
            [
              119.0,
              136.0
            ],
            [
              0.0,
              1.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              37,
              58
            ],
            "position": [
              247.0,
              1.0
            ],
            "originalSize": [
              37,
              58
            ],
            "penColor": "black",
            "penThickness": 2,
            "fillColor": "#A47D5D"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              37.0,
              58.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.StopAnimating()\ncard.AnimateBgColor(1,\"black\")\n\ncircle.StopAnimating()\ncircle.AnimateFillColor(1,\"grey\")"
          },
          "properties": {
            "name": "night",
            "size": [
              124,
              24
            ],
            "position": [
              39.0,
              455.0
            ],
            "title": "Night",
            "border": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9"
}
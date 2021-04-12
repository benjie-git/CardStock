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
        "OnKeyDown": "print(keyName)\n\nif keyName == \"N\":\n   night.Click()\nif keyName == \"D\":\n   day.Click()",
        "OnIdle": "o = card.AddOval()\no.size = (10,10)\no.position = (randint(0,490),0)\no.fillColor = 'white'\no.penThickness = 1\no.AnimatePosition(randint(120,280)/100.0, (o.position.x + randint(-20,20), 500), o.Delete)\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#88AAFF"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.AnimateBgColor(1,\"#88AAFF\")\ncircle.AnimateFillColor(1,\"yellow\")"
          },
          "properties": {
            "name": "day",
            "size": [
              124,
              29
            ],
            "position": [
              41.0,
              53.0
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
              353.0
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
              33.0
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
              216.0
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
              136.0
            ],
            [
              119.0,
              0.0
            ],
            [
              0.0,
              135.0
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
              441.0
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
            "OnClick": "card.AnimateBgColor(1,\"black\")\ncircle.AnimateFillColor(1,\"grey\")"
          },
          "properties": {
            "name": "night",
            "size": [
              124,
              29
            ],
            "position": [
              39.0,
              21.0
            ],
            "title": "Night",
            "border": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.8.10"
}
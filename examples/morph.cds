{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "def MorphToCardNumber(cardNumber, duration):\n   \"\"\"\n   Morph from the current card to the card at the given index over dration seconds.\n   Do this by finding all objects by name that exist on both cards, and \n   animating their properties from the current card's version, to the destination\n   card's version.\n   \"\"\"\n   oldProps = {}\n   for obj in card.children:\n      d = {\n         \"position\": obj.position,\n         \"size\": obj.size,\n         \"penThickness\": obj.penThickness if hasattr(obj, \"penThickness\") else None,\n         \"penColor\": obj.penColor if hasattr(obj, \"penColor\") else None,\n         \"fillColor\": obj.fillColor if hasattr(obj, \"fillColor\") else None,\n         \"cornerRadius\": obj.cornerRadius if hasattr(obj, \"cornerRadius\") else None\n      }\n      oldProps[obj.name] = d\n   \n   newCard = stack.CardWithNumber(cardNumber)\n   newProps = {}\n   for name, d in oldProps.items():\n      newObj = None\n      for obj in newCard.children:\n         if obj.name == name:\n            newObj = obj\n      if newObj:\n         d = {\n            \"position\": newObj.position,\n            \"size\": newObj.size,\n            \"penThickness\": newObj.penThickness if hasattr(newObj, \"penThickness\") else None,\n            \"penColor\": newObj.penColor if hasattr(newObj, \"penColor\") else None,\n            \"fillColor\": newObj.fillColor if hasattr(newObj, \"fillColor\") else None,\n            \"cornerRadius\": newObj.cornerRadius if hasattr(newObj, \"cornerRadius\") else None\n         }\n         newProps[name] = d\n   \n   for name, d in newProps.items():\n      obj = None\n      for o in newCard.children:\n         if o.name == name:\n            obj = o\n      if obj:\n         obj.position = oldProps[name][\"position\"]\n         obj.size = oldProps[name][\"size\"]\n         if oldProps[name][\"penThickness\"]: obj.penThickness = oldProps[name][\"penThickness\"]\n         if oldProps[name][\"penColor\"]: obj.penColor = oldProps[name][\"penColor\"]\n         if oldProps[name][\"fillColor\"]: obj.fillColor = oldProps[name][\"fillColor\"]\n         if oldProps[name][\"cornerRadius\"]: obj.cornerRadius = oldProps[name][\"cornerRadius\"]\n         \n         obj.AnimatePosition(duration, newProps[name][\"position\"])\n         obj.AnimateSize(duration, newProps[name][\"size\"])\n         if oldProps[name][\"penThickness\"]: obj.AnimatePenThickness(duration, newProps[name][\"penThickness\"])\n         if oldProps[name][\"penColor\"]: obj.AnimatePenColor(duration, newProps[name][\"penColor\"])\n         if oldProps[name][\"fillColor\"]: obj.AnimateFillColor(duration, newProps[name][\"fillColor\"])\n         if oldProps[name][\"cornerRadius\"]: obj.AnimateCornerRadius(duration, newProps[name][\"cornerRadius\"])\n\n   GotoCard(cardNumber)\n   "
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              419,
              341
            ],
            "position": [
              50.0,
              133.0
            ],
            "originalSize": [
              138,
              84
            ],
            "penColor": "grey",
            "penThickness": 4,
            "fillColor": "#D5E1D3"
          },
          "points": [
            [
              0.0,
              84.0
            ],
            [
              138.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_4",
            "size": [
              187,
              112
            ],
            "position": [
              63.0,
              151.0
            ],
            "originalSize": [
              187,
              112
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white",
            "cornerRadius": 8
          },
          "points": [
            [
              0.0,
              112.0
            ],
            [
              187.0,
              0.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_5",
            "size": [
              101,
              116
            ],
            "position": [
              97.0,
              324.0
            ],
            "originalSize": [
              65,
              128
            ],
            "penColor": "black",
            "penThickness": 4
          },
          "points": [
            [
              50.0,
              0.0
            ],
            [
              43.0,
              0.0
            ],
            [
              36.0,
              0.0
            ],
            [
              31.0,
              0.0
            ],
            [
              24.0,
              0.0
            ],
            [
              18.0,
              1.0
            ],
            [
              15.0,
              4.0
            ],
            [
              12.0,
              8.0
            ],
            [
              11.0,
              12.0
            ],
            [
              10.0,
              16.0
            ],
            [
              9.0,
              22.0
            ],
            [
              9.0,
              28.0
            ],
            [
              9.0,
              33.0
            ],
            [
              11.0,
              38.0
            ],
            [
              14.0,
              42.0
            ],
            [
              16.0,
              45.0
            ],
            [
              18.0,
              47.0
            ],
            [
              20.0,
              49.0
            ],
            [
              22.0,
              51.0
            ],
            [
              24.0,
              54.0
            ],
            [
              28.0,
              57.0
            ],
            [
              30.0,
              60.0
            ],
            [
              34.0,
              63.0
            ],
            [
              38.0,
              65.0
            ],
            [
              41.0,
              68.0
            ],
            [
              46.0,
              69.0
            ],
            [
              51.0,
              71.0
            ],
            [
              56.0,
              73.0
            ],
            [
              61.0,
              75.0
            ],
            [
              64.0,
              79.0
            ],
            [
              65.0,
              85.0
            ],
            [
              63.0,
              89.0
            ],
            [
              60.0,
              92.0
            ],
            [
              57.0,
              96.0
            ],
            [
              53.0,
              99.0
            ],
            [
              48.0,
              101.0
            ],
            [
              44.0,
              103.0
            ],
            [
              41.0,
              104.0
            ],
            [
              39.0,
              106.0
            ],
            [
              34.0,
              108.0
            ],
            [
              31.0,
              110.0
            ],
            [
              26.0,
              112.0
            ],
            [
              23.0,
              113.0
            ],
            [
              19.0,
              116.0
            ],
            [
              16.0,
              118.0
            ],
            [
              11.0,
              120.0
            ],
            [
              7.0,
              122.0
            ],
            [
              3.0,
              125.0
            ],
            [
              0.0,
              128.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              84,
              64
            ],
            "position": [
              346.0,
              378.0
            ],
            "originalSize": [
              156,
              120
            ],
            "penColor": "black",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              120.0
            ],
            [
              156.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "MorphToCardNumber(2, 1)"
          },
          "properties": {
            "name": "button_1",
            "size": [
              138,
              26
            ],
            "position": [
              341.0,
              33.0
            ],
            "title": "Morph",
            "border": true
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              111,
              88
            ],
            "position": [
              237.0,
              302.0
            ],
            "originalSize": [
              111,
              88
            ],
            "penColor": "black",
            "penThickness": 12,
            "fillColor": "white"
          },
          "points": [
            [
              111.0,
              0.0
            ],
            [
              0.0,
              88.0
            ]
          ]
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "card_2",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              298,
              293
            ],
            "position": [
              152.0,
              151.0
            ],
            "originalSize": [
              138,
              84
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              84.0
            ],
            [
              138.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_4",
            "size": [
              156,
              194
            ],
            "position": [
              72.0,
              27.0
            ],
            "originalSize": [
              187,
              112
            ],
            "penColor": "green",
            "penThickness": 0,
            "fillColor": "green",
            "cornerRadius": 50
          },
          "points": [
            [
              0.0,
              112.0
            ],
            [
              187.0,
              0.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_5",
            "size": [
              323,
              410
            ],
            "position": [
              81.0,
              68.0
            ],
            "originalSize": [
              65,
              128
            ],
            "penColor": "#FFFFFF00",
            "penThickness": 100
          },
          "points": [
            [
              50.0,
              0.0
            ],
            [
              43.0,
              0.0
            ],
            [
              36.0,
              0.0
            ],
            [
              31.0,
              0.0
            ],
            [
              24.0,
              0.0
            ],
            [
              18.0,
              1.0
            ],
            [
              15.0,
              4.0
            ],
            [
              12.0,
              8.0
            ],
            [
              11.0,
              12.0
            ],
            [
              10.0,
              16.0
            ],
            [
              9.0,
              22.0
            ],
            [
              9.0,
              28.0
            ],
            [
              9.0,
              33.0
            ],
            [
              11.0,
              38.0
            ],
            [
              14.0,
              42.0
            ],
            [
              16.0,
              45.0
            ],
            [
              18.0,
              47.0
            ],
            [
              20.0,
              49.0
            ],
            [
              22.0,
              51.0
            ],
            [
              24.0,
              54.0
            ],
            [
              28.0,
              57.0
            ],
            [
              30.0,
              60.0
            ],
            [
              34.0,
              63.0
            ],
            [
              38.0,
              65.0
            ],
            [
              41.0,
              68.0
            ],
            [
              46.0,
              69.0
            ],
            [
              51.0,
              71.0
            ],
            [
              56.0,
              73.0
            ],
            [
              61.0,
              75.0
            ],
            [
              64.0,
              79.0
            ],
            [
              65.0,
              85.0
            ],
            [
              63.0,
              89.0
            ],
            [
              60.0,
              92.0
            ],
            [
              57.0,
              96.0
            ],
            [
              53.0,
              99.0
            ],
            [
              48.0,
              101.0
            ],
            [
              44.0,
              103.0
            ],
            [
              41.0,
              104.0
            ],
            [
              39.0,
              106.0
            ],
            [
              34.0,
              108.0
            ],
            [
              31.0,
              110.0
            ],
            [
              26.0,
              112.0
            ],
            [
              23.0,
              113.0
            ],
            [
              19.0,
              116.0
            ],
            [
              16.0,
              118.0
            ],
            [
              11.0,
              120.0
            ],
            [
              7.0,
              122.0
            ],
            [
              3.0,
              125.0
            ],
            [
              0.0,
              128.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              158,
              96
            ],
            "position": [
              170.0,
              197.0
            ],
            "originalSize": [
              156,
              120
            ],
            "penColor": "#0A5FFF",
            "penThickness": 20
          },
          "points": [
            [
              0.0,
              120.0
            ],
            [
              156.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "MorphToCardNumber(1, 1)"
          },
          "properties": {
            "name": "button_1",
            "size": [
              138,
              26
            ],
            "position": [
              341.0,
              33.0
            ],
            "title": "Morph",
            "border": true
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              191,
              171
            ],
            "position": [
              247.0,
              228.0
            ],
            "originalSize": [
              111,
              88
            ],
            "penColor": "#000000",
            "penThickness": 1,
            "fillColor": "#FF0000"
          },
          "points": [
            [
              111.0,
              0.0
            ],
            [
              0.0,
              88.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9.2"
}
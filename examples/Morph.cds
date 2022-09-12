{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "is_morphing = False\n\ndef MorphToCardNumber(duration, cardNumber):\n   \"\"\"\n   Morph from the current card to the card at the given index over dration seconds.\n   Do this by finding all objects by name that exist on both cards, and \n   animating their properties from the current card's version, to the destination\n   card's version.\n   \"\"\"\n   global is_morphing\n   \n   oldProps = {}\n   is_morphing = True\n   for obj in card.children:\n      props = {\n         \"position\": obj.position,\n         \"size\": obj.size,\n         \"pen_thickness\": obj.pen_thickness if hasattr(obj, \"pen_thickness\") else None,\n         \"pen_color\": obj.pen_color if hasattr(obj, \"pen_color\") else None,\n         \"fill_color\": obj.fill_color if hasattr(obj, \"fill_color\") else None,\n         \"corner_radius\": obj.corner_radius if hasattr(obj, \"corner_radius\") else None,\n         \"rotation\": obj.rotation if hasattr(obj, \"rotation\") else None\n      }\n      oldProps[obj.name] = props\n   \n   newCard = stack.card_with_number(cardNumber)\n   newProps = {}\n   for name, props in oldProps.items():\n      newObj = None\n      for obj in newCard.children:\n         if obj.name == name:\n            newObj = obj\n      if newObj:\n         props = {\n            \"position\": newObj.position,\n            \"size\": newObj.size,\n            \"pen_thickness\": newObj.pen_thickness if hasattr(newObj, \"pen_thickness\") else None,\n            \"pen_color\": newObj.pen_color if hasattr(newObj, \"pen_color\") else None,\n            \"fill_color\": newObj.fill_color if hasattr(newObj, \"fill_color\") else None,\n            \"corner_radius\": newObj.corner_radius if hasattr(newObj, \"corner_radius\") else None,\n            \"rotation\": newObj.rotation if hasattr(newObj, \"rotation\") else None\n         }\n         newProps[name] = props\n   \n   for name, props in newProps.items():\n      obj = None\n      for o in newCard.children:\n         if o.name == name:\n            obj = o\n      if obj:\n         obj.position = oldProps[name][\"position\"]\n         obj.size = oldProps[name][\"size\"]\n         if oldProps[name][\"pen_thickness\"] is not None: obj.pen_thickness = oldProps[name][\"pen_thickness\"]\n         if oldProps[name][\"pen_color\"] is not None: obj.pen_color = oldProps[name][\"pen_color\"]\n         if oldProps[name][\"fill_color\"] is not None: obj.fill_color = oldProps[name][\"fill_color\"]\n         if oldProps[name][\"corner_radius\"] is not None: obj.corner_radius = oldProps[name][\"corner_radius\"]\n         if oldProps[name][\"rotation\"] is not None: obj.rotation = oldProps[name][\"rotation\"]\n         \n         obj.animate_position(duration, newProps[name][\"position\"])\n         obj.animate_size(duration, newProps[name][\"size\"])\n         if oldProps[name][\"pen_thickness\"] is not None: obj.animate_pen_thickness(duration, newProps[name][\"pen_thickness\"])\n         if oldProps[name][\"pen_color\"] is not None: obj.animate_pen_color(duration, newProps[name][\"pen_color\"])\n         if oldProps[name][\"fill_color\"] is not None: obj.animate_fill_color(duration, newProps[name][\"fill_color\"])\n         if oldProps[name][\"corner_radius\"] is not None: obj.animate_corner_radius(duration, newProps[name][\"corner_radius\"])\n         if oldProps[name][\"rotation\"] is not None: obj.animate_rotation(duration, newProps[name][\"rotation\"])\n\n   goto_card(cardNumber)\n   \n   def allDone(): \n      global is_morphing\n      is_morphing = False\n   run_after_delay(1, allDone)\n\nis_morphing = False"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "white"
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
            "pen_color": "grey",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#D5E1D3"
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
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
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
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0
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
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0
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
            "on_click": "if not is_morphing:\n   MorphToCardNumber(1.0, 2)"
          },
          "properties": {
            "name": "button_1",
            "size": [
              138,
              26
            ],
            "position": [
              24.0,
              24.0
            ],
            "title": "Morph",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
            "pen_color": "black",
            "pen_thickness": 12,
            "rotation": 0.0,
            "fill_color": "white"
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
        "fill_color": "white"
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
              128.0,
              150.0
            ],
            "originalSize": [
              138,
              84
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 321.3,
            "fill_color": "white"
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
              134,
              188
            ],
            "position": [
              156.0,
              27.0
            ],
            "originalSize": [
              187,
              112
            ],
            "pen_color": "green",
            "pen_thickness": 0,
            "rotation": 45.6,
            "fill_color": "green",
            "corner_radius": 50
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
            "pen_color": "#FFFFFF00",
            "pen_thickness": 100,
            "rotation": 0.0
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
            "pen_color": "#0A5FFF",
            "pen_thickness": 20,
            "rotation": 0.0
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
            "on_click": "if not is_morphing:\n   MorphToCardNumber(1.0, 3)"
          },
          "properties": {
            "name": "button_1",
            "size": [
              138,
              26
            ],
            "position": [
              266.0,
              19.0
            ],
            "title": "Morph",
            "style": "Border",
            "is_selected": false,
            "rotation": 167.2
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
              205.0,
              262.0
            ],
            "originalSize": [
              111,
              88
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#FF0000"
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
        "name": "card_3",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              181,
              46
            ],
            "position": [
              254.0,
              246.0
            ],
            "originalSize": [
              138,
              84
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 37.7,
            "fill_color": "white"
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
              35,
              240
            ],
            "position": [
              72.0,
              27.0
            ],
            "originalSize": [
              187,
              112
            ],
            "pen_color": "#000080",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "#000080",
            "corner_radius": 0
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
              166,
              63
            ],
            "position": [
              92.0,
              276.0
            ],
            "originalSize": [
              65,
              128
            ],
            "pen_color": "#800080",
            "pen_thickness": 6,
            "rotation": 0.0
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
              163,
              94
            ],
            "position": [
              32.0,
              341.0
            ],
            "originalSize": [
              156,
              120
            ],
            "pen_color": "#0A5FFF",
            "pen_thickness": 20,
            "rotation": 289.4
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
            "on_click": "if not is_morphing:\n   MorphToCardNumber(1.0, 1)"
          },
          "properties": {
            "name": "button_1",
            "size": [
              138,
              26
            ],
            "position": [
              345.0,
              147.0
            ],
            "title": "Morph",
            "style": "Border",
            "is_selected": false,
            "rotation": 323.5
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              395,
              69
            ],
            "position": [
              48.0,
              154.0
            ],
            "originalSize": [
              111,
              88
            ],
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 306.2,
            "fill_color": "#FFFF0A"
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
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
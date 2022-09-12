{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      822,
      211
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_mouse_move": "# The egg can't go further right than the tube's center\negg.center.x = min(mouse_pos.x, tube.center.x)\n\n# And ship can't go further left than the tube's center\nship.center.x = max(mouse_pos.x, tube.center.x)"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#E6E6E6"
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
              53.0
            ],
            "originalSize": [
              60,
              113
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white"
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
              12.0
            ],
            "file": "ship-off.png",
            "fit": "Contain",
            "rotation": 0.0,
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
              8.0
            ],
            "originalSize": [
              234,
              190
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#66FFFF"
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
              89.0
            ],
            "text": "Magic Tube!",
            "alignment": "Center",
            "text_color": "#074080",
            "font": "Default",
            "font_size": 20,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
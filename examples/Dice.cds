{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      269,
      267
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint",
        "on_key_press": "if key_name == \"Space\":\n   roll.click()"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#88D174"
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
            "text_color": "black",
            "font": "Default",
            "font_size": 14,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
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
            "text_color": "black",
            "font": "Default",
            "font_size": 30,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
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
            "text_color": "black",
            "font": "Default",
            "font_size": 30,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "# Roll the dice\na = randint(1,6)\nb = randint(1,6)\nlabel_1.text = a\nlabel_2.text = b\n\n# show the total\ntotalLabel.text = \"The total is \" + str(a+b)"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
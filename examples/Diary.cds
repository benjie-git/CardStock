{
  "type": "stack",
  "handlers": {},
  "properties": {
    "can_save": true,
    "author": "",
    "info": ""
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_show_card": "i = card.number\ntotal = stack.num_cards\ncardNum.text = str(i) + '/' + str(total)\nfield.focus()\n"
      },
      "properties": {
        "name": "card_1",
        "size": [
          500,
          500
        ],
        "fill_color": "#C4ACA9",
        "can_resize": false
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "header",
            "size": [
              122,
              29
            ],
            "position": [
              190.0,
              463.0
            ],
            "text": "My Diary",
            "alignment": "Center",
            "text_color": "black",
            "font": "Serif",
            "font_size": 18,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              479,
              411
            ],
            "position": [
              10.0,
              10.0
            ],
            "originalSize": [
              480,
              450
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#FFFFFF"
          },
          "points": [
            [
              2,
              2
            ],
            [
              478,
              448
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
          },
          "properties": {
            "name": "fwdButton",
            "size": [
              53,
              29
            ],
            "position": [
              434.0,
              464.0
            ],
            "text": ">",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "backButton",
            "size": [
              53,
              29
            ],
            "position": [
              11.0,
              464.0
            ],
            "text": "<",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field",
            "size": [
              471,
              404
            ],
            "position": [
              12.0,
              15.0
            ],
            "text": "",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "newCard = card.clone()\nnewCard.field.text = \"\"\nnewCard.title.text = \"Title\"\n"
          },
          "properties": {
            "name": "addButton",
            "size": [
              44,
              28
            ],
            "position": [
              77.0,
              464.0
            ],
            "text": "Add",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "cardNum",
            "size": [
              76,
              26
            ],
            "position": [
              332.0,
              466.0
            ],
            "text": "1/2",
            "alignment": "Right",
            "text_color": "black",
            "font": "Serif",
            "font_size": 18,
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
            "on_click": "card.delete()\n"
          },
          "properties": {
            "name": "deleteButton",
            "size": [
              44,
              28
            ],
            "position": [
              132.0,
              464.0
            ],
            "text": "Del",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              406,
              25
            ],
            "position": [
              41.0,
              427.0
            ],
            "text": "Title",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 9,
  "CardStock_stack_version": "0.99.6"
}
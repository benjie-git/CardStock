{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      313,
      267
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "# After an operation like +, -, =, etc., then next number key should replace the old number\nshouldReplaceText = True\n# Which operation was last clicked, so we know what = should do\nop = \"\"",
        "on_show_card": "field.focus()\nfield.select_all()"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#555555"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "button_eq.click()"
          },
          "properties": {
            "name": "field",
            "size": [
              230,
              28
            ],
            "position": [
              40.0,
              209.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Mono",
            "font_size": 14,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "oldVal = float(field.text)\nfield.focus()\nfield.select_all()\nshouldReplaceText = True\nop = \"+\"\n"
          },
          "properties": {
            "name": "button_16",
            "size": [
              50,
              30
            ],
            "position": [
              220.0,
              165.0
            ],
            "title": "+",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "oldVal = float(field.text)\nfield.focus()\nfield.select_all()\nshouldReplaceText = True\nop = \"*\"\n"
          },
          "properties": {
            "name": "button_1",
            "size": [
              50,
              30
            ],
            "position": [
              220.0,
              75.0
            ],
            "title": "*",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "oldVal = float(field.text)\nfield.focus()\nfield.select_all()\nshouldReplaceText = True\nop = \"/\"\n"
          },
          "properties": {
            "name": "button_3",
            "size": [
              50,
              30
            ],
            "position": [
              220.0,
              37.0
            ],
            "title": "/",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "newVal = float(field.text)\n\nif op==\"+\":\n  ans = oldVal+newVal\nelif op==\"-\":\n  ans = oldVal-newVal\nelif op==\"*\":\n  ans = oldVal*newVal\nelif op==\"/\":\n  ans = oldVal/newVal\nelse:\n   ans = 0\n   \noldVal = newVal\n\nfield.text = ans\nfield.focus()\nfield.select_all()\nshouldReplaceText = True\n"
          },
          "properties": {
            "name": "button_eq",
            "size": [
              110,
              30
            ],
            "position": [
              100.0,
              37.0
            ],
            "title": "=",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"1\"\n   shouldReplaceText = False\nelse:\n   field.text += \"1\""
          },
          "properties": {
            "name": "button_5",
            "size": [
              50,
              30
            ],
            "position": [
              41.0,
              164.0
            ],
            "title": "1",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"2\"\n   shouldReplaceText = False\nelse:\n   field.text += \"2\""
          },
          "properties": {
            "name": "button_6",
            "size": [
              50,
              30
            ],
            "position": [
              100.0,
              165.0
            ],
            "title": "2",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"3\"\n   shouldReplaceText = False\nelse:\n   field.text += \"3\""
          },
          "properties": {
            "name": "button_7",
            "size": [
              50,
              30
            ],
            "position": [
              160.0,
              165.0
            ],
            "title": "3",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"4\"\n   shouldReplaceText = False\nelse:\n   field.text += \"4\""
          },
          "properties": {
            "name": "button_8",
            "size": [
              50,
              30
            ],
            "position": [
              40.0,
              118.0
            ],
            "title": "4",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"5\"\n   shouldReplaceText = False\nelse:\n   field.text += \"5\""
          },
          "properties": {
            "name": "button_9",
            "size": [
              50,
              30
            ],
            "position": [
              100.0,
              119.0
            ],
            "title": "5",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"6\"\n   shouldReplaceText = False\nelse:\n   field.text += \"6\""
          },
          "properties": {
            "name": "button_10",
            "size": [
              50,
              30
            ],
            "position": [
              160.0,
              118.0
            ],
            "title": "6",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"7\"\n   shouldReplaceText = False\nelse:\n   field.text += \"7\""
          },
          "properties": {
            "name": "button_11",
            "size": [
              50,
              30
            ],
            "position": [
              40.0,
              75.0
            ],
            "title": "7",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"8\"\n   shouldReplaceText = False\nelse:\n   field.text += \"8\""
          },
          "properties": {
            "name": "button_12",
            "size": [
              50,
              30
            ],
            "position": [
              100.0,
              75.0
            ],
            "title": "8",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"9\"\n   shouldReplaceText = False\nelse:\n   field.text += \"9\""
          },
          "properties": {
            "name": "button_13",
            "size": [
              50,
              30
            ],
            "position": [
              160.0,
              75.0
            ],
            "title": "9",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if shouldReplaceText:\n   field.text = \"0\"\n   shouldReplaceText = False\nelse:\n   field.text += \"0\""
          },
          "properties": {
            "name": "button_14",
            "size": [
              50,
              30
            ],
            "position": [
              40.0,
              37.0
            ],
            "title": "0",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "oldVal = float(field.text)\nfield.focus()\nfield.select_all()\nshouldReplaceText = True\nop = \"-\"\n"
          },
          "properties": {
            "name": "button_15",
            "size": [
              50,
              30
            ],
            "position": [
              220.0,
              119.0
            ],
            "title": "-",
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
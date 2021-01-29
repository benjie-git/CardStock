{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      313,
      267
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "shouldReplaceText = False\nop = \"\""
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#555555"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "f",
            "size": [
              230,
              28
            ],
            "position": [
              40,
              30
            ],
            "text": "",
            "alignment": "Right",
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "oldVal = float(f.text)\nf.Focus()\nf.SelectAll()\nshouldReplaceText = True\nop = \"+\"\n"
          },
          "properties": {
            "name": "button_16",
            "size": [
              50,
              30
            ],
            "position": [
              220,
              72
            ],
            "title": "+",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "oldVal = float(f.text)\nf.Focus()\nf.SelectAll()\nshouldReplaceText = True\nop = \"*\"\n"
          },
          "properties": {
            "name": "button_1",
            "size": [
              50,
              30
            ],
            "position": [
              220,
              162
            ],
            "title": "*",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "oldVal = float(f.text)\nf.Focus()\nf.SelectAll()\nshouldReplaceText = True\nop = \"/\"\n"
          },
          "properties": {
            "name": "button_3",
            "size": [
              50,
              30
            ],
            "position": [
              220,
              200
            ],
            "title": "/",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "newVal = float(f.text)\n\nif op==\"+\":\n  ans = oldVal+newVal\nif op==\"-\":\n  ans = oldVal-newVal\nif op==\"*\":\n  ans = oldVal*newVal\nif op==\"/\":\n  ans = oldVal/newVal\nelse:\n   ans = 0\n   \noldVal = newVal\n\nf.text = ans\nf.Focus()\nf.SelectAll()\nshouldReplaceText = True\n"
          },
          "properties": {
            "name": "button_4",
            "size": [
              110,
              30
            ],
            "position": [
              100,
              200
            ],
            "title": "=",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"1\"\n   shouldReplaceText = False\nelse:\n   f.text += \"1\""
          },
          "properties": {
            "name": "button_5",
            "size": [
              50,
              30
            ],
            "position": [
              41,
              73
            ],
            "title": "1",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"2\"\n   shouldReplaceText = False\nelse:\n   f.text += \"2\""
          },
          "properties": {
            "name": "button_6",
            "size": [
              50,
              30
            ],
            "position": [
              100,
              72
            ],
            "title": "2",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"3\"\n   shouldReplaceText = False\nelse:\n   f.text += \"3\""
          },
          "properties": {
            "name": "button_7",
            "size": [
              50,
              30
            ],
            "position": [
              160,
              72
            ],
            "title": "3",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"4\"\n   shouldReplaceText = False\nelse:\n   f.text += \"4\""
          },
          "properties": {
            "name": "button_8",
            "size": [
              50,
              30
            ],
            "position": [
              40,
              119
            ],
            "title": "4",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"5\"\n   shouldReplaceText = False\nelse:\n   f.text += \"5\""
          },
          "properties": {
            "name": "button_9",
            "size": [
              50,
              30
            ],
            "position": [
              100,
              118
            ],
            "title": "5",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"6\"\n   shouldReplaceText = False\nelse:\n   f.text += \"6\""
          },
          "properties": {
            "name": "button_10",
            "size": [
              50,
              30
            ],
            "position": [
              160,
              119
            ],
            "title": "6",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"7\"\n   shouldReplaceText = False\nelse:\n   f.text += \"7\""
          },
          "properties": {
            "name": "button_11",
            "size": [
              50,
              30
            ],
            "position": [
              40,
              162
            ],
            "title": "7",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"8\"\n   shouldReplaceText = False\nelse:\n   f.text += \"8\""
          },
          "properties": {
            "name": "button_12",
            "size": [
              50,
              30
            ],
            "position": [
              100,
              162
            ],
            "title": "8",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"9\"\n   shouldReplaceText = False\nelse:\n   f.text += \"9\""
          },
          "properties": {
            "name": "button_13",
            "size": [
              50,
              30
            ],
            "position": [
              160,
              162
            ],
            "title": "9",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if shouldReplaceText:\n   f.text = \"0\"\n   shouldReplaceText = False\nelse:\n   f.text += \"0\""
          },
          "properties": {
            "name": "button_14",
            "size": [
              50,
              30
            ],
            "position": [
              40,
              200
            ],
            "title": "0",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "oldVal = float(f.text)\nf.Focus()\nf.SelectAll()\nshouldReplaceText = True\nop = \"-\"\n"
          },
          "properties": {
            "name": "button_15",
            "size": [
              50,
              30
            ],
            "position": [
              220,
              118
            ],
            "title": "-",
            "border": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
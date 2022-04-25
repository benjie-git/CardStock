{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      887,
      675
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnResize": "webview_1.size = (card.size.width-6, card.size.height-32)\n#group_1.position = (0, webview_1.size.height)\n#group_1.size = (card.size.width, 32)"
      },
      "properties": {
        "name": "card_1",
        "fillColor": "#D6D4D7"
      },
      "childModels": [
        {
          "type": "webview",
          "handlers": {
            "OnDoneLoading": "print(URL, didLoad)\n",
            "OnCardStockLink": "if message == \"alert\":\n   Alert(\"Beep!\")\nelif message == \"red\":\n   card.fillColor='red'\nelif message == \"white\":\n   card.fillColor='white'"
          },
          "properties": {
            "name": "webview_1",
            "size": [
              881,
              634
            ],
            "position": [
              3.0,
              4.0
            ],
            "URL": "",
            "HTML": "",
            "allowedHosts": []
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "webview_1.GoBack()"
          },
          "properties": {
            "name": "button_1",
            "size": [
              141,
              33
            ],
            "position": [
              2.0,
              641.0
            ],
            "title": "Back",
            "hasBorder": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "webview_1.HTML = \"\"\"\nThis should do a thing: \n<a href=\"cardstock:alert\">Alert</a><br/>\nSet background color: \n<a href=\"cardstock:red\">Red</a> |\n<a href=\"cardstock:white\">White</a>\n<br/>\n\"\"\"\n"
          },
          "properties": {
            "name": "button_2",
            "size": [
              141,
              33
            ],
            "position": [
              187.0,
              641.0
            ],
            "title": "Custom",
            "hasBorder": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "webview_1.URL = \"slashdot.org\""
          },
          "properties": {
            "name": "button_3",
            "size": [
              141,
              33
            ],
            "position": [
              373.0,
              641.0
            ],
            "title": "Slashdot",
            "hasBorder": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "webview_1.URL = \"google.com\""
          },
          "properties": {
            "name": "button_4",
            "size": [
              141,
              33
            ],
            "position": [
              559.0,
              641.0
            ],
            "title": "Google",
            "hasBorder": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "webview_1.GoForward()"
          },
          "properties": {
            "name": "button_5",
            "size": [
              141,
              33
            ],
            "position": [
              745.0,
              641.0
            ],
            "title": "Forward",
            "hasBorder": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "card_2",
        "fillColor": "white"
      },
      "childModels": []
    }
  ],
  "CardStock_stack_format": 3,
  "CardStock_stack_version": "0.9.8"
}
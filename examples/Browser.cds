{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      887,
      680
    ],
    "can_save": false,
    "can_resize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_resize": "webview_1.size = (card.size.width-6, card.size.height-40)\ngroup_1.position = (0, webview_1.size.height+5)\ngroup_1.size = (card.size.width, 32)"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#D6D4D7"
      },
      "childModels": [
        {
          "type": "webview",
          "handlers": {
            "on_done_loading": "print(URL, did_load)\n",
            "on_card_stock_link": "if message == \"alert\":\n   alert(\"Beep!\")\nelif message == \"red\":\n   card.fill_color='red'\nelif message == \"white\":\n   card.fill_color='white'"
          },
          "properties": {
            "name": "webview_1",
            "size": [
              887,
              640
            ],
            "position": [
              0.0,
              0.0
            ],
            "URL": "",
            "HTML": "",
            "allowed_hosts": []
          }
        },
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "group_1",
            "size": [
              883,
              32
            ],
            "position": [
              3.0,
              645.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "button",
              "handlers": {
                "on_click": "webview_1.go_back()"
              },
              "properties": {
                "name": "button_1",
                "size": [
                  141,
                  33
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "title": "Back",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "webview_1.HTML = \"\"\"\nThis should do a thing: \n<a href=\"cardstock:alert\">alert</a><br/>\nSet background color: \n<a href=\"cardstock:red\">Red</a> |\n<a href=\"cardstock:white\">White</a>\n<br/>\n\"\"\"\n"
              },
              "properties": {
                "name": "button_2",
                "size": [
                  141,
                  33
                ],
                "position": [
                  185.0,
                  0.0
                ],
                "title": "Custom",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "webview_1.URL = \"slashdot.org\""
              },
              "properties": {
                "name": "button_3",
                "size": [
                  141,
                  33
                ],
                "position": [
                  371.0,
                  0.0
                ],
                "title": "Slashdot",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "webview_1.URL = \"google.com\""
              },
              "properties": {
                "name": "button_4",
                "size": [
                  141,
                  33
                ],
                "position": [
                  557.0,
                  0.0
                ],
                "title": "Google",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "webview_1.go_forward()"
              },
              "properties": {
                "name": "button_5",
                "size": [
                  141,
                  33
                ],
                "position": [
                  743.0,
                  0.0
                ],
                "title": "Forward",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            }
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
      "childModels": []
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
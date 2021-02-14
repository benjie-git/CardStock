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
        "OnSetup": "pieces = []\n\ndef Reset():\n   global cells, player, moves, pieces\n   cells = [\"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\"]\n   player = 'X'\n   moves = 0\n   for p in pieces:\n      p.Delete()\n   pieces = []\n\ndef CheckBoard():\n   # Test across\n   if cells[0]+cells[1]+cells[2] in [\"XXX\", \"OOO\"]:\n      return cells[0]\n   if cells[3]+cells[4]+cells[5] in [\"XXX\", \"OOO\"]:\n      return cells[3]\n   if cells[6]+cells[7]+cells[8] in [\"XXX\", \"OOO\"]:\n      return cells[6]\n   \n   # Test down\n   if cells[0]+cells[3]+cells[6] in [\"XXX\", \"OOO\"]:\n      return cells[0]\n   if cells[1]+cells[4]+cells[7] in [\"XXX\", \"OOO\"]:\n      return cells[1]\n   if cells[2]+cells[5]+cells[8] in [\"XXX\", \"OOO\"]:\n      return cells[2]\n\n   # Test diagonals\n   if cells[0]+cells[4]+cells[8] in [\"XXX\", \"OOO\"]:\n      return cells[0]\n   if cells[2]+cells[4]+cells[6] in [\"XXX\", \"OOO\"]:\n      return cells[2]\n   \n   # No wins yet\n   return None",
        "OnShowCard": "x.Hide()\no.Hide()\n\nbuttons = [button_1, button_2, button_3,\n          button_4, button_5, button_6, \n          button_7, button_8, button_9]\n\nReset()\n",
        "OnMessage": "cellIndex = int(message) - 1\n\nif cells[cellIndex] == \"\":\n   marker = x.Clone() if (player == 'X') else o.Clone()\n   marker.center = buttons[cellIndex].center\n   pieces.append(marker)\n   cells[cellIndex] = player\n   moves += 1\n   \n   winner = CheckBoard()\n   if winner == 'X':\n      Alert(\"X Wins!\")\n      Reset()\n   elif winner == 'O':\n      Alert(\"O Wins!\")\n      Reset()\n   elif moves == 9:\n      Alert(\"It's a Tie!\")\n      Reset()\n   else:\n      player = 'X' if (player == 'O') else 'O'\n\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              390,
              20
            ],
            "position": [
              54.0,
              188.0
            ],
            "originalSize": [
              395,
              20
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              395.0,
              0.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              390,
              20
            ],
            "position": [
              54.0,
              328.0
            ],
            "originalSize": [
              395,
              20
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              395.0,
              0.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              20,
              390
            ],
            "position": [
              174.0,
              63.0
            ],
            "originalSize": [
              20,
              339
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              0.0,
              339.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_4",
            "size": [
              20,
              390
            ],
            "position": [
              319.0,
              63.0
            ],
            "originalSize": [
              20,
              339
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              0.0,
              339.0
            ]
          ]
        },
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "x",
            "size": [
              76,
              78
            ],
            "position": [
              74.0,
              10.0
            ]
          },
          "childModels": [
            {
              "type": "line",
              "handlers": {},
              "properties": {
                "name": "shape_6",
                "size": [
                  76,
                  76
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  76,
                  76
                ],
                "penColor": "#000000",
                "penThickness": 4
              },
              "points": [
                [
                  0.0,
                  0.0
                ],
                [
                  76.0,
                  76.0
                ]
              ]
            },
            {
              "type": "line",
              "handlers": {},
              "properties": {
                "name": "shape_7",
                "size": [
                  76,
                  78
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  75,
                  73
                ],
                "penColor": "#000000",
                "penThickness": 4
              },
              "points": [
                [
                  75.0,
                  0.0
                ],
                [
                  0.0,
                  73.0
                ]
              ]
            }
          ]
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "o",
            "size": [
              69,
              69
            ],
            "position": [
              17.0,
              13.0
            ],
            "originalSize": [
              69,
              69
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              69.0,
              69.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(1)"
          },
          "properties": {
            "name": "button_1",
            "size": [
              131,
              123
            ],
            "position": [
              41.0,
              62.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(2)"
          },
          "properties": {
            "name": "button_2",
            "size": [
              139,
              128
            ],
            "position": [
              177.0,
              58.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(3)"
          },
          "properties": {
            "name": "button_3",
            "size": [
              139,
              128
            ],
            "position": [
              322.0,
              58.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(4)"
          },
          "properties": {
            "name": "button_4",
            "size": [
              139,
              135
            ],
            "position": [
              32.0,
              191.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(5)"
          },
          "properties": {
            "name": "button_5",
            "size": [
              139,
              135
            ],
            "position": [
              177.0,
              191.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(6)"
          },
          "properties": {
            "name": "button_6",
            "size": [
              139,
              135
            ],
            "position": [
              320.0,
              191.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(7)"
          },
          "properties": {
            "name": "button_7",
            "size": [
              139,
              135
            ],
            "position": [
              33.0,
              331.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(8)"
          },
          "properties": {
            "name": "button_8",
            "size": [
              139,
              135
            ],
            "position": [
              177.0,
              331.0
            ],
            "title": "",
            "border": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.SendMessage(9)"
          },
          "properties": {
            "name": "button_9",
            "size": [
              139,
              135
            ],
            "position": [
              322.0,
              331.0
            ],
            "title": "",
            "border": false
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.7"
}
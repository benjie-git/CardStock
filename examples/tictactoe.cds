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
        "OnShowCard": "x.Hide()\no.Hide()\n\nbuttons = [cell_1, cell_2, cell_3,\n          cell_4, cell_5, cell_6, \n          cell_7, cell_8, cell_9]\n\nReset()\n",
        "OnMessage": "cellIndex = int(message) - 1\n\nif cells[cellIndex] == \"\":\n   marker = x.Clone() if (player == 'X') else o.Clone()\n   marker.center = buttons[cellIndex].center\n   pieces.append(marker)\n   cells[cellIndex] = player\n   moves += 1\n   \n   winner = CheckBoard()\n   if winner == 'X':\n      Alert(\"X Wins!\")\n      Reset()\n   elif winner == 'O':\n      Alert(\"O Wins!\")\n      Reset()\n   elif moves == 9:\n      Alert(\"It's a Tie!\")\n      Reset()\n   else:\n      player = 'X' if (player == 'O') else 'O'\n\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(9)"
          },
          "properties": {
            "name": "cell_9",
            "size": [
              127,
              125
            ],
            "position": [
              326.0,
              335.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(8)"
          },
          "properties": {
            "name": "cell_8",
            "size": [
              127,
              125
            ],
            "position": [
              184.0,
              335.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(7)"
          },
          "properties": {
            "name": "cell_7",
            "size": [
              127,
              125
            ],
            "position": [
              44.0,
              335.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(6)"
          },
          "properties": {
            "name": "cell_6",
            "size": [
              127,
              125
            ],
            "position": [
              325.0,
              196.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(5)"
          },
          "properties": {
            "name": "cell_5",
            "size": [
              127,
              125
            ],
            "position": [
              184.0,
              197.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(4)"
          },
          "properties": {
            "name": "cell_4",
            "size": [
              127,
              125
            ],
            "position": [
              44.0,
              196.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(3)"
          },
          "properties": {
            "name": "cell_3",
            "size": [
              127,
              125
            ],
            "position": [
              325.0,
              59.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(2)"
          },
          "properties": {
            "name": "cell_2",
            "size": [
              137,
              123
            ],
            "position": [
              180.0,
              60.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "OnMouseDown": "card.SendMessage(1)"
          },
          "properties": {
            "name": "cell_1",
            "size": [
              127,
              125
            ],
            "position": [
              46.0,
              60.0
            ],
            "originalSize": [
              127,
              125
            ],
            "penColor": "white",
            "penThickness": 0,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              127.0,
              125.0
            ]
          ]
        },
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.7"
}
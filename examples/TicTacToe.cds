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
        "on_setup": "x.hide()\no.hide()\n\nbuttons = [cell_1, cell_2, cell_3,\n          cell_4, cell_5, cell_6, \n          cell_7, cell_8, cell_9]\n\npieces = []\n\ndef Reset():\n   global cells, player, moves, pieces\n   cells = [\"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\", \"\"]\n   player = 'X'\n   moves = 0\n   for p in pieces:\n      p.delete()\n   pieces = []\n\n# Test for a win, and return None (no win), or \"X\" or \"O\" for a win for that player\ndef CheckBoard():\n   # Test across\n   if cells[0]+cells[1]+cells[2] in [\"XXX\", \"OOO\"]:\n      return cells[0]\n   if cells[3]+cells[4]+cells[5] in [\"XXX\", \"OOO\"]:\n      return cells[3]\n   if cells[6]+cells[7]+cells[8] in [\"XXX\", \"OOO\"]:\n      return cells[6]\n   \n   # Test down\n   if cells[0]+cells[3]+cells[6] in [\"XXX\", \"OOO\"]:\n      return cells[0]\n   if cells[1]+cells[4]+cells[7] in [\"XXX\", \"OOO\"]:\n      return cells[1]\n   if cells[2]+cells[5]+cells[8] in [\"XXX\", \"OOO\"]:\n      return cells[2]\n\n   # Test diagonals\n   if cells[0]+cells[4]+cells[8] in [\"XXX\", \"OOO\"]:\n      return cells[0]\n   if cells[2]+cells[4]+cells[6] in [\"XXX\", \"OOO\"]:\n      return cells[2]\n   \n   # No wins yet\n   return None\n\nReset()",
        "on_message": "cellIndex = int(message) - 1\n\nif cells[cellIndex] == \"\":\n   # This cell is open\n   marker = x.clone() if player == 'X' else o.clone()\n   marker.center = buttons[cellIndex].center\n   marker.show()\n   pieces.append(marker)\n   cells[cellIndex] = player\n   moves += 1\n   \n   winner = CheckBoard()\n   if winner == 'X':\n      alert(\"X Wins!\")\n      Reset()\n   elif winner == 'O':\n      alert(\"O Wins!\")\n      Reset()\n   elif moves == 9:\n      alert(\"It's a Tie!\")\n      Reset()\n   else:\n      player = 'X' if (player == 'O') else 'O'\n\n"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {
            "on_mouse_press": "card.send_message(\"9\")"
          },
          "properties": {
            "name": "cell_9",
            "size": [
              127,
              125
            ],
            "position": [
              326.0,
              40.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"8\")"
          },
          "properties": {
            "name": "cell_8",
            "size": [
              127,
              125
            ],
            "position": [
              184.0,
              40.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"7\")"
          },
          "properties": {
            "name": "cell_7",
            "size": [
              127,
              125
            ],
            "position": [
              44.0,
              40.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"6\")"
          },
          "properties": {
            "name": "cell_6",
            "size": [
              127,
              125
            ],
            "position": [
              325.0,
              179.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"5\")"
          },
          "properties": {
            "name": "cell_5",
            "size": [
              127,
              125
            ],
            "position": [
              184.0,
              178.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"4\")"
          },
          "properties": {
            "name": "cell_4",
            "size": [
              127,
              125
            ],
            "position": [
              44.0,
              179.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"3\")"
          },
          "properties": {
            "name": "cell_3",
            "size": [
              127,
              125
            ],
            "position": [
              325.0,
              316.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"2\")"
          },
          "properties": {
            "name": "cell_2",
            "size": [
              137,
              123
            ],
            "position": [
              180.0,
              317.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
            "on_mouse_press": "card.send_message(\"1\")"
          },
          "properties": {
            "name": "cell_1",
            "size": [
              127,
              125
            ],
            "position": [
              46.0,
              315.0
            ],
            "originalSize": [
              127,
              125
            ],
            "pen_color": "white",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "white"
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
              292.0
            ],
            "originalSize": [
              395,
              20
            ],
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              20.0
            ],
            [
              395.0,
              20.0
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
              152.0
            ],
            "originalSize": [
              395,
              20
            ],
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              20.0
            ],
            [
              395.0,
              20.0
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
              47.0
            ],
            "originalSize": [
              20,
              339
            ],
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              339.0
            ],
            [
              0.0,
              0.0
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
              47.0
            ],
            "originalSize": [
              20,
              339
            ],
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              339.0
            ],
            [
              0.0,
              0.0
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
              82.0,
              411.0
            ],
            "rotation": 0.0
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
                  2.0
                ],
                "originalSize": [
                  76,
                  76
                ],
                "pen_color": "#000000",
                "pen_thickness": 4,
                "rotation": 0.0
              },
              "points": [
                [
                  0.0,
                  76.0
                ],
                [
                  76.0,
                  0.0
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
                "pen_color": "#000000",
                "pen_thickness": 4,
                "rotation": 0.0
              },
              "points": [
                [
                  75.0,
                  73.0
                ],
                [
                  0.0,
                  0.0
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
              417.0
            ],
            "originalSize": [
              69,
              69
            ],
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#FFFFFF"
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
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
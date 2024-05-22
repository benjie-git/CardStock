{
  "type": "stack",
  "handlers": {},
  "properties": {
    "can_save": false,
    "author": "",
    "info": ""
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\n\nisMoving = False\nspace.hide() # hide the space piece\n\npieces = [c for c in card.children if c.name.startswith(\"group\")]\npieces.append(space)\n\norigPieces = pieces.copy()\n\ndef Shuffle():\n   # Switch each piece with a random other piece.\n   # Make one more swap so it's an even number of swaps\n   # otherwise it would be unsolvable.\n   shuffleList = list(range(len(pieces)-1))\n   shuffleList.append(randint(0,14))\n   for i in shuffleList:\n      j = i\n      while j == i:\n         # make sure we're not swapping a piece with itself\n         j = randint(0,len(pieces)-2)\n      pieces[i], pieces[j] = pieces[j], pieces[i]\n      tmp = pieces[j].position\n      pieces[j].position = pieces[i].position\n      pieces[i].position = tmp\n\ndef SlideSpots(moves):\n   # Animate sliding\n   global isMoving\n   if not isMoving:\n      tmpPieces = {}\n      tmpPositions = {}\n      for i,j in moves:\n         tmpPieces[i] = pieces[i]\n         tmpPositions[i] = pieces[i].position\n      for i,j in moves:\n         pieces[i].animate_position(0.15, tmpPositions[j], \"InOut\", DoneMoving)\n      for i,j in moves:\n         pieces[j] = tmpPieces[i]\n      isMoving = True\n\ndef DoneMoving():\n   global isMoving\n   isMoving = False\n   CheckForWin()\n\ndef CheckForWin():\n   if pieces == origPieces:\n      play_sound(\"yay.wav\")\n      wait(3)\n      Shuffle()\n\ndef BuildCycleList(start, offset, n):\n   # Create move list that moves n peices, and swaps the space piece to the other end of the list\n   spots = list(reversed([start + offset*i for i in range(n+1)]))\n   moves = []\n   for i in range(len(spots)-1):\n      moves.append((spots[i], spots[i+1]))\n   moves.append((spots[-1], spots[0]))\n   return moves\n\ndef MoveDir(dir, n):\n   # Move n pieces in direction\n   i = pieces.index(space)\n   if dir == \"Right\" and i%4 != 0:\n      SlideSpots(BuildCycleList(i, -1, n))\n   elif dir == \"Left\" and i%4 != 3:\n      SlideSpots(BuildCycleList(i, 1, n))\n   elif dir == \"Up\" and i<12:\n      SlideSpots(BuildCycleList(i, 4, n))\n   elif dir == \"Down\" and i>=4:\n      SlideSpots(BuildCycleList(i, -4, n))\n\ndef MoveFrom(obj):\n   # Slide pieces from the clicked object obj, to the space piece, if they are in the same row/col\n   global isMoving\n   s = pieces.index(space)\n   o = pieces.index(obj)\n   sx, sy = s%4, int(s/4)\n   ox, oy = o%4, int(o/4)\n   if sx == ox and sy < oy:\n      MoveDir(\"Up\", oy-sy)\n   elif sx == ox and sy > oy:\n      MoveDir(\"Down\", sy-oy)\n   elif sy == oy and sx < ox:\n      MoveDir(\"Left\", ox-sx)\n   elif sy == oy and sx > ox:\n      MoveDir(\"Right\", sx-ox)\n\n# Shuffle when we start the stack\nShuffle()",
        "on_key_press": "if key_name in [\"Left\", \"Right\", \"Up\", \"Down\"]:\n   MoveDir(key_name, 1)"
      },
      "properties": {
        "name": "card_1",
        "size": [
          455,
          455
        ],
        "fill_color": "#BBD4BF",
        "can_resize": false
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              400,
              400
            ],
            "position": [
              30.0,
              30.0
            ],
            "originalSize": [
              438,
              438
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#E7E5E8"
          },
          "points": [
            [
              0.0,
              438.0
            ],
            [
              438.0,
              0.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "space",
            "size": [
              100,
              100
            ],
            "position": [
              330.0,
              30.0
            ],
            "originalSize": [
              103,
              102
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#FFFFFF00"
          },
          "points": [
            [
              103.0,
              0.0
            ],
            [
              0.0,
              102.0
            ]
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_1",
            "size": [
              100,
              100
            ],
            "position": [
              30.0,
              330.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_1",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_1",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "1",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_2",
            "size": [
              100,
              100
            ],
            "position": [
              130.0,
              330.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_3",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_2",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "2",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_3",
            "size": [
              100,
              100
            ],
            "position": [
              230.0,
              330.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_4",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_3",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "3",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_4",
            "size": [
              100,
              100
            ],
            "position": [
              330.0,
              330.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_5",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_4",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "4",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_5",
            "size": [
              100,
              100
            ],
            "position": [
              30.0,
              230.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_6",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_5",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "5",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_6",
            "size": [
              100,
              100
            ],
            "position": [
              130.0,
              230.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_7",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_6",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "6",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_7",
            "size": [
              100,
              100
            ],
            "position": [
              230.0,
              230.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_8",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_7",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "7",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_8",
            "size": [
              100,
              100
            ],
            "position": [
              330.0,
              230.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_9",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_8",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "8",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_9",
            "size": [
              100,
              100
            ],
            "position": [
              30.0,
              130.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_10",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_9",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "9",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_10",
            "size": [
              100,
              100
            ],
            "position": [
              130.0,
              130.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_11",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_10",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "10",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_11",
            "size": [
              100,
              100
            ],
            "position": [
              230.0,
              130.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_12",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_11",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "11",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_12",
            "size": [
              100,
              100
            ],
            "position": [
              330.0,
              130.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_13",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_12",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "12",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_13",
            "size": [
              100,
              100
            ],
            "position": [
              30.0,
              30.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_14",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_13",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "13",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_14",
            "size": [
              100,
              100
            ],
            "position": [
              130.0,
              30.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_15",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_14",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "14",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "on_mouse_press": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_15",
            "size": [
              100,
              100
            ],
            "position": [
              230.0,
              30.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {},
              "properties": {
                "name": "shape_16",
                "size": [
                  100,
                  100
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  81,
                  81
                ],
                "pen_color": "black",
                "pen_style": "Solid",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white"
              },
              "points": [
                [
                  0.0,
                  81.0
                ],
                [
                  81.0,
                  0.0
                ]
              ]
            },
            {
              "type": "textlabel",
              "handlers": {},
              "properties": {
                "name": "label_15",
                "size": [
                  85,
                  83
                ],
                "position": [
                  7.0,
                  8.0
                ],
                "text": "15",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 50,
                "is_bold": false,
                "is_italic": false,
                "is_underlined": false,
                "can_auto_shrink": true,
                "rotation": 0.0
              }
            }
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 9,
  "CardStock_stack_version": "0.99.6"
}
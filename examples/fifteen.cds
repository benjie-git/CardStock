{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      455,
      455
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n\nisMoving = False\nspace.Hide() # hide the space piece\n\npieces = [c for c in card.children if c.name.startswith(\"group\")]\npieces.append(space)\n\norigPieces = pieces.copy()\n\ndef Shuffle():\n   # Switch each piece with a random other piece.\n   # Make one more swap so it's an even number of swaps\n   # otherwise it would be unsolvable.\n   shuffleList = list(range(len(pieces)-1))\n   shuffleList.append(randint(0,14))\n   for i in shuffleList:\n      j = i\n      while j == i:\n         # make sure we're not swapping a piece with itself\n         j = randint(0,len(pieces)-2)\n      pieces[i], pieces[j] = pieces[j], pieces[i]\n      tmp = pieces[j].position\n      pieces[j].position = pieces[i].position\n      pieces[i].position = tmp\n\ndef SlideSpots(moves):\n   # Animate sliding\n   global isMoving\n   if not isMoving:\n      tmpPieces = {}\n      tmpPositions = {}\n      for i,j in moves:\n         tmpPieces[i] = pieces[i]\n         tmpPositions[i] = pieces[i].position\n      for i,j in moves:\n         pieces[i].AnimatePosition(0.15, tmpPositions[j], DoneMoving)\n      for i,j in moves:\n         pieces[j] = tmpPieces[i]\n      isMoving = True\n\ndef DoneMoving():\n   global isMoving\n   isMoving = False\n\ndef CheckForWin():\n   if pieces == origPieces:\n      PlaySound(\"yay.wav\")\n      Wait(3)\n      Shuffle()\n\ndef BuildCycleList(start, offset, n):\n   # Create move list that moves n peices, and swaps the space piece to the other end of the list\n   spots = list(reversed([start + offset*i for i in range(n+1)]))\n   moves = []\n   for i in range(len(spots)-1):\n      moves.append((spots[i], spots[i+1]))\n   moves.append((spots[-1], spots[0]))\n   return moves\n\ndef MoveDir(dir, n):\n   # Move n pieces in direction\n   i = pieces.index(space)\n   if dir == \"Right\" and i%4 != 0:\n      SlideSpots(BuildCycleList(i, -1, n))\n   elif dir == \"Left\" and i%4 != 3:\n      SlideSpots(BuildCycleList(i, 1, n))\n   elif dir == \"Up\" and i<12:\n      SlideSpots(BuildCycleList(i, 4, n))\n   elif dir == \"Down\" and i>=4:\n      SlideSpots(BuildCycleList(i, -4, n))\n   CheckForWin()\n\ndef MoveFrom(obj):\n   # Slide pieces from the clicked object obj, to the space piece, if they are in the same row/col\n   global isMoving\n   s = pieces.index(space)\n   o = pieces.index(obj)\n   sx, sy = s%4, int(s/4)\n   ox, oy = o%4, int(o/4)\n   if sx == ox and sy < oy:\n      MoveDir(\"Up\", oy-sy)\n   elif sx == ox and sy > oy:\n      MoveDir(\"Down\", sy-oy)\n   elif sy == oy and sx < ox:\n      MoveDir(\"Left\", ox-sx)\n   elif sy == oy and sx > ox:\n      MoveDir(\"Right\", sx-ox)\n\n# Shuffle when we start the stack\nShuffle()",
        "OnKeyDown": "if keyName in [\"Left\", \"Right\", \"Up\", \"Down\"]:\n   MoveDir(keyName, 1)"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#BBD4BF"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              394,
              394
            ],
            "position": [
              31.0,
              31.0
            ],
            "originalSize": [
              438,
              438
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "#E7E5E8"
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
              325.0,
              31.0
            ],
            "originalSize": [
              103,
              102
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "#FFFFFF00"
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
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_1",
            "size": [
              100,
              100
            ],
            "position": [
              31.0,
              325.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_2",
            "size": [
              100,
              100
            ],
            "position": [
              129.0,
              325.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_3",
            "size": [
              100,
              100
            ],
            "position": [
              227.0,
              325.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_4",
            "size": [
              100,
              100
            ],
            "position": [
              325.0,
              325.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_5",
            "size": [
              100,
              100
            ],
            "position": [
              31.0,
              227.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_6",
            "size": [
              100,
              100
            ],
            "position": [
              129.0,
              227.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_7",
            "size": [
              100,
              100
            ],
            "position": [
              227.0,
              227.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_8",
            "size": [
              100,
              100
            ],
            "position": [
              325.0,
              227.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_9",
            "size": [
              100,
              100
            ],
            "position": [
              31.0,
              129.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_10",
            "size": [
              100,
              100
            ],
            "position": [
              129.0,
              129.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_11",
            "size": [
              100,
              100
            ],
            "position": [
              227.0,
              129.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_12",
            "size": [
              100,
              100
            ],
            "position": [
              325.0,
              129.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_13",
            "size": [
              100,
              100
            ],
            "position": [
              31.0,
              31.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_14",
            "size": [
              100,
              100
            ],
            "position": [
              129.0,
              31.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        },
        {
          "type": "group",
          "handlers": {
            "OnMouseDown": "MoveFrom(self)"
          },
          "properties": {
            "name": "group_15",
            "size": [
              100,
              100
            ],
            "position": [
              227.0,
              31.0
            ]
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
                "penColor": "black",
                "penThickness": 4,
                "fillColor": "white"
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
                "textColor": "black",
                "font": "Default",
                "fontSize": 50
              }
            }
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9.2"
}
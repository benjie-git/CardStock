{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      455,
      455
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n\nisMoving = False\nspace.Hide() # hide the space piece\n\npieces = [c for c in card.children if c.name.startswith(\"group\")]\npieces.append(space)\n\norigPieces = pieces.copy()\n\ndef Shuffle():\n   # Switch each piece with a random other piece.\n   # Make one more swap so it's an even number of swaps\n   # otherwise it would be unsolvable.\n   shuffleList = list(range(len(pieces)-1))\n   shuffleList.append(randint(0,14))\n   for i in shuffleList:\n      j = i\n      while j == i:\n         # make sure we're not swapping a piece with itself\n         j = randint(0,len(pieces)-2)\n      pieces[i], pieces[j] = pieces[j], pieces[i]\n      tmp = pieces[j].position\n      pieces[j].position = pieces[i].position\n      pieces[i].position = tmp\n\ndef SwapSpots(i, j):\n   # Animate swapping a piece with the space piece\n   global isMoving\n   if not isMoving:\n      pieces[i], pieces[j] = pieces[j], pieces[i]\n      isMoving = True\n      pieces[i].AnimatePosition(0.15, pieces[j].position)\n      pieces[j].AnimatePosition(0.15, pieces[i].position, DoneMoving)\n\ndef DoneMoving():\n   global isMoving\n   isMoving = False\n\ndef CheckForWin():\n   if pieces == origPieces:\n      SoundPlay(\"yay.wav\")\n      Wait(3)\n      Shuffle()\n   \ndef MoveDir(dir):\n   i = pieces.index(space)\n   if dir == \"Right\" and i%4 != 0:\n      SwapSpots(i, i-1)\n   elif dir == \"Left\" and i%4 != 3:\n      SwapSpots(i, i+1)\n   elif dir == \"Up\" and i<12:\n      SwapSpots(i, i+4)\n   elif dir == \"Down\" and i>=4:\n      SwapSpots(i, i-4)\n   CheckForWin()\n\ndef MoveFrom(obj):\n   global isMoving\n   i = pieces.index(space)\n   j = pieces.index(obj)\n   diff = j-i\n   if diff == 4:\n      MoveDir(\"Up\")\n   elif diff == -4:\n      MoveDir(\"Down\")\n   elif diff == 1:\n      MoveDir(\"Left\")\n   elif diff == -1:\n      MoveDir(\"Right\")\n\n# Shuffle when we start the stack\nShuffle()",
        "OnKeyDown": "if keyName in [\"Left\", \"Right\", \"Up\", \"Down\"]:\n   MoveDir(keyName)"
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
              34.0,
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
              34.0,
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
              132.0,
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
              230.0,
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
              328.0,
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
              34.0,
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
              132.0,
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
              230.0,
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
              328.0,
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
              34.0,
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
              132.0,
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
              230.0,
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
              328.0,
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
              34.0,
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
              132.0,
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
              230.0,
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
              328.0,
              31.0
            ],
            "originalSize": [
              103,
              102
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9"
}
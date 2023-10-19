{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      757,
      493
    ],
    "can_save": true,
    "can_resize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "points = None\npos = None\nrot = None\nisPenDown = True\n\n# Define LOGO functions\n\ndef pd(): # Pen Down\n   global points\n   global isPenDown\n   isPenDown = True\n   if len(points[-1]) > 0:\n      points.append([Point(*pos)])\n   else:\n      points[-1].append(Point(*pos))\n\ndef pu():  # Pen Up\n   global isPenDown\n   isPenDown = False\n   if len(points[-1]) == 1:\n      del points[-1][0]\n\ndef fd(dist):  # ForwarD\n   global pos\n   global rot\n   global points\n   global isPenDown\n   pos += rotate_point((0, dist), rot)\n   if isPenDown:\n      points[-1].append(Point(*pos))\n\ndef bk(dist):  # BacK\n   fd(-dist)\n\ndef home():  # Go back home\n   global pos\n   global rot\n   global points\n   global isPenDown\n   pos = Point(code.size.width + (card.size.width - code.size.width)/2,\n         card.size.height/2)\n   rot = 0\n   if isPenDown:\n      points[-1].append(pos)\n\ndef rt(angle):  # rotate RighT\n   global rot\n   rot = (rot + angle) % 360\n\ndef lt(angle):  # rotate LefT\n   rt(-angle)\n\nenv = {\"pd\":pd, \"pu\":pu, \"fd\":fd, \"bk\":bk, \n       \"rt\":rt, \"lt\":lt, \"home\":home}\n\ndef run_logo(text):\n   global points\n   global cVars\n   \n   clear.click()\n   points = [[]]\n   isPenDown = True\n   home()\n\n   exec(text, env)\n   \n   lines = []\n   # Build a multipoint line for each pen-down stretch\n   for l in points:\n      # Start lines off hidden, to avoid flickering\n      newLine = card.add_line(l, \"output_line\", is_visible=False)\n      newLine.pen_thickness = 1\n      lines.append(newLine)\n      newLine.order_to_back()\n   \n   # Group multiple lines\n   if len(lines) > 1:\n      output_group = card.add_group(lines, \"output_group\")\n      output_group.order_to_back()\n   \n   # Show all lines now that we're done\n   for line in lines:\n      line.is_visible = True\n\ndef clear_logo():\n   # Delete old lines\n   for obj in card.children:\n      if obj.name.startswith(\"output\"):\n         obj.delete()\n\ndef ShowHelp():\n   alert(\n      \"Logo Commands:\\n\\n\"\n      \"pu() - Pen Up\\n\"\n      \"pd() - Pen Down\\n\"\n      \"fd(x) - Move Forward X pixels\\n\"\n      \"bk(x) - Move Backwards X pixels\\n\"\n      \"rt(x) - Rotate Right X degrees\\n\"\n      \"lt(x) - Rotate Left X degrees\\n\"\n      \"home() - Move to the center, pointing right\"\n      )\n",
        "on_resize": "header_group.position.y = card.size.height - header_group.size.height\ncode.size.height = card.size.height - header_group.size.height"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "header_group",
            "size": [
              248,
              51
            ],
            "position": [
              2.0,
              440.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_previous_card()"
              },
              "properties": {
                "name": "prev",
                "size": [
                  35,
                  22
                ],
                "position": [
                  0.0,
                  27.0
                ],
                "title": "<",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_next_card()"
              },
              "properties": {
                "name": "next",
                "size": [
                  35,
                  22
                ],
                "position": [
                  212.0,
                  27.0
                ],
                "title": ">",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "c = card.clone()\nc.set_code_for_event(\"on_setup\", \"\")\ngoto_card(c.name)"
              },
              "properties": {
                "name": "new",
                "size": [
                  60,
                  22
                ],
                "position": [
                  1.0,
                  0.0
                ],
                "title": "New",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "textfield",
              "handlers": {},
              "properties": {
                "name": "title",
                "size": [
                  167,
                  25
                ],
                "position": [
                  40.0,
                  26.0
                ],
                "text": "Square",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 12,
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
                "on_click": "run_logo(code.text)"
              },
              "properties": {
                "name": "run",
                "size": [
                  60,
                  21
                ],
                "position": [
                  188.0,
                  1.0
                ],
                "title": "Run",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "ShowHelp()"
              },
              "properties": {
                "name": "help",
                "size": [
                  41,
                  21
                ],
                "position": [
                  139.0,
                  1.0
                ],
                "title": "?",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "clear_logo()"
              },
              "properties": {
                "name": "clear",
                "size": [
                  60,
                  21
                ],
                "position": [
                  71.0,
                  1.0
                ],
                "title": "Clear",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "code",
            "size": [
              250,
              437
            ],
            "position": [
              0.0,
              0.0
            ],
            "text": "for _ in range(4):\n   fd(100)\n   rt(90)\n",
            "alignment": "Left",
            "text_color": "black",
            "font": "Mono",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_resize": "header_group.position.y = card.size.height - header_group.size.height\ncode.size.height = card.size.height - header_group.size.height"
      },
      "properties": {
        "name": "card_2",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "header_group",
            "size": [
              248,
              51
            ],
            "position": [
              2.0,
              440.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_previous_card()"
              },
              "properties": {
                "name": "prev",
                "size": [
                  35,
                  22
                ],
                "position": [
                  0.0,
                  27.0
                ],
                "title": "<",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_next_card()"
              },
              "properties": {
                "name": "next",
                "size": [
                  35,
                  22
                ],
                "position": [
                  212.0,
                  27.0
                ],
                "title": ">",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "c = card.clone()\ngoto_card(c.name)"
              },
              "properties": {
                "name": "new",
                "size": [
                  60,
                  22
                ],
                "position": [
                  1.0,
                  0.0
                ],
                "title": "New",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "textfield",
              "handlers": {},
              "properties": {
                "name": "title",
                "size": [
                  167,
                  25
                ],
                "position": [
                  40.0,
                  26.0
                ],
                "text": "Squares",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 12,
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
                "on_click": "run_logo(code.text)"
              },
              "properties": {
                "name": "run",
                "size": [
                  60,
                  21
                ],
                "position": [
                  188.0,
                  1.0
                ],
                "title": "Run",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "ShowHelp()"
              },
              "properties": {
                "name": "help",
                "size": [
                  41,
                  21
                ],
                "position": [
                  139.0,
                  1.0
                ],
                "title": "?",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "clear_logo()"
              },
              "properties": {
                "name": "clear",
                "size": [
                  60,
                  21
                ],
                "position": [
                  71.0,
                  1.0
                ],
                "title": "Clear",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "code",
            "size": [
              250,
              437
            ],
            "position": [
              0.0,
              0.0
            ],
            "text": "pu()\nrt(45)\nbk(300)\nlt(45)\npd()\n\nfor _ in range(4):\n   pu()\n   rt(45)\n   fd(80)\n   lt(45)\n   pd()\n\n   for _ in range(4):\n      fd(100)\n      rt(90)\n",
            "alignment": "Left",
            "text_color": "black",
            "font": "Mono",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_resize": "header_group.position.y = card.size.height - header_group.size.height\ncode.size.height = card.size.height - header_group.size.height"
      },
      "properties": {
        "name": "card_3",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "header_group",
            "size": [
              248,
              51
            ],
            "position": [
              2.0,
              440.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_previous_card()"
              },
              "properties": {
                "name": "prev",
                "size": [
                  35,
                  22
                ],
                "position": [
                  0.0,
                  27.0
                ],
                "title": "<",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_next_card()"
              },
              "properties": {
                "name": "next",
                "size": [
                  35,
                  22
                ],
                "position": [
                  212.0,
                  27.0
                ],
                "title": ">",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "c = card.clone()\ngoto_card(c.name)"
              },
              "properties": {
                "name": "new",
                "size": [
                  60,
                  22
                ],
                "position": [
                  1.0,
                  0.0
                ],
                "title": "New",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "textfield",
              "handlers": {},
              "properties": {
                "name": "title",
                "size": [
                  167,
                  25
                ],
                "position": [
                  40.0,
                  26.0
                ],
                "text": "Circle",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 12,
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
                "on_click": "clear_logo()"
              },
              "properties": {
                "name": "clear",
                "size": [
                  60,
                  21
                ],
                "position": [
                  71.0,
                  1.0
                ],
                "title": "Clear",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "ShowHelp()"
              },
              "properties": {
                "name": "help",
                "size": [
                  41,
                  21
                ],
                "position": [
                  139.0,
                  1.0
                ],
                "title": "?",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "run_logo(code.text)"
              },
              "properties": {
                "name": "run",
                "size": [
                  60,
                  21
                ],
                "position": [
                  188.0,
                  1.0
                ],
                "title": "Run",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "code",
            "size": [
              250,
              437
            ],
            "position": [
              0.0,
              0.0
            ],
            "text": "pu()\nbk(180)\nlt(90)\npd()\n\nfor _ in range(360):\n   fd(3)\n   rt(1)\n",
            "alignment": "Left",
            "text_color": "black",
            "font": "Mono",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_resize": "header_group.position.y = card.size.height - header_group.size.height\ncode.size.height = card.size.height - header_group.size.height"
      },
      "properties": {
        "name": "card_4",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "header_group",
            "size": [
              248,
              51
            ],
            "position": [
              2.0,
              440.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_previous_card()"
              },
              "properties": {
                "name": "prev",
                "size": [
                  35,
                  22
                ],
                "position": [
                  0.0,
                  27.0
                ],
                "title": "<",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_next_card()"
              },
              "properties": {
                "name": "next",
                "size": [
                  35,
                  22
                ],
                "position": [
                  212.0,
                  27.0
                ],
                "title": ">",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "c = card.clone()\ngoto_card(c.name)"
              },
              "properties": {
                "name": "new",
                "size": [
                  60,
                  22
                ],
                "position": [
                  1.0,
                  0.0
                ],
                "title": "New",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "textfield",
              "handlers": {},
              "properties": {
                "name": "title",
                "size": [
                  167,
                  25
                ],
                "position": [
                  40.0,
                  26.0
                ],
                "text": "Star",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 12,
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
                "on_click": "clear_logo()"
              },
              "properties": {
                "name": "clear",
                "size": [
                  60,
                  21
                ],
                "position": [
                  71.0,
                  1.0
                ],
                "title": "Clear",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "ShowHelp()"
              },
              "properties": {
                "name": "help",
                "size": [
                  41,
                  21
                ],
                "position": [
                  139.0,
                  1.0
                ],
                "title": "?",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "run_logo(code.text)"
              },
              "properties": {
                "name": "run",
                "size": [
                  60,
                  21
                ],
                "position": [
                  188.0,
                  1.0
                ],
                "title": "Run",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "code",
            "size": [
              250,
              437
            ],
            "position": [
              0.0,
              0.0
            ],
            "text": "pu()\nrt(20)\nbk(170)\nlt(20)\npd()\n\nfor _ in range(5):\n   fd(300)\n   rt(180-(180/5))\n",
            "alignment": "Left",
            "text_color": "black",
            "font": "Mono",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_resize": "header_group.position.y = card.size.height - header_group.size.height\ncode.size.height = card.size.height - header_group.size.height"
      },
      "properties": {
        "name": "card_5",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "header_group",
            "size": [
              248,
              51
            ],
            "position": [
              2.0,
              440.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_previous_card()"
              },
              "properties": {
                "name": "prev",
                "size": [
                  35,
                  22
                ],
                "position": [
                  0.0,
                  27.0
                ],
                "title": "<",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "goto_next_card()"
              },
              "properties": {
                "name": "next",
                "size": [
                  35,
                  22
                ],
                "position": [
                  212.0,
                  27.0
                ],
                "title": ">",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "c = card.clone()\ngoto_card(c.name)"
              },
              "properties": {
                "name": "new",
                "size": [
                  60,
                  22
                ],
                "position": [
                  1.0,
                  0.0
                ],
                "title": "New",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "textfield",
              "handlers": {},
              "properties": {
                "name": "title",
                "size": [
                  167,
                  25
                ],
                "position": [
                  40.0,
                  26.0
                ],
                "text": "Moire",
                "alignment": "Center",
                "text_color": "black",
                "font": "Default",
                "font_size": 12,
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
                "on_click": "clear_logo()"
              },
              "properties": {
                "name": "clear",
                "size": [
                  60,
                  21
                ],
                "position": [
                  71.0,
                  1.0
                ],
                "title": "Clear",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "ShowHelp()"
              },
              "properties": {
                "name": "help",
                "size": [
                  41,
                  21
                ],
                "position": [
                  139.0,
                  1.0
                ],
                "title": "?",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            },
            {
              "type": "button",
              "handlers": {
                "on_click": "run_logo(code.text)"
              },
              "properties": {
                "name": "run",
                "size": [
                  60,
                  21
                ],
                "position": [
                  188.0,
                  1.0
                ],
                "title": "Run",
                "style": "Border",
                "is_selected": false,
                "rotation": 0.0
              }
            }
          ]
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "code",
            "size": [
              250,
              437
            ],
            "position": [
              0.0,
              0.0
            ],
            "text": "pu()\nd = 450\nbk(d/2)\npd()\n\nfor _ in range(180):\n   fd(d)\n   rt(178)\n",
            "alignment": "Left",
            "text_color": "black",
            "font": "Mono",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 7,
  "CardStock_stack_version": "0.99.4"
}
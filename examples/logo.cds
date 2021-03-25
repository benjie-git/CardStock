{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      757,
      493
    ],
    "canSave": true,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "import math\nhomePos = None\npoints = None\npos = None\nrot = None\nisPenDown = True\n\ndef pd():\n   global points\n   global isPenDown\n   isPenDown = True\n   if len(points[-1]) > 0:\n      points.append([pos.copy()])\n   else:\n      points[-1].append(pos.copy())\n\ndef pu():\n   global isPenDown\n   isPenDown = False\n   if len(points[-1]) == 1:\n      del points[-1][0]\n\ndef fd(dist):\n   global pos\n   global rot\n   global points\n   global isPenDown\n   pos = [pos[0]+math.cos(math.radians(rot))*dist,\n         pos[1]+math.sin(math.radians(rot))*dist]\n   if isPenDown:\n      points[-1].append(pos.copy())\n\ndef bk(dist):\n   fd(-dist)\n\ndef home():\n   global pos\n   global rot\n   global points\n   global isPenDown\n   pos = [code.size.width + (card.size.width - code.size.width)/2,\n         card.size.height/2]\n   rot = 0\n   if isPenDown:\n      points[-1].append(pos.copy())\n\ndef rt(angle):\n   global rot\n   rot = (rot + angle) % 360\n\ndef lt(angle):\n   rt(-angle)\n\ndef run_logo(text):\n   global points\n   \n   clear.Click()\n   points = [[]]\n   isPenDown = True\n   home()\n\n   exec(text)\n   \n   lines = []\n   for l in points:\n      newLine = card.AddLine(l, \"output_line\")\n      newLine.penThickness = 1\n      lines.append(newLine)\n   if len(lines) > 1:\n      card.AddGroup(lines, \"output\")\n",
        "OnShowCard": "code.size.height = card.size.height - code.position.y",
        "OnResize": "code.size.height = card.size.height - code.position.y"
      },
      "properties": {
        "name": "card_3",
        "bgColor": "white"
      },
      "childModels": [
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
              56.0
            ],
            "text": "for _ in range(4):\n  for _ in range(4):\n    fd(100)\n    rt(90)\n",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": 12,
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "prev",
            "size": [
              35,
              22
            ],
            "position": [
              2.0,
              4.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "next",
            "size": [
              35,
              22
            ],
            "position": [
              214.0,
              4.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "c = card.Clone()\nGotoCard(c.name)"
          },
          "properties": {
            "name": "new",
            "size": [
              60,
              22
            ],
            "position": [
              3.0,
              31.0
            ],
            "title": "New",
            "border": true
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
              42.0,
              2.0
            ],
            "text": "Square",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "run_logo(code.text)"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              32.0
            ],
            "title": "Run",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "for obj in card.children:\n   if obj.name.startswith(\"output\"):\n      obj.Delete()\n"
          },
          "properties": {
            "name": "clear",
            "size": [
              60,
              21
            ],
            "position": [
              93.0,
              31.0
            ],
            "title": "Clear",
            "border": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnSetup": "import math\nhomePos = None\npoints = None\npos = None\nrot = None\nisPenDown = True\n\ndef pd():\n   global points\n   global isPenDown\n   isPenDown = True\n   if len(points[-1]) > 0:\n      points.append([pos.copy()])\n   else:\n      points[-1].append(pos.copy())\n\ndef pu():\n   global isPenDown\n   isPenDown = False\n   if len(points[-1]) == 1:\n      del points[-1][0]\n\ndef fd(dist):\n   global pos\n   global rot\n   global points\n   global isPenDown\n   pos = [pos[0]+math.cos(math.radians(rot))*dist,\n         pos[1]+math.sin(math.radians(rot))*dist]\n   if isPenDown:\n      points[-1].append(pos.copy())\n\ndef bk(dist):\n   fd(-dist)\n\ndef home():\n   global pos\n   global rot\n   global points\n   global isPenDown\n   pos = [code.size.width + (card.size.width - code.size.width)/2,\n         card.size.height/2]\n   rot = 0\n   if isPenDown:\n      points[-1].append(pos.copy())\n\ndef rt(angle):\n   global rot\n   rot = (rot + angle) % 360\n\ndef lt(angle):\n   rt(-angle)\n\ndef run_logo(text):\n   global points\n   \n   clear.Click()\n   points = [[]]\n   isPenDown = True\n   home()\n\n   exec(text)\n   \n   lines = []\n   for l in points:\n      newLine = card.AddLine(l, \"output_line\")\n      newLine.penThickness = 1\n      lines.append(newLine)\n   if len(lines) > 1:\n      card.AddGroup(lines, \"output\")\n",
        "OnShowCard": "code.size.height = card.size.height - code.position.y",
        "OnResize": "code.size.height = card.size.height - code.position.y"
      },
      "properties": {
        "name": "card_5",
        "bgColor": "white"
      },
      "childModels": [
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
              56.0
            ],
            "text": "pu()\nrt(45)\nbk(300)\nlt(45)\npd()\n\nfor _ in range(4):\n  pu()\n  rt(45)\n  fd(80)\n  lt(45)\n  pd()\n\n  for _ in range(4):\n    fd(100)\n    rt(90)\n",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": 12,
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "prev",
            "size": [
              35,
              22
            ],
            "position": [
              2.0,
              4.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "next",
            "size": [
              35,
              22
            ],
            "position": [
              214.0,
              4.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "c = card.Clone()\nGotoCard(c.name)"
          },
          "properties": {
            "name": "new",
            "size": [
              60,
              22
            ],
            "position": [
              3.0,
              31.0
            ],
            "title": "New",
            "border": true
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
              42.0,
              2.0
            ],
            "text": "Squares",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "run_logo(code.text)"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              32.0
            ],
            "title": "Run",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "for obj in card.children:\n   if obj.name.startswith(\"output\"):\n      obj.Delete()\n"
          },
          "properties": {
            "name": "clear",
            "size": [
              60,
              21
            ],
            "position": [
              93.0,
              31.0
            ],
            "title": "Clear",
            "border": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "code.size.height = card.size.height - code.position.y",
        "OnResize": "code.size.height = card.size.height - code.position.y"
      },
      "properties": {
        "name": "card_4",
        "bgColor": "white"
      },
      "childModels": [
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
              56.0
            ],
            "text": "pu()\nbk(180)\nlt(90)\npd()\n\nfor _ in range(360):\n  fd(3)\n  rt(1)\n",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": 12,
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "prev",
            "size": [
              35,
              22
            ],
            "position": [
              2.0,
              4.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "next",
            "size": [
              35,
              22
            ],
            "position": [
              214.0,
              4.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "c = card.Clone()\nGotoCard(c.name)"
          },
          "properties": {
            "name": "new",
            "size": [
              60,
              22
            ],
            "position": [
              3.0,
              31.0
            ],
            "title": "New",
            "border": true
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
              42.0,
              2.0
            ],
            "text": "Circle",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "for obj in card.children:\n   if obj.name.startswith(\"output\"):\n      obj.Delete()\n"
          },
          "properties": {
            "name": "clear",
            "size": [
              60,
              21
            ],
            "position": [
              93.0,
              31.0
            ],
            "title": "Clear",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "run_logo(code.text)"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              32.0
            ],
            "title": "Run",
            "border": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "code.size.height = card.size.height - code.position.y",
        "OnResize": "code.size.height = card.size.height - code.position.y"
      },
      "properties": {
        "name": "card_2",
        "bgColor": "white"
      },
      "childModels": [
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
              56.0
            ],
            "text": "pu()\nrt(20)\nbk(170)\nlt(20)\npd()\n\nfor _ in range(5):\n  fd(300)\n  rt(180-(180/5))\n",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": 12,
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "prev",
            "size": [
              35,
              22
            ],
            "position": [
              2.0,
              4.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "next",
            "size": [
              35,
              22
            ],
            "position": [
              214.0,
              4.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "c = card.Clone()\nGotoCard(c.name)"
          },
          "properties": {
            "name": "new",
            "size": [
              60,
              22
            ],
            "position": [
              3.0,
              31.0
            ],
            "title": "New",
            "border": true
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
              42.0,
              2.0
            ],
            "text": "Star",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "for obj in card.children:\n   if obj.name.startswith(\"output\"):\n      obj.Delete()\n"
          },
          "properties": {
            "name": "clear",
            "size": [
              60,
              21
            ],
            "position": [
              93.0,
              31.0
            ],
            "title": "Clear",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "run_logo(code.text)"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              32.0
            ],
            "title": "Run",
            "border": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "code.size.height = card.size.height - code.position.y",
        "OnResize": "code.size.height = card.size.height - code.position.y"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
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
              56.0
            ],
            "text": "pu()\nd = 450\nbk(d/2)\npd()\n\nfor _ in range(180):\n  fd(d)\n  rt(178)\n",
            "alignment": "Left",
            "textColor": "black",
            "font": "Mono",
            "fontSize": 12,
            "editable": true,
            "multiline": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoPreviousCard()"
          },
          "properties": {
            "name": "prev",
            "size": [
              35,
              22
            ],
            "position": [
              2.0,
              4.0
            ],
            "title": "<",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "next",
            "size": [
              35,
              22
            ],
            "position": [
              214.0,
              4.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "c = card.Clone()\nGotoCard(c.name)"
          },
          "properties": {
            "name": "new",
            "size": [
              60,
              22
            ],
            "position": [
              3.0,
              31.0
            ],
            "title": "New",
            "border": true
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
              42.0,
              2.0
            ],
            "text": "Moire",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "for obj in card.children:\n   if obj.name.startswith(\"output\"):\n      obj.Delete()\n"
          },
          "properties": {
            "name": "clear",
            "size": [
              60,
              21
            ],
            "position": [
              93.0,
              31.0
            ],
            "title": "Clear",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "run_logo(code.text)"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              32.0
            ],
            "title": "Run",
            "border": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.8.7"
}
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      750,
      500
    ],
    "canSave": true,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {},
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
              444
            ],
            "position": [
              0.0,
              56.0
            ],
            "text": "for _ in range(4):\n  fd(100)\n  rt(90)\n",
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
              27,
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
              27,
              22
            ],
            "position": [
              223.0,
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
              183,
              25
            ],
            "position": [
              34.0,
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
            "OnClick": "clear.Click()\n\npoints = []\nhome()\n\nexec(code.text)\n\ncard.AddLine(points, \"output\")\noutput.penThickness = 1",
            "OnSetup": "import math\nhomePos = [code.size.width + 250, 250]\npoints = []\npos = homePos\nrot = None\n\ndef fd(dist):\n   global pos\n   global rot\n   global points\n   pos = [pos[0]+math.cos(math.radians(rot))*dist,\n         pos[1]+math.sin(math.radians(rot))*dist]\n   points.append(pos.copy())\n\ndef bk(dist):\n   fd(-dist)\n\ndef home():\n   global pos\n   global rot\n   pos = homePos\n   rot = 0\n   points.append(pos.copy())\n\ndef rt(angle):\n   global rot\n   rot = (rot + angle) % 360\n\ndef lt(angle):\n   rt(-angle)\n\n"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              31.0
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
      "handlers": {},
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
              444
            ],
            "position": [
              0.0,
              56.0
            ],
            "text": "bk(150)\n\nfor _ in range(5):\n  fd(300)\n  rt(180-(180/5))\n",
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
              27,
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
              27,
              22
            ],
            "position": [
              223.0,
              4.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              183,
              25
            ],
            "position": [
              34.0,
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
            "OnClick": "clear.Click()\n\npoints = []\nhome()\n\nexec(code.text)\n\ncard.AddLine(points, \"output\")\noutput.penThickness = 1",
            "OnSetup": "import math\nhomePos = [code.size.width + 250, 250]\npoints = []\npos = homePos\nrot = None\n\ndef fd(dist):\n   global pos\n   global rot\n   global points\n   pos = [pos[0]+math.cos(math.radians(rot))*dist,\n         pos[1]+math.sin(math.radians(rot))*dist]\n   points.append(pos.copy())\n\ndef bk(dist):\n   fd(-dist)\n\ndef home():\n   global pos\n   global rot\n   pos = homePos\n   rot = 0\n   points.append(pos.copy())\n\ndef rt(angle):\n   global rot\n   rot = (rot + angle) % 360\n\ndef lt(angle):\n   rt(-angle)\n\n"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              30.0
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
              30.0
            ],
            "title": "Clear",
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
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
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
              444
            ],
            "position": [
              0.0,
              56.0
            ],
            "text": "bk(150)\n\nfor _ in range(180):\n  fd(300)\n  rt(178)\n",
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
              27,
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
              27,
              22
            ],
            "position": [
              223.0,
              4.0
            ],
            "title": ">",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "title",
            "size": [
              183,
              25
            ],
            "position": [
              34.0,
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
            "OnClick": "clear.Click()\n\npoints = []\nhome()\n\nexec(code.text)\n\ncard.AddLine(points, \"output\")\noutput.penThickness = 1",
            "OnSetup": "import math\nhomePos = [code.size.width + 250, 250]\npoints = []\npos = homePos\nrot = None\n\ndef fd(dist):\n   global pos\n   global rot\n   global points\n   pos = [pos[0]+math.cos(math.radians(rot))*dist,\n         pos[1]+math.sin(math.radians(rot))*dist]\n   points.append(pos.copy())\n\ndef bk(dist):\n   fd(-dist)\n\ndef home():\n   global pos\n   global rot\n   pos = homePos\n   rot = 0\n   points.append(pos.copy())\n\ndef rt(angle):\n   global rot\n   rot = (rot + angle) % 360\n\ndef lt(angle):\n   rt(-angle)\n\n"
          },
          "properties": {
            "name": "run",
            "size": [
              60,
              21
            ],
            "position": [
              190.0,
              30.0
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
              30.0
            ],
            "title": "Clear",
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.8.4"
}
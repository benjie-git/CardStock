{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      655,
      434
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "pegs = [peg1, peg2, peg3]\ndisks = [disk1, disk2, disk3, disk4, disk5]\nstacks = [[disk5, disk4, disk3, disk2, disk1], [], []]\nisRunning = False\nisSetup = False\n\ndef PlaceDisk(disk, peg, height, animate, onFinished):\n   center = [peg.center.x,\n      peg.position.y + (height + 1)*40]\n   if animate:\n      disk.AnimateCenter(0.6, center, onFinished)\n   else:\n      disk.center = center\n      if onFinished: onFinished()\n\ndef ShowStacks(animate, onFinished=None):\n   i = 0\n   for p in range(3):\n      for d in range(len(stacks[p])):\n         i += 1\n         PlaceDisk(stacks[p][d], pegs[p], d, animate, onFinished if (i == len(disks)) else None)\n\ndef MoveTower(disk, source, dest, spare):\n   if disk == 0:\n      steps.append([disk, source, dest])\n   else:\n      MoveTower(disk-1, source, spare, dest)\n      steps.append([disk, source, dest])\n      MoveTower(disk-1, spare, dest, source)\n\ndef MakeNextMove():\n   if len(steps):\n      disk, source, dest = steps.pop(0)\n      stacks[source].remove(disks[disk])\n      stacks[dest].append(disks[disk])\n      ShowStacks(True, MakeNextMove)\n   else:\n      isRunning = False\n\nShowStacks(False)\nisSetup = True"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "peg1",
            "size": [
              25,
              240
            ],
            "position": [
              106.0,
              27.0
            ],
            "originalSize": [
              585,
              34
            ],
            "penColor": "#000000",
            "penThickness": 0,
            "fillColor": "#926143"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              584.0,
              33.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "peg2",
            "size": [
              25,
              240
            ],
            "position": [
              306.0,
              27.0
            ],
            "originalSize": [
              585,
              34
            ],
            "penColor": "#000000",
            "penThickness": 0,
            "fillColor": "#926143"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              584.0,
              33.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "peg3",
            "size": [
              25,
              240
            ],
            "position": [
              506.0,
              27.0
            ],
            "originalSize": [
              585,
              34
            ],
            "penColor": "#000000",
            "penThickness": 0,
            "fillColor": "#926143"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              584.0,
              33.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              585,
              34
            ],
            "position": [
              33.0,
              13.0
            ],
            "originalSize": [
              585,
              34
            ],
            "penColor": "#000000",
            "penThickness": 0,
            "fillColor": "#926143"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              584.0,
              33.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "disk3",
            "size": [
              154,
              36
            ],
            "position": [
              41.0,
              129.0
            ],
            "originalSize": [
              163,
              36
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF",
            "cornerRadius": 8
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              161.0,
              34.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "disk2",
            "size": [
              119,
              36
            ],
            "position": [
              58.0,
              169.0
            ],
            "originalSize": [
              163,
              36
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF",
            "cornerRadius": 8
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              161.0,
              34.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "disk1",
            "size": [
              76,
              36
            ],
            "position": [
              80.0,
              209.0
            ],
            "originalSize": [
              163,
              36
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF",
            "cornerRadius": 8
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              161.0,
              34.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if isRunning:\n   card.StopAllAnimating()\n\nstacks = [[disk5, disk4, disk3, disk2, disk1], [], []]\nsteps = []\nMoveTower(len(disks)-1, 0, 1, 2)\n\nisRunning = True\n\nif not isSetup:\n   ShowStacks(True, MakeNextMove)\nelse:\n   MakeNextMove()\n\nisSetup = False"
          },
          "properties": {
            "name": "solve",
            "size": [
              151,
              37
            ],
            "position": [
              16.0,
              382.0
            ],
            "title": "Solve",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "if isRunning:\n   card.StopAllAnimating()\n\nstacks = [[disk5, disk4, disk3, disk2, disk1], [], []]\nsteps = []\nisSetup = True\nShowStacks(True)\nisRunning = False\n"
          },
          "properties": {
            "name": "reset",
            "size": [
              151,
              37
            ],
            "position": [
              201.0,
              382.0
            ],
            "title": "Reset",
            "border": true
          }
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "disk4",
            "size": [
              185,
              36
            ],
            "position": [
              25.0,
              89.0
            ],
            "originalSize": [
              163,
              36
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF",
            "cornerRadius": 8
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              161.0,
              34.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "disk5",
            "size": [
              218,
              36
            ],
            "position": [
              9.0,
              49.0
            ],
            "originalSize": [
              163,
              36
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FFFFFF",
            "cornerRadius": 8
          },
          "points": [
            [
              2.0,
              2.0
            ],
            [
              161.0,
              34.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9"
}
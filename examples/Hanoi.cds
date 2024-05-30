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
        "on_show_card": "pegs = [peg1, peg2, peg3]\ndisks = [disk1, disk2, disk3, disk4, disk5]\norigStackState = [[disk5, disk4, disk3, disk2, disk1], [], []]\nstackGoal = [[], [disk5, disk4, disk3, disk2, disk1], []]\nstacks = [x.copy() for x in origStackState]\n\nisRunning = False\n\ncard.dragDisk = None\ncard.dragDiskStartPeg = None\n\ndef DragDiskStart(disk):\n   if not isRunning:\n      i = 0\n      for s in stacks:\n         if len(s) and s[-1] == disk:\n            s.remove(disk)\n            card.dragDisk = disk\n            card.dragDiskStartPeg = i\n         i += 1\n\ndef PlaceDisk(disk, peg, height, animate, onFinished, duration=0.6):\n   center = [peg.center.x,\n      peg.bottom + (height + 1)*40]\n   if animate:\n      disk.animate_center(duration, center, easing=\"inout\", on_finished=onFinished)\n   else:\n      disk.center = center\n      if onFinished: onFinished()\n\ndef ShowStacks(animate, onFinished=None):\n   i = 0\n   for p in range(3):\n      for d in range(len(stacks[p])):\n         i += 1\n         PlaceDisk(stacks[p][d], pegs[p], d, animate, onFinished if (i == len(disks)) else None)\n\ndef MoveTower(disk, source, dest, spare):\n   if disk == 0:\n      steps.append([disk, source, dest])\n   else:\n      MoveTower(disk-1, source, spare, dest)\n      steps.append([disk, source, dest])\n      MoveTower(disk-1, spare, dest, source)\n\ndef MakeNextMove():\n   if len(steps):\n      disk, source, dest = steps.pop(0)\n      stacks[source].remove(disks[disk])\n      stacks[dest].append(disks[disk])\n      ShowStacks(True, MakeNextMove)\n   else:\n      isRunning = False\n\nShowStacks(False)",
        "on_mouse_move": "if card.dragDisk:\n   if is_mouse_pressed():\n         card.dragDisk.center = mouse_pos\n   else:\n      card.dragDisk = None",
        "on_mouse_release": "if card.dragDisk:\n   if card.dragDisk.center.x < 215:\n      p = 0\n   elif card.dragDisk.center.x > 425:\n      p = 2\n   else:\n      p = 1\n   \n   if len(stacks[p]) == 0 or stacks[p][-1].size.width > card.dragDisk.size.width:\n      stacks[p].append(card.dragDisk)\n      PlaceDisk(card.dragDisk, pegs[p], len(stacks[p])-1, True, None, 0.25)\n      if stacks == stackGoal:\n         play_sound(\"yay.wav\")\n         wait(2)\n         reset.click()\n   else:\n      stacks[card.dragDiskStartPeg].append(card.dragDisk)\n      PlaceDisk(card.dragDisk, pegs[card.dragDiskStartPeg], len(stacks[card.dragDiskStartPeg])-1, True, None, 0.25)\n   card.dragDisk = None"
      },
      "properties": {
        "name": "card_1",
        "size": [
          648,
          344
        ],
        "fill_color": "#dae9e9",
        "can_resize": false
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
            "center": [
              123.0,
              147.0
            ],
            "originalSize": [
              585,
              34
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "#926143"
          },
          "points": [
            [
              1,
              1
            ],
            [
              584,
              33
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
            "center": [
              323.0,
              147.0
            ],
            "originalSize": [
              585,
              34
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "#926143"
          },
          "points": [
            [
              1,
              1
            ],
            [
              584,
              33
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
            "center": [
              523.0,
              147.0
            ],
            "originalSize": [
              585,
              34
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "#926143"
          },
          "points": [
            [
              1,
              1
            ],
            [
              584,
              33
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              610,
              34
            ],
            "center": [
              323.0,
              30.0
            ],
            "originalSize": [
              585,
              34
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "#926143"
          },
          "points": [
            [
              1,
              1
            ],
            [
              584,
              33
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if isRunning:\n   card.stop_all_animating()\n\nwasSetup = (stacks == origStackState)\nstacks = [x.copy() for x in origStackState]\nsteps = []\nMoveTower(len(disks)-1, 0, 1, 2)\n\nisRunning = True\n\nif not wasSetup:\n   ShowStacks(True, MakeNextMove)\nelse:\n   MakeNextMove()"
          },
          "properties": {
            "name": "solve",
            "size": [
              100,
              28
            ],
            "center": [
              572.0,
              316.0
            ],
            "text": "Solve",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "if isRunning:\n   card.stop_all_animating()\n\nstacks = [x.copy() for x in origStackState]\nsteps = []\nShowStacks(True)\nisRunning = False\n"
          },
          "properties": {
            "name": "reset",
            "size": [
              100,
              28
            ],
            "center": [
              456.0,
              316.0
            ],
            "text": "Reset",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_press": "DragDiskStart(self)"
          },
          "properties": {
            "name": "disk5",
            "size": [
              200,
              38
            ],
            "center": [
              123.0,
              68.0
            ],
            "originalSize": [
              163,
              36
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#dac6ac",
            "corner_radius": 8
          },
          "points": [
            [
              2,
              2
            ],
            [
              161,
              34
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_press": "DragDiskStart(self)"
          },
          "properties": {
            "name": "disk4",
            "size": [
              170,
              38
            ],
            "center": [
              123.0,
              108.0
            ],
            "originalSize": [
              163,
              36
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#dac6ac",
            "corner_radius": 8
          },
          "points": [
            [
              2,
              2
            ],
            [
              161,
              34
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_press": "DragDiskStart(self)"
          },
          "properties": {
            "name": "disk3",
            "size": [
              140,
              38
            ],
            "center": [
              123.0,
              148.0
            ],
            "originalSize": [
              163,
              36
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#dac6ac",
            "corner_radius": 8
          },
          "points": [
            [
              2,
              2
            ],
            [
              161,
              34
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_press": "DragDiskStart(self)"
          },
          "properties": {
            "name": "disk2",
            "size": [
              110,
              38
            ],
            "center": [
              123.0,
              188.0
            ],
            "originalSize": [
              163,
              36
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#dac6ac",
            "corner_radius": 8
          },
          "points": [
            [
              2,
              2
            ],
            [
              161,
              34
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_press": "DragDiskStart(self)"
          },
          "properties": {
            "name": "disk1",
            "size": [
              70,
              38
            ],
            "center": [
              123.0,
              228.0
            ],
            "originalSize": [
              163,
              36
            ],
            "pen_color": "#000000",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#dac6ac",
            "corner_radius": 8
          },
          "points": [
            [
              2,
              2
            ],
            [
              161,
              34
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 10,
  "CardStock_stack_version": "0.99.7"
}
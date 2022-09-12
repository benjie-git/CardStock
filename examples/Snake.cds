{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      420,
      420
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\nSTEPS = 10  # number of rows, columns in the grid\nSTEP  = 40  # grid spacing\nSPEED_TICK = 0.3  # seconds per move\n\nstepDirs = [(STEP, 0), (0, -STEP), (-STEP, 0), (0, STEP)]\n\ndef reset():\n   global move, lastMove, elapsed, tick, isRunning, keyQueue\n   snake.points = [(30,30), (30+STEP,30)]\n   head.center = snake.points[-1]\n   move = (0, 0)  # start moving to the right\n   lastMove = (STEP, 0)\n   elapsed = 0\n   isRunning = True\n   gameOverLabel.hide()\n   score.text = len(snake.points)\n   keyQueue = []\n   placeApple()\n\ndef backup():\n   global elapsed, isRunning, move, lastMove\n   # Backspace after a GAME OVER will reset you a few moves back\n   if len(snake.points) > 5:\n      gameOverLabel.hide()\n      snake.points = snake.points[:-4]\n      head.center = snake.points[-1]\n      move = (0,0)\n      lastMove = snake.points[-1] - snake.points[-2]\n      elapsed = 0\n      score.text = len(snake.points)\n      isRunning = True\n   \ndef placeApple():\n   if len(snake.points) < STEPS*STEPS-1:\n      oldPos = apple.center\n      # pick a random spot\n      pos = Point(randint(0,STEPS-1)*40+30, randint(0,STEPS-1)*40+30)\n      while pos in snake.points or pos == oldPos:\n         # if the random spot is in the snake, or the same as the old spot,\n         # then step it through the grid until we find an open spot\n         pos += (40, 0)\n         if pos.x > STEPS*STEP:\n            pos = Point(30, pos.y+40)\n         if pos.y > STEPS*STEP:\n            pos = Point(30,30)\n      apple.center = pos\n      apple.show()\n   else:\n      apple.hide()\n   \ndef gameOver(didWin):\n   global isRunning\n   isRunning = False\n   gameOverLabel.text = \"YOU WON!\" if didWin else \"GAME OVER\"\n   gameOverLabel.show()\n\nreset()",
        "on_key_press": "if not isRunning:\n   if key_name in [\"Space\", \"Return\"]:\n      reset()\n   elif key_name in [\"delete\", \"Backspace\"]:\n      backup()\n   return\n\nif key_name in (\"Up\", \"Down\", \"Left\", \"Right\"):\n   keyQueue.append(key_name)",
        "on_mouse_press": "if not isRunning:\n   reset()\nelse:\n   if move == (0,0):\n      move = lastMove\n      return\n   if move[1]:  # is moving vertically\n      if mouse_pos.x > head.center.x:\n         keyQueue.append(\"Right\")\n      else:\n         keyQueue.append(\"Left\")\n   else:\n      if mouse_pos.y > head.center.y:\n         keyQueue.append(\"Up\")\n      else:\n         keyQueue.append(\"Down\")\n",
        "on_periodic": "if not isRunning:\n   return\n\nelapsed += elapsed_time\nif elapsed > SPEED_TICK:\n   elapsed -= SPEED_TICK\n\n   points = snake.points[:]  # Get a copy of the points list\n   \n   if len(keyQueue):\n      key_name = keyQueue[0]\n      keyQueue = keyQueue[1:]\n      if key_name == \"Up\" and lastMove != (0, -STEP):\n         move = (0, STEP)\n      elif key_name == \"Down\" and lastMove != (0, STEP):\n         move = (0, -STEP)\n      elif key_name == \"Left\" and lastMove != (STEP, 0):\n         move = (-STEP, 0)\n      elif key_name == \"Right\" and lastMove != (-STEP, 0):\n         move = (STEP, 0)\n\n   if move == (0,0):\n      return\n   \n   points.append(snake.points[-1] + move)\n   \n   p = points[-1]\n   \n   dropTail = True\n   if p == apple.center:\n      # we got the apple!\n      score.text = int(score.text)+1\n      placeApple()\n      dropTail = False\n   \n   lastMove = move\n   snake.points = points\n   head.center = points[-1]\n   \n   if len(points) == STEPS*STEPS:\n      # the board is ompletely full of snake!  you win!\n      gameOver(True)\n      return\n   \n   for snakeP in snake.points[1:-1]:\n      if p == snakeP:\n         # Stop hitting yourself!  GAME OVER\n         gameOver(False)\n         return\n   if p[0] < 0 or p[1] < 0 or p[0] > card.size.width-STEP/2 or \\\n         p[1] > card.size.height-STEP/2:\n      # Hit the wall.  GAME OVER\n      gameOver(False)\n      return\n   \n   if dropTail:\n      # otherwise drop the oldest snake point\n      snake.points = snake.points[1:]\n"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#C7FDD7"
      },
      "childModels": [
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "snake",
            "size": [
              51,
              20
            ],
            "position": [
              30.0,
              30.0
            ],
            "originalSize": [
              194,
              2
            ],
            "pen_color": "black",
            "pen_thickness": 34,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              194.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "gameOverLabel",
            "size": [
              388,
              88
            ],
            "position": [
              16.0,
              245.0
            ],
            "text": "GAME OVER",
            "alignment": "Center",
            "text_color": "#CD0000",
            "font": "Default",
            "font_size": 54,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "apple",
            "size": [
              36,
              40
            ],
            "position": [
              213.0,
              82.0
            ],
            "file": "simple-red-apple.png",
            "fit": "Contain",
            "rotation": 0.0,
            "xFlipped": false,
            "yFlipped": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "head",
            "size": [
              31,
              31
            ],
            "position": [
              65.0,
              15.0
            ],
            "originalSize": [
              35,
              35
            ],
            "pen_color": "black",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "#0FB81A"
          },
          "points": [
            [
              0.0,
              35.0
            ],
            [
              35.0,
              0.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "line_1",
            "size": [
              420,
              2
            ],
            "position": [
              0.0,
              417.0
            ],
            "originalSize": [
              494,
              2
            ],
            "pen_color": "black",
            "pen_thickness": 6,
            "rotation": 0.0
          },
          "points": [
            [
              494.0,
              0.0
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
            "name": "line_2",
            "size": [
              420,
              2
            ],
            "position": [
              207.0,
              210.0
            ],
            "originalSize": [
              494,
              2
            ],
            "pen_color": "black",
            "pen_thickness": 6,
            "rotation": 269.8851789522798
          },
          "points": [
            [
              494.0,
              0.0
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
            "name": "line_3",
            "size": [
              420,
              2
            ],
            "position": [
              -209.0,
              210.0
            ],
            "originalSize": [
              494,
              2
            ],
            "pen_color": "black",
            "pen_thickness": 6,
            "rotation": 269.8851789522798
          },
          "points": [
            [
              494.0,
              0.0
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
            "name": "line_4",
            "size": [
              420,
              2
            ],
            "position": [
              0.0,
              2.0
            ],
            "originalSize": [
              494,
              2
            ],
            "pen_color": "black",
            "pen_thickness": 6,
            "rotation": 0.0
          },
          "points": [
            [
              494.0,
              0.0
            ],
            [
              0.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "score",
            "size": [
              101,
              39
            ],
            "position": [
              14.0,
              369.0
            ],
            "text": "2",
            "alignment": "Left",
            "text_color": "#5D5D5D",
            "font": "Default",
            "font_size": 16,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      420,
      420
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\nSTEPS = 10  # number of rows, columns in the grid\nSTEP  = 40  # grid spacing\nSPEED_TICK = 0.3  # seconds per move\n\nstepDirs = [(STEP, 0), (0, -STEP), (-STEP, 0), (0, STEP)]\n\ndef reset():\n   global move, lastMove, elapsed, tick, isRunning, keyQueue\n   snake.points = [(30,30), (30+STEP,30)]\n   head.center = snake.points[-1]\n   move = (0, 0)  # start moving to the right\n   lastMove = (STEP, 0)\n   elapsed = 0\n   isRunning = True\n   gameOverLabel.Hide()\n   score.text = len(snake.points)\n   keyQueue = []\n   placeApple()\n\ndef backup():\n   global elapsed, isRunning, move, lastMove\n   # Backspace after a GAME OVER will reset you a few moves back\n   if len(snake.points) > 5:\n      gameOverLabel.Hide()\n      snake.points = snake.points[:-4]\n      head.center = snake.points[-1]\n      move = (0,0)\n      lastMove = snake.points[-1] - snake.points[-2]\n      elapsed = 0\n      score.text = len(snake.points)\n      isRunning = True\n   \ndef placeApple():\n   if len(snake.points) < STEPS*STEPS-1:\n      oldPos = apple.center\n      # pick a random spot\n      pos = Point(randint(0,STEPS-1)*40+30, randint(0,STEPS-1)*40+30)\n      while pos in snake.points or pos == oldPos:\n         # if the random spot is in the snake, or the same as the old spot,\n         # then step it through the grid until we find an open spot\n         pos += (40, 0)\n         if pos.x > STEPS*STEP:\n            pos = Point(30, pos.y+40)\n         if pos.y > STEPS*STEP:\n            pos = Point(30,30)\n      apple.center = pos\n      apple.Show()\n   else:\n      apple.Hide()\n   \ndef gameOver(didWin):\n   global isRunning\n   isRunning = False\n   gameOverLabel.text = \"YOU WON!\" if didWin else \"GAME OVER\"\n   gameOverLabel.Show()\n\nreset()",
        "OnKeyDown": "if not isRunning:\n   if keyName in [\"Space\", \"Return\"]:\n      reset()\n   elif keyName in [\"Delete\", \"Backspace\"]:\n      backup()\n   return\n\nif keyName in (\"Up\", \"Down\", \"Left\", \"Right\"):\n   keyQueue.append(keyName)",
        "OnMouseDown": "if not isRunning:\n   reset()\nelse:\n   if move == (0,0):\n      move = lastMove\n      return\n   if mousePos.x > card.size.width/2:\n      keyQueue.append(\"tR\")\n   else:\n      keyQueue.append(\"tL\")",
        "OnPeriodic": "if not isRunning:\n   return\n\nelapsed += elapsedTime\nif elapsed > SPEED_TICK:\n   elapsed -= SPEED_TICK\n\n   points = snake.points[:]  # Get a copy of the points list\n   \n   if len(keyQueue):\n      keyName = keyQueue[0]\n      keyQueue = keyQueue[1:]\n      if keyName == \"Up\" and lastMove != (0, -STEP):\n         move = (0, STEP)\n      elif keyName == \"Down\" and lastMove != (0, STEP):\n         move = (0, -STEP)\n      elif keyName == \"Left\" and lastMove != (STEP, 0):\n         move = (-STEP, 0)\n      elif keyName == \"Right\" and lastMove != (-STEP, 0):\n         move = (STEP, 0)\n      elif keyName == \"tR\":\n         index = stepDirs.index(move)\n         move = stepDirs[(index+1)%4]\n      elif keyName == \"tL\":\n         index = stepDirs.index(move)\n         move = stepDirs[(index-1)%4]\n\n   if move == (0,0):\n      return\n   \n   points.append(snake.points[-1] + move)\n   \n   p = points[-1]\n   \n   dropTail = True\n   if p == apple.center:\n      # we got the apple!\n      score.text = int(score.text)+1\n      placeApple()\n      dropTail = False\n   \n   lastMove = move\n   snake.points = points\n   head.center = points[-1]\n   \n   if len(points) == STEPS*STEPS:\n      # the board is ompletely full of snake!  you win!\n      gameOver(True)\n      return\n   \n   for snakeP in snake.points[1:-1]:\n      if p == snakeP:\n         # Stop hitting yourself!  GAME OVER\n         gameOver(False)\n         return\n   if p[0] < 0 or p[1] < 0 or p[0] > card.size.width-STEP/2 or \\\n         p[1] > card.size.height-STEP/2:\n      # Hit the wall.  GAME OVER\n      gameOver(False)\n      return\n   \n   if dropTail:\n      # otherwise drop the oldest snake point\n      snake.points = snake.points[1:]\n"
      },
      "properties": {
        "name": "card_1",
        "fillColor": "#C7FDD7"
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
            "penColor": "black",
            "penThickness": 34,
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
            "textColor": "#CD0000",
            "font": "Default",
            "fontSize": 54,
            "canAutoShrink": true,
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
            "penColor": "black",
            "penThickness": 0,
            "rotation": 0.0,
            "fillColor": "#0FB81A"
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
            "penColor": "black",
            "penThickness": 6,
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
            "penColor": "black",
            "penThickness": 6,
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
            "penColor": "black",
            "penThickness": 6,
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
            "penColor": "black",
            "penThickness": 6,
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
            "textColor": "#5D5D5D",
            "font": "Default",
            "fontSize": 16,
            "canAutoShrink": true,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 3,
  "CardStock_stack_version": "0.9.8"
}
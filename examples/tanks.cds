{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      1146,
      495
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n\ndef resetShot():\n   # The shot finished.  Stop it moving, move it back to tank_1, and hide it.\n   shot.speed = (0,0)\n   shot.visible = False\n   shot.position = tank_1.position + list(tank_1.size) - (5,5)\n\ndef generateTerrain():\n   # Create a new ground line\n   # Add another point along the line every 10 px\n   # Smooth out the ground by randomly increasing or decreasing the rate of change of y (called dy)\n   # Move up or down by dy every 4 px, and then modify dy.\n   STEP = 9\n   y = 40 # Start 40px above the bottom\n   dy = 0 # Start flat (not getting higher or lower)\n   points = [(0,y),] # Start building new list of points\n   for x in range(int(self.size.width/STEP+2)):\n      dy += randint(-int(STEP/3),int(STEP/3)) # modify dy\n      y += dy\n      if y < 1:\n         # Keep y above 0\n         y = 1\n         dy = 2\n      if y > self.size.height/2:\n         # Keep y below the midline\n         y = int(self.size.height/2)\n         dy = -2\n      points.append((x*STEP,y))\n   \n   # Update the points that make up the ground line\n   ground.points = points\n   \n   # Update the tank positions\n   tank_1.position.y = points[int((tank_1.center.x+20)/STEP)][1]\n   line.position = tank_1.position + list(tank_1.size) - (5,5)\n   resetShot()\n   \n   # Pick a location for tank_2, in the right 1/2 of the card\n   x = randint(int(self.size.width/2)-20, self.size.width-60)\n   tank_2.position = (x, points[int((x+30)/STEP)][1])\n\n\n# When the stack starts running, generate new terrain\ngenerateTerrain()\n\ndidResize = False",
        "OnKeyDown": "if not shot.visible and keyName == \"Space\":\n   # Fire a shot on Space key press, if the shot is not already visible\n   # The shot's speed is set to 5x the line vector, per second.\n   # Gravity will decrease the speed in the y direction over time, on the OnPeriodic event\n   shot.speed = [n*5 for n in line.size]\n   shot.Show()",
        "OnKeyHold": "# Change the line length and direction using the arrow keys\nif keyName == \"Up\":\n   line.size.height += 1\nif keyName == \"Down\":\n   if line.size.height > 0:\n      line.size.height -= 1\nif keyName == \"Right\":\n   line.size.width += 1\nif keyName == \"Left\":\n   if line.size.width> 0:\n      line.size.width -= 1\n",
        "OnResize": "# Update the terrain in OnPeriodic, when the window is done resizing\ndidResize = True\n",
        "OnPeriodic": "# After resizing the window, generate new terrain\nif didResize and not IsMouseDown():\n   generateTerrain()\n   didResize = False\n\nif shot.visible:\n   # Apply gravity to the shot if it's visible, at -500px/sec/sec\n   shot.speed.y -= elapsedTime*500\n   \n   # Add a tiny bit of air resistance\n   shot.speed.x *= 0.998\n\n\nif shot.IsTouching(tank_2):\n   # If the shot touches tank_2, you win!  Then reset the shot and regenerate the terrain\n   shot.speed = (0,0)\n   Alert(\"Good Shot!\")\n   resetShot()\n   generateTerrain()\n\nif shot.IsTouching(ground) or shot.position.y < 0 or shot.position.x > card.size.width:\n   # If the shot touches the ground or gets below the card bottom, or past its right edge, reset the shot.\n   resetShot()\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "ground",
            "size": [
              1140,
              80
            ],
            "position": [
              7.0,
              28.0
            ],
            "originalSize": [
              637,
              87
            ],
            "penColor": "black",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              7.0,
              0.0
            ],
            [
              14.0,
              0.0
            ],
            [
              21.0,
              0.0
            ],
            [
              28.0,
              0.0
            ],
            [
              35.0,
              0.0
            ],
            [
              42.0,
              0.0
            ],
            [
              49.0,
              0.0
            ],
            [
              56.0,
              0.0
            ],
            [
              63.0,
              0.0
            ],
            [
              69.0,
              1.0
            ],
            [
              74.0,
              2.0
            ],
            [
              81.0,
              2.0
            ],
            [
              86.0,
              3.0
            ],
            [
              93.0,
              3.0
            ],
            [
              99.0,
              4.0
            ],
            [
              104.0,
              6.0
            ],
            [
              108.0,
              8.0
            ],
            [
              112.0,
              11.0
            ],
            [
              116.0,
              13.0
            ],
            [
              119.0,
              15.0
            ],
            [
              123.0,
              18.0
            ],
            [
              127.0,
              21.0
            ],
            [
              131.0,
              24.0
            ],
            [
              135.0,
              27.0
            ],
            [
              139.0,
              30.0
            ],
            [
              143.0,
              33.0
            ],
            [
              147.0,
              36.0
            ],
            [
              152.0,
              38.0
            ],
            [
              157.0,
              40.0
            ],
            [
              162.0,
              42.0
            ],
            [
              167.0,
              44.0
            ],
            [
              173.0,
              45.0
            ],
            [
              179.0,
              46.0
            ],
            [
              185.0,
              47.0
            ],
            [
              191.0,
              48.0
            ],
            [
              198.0,
              48.0
            ],
            [
              205.0,
              48.0
            ],
            [
              212.0,
              48.0
            ],
            [
              218.0,
              49.0
            ],
            [
              225.0,
              49.0
            ],
            [
              231.0,
              49.0
            ],
            [
              236.0,
              50.0
            ],
            [
              242.0,
              50.0
            ],
            [
              247.0,
              50.0
            ],
            [
              253.0,
              51.0
            ],
            [
              259.0,
              52.0
            ],
            [
              264.0,
              54.0
            ],
            [
              269.0,
              56.0
            ],
            [
              274.0,
              58.0
            ],
            [
              278.0,
              61.0
            ],
            [
              283.0,
              63.0
            ],
            [
              288.0,
              65.0
            ],
            [
              292.0,
              67.0
            ],
            [
              296.0,
              70.0
            ],
            [
              300.0,
              72.0
            ],
            [
              305.0,
              74.0
            ],
            [
              309.0,
              76.0
            ],
            [
              312.0,
              78.0
            ],
            [
              317.0,
              79.0
            ],
            [
              322.0,
              81.0
            ],
            [
              327.0,
              82.0
            ],
            [
              332.0,
              84.0
            ],
            [
              337.0,
              85.0
            ],
            [
              342.0,
              85.0
            ],
            [
              348.0,
              86.0
            ],
            [
              353.0,
              87.0
            ],
            [
              360.0,
              87.0
            ],
            [
              367.0,
              87.0
            ],
            [
              373.0,
              87.0
            ],
            [
              379.0,
              86.0
            ],
            [
              384.0,
              85.0
            ],
            [
              389.0,
              83.0
            ],
            [
              393.0,
              81.0
            ],
            [
              397.0,
              79.0
            ],
            [
              401.0,
              77.0
            ],
            [
              405.0,
              75.0
            ],
            [
              409.0,
              72.0
            ],
            [
              412.0,
              69.0
            ],
            [
              415.0,
              66.0
            ],
            [
              419.0,
              63.0
            ],
            [
              423.0,
              60.0
            ],
            [
              426.0,
              56.0
            ],
            [
              430.0,
              53.0
            ],
            [
              434.0,
              50.0
            ],
            [
              438.0,
              47.0
            ],
            [
              442.0,
              44.0
            ],
            [
              446.0,
              42.0
            ],
            [
              450.0,
              39.0
            ],
            [
              455.0,
              37.0
            ],
            [
              460.0,
              35.0
            ],
            [
              466.0,
              34.0
            ],
            [
              472.0,
              33.0
            ],
            [
              479.0,
              33.0
            ],
            [
              486.0,
              33.0
            ],
            [
              493.0,
              33.0
            ],
            [
              500.0,
              33.0
            ],
            [
              506.0,
              33.0
            ],
            [
              511.0,
              31.0
            ],
            [
              515.0,
              29.0
            ],
            [
              519.0,
              26.0
            ],
            [
              522.0,
              22.0
            ],
            [
              526.0,
              19.0
            ],
            [
              529.0,
              16.0
            ],
            [
              533.0,
              13.0
            ],
            [
              538.0,
              11.0
            ],
            [
              544.0,
              10.0
            ],
            [
              550.0,
              9.0
            ],
            [
              556.0,
              8.0
            ],
            [
              561.0,
              6.0
            ],
            [
              568.0,
              6.0
            ],
            [
              575.0,
              6.0
            ],
            [
              582.0,
              6.0
            ],
            [
              588.0,
              5.0
            ],
            [
              595.0,
              5.0
            ],
            [
              601.0,
              6.0
            ],
            [
              608.0,
              6.0
            ],
            [
              615.0,
              6.0
            ],
            [
              622.0,
              6.0
            ],
            [
              629.0,
              6.0
            ],
            [
              634.0,
              4.0
            ],
            [
              637.0,
              4.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "line",
            "size": [
              50,
              50
            ],
            "position": [
              61.0,
              78.0
            ],
            "originalSize": [
              90,
              96
            ],
            "penColor": "#BFBFBF",
            "penThickness": 1
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              90.0,
              96.0
            ]
          ]
        },
        {
          "type": "poly",
          "handlers": {},
          "properties": {
            "name": "tank_1",
            "size": [
              50,
              50
            ],
            "position": [
              15.0,
              32.0
            ],
            "originalSize": [
              87,
              87
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              85.0,
              0.0
            ],
            [
              85.0,
              39.0
            ],
            [
              50.0,
              49.0
            ],
            [
              87.0,
              78.0
            ],
            [
              74.0,
              87.0
            ],
            [
              27.0,
              45.0
            ],
            [
              3.0,
              38.0
            ]
          ]
        },
        {
          "type": "poly",
          "handlers": {},
          "properties": {
            "name": "tank_2",
            "size": [
              50,
              50
            ],
            "position": [
              1083.0,
              27.0
            ],
            "originalSize": [
              87,
              87
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              87.0,
              0.0
            ],
            [
              2.0,
              0.0
            ],
            [
              2.0,
              39.0
            ],
            [
              37.0,
              49.0
            ],
            [
              0.0,
              78.0
            ],
            [
              13.0,
              87.0
            ],
            [
              60.0,
              45.0
            ],
            [
              84.0,
              38.0
            ]
          ]
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "shot",
            "size": [
              10,
              10
            ],
            "position": [
              62.0,
              80.0
            ],
            "originalSize": [
              21,
              18
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "#111919"
          },
          "points": [
            [
              0.0,
              18.0
            ],
            [
              21.0,
              0.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9.6"
}
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      1146,
      495
    ],
    "can_save": false,
    "can_resize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\n\ndef resetShot():\n   # The shot finished.  Stop it moving, move it back to tank_1, and hide it.\n   shot.speed = (0,0)\n   shot.is_visible = False\n   shot.position = tank_1.position + list(tank_1.size) - (5,5)\n\ndef generateTerrain():\n   # Create a new ground line\n   # Add another point along the line every STEP px\n   # Smooth out the ground by randomly increasing or decreasing the rate of change of y (called dy)\n   # Move up or down by dy every STEP px, and then modify dy.\n   global didResize\n   STEP = 20\n   y = 60 # Start y px above the bottom\n   dy = 0 # Start flat (not getting higher or lower)\n   points = [] # Start building new list of points\n   for x in range(int(self.size.width/STEP+2)):\n      dy += randint(-int(STEP/3),int(STEP/3)) # modify dy\n      y += dy\n      if y < 1:\n         # Keep y above 0\n         y = 1\n         dy = 2\n      if y > self.size.height/2:\n         # Keep y below the midline\n         y = int(self.size.height/2)\n         dy = -2\n      points.append((x*STEP,y))\n   \n   # Update the points that make up the ground line\n   points.extend([(points[-1][0],-10), (0,-10)])\n   ground.points = points\n   \n   # Pick a location for tank_2, in the right 1/2 of the card\n   x = randint(int(self.size.width/2)-20, self.size.width-60)\n   tank_2.position = (x, points[int((x+30)/STEP)][1])\n\n   # Update the tank positions\n   tank_1.position.y = points[int((tank_1.center.x+20)/STEP)][1]\n   line.position = tank_1.position + list(tank_1.size) - (5,5)\n   resetShot()\n   didResize = False\n\n# When the stack starts running, generate new terrain\ngenerateTerrain()\ndidResize = False",
        "on_key_press": "if not shot.is_visible and key_name == \"Space\":\n   # Fire a shot on Space key press, if the shot is not already visible\n   self.send_message(\"shoot\")",
        "on_key_hold": "# Change the line length and direction using the arrow keys\nif key_name == \"Up\":\n   line.size.height += 1\nelif key_name == \"Down\":\n   if line.size.height > 0:\n      line.size.height -= 1\nelif key_name == \"Right\":\n   line.size.width += 1\nelif key_name == \"Left\":\n   if line.size.width> 0:\n      line.size.width -= 1",
        "on_mouse_release": "if not shot.is_visible:\n   # Fire a shot on MouseUp, if the shot is not already visible\n   self.send_message(\"shoot\")",
        "on_message": "if message == \"shoot\":\n   # The shot's speed is set to 5x the line vector, per second.\n   # Gravity will decrease the speed in the y direction over time, on the on_periodic event\n   shot.speed = [n*5 for n in line.size]\n   shot.show()",
        "on_periodic": "# After resizing the window, generate new terrain\nif didResize and not is_mouse_pressed():\n   generateTerrain()\n\nif shot.is_visible:\n   # Apply gravity to the shot if it's visible, at -500px/sec/sec\n   shot.speed.y -= elapsed_time*500\n   \n   # Add a tiny bit of air resistance\n   shot.speed.x *= 0.998\n\n   if shot.is_touching(ground) or shot.position.y < 0 or shot.position.x > card.size.width:\n      # If the shot touches the ground or gets below the card bottom, or past its right edge, reset the shot.\n      resetShot()\n\n   if shot.is_touching(tank_2):\n      # If the shot touches tank_2, you win!  Then reset the shot and regenerate the terrain\n      shot.speed = (0,0)\n      alert(\"Good Shot!\")\n      resetShot()\n      generateTerrain()\nelse:\n   if is_mouse_pressed():\n      mouse_pos = get_mouse_pos()\n      aimPos = line.position + tuple(line.size)\n      if mouse_pos.x > aimPos.x +6:\n         line.size.width += 1\n      elif mouse_pos.x < aimPos.x -6:\n         line.size.width -= 1\n      if mouse_pos.y > aimPos.y +6:\n         line.size.height += 1\n      elif mouse_pos.y < aimPos.y -6:\n         line.size.height -= 1",
        "on_resize": "# Update the terrain in on_periodic, when the window is done resizing\nif not is_initial:\n   didResize = True"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#D0F9FF"
      },
      "childModels": [
        {
          "type": "polygon",
          "handlers": {},
          "properties": {
            "name": "ground",
            "size": [
              1144,
              75
            ],
            "position": [
              4.0,
              -15.0
            ],
            "originalSize": [
              1144,
              75
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#51A152"
          },
          "points": [
            [
              3.0,
              17.0
            ],
            [
              277.0,
              50.0
            ],
            [
              437.0,
              34.0
            ],
            [
              876.0,
              75.0
            ],
            [
              1143.0,
              43.0
            ],
            [
              1144.0,
              15.0
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
            "name": "line",
            "size": [
              50,
              50
            ],
            "position": [
              78.0,
              57.0
            ],
            "originalSize": [
              90,
              96
            ],
            "pen_color": "red",
            "pen_thickness": 1,
            "rotation": 0.0
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
          "type": "polygon",
          "handlers": {},
          "properties": {
            "name": "tank_1",
            "size": [
              50,
              50
            ],
            "position": [
              32.0,
              11.0
            ],
            "originalSize": [
              87,
              87
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#856E6E"
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
          "type": "polygon",
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
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#856E6E"
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
              79.0,
              59.0
            ],
            "originalSize": [
              21,
              18
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#111919"
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
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      400,
      800
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "import random\n\nCOLS, ROWS = (10, 20)\nNUM_BLINKS = 4\nSTEP_DELAY = 0.25\nKEY_REPEAT_DELAY = 0.15\nkeySkipL = 0\nkeySkipR = 0\nkeySkipU = 0\nshouldDrop = False\nscore = 0\nscores = (0, 40, 100, 300, 1200)\npaused = False\nactive = None\npaused_label.is_visible = paused\n\ngroup_pads.hide()\n\n# Shape Template object\nclass Shape_t(object):\n   def __init__(self, c, w, shape_data):\n      self.color = c\n      self.width = w\n      self.shape_data = list(Point(*p) for p in shape_data)\n\n# Shape object, inits based on a shape template\nclass Shape(Shape_t):\n   def __init__(self, t, pos):\n      super().__init__(t.color, t.width-1, t.shape_data)\n      self.pos = pos\n      self.rects = []\n      for d in self.shape_data:\n         r = card.add_rectangle(\n            fill_color=self.color,\n            size=(40,40),\n            pen_thickness=1)\n         r.order_to_back()\n         self.rects.append(r)\n      self.update_rects()\n\n   def delete(self):\n      for r in self.rects:\n         r.delete()\n\n   def rotateL(self):\n      self.shape_data = list(Point(self.width-p.y, p.x) for p in self.shape_data)\n\n   def rotateR(self):\n      self.shape_data = list(Point(p.y, self.width-p.x) for p in self.shape_data)\n\n   def update_rects(self):\n      for i in range(len(self.shape_data)):\n         self.rects[i].position = (self.pos+self.shape_data[i])*40\n\n\nshapes =(Shape_t(\"#AFBDAF\", 4, ((1,0), (1,1), (1,2), (1,3))),\n         Shape_t(\"#0893B6\", 2, ((0,0), (0,1), (1,0), (1,1))),\n         Shape_t(\"#BCAE0F\", 3, ((0,0), (0,1), (1,1), (1,2))),\n         Shape_t(\"#65B343\", 3, ((1,0), (1,1), (0,1), (0,2))),\n         Shape_t(\"#E27838\", 3, ((0,0), (0,1), (1,1), (0,2))),\n         Shape_t(\"#CC55AA\", 3, ((0,0), (0,1), (0,2), (1,2))),\n         Shape_t(\"#FF0000\", 3, ((0,0), (1,0), (0,1), (0,2))))\n\npieces = []\ngrid = []\n\ndef clear_grid():\n   global grid\n   grid = []\n   for y in range(ROWS):\n      line = []\n      for x in range(COLS):\n         line.append(None)\n      grid.append(line)\n\ndef add_to_grid(s):\n   for i in range(len(s.shape_data)):\n      p = s.pos+s.shape_data[i]\n      if p.y < ROWS:\n         grid[round(p.y)][round(p.x)] = s.rects[i]\n\ndef remove_full_rows():\n   global score\n   full_rows = []\n   for i in range(ROWS):\n      if None not in grid[i]:\n         full_rows.append(i)\n\n   if len(full_rows):\n      for n in range(NUM_BLINKS):\n         for r in full_rows:\n            for c in range(COLS):\n               grid[r][c].hide()\n         wait(0.10)\n         for r in full_rows:\n            for c in range(COLS):\n               grid[r][c].show()\n         wait(0.10)\n         \n      for i in reversed(full_rows):\n         for c in range(COLS):\n            grid[i][c].delete()\n         for r in range(i+1, ROWS,):\n            for c in range(COLS):\n               if grid[r][c]:\n                  grid[r][c].position.y -= 40\n               grid[r-1][c] = grid[r][c]\n      score += scores[len(full_rows)]\n      score_label.text = str(score)\n\ndef does_collide_with_grid(s, col_offset, row_offset):\n   for i in range(len(s.shape_data)):\n      p = s.pos+s.shape_data[i]\n      x = round(p.x+col_offset)\n      y = round(p.y+row_offset)\n      if y >= 0 and y < len(grid) and x >= 0 and x < len(grid[0]):\n         if grid[y][x]:\n            return True\n      else:\n         if y < len(grid):\n            return True\n   return False\n\ndef reset():\n   global active, last_tick, pieces, score\n   for p in pieces:\n      p.delete()\n   pieces = []\n   active = None\n   clear_grid()\n   last_tick = time()\n   score = 0\n   score_label.text = str(score)\n\nreset()",
        "on_key_press": "if active:\n   if key_name == \"P\":\n      paused = not paused\n      paused_label.is_visible = paused\n      paused_label.order_to_front()\n   if paused:\n      return\n   if key_name == \"Left\":\n      if not does_collide_with_grid(active, -1, 0):\n         active.pos.x -= 1\n         active.update_rects()\n         keySkipL = 0\n   elif key_name == \"Right\":\n      if not does_collide_with_grid(active, 1, 0):\n         active.pos.x += 1\n         active.update_rects()\n         keySkipR = 0\n   elif key_name == \"Up\":\n      active.rotateL()\n      if does_collide_with_grid(active, 0, 0):\n         active.rotateR()\n      else:\n         active.update_rects()\n      keySkipU = 0\n   elif key_name == \"Down\":\n      shouldDrop = True",
        "on_key_hold": "if active:\n   if paused:\n      return\n   if key_name == \"Left\":\n      keySkipL += elapsed_time\n      if keySkipL >= KEY_REPEAT_DELAY:\n         if not does_collide_with_grid(active, -1, 0):\n            active.pos.x -= 1\n            active.update_rects()\n            keySkipL = 0\n   elif key_name == \"Right\":\n      keySkipR += elapsed_time\n      if keySkipR >= KEY_REPEAT_DELAY:\n         if not does_collide_with_grid(active, 1, 0):\n            active.pos.x += 1\n            active.update_rects()\n            keySkipR = 0\n   elif key_name == \"Up\":\n      keySkipU += elapsed_time\n      if keySkipU >= KEY_REPEAT_DELAY*2:\n         active.rotateL()\n         if does_collide_with_grid(active, 0, 0):\n            active.rotateR()\n         else:\n            active.update_rects()\n         keySkipU = 0",
        "on_key_release": "if key_name == \"Down\":\n   shouldDrop = False",
        "on_mouse_press": "if is_using_touch_screen():\n   if not group_pads.is_visible:\n      group_pads.show()",
        "on_mouse_release": "if is_using_touch_screen():\n   shouldDrop = False",
        "on_periodic": "if paused:\n   return\n\nif time() >= last_tick + STEP_DELAY or shouldDrop:\n   last_tick = time()\n   if not active:\n      active = Shape(random.choice(shapes), Point(COLS//2-1, ROWS-1))\n      pieces.append(active)\n      if does_collide_with_grid(active, 0, 0):\n         alert(\"Game Over\")\n         reset()\n         return\n   else:\n      if not does_collide_with_grid(active, 0, -1):\n         active.pos.y -= 1\n         active.update_rects()\n      else:\n         add_to_grid(active)\n         remove_full_rows()\n         active = None"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#D9D9D9"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {
            "on_mouse_press": "if is_using_touch_screen():\n   paused = not paused\n   paused_label.is_visible = paused\n   paused_label.order_to_front()\n   self.stop_handling_mouse_event()"
          },
          "properties": {
            "name": "score_label",
            "size": [
              150,
              53
            ],
            "position": [
              10.0,
              740.0
            ],
            "text": "0",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 18,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "paused_label",
            "size": [
              400,
              70
            ],
            "position": [
              0.0,
              506.0
            ],
            "text": "PAUSED",
            "alignment": "Center",
            "text_color": "#FB0207",
            "font": "Default",
            "font_size": 40,
            "is_bold": true,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "group_pads",
            "size": [
              399,
              339
            ],
            "position": [
              0.0,
              0.0
            ],
            "rotation": 0.0
          },
          "childModels": [
            {
              "type": "rect",
              "handlers": {
                "on_mouse_press": "if is_using_touch_screen():\n   if paused:\n      return\n   active.rotateL()\n   if does_collide_with_grid(active, 0, 0):\n      active.rotateR()\n   else:\n      active.update_rects()\n   self.stop_handling_mouse_event()"
              },
              "properties": {
                "name": "pad_rot",
                "size": [
                  400,
                  176
                ],
                "position": [
                  0.0,
                  164.0
                ],
                "originalSize": [
                  390,
                  144
                ],
                "pen_color": "#00000022",
                "pen_thickness": 1,
                "rotation": 0.0,
                "fill_color": "#ffffff22"
              },
              "points": [
                [
                  0.0,
                  144.0
                ],
                [
                  390.0,
                  0.0
                ]
              ]
            },
            {
              "type": "rect",
              "handlers": {
                "on_mouse_press": "if is_using_touch_screen():\n   if paused:\n      return\n   if not does_collide_with_grid(active, 1, 0):\n      active.pos.x += 1\n      active.update_rects()\n   self.stop_handling_mouse_event()"
              },
              "properties": {
                "name": "pad_right",
                "size": [
                  200,
                  164
                ],
                "position": [
                  200.0,
                  0.0
                ],
                "originalSize": [
                  390,
                  144
                ],
                "pen_color": "#00000022",
                "pen_thickness": 1,
                "rotation": 0.0,
                "fill_color": "#ffffff22"
              },
              "points": [
                [
                  0.0,
                  144.0
                ],
                [
                  390.0,
                  0.0
                ]
              ]
            },
            {
              "type": "rect",
              "handlers": {
                "on_mouse_press": "if is_using_touch_screen():\n   if paused:\n      return\n   if not does_collide_with_grid(active, -1, 0):\n      active.pos.x -= 1\n      active.update_rects()\n   self.stop_handling_mouse_event()"
              },
              "properties": {
                "name": "pad_left",
                "size": [
                  200,
                  164
                ],
                "position": [
                  0.0,
                  0.0
                ],
                "originalSize": [
                  390,
                  144
                ],
                "pen_color": "#00000022",
                "pen_thickness": 1,
                "rotation": 0.0,
                "fill_color": "#ffffff22"
              },
              "points": [
                [
                  0.0,
                  144.0
                ],
                [
                  390.0,
                  0.0
                ]
              ]
            },
            {
              "type": "rect",
              "handlers": {
                "on_mouse_press": "if is_using_touch_screen():\n   if paused:\n      return\n   shouldDrop = True\n   self.stop_handling_mouse_event()"
              },
              "properties": {
                "name": "pad_drop",
                "size": [
                  98,
                  46
                ],
                "position": [
                  148.0,
                  0.0
                ],
                "originalSize": [
                  390,
                  144
                ],
                "pen_color": "#00000022",
                "pen_thickness": 1,
                "rotation": 0.0,
                "fill_color": "#ffffff00"
              },
              "points": [
                [
                  0.0,
                  144.0
                ],
                [
                  390.0,
                  0.0
                ]
              ]
            }
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.2"
}
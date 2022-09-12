{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      389,
      459
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\n\n# Set up empty stats\nstats_list = [0 for i in range(0,13)]\nstats_label.send_message(\"update\")\n\ndef RollOnce():\n   # Roll the dice\n   a = randint(1,6)\n   b = randint(1,6)\n   label_1.text = a\n   label_2.text = b\n\n   # show the total\n   total = a+b\n   totalLabel.text = \"The total is \" + str(total)\n\n   # Update the stats\n   stats_list[total] += 1\n"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#88D174"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "totalLabel",
            "size": [
              185,
              32
            ],
            "position": [
              42.0,
              220.0
            ],
            "text": "",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 14,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              77,
              77
            ],
            "position": [
              156.0,
              273.0
            ],
            "originalSize": [
              77,
              77
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              77.0,
              77.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              51,
              50
            ],
            "position": [
              167.0,
              288.0
            ],
            "text": "",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 30,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              77,
              77
            ],
            "position": [
              36.0,
              273.0
            ],
            "originalSize": [
              77,
              77
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              77.0,
              77.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              51,
              50
            ],
            "position": [
              47.0,
              288.0
            ],
            "text": "",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 30,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "RollOnce()\nbroadcast_message(\"update\")"
          },
          "properties": {
            "name": "roll",
            "size": [
              177,
              24
            ],
            "position": [
              46.0,
              425.0
            ],
            "title": "Roll",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "on_message": "if message == \"update\":\n   lines = [f\" {n}: {stats_list[n]}\" for n in range(2,10)]\n   lines.extend([f\"{n}: {stats_list[n]}\" for n in range(10,13)])\n   self.text = '\\n'.join(lines)\n"
          },
          "properties": {
            "name": "stats_label",
            "size": [
              120,
              246
            ],
            "position": [
              265.0,
              175.0
            ],
            "text": "",
            "alignment": "Left",
            "text_color": "black",
            "font": "Mono",
            "font_size": 14,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "stepSize = 20\n\nfor i in range(5000):\n   RollOnce()\n   \n   # Update the stats displays once per step_size rolls\n   if i % stepSize == stepSize-1:\n      broadcast_message(\"update\")\n"
          },
          "properties": {
            "name": "roll_5000",
            "size": [
              116,
              24
            ],
            "position": [
              267.0,
              425.0
            ],
            "title": "Roll 5000x",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "rect",
          "handlers": {
            "on_message": "if message == \"update\":\n   items = stats_list[2:]\n   low = min(items)\n   high = max(items)\n   num_points = len(items)\n\n   pos = graph_frame.position\n   s = graph_frame.size\n\n   xStep = (s.width-2)/(num_points-1)\n   yStep = (s.height-3)/(high)\n\n   points = []\n   for n in range(len(items)):\n      points.append((xStep*n+pos.x, yStep*(items[n])+pos.y))\n\n   stat_line.points = points"
          },
          "properties": {
            "name": "graph_frame",
            "size": [
              370,
              160
            ],
            "position": [
              10.0,
              7.0
            ],
            "originalSize": [
              370,
              171
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              171.0
            ],
            [
              370.0,
              0.0
            ]
          ]
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "stat_line",
            "size": [
              365,
              2
            ],
            "position": [
              12.0,
              9.0
            ],
            "originalSize": [
              365,
              2
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              365.0,
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
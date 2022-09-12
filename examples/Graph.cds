{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      691,
      387
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "card_1",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "items = [float(l) for l in field.text.split('\\n') if len(l)]\nlow = min(items)\nhigh = max(items)\nnum = len(items)\n\npos = graph_frame.position\ns = graph_frame.size\n\nxStep = (s.width-2)/(num-1)\nyStep = (s.height-3)/(high-low)\n\npoints = []\nfor i in range(len(items)):\n   points.append((xStep*i+pos.x, yStep*(items[i]-low)+pos.y))\n\nfor obj in card.children:\n   if obj.name == \"line_1\":\n      obj.delete()\nline = card.add_line(points, \"line_1\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              141,
              28
            ],
            "position": [
              118.0,
              348.0
            ],
            "title": "Graph This List",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "graph_frame",
            "size": [
              568,
              329
            ],
            "position": [
              115.0,
              10.0
            ],
            "originalSize": [
              428,
              221
            ],
            "pen_color": "#B6B5B7",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              221.0
            ],
            [
              428.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              42,
              26
            ],
            "position": [
              561.0,
              349.0
            ],
            "title": "<",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
          },
          "properties": {
            "name": "button_3",
            "size": [
              42,
              26
            ],
            "position": [
              621.0,
              349.0
            ],
            "title": ">",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field",
            "size": [
              109,
              386
            ],
            "position": [
              0.0,
              2.0
            ],
            "text": "1\n1.1\n1.2\n1.4\n1.7\n2.3\n3.5\n4.5\n4.9\n5.1\n5.2\n5.3\n5.4\n5.45\n5.47\n5.45\n5.4\n5.3\n5.2\n5.1\n4.9\n4.5\n3.5\n2.3\n1.7\n1.4\n1.2\n1.1\n1\n",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "card_2",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "def func(x):\n   return eval(field.text)\nitems = [func(x/10+0.001) for x in range(-50,51)]\nlow = min(items)\nhigh = max(items)\nnum = len(items)\n\npos = graph_frame.position\ns = graph_frame.size\n\nxStep = (s.width-2)/(num-1)\nyStep = (s.height-3)/high-(min(0, low))\n\npoints = []\nfor i in range(len(items)):\n   points.append((xStep*i+pos.x, yStep*items[i]+pos.y))\n\nfor obj in card.children:\n   if obj.name == \"line_1\":\n      obj.delete()\nline = card.add_line(points, \"line_1\")\nline.position = graph_frame.position\nline.size = graph_frame.size - (1,1)"
          },
          "properties": {
            "name": "button_1",
            "size": [
              161,
              21
            ],
            "position": [
              13.0,
              355.0
            ],
            "title": "Graph This Function",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "graph_frame",
            "size": [
              568,
              329
            ],
            "position": [
              115.0,
              10.0
            ],
            "originalSize": [
              428,
              221
            ],
            "pen_color": "#B6B5B7",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              221.0
            ],
            [
              428.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              52,
              26
            ],
            "position": [
              186.0,
              351.0
            ],
            "text": "y =",
            "alignment": "Left",
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
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              42,
              26
            ],
            "position": [
              561.0,
              349.0
            ],
            "title": "<",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
          },
          "properties": {
            "name": "button_3",
            "size": [
              42,
              26
            ],
            "position": [
              621.0,
              349.0
            ],
            "title": ">",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "button_1.click()"
          },
          "properties": {
            "name": "field",
            "size": [
              320,
              25
            ],
            "position": [
              221.0,
              353.0
            ],
            "text": "x**2 + 1",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
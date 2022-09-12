{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      519,
      506
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "gotBall = False",
        "on_mouse_move": "if gotBall:\n   ball.center = mouse_pos\n"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#FFFFFF"
      },
      "childModels": [
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "gotBall = True",
            "on_message": "if message == \"reset\":\n   play_sound(\"click.wav\")\n   self.position = (10, 10)\n   gotBall = False\nelif message == \"win\":\n   play_sound(\"yay.wav\")\n   self.position = (10, 10)\n   gotBall = False"
          },
          "properties": {
            "name": "ball",
            "size": [
              46,
              47
            ],
            "position": [
              19.0,
              10.0
            ],
            "originalSize": [
              46,
              43
            ],
            "pen_color": "black",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "#0A5FFF",
            "corner_radius": 10
          },
          "points": [
            [
              1,
              1
            ],
            [
              45,
              42
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"win\")\n"
          },
          "properties": {
            "name": "goal",
            "size": [
              20,
              92
            ],
            "position": [
              106.0,
              426.0
            ],
            "originalSize": [
              102,
              24
            ],
            "pen_color": "#000000",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "green"
          },
          "points": [
            [
              1.0,
              1.0
            ],
            [
              101.0,
              23.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_1",
            "size": [
              360,
              20
            ],
            "position": [
              88.0,
              412.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_2",
            "size": [
              20,
              86
            ],
            "position": [
              88.0,
              428.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_3",
            "size": [
              196,
              20
            ],
            "position": [
              104.0,
              302.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_4",
            "size": [
              20,
              362
            ],
            "position": [
              90.0,
              -40.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_5",
            "size": [
              196,
              20
            ],
            "position": [
              236.0,
              179.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_6",
            "size": [
              20,
              236
            ],
            "position": [
              428.0,
              179.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_7",
            "size": [
              20,
              117
            ],
            "position": [
              429.0,
              -28.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_8",
            "size": [
              20,
              98
            ],
            "position": [
              236.0,
              99.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {
            "on_periodic": "if self.is_touching(ball):\n   ball.send_message(\"reset\")\n"
          },
          "properties": {
            "name": "wall_9",
            "size": [
              86,
              20
            ],
            "position": [
              351.0,
              69.0
            ],
            "originalSize": [
              211,
              66
            ],
            "pen_color": "#000000",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#000000"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              211.0,
              66.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
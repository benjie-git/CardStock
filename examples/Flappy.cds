{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      1000,
      500
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "isGameOver = False\n\ntubes = [shape_1, shape_2, shape_3, shape_4]",
        "on_key_press": "if key_name == \"Space\":\n   self.send_message(\"tap\")",
        "on_mouse_press": "self.send_message(\"tap\")",
        "on_message": "if message == \"tap\":\n   if not isGameOver:\n      bird.speed.y += 250  # Flap!\n\n   if isGameOver:\n      # Reset positions of bird and tubes\n      bird.position.y = 200\n      for tube in tubes:\n         tube.position.x += 200\n      isGameOver = False",
        "on_periodic": "if not isGameOver:\n   bird.speed.y -= 18  # Apply gravity\n   \n   if bird.is_touching_edge(card):\n      # Bird hit the floor or ceiling\n      isGameOver = True\n      bird.speed.y = 0\n\n   for tube in tubes:\n      if tube.is_touching(bird):\n         # Bird hit this tube\n         isGameOver = True\n         bird.speed.y = 0\n\n   for tube in tubes:\n      # Move the tubes\n      tube.position.x -= 3\n      if tube.position.x < -tube.size.width:\n         # Wrap the tubes back to the right edge of the card\n         tube.position.x = card.size.width"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              70,
              206
            ],
            "position": [
              77.0,
              322.0
            ],
            "originalSize": [
              70,
              206
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#9C00FF"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              70.0,
              206.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              76,
              334
            ],
            "position": [
              318.0,
              -54.0
            ],
            "originalSize": [
              70,
              206
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#9C00FF"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              70.0,
              206.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              83,
              253
            ],
            "position": [
              581.0,
              280.0
            ],
            "originalSize": [
              70,
              206
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#9C00FF"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              70.0,
              206.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_4",
            "size": [
              109,
              325
            ],
            "position": [
              806.0,
              -159.0
            ],
            "originalSize": [
              70,
              206
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#9C00FF"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              70.0,
              206.0
            ]
          ]
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "bird",
            "size": [
              53,
              53
            ],
            "position": [
              104.0,
              132.0
            ],
            "originalSize": [
              53,
              53
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#FB0207"
          },
          "points": [
            [
              0.0,
              53.0
            ],
            [
              53.0,
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
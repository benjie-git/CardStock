{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      1000,
      500
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "isGameOver = False\n\ntubes = [shape_1, shape_2, shape_3, shape_4]\n",
        "OnKeyDown": "if not isGameOver:\n   if keyName == \"Space\":\n      bird.speed.y += 250  # Flap!\n\nif isGameOver:\n   if keyName == \"Space\":\n      # Reset positions of bird and tubes\n      bird.position.y = 200\n      for tube in tubes:\n         tube.position.x += 200\n      isGameOver = False\n",
        "OnPeriodic": "if not isGameOver:\n   bird.speed.y -= 18  # Apply gravity\n   \n   if bird.IsTouchingEdge(card):\n      # Bird hit the floor or ceiling\n      isGameOver = True\n      bird.speed.y = 0\n\n   for tube in tubes:\n      if tube.IsTouching(bird):\n         # Bird hit this tube\n         isGameOver = True\n         bird.speed.y = 0\n\n   for tube in tubes:\n      # Move the tubes\n      tube.position.x -= 3\n      if tube.position.x < -tube.size.width:\n         # Wrap the tubes back to the right edge of the card\n         tube.position.x = card.size.width\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
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
            "penColor": "black",
            "penThickness": 2,
            "fillColor": "#9C00FF"
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
            "penColor": "black",
            "penThickness": 2,
            "fillColor": "#9C00FF"
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
            "penColor": "black",
            "penThickness": 2,
            "fillColor": "#9C00FF"
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
            "penColor": "black",
            "penThickness": 2,
            "fillColor": "#9C00FF"
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
            "penColor": "black",
            "penThickness": 2,
            "fillColor": "#FB0207"
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
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9.2.2"
}
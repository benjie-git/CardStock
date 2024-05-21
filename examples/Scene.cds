{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "can_save": false,
    "author": "",
    "notes": "lots of notes\n\n\ngo here\n\n\n\n\nand here."
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint",
        "on_key_press": "if key_name == \"N\":\n   night.click()\nelif key_name == \"D\":\n   day.click()",
        "on_periodic": "# Create a new piece of snow every 30th of a second, if we can keep up!\no = card.add_oval(\n   size = (10,10),\n   position = (randint(0,490),490),\n   fill_color = 'white',\n   pen_thickness = 1)\n\n# Animate it to the bottom of the stack, moving slightly on the x axis too, for fun.\n# When the animation is complete, run o.delete() to remove the new snow from\n# the card, so we don't accumulate old snow, which would slow down the stack and waste memory.\no.animate_position(\n   randint(300,450)/100.0,\n   (o.position.x + randint(-20,20), -10),\n   on_finished=o.delete)\n"
      },
      "properties": {
        "name": "card_1",
        "size": [
          500,
          500
        ],
        "fill_color": "#88AAFF",
        "can_resize": false
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "card.stop_animating()\ncard.animate_fill_color(1,\"#88AAFF\")\n\ncircle.stop_animating()\ncircle.animate_fill_color(1,\"yellow\")"
          },
          "properties": {
            "name": "day",
            "size": [
              124,
              24
            ],
            "position": [
              39.0,
              425.0
            ],
            "text": "Day",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              143,
              147
            ],
            "position": [
              178.0,
              0.0
            ],
            "originalSize": [
              143,
              147
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "brown"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              143.0,
              147.0
            ]
          ]
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "circle",
            "size": [
              97,
              94
            ],
            "position": [
              386.0,
              373.0
            ],
            "originalSize": [
              97,
              94
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 0,
            "rotation": 0.0,
            "fill_color": "yellow"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              97.0,
              94.0
            ]
          ]
        },
        {
          "type": "polygon",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              232,
              136
            ],
            "position": [
              136.0,
              148.0
            ],
            "originalSize": [
              232,
              136
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "brown"
          },
          "points": [
            [
              232.0,
              0.0
            ],
            [
              119.0,
              136.0
            ],
            [
              0.0,
              1.0
            ]
          ]
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              37,
              58
            ],
            "position": [
              247.0,
              1.0
            ],
            "originalSize": [
              37,
              58
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#A47D5D"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              37.0,
              58.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "card.stop_animating()\ncard.animate_fill_color(1,\"black\")\n\ncircle.stop_animating()\ncircle.animate_fill_color(1,\"grey\")"
          },
          "properties": {
            "name": "night",
            "size": [
              124,
              24
            ],
            "position": [
              39.0,
              455.0
            ],
            "text": "Night",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 9,
  "CardStock_stack_version": "0.99.6"
}
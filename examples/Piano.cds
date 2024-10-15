{
  "type": "stack",
  "handlers": {},
  "properties": {
    "can_save": false,
    "author": "",
    "info": ""
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "current_note = None\nlast_note = None",
        "on_mouse_enter": "current_note = None\nself.send_message(\"update\")",
        "on_mouse_press": "self.send_message(\"update\")",
        "on_mouse_release": "self.send_message(\"update\")",
        "on_message": "if message == \"update\":\n    if last_note and (current_note != last_note or not is_mouse_pressed()):\n        # Time to stop the previous note\n        last_note = None\n        stop_sound()\n    if current_note != last_note and current_note and is_mouse_pressed():\n        # Start playing the currently selected note\n        last_note = current_note\n        play_note(current_note, 6)"
      },
      "properties": {
        "name": "card_1",
        "size": [
          700,
          221
        ],
        "fill_color": "#695028",
        "can_resize": false
      },
      "childModels": [
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"G5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_18",
            "size": [
              45,
              200
            ],
            "position": [
              509.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"C4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_6",
            "size": [
              45,
              200
            ],
            "position": [
              14.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"D4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_7",
            "size": [
              45,
              200
            ],
            "position": [
              59.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"E4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_8",
            "size": [
              45,
              200
            ],
            "position": [
              104.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"F4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_9",
            "size": [
              45,
              200
            ],
            "position": [
              149.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"G4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_10",
            "size": [
              45,
              200
            ],
            "position": [
              194.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"A4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_11",
            "size": [
              45,
              200
            ],
            "position": [
              239.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"B4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_12",
            "size": [
              45,
              200
            ],
            "position": [
              284.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"C#4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_1",
            "size": [
              32,
              100
            ],
            "position": [
              43.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"D#4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_2",
            "size": [
              32,
              100
            ],
            "position": [
              88.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"F#4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_3",
            "size": [
              32,
              100
            ],
            "position": [
              178.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"G#4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_4",
            "size": [
              32,
              100
            ],
            "position": [
              223.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"A#4\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_5",
            "size": [
              32,
              100
            ],
            "position": [
              268.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"C5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_14",
            "size": [
              45,
              200
            ],
            "position": [
              329.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"D5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_15",
            "size": [
              45,
              200
            ],
            "position": [
              374.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"E5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_16",
            "size": [
              45,
              200
            ],
            "position": [
              419.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"F5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_17",
            "size": [
              45,
              200
            ],
            "position": [
              464.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"A5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_19",
            "size": [
              45,
              200
            ],
            "position": [
              554.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"B5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_20",
            "size": [
              45,
              200
            ],
            "position": [
              599.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"C6\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_21",
            "size": [
              45,
              200
            ],
            "position": [
              644.0,
              28.0
            ],
            "originalSize": [
              45,
              197
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "white",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              197.0
            ],
            [
              45.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"C#5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_22",
            "size": [
              32,
              100
            ],
            "position": [
              358.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"D#5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_23",
            "size": [
              32,
              100
            ],
            "position": [
              403.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"F#5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_24",
            "size": [
              32,
              100
            ],
            "position": [
              493.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"G#5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_25",
            "size": [
              32,
              100
            ],
            "position": [
              538.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        },
        {
          "type": "roundrect",
          "handlers": {
            "on_mouse_enter": "current_note = \"A#5\"\ncard.send_message(\"update\")"
          },
          "properties": {
            "name": "roundrect_26",
            "size": [
              32,
              100
            ],
            "position": [
              583.0,
              128.0
            ],
            "originalSize": [
              30,
              130
            ],
            "pen_color": "black",
            "pen_style": "Solid",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#000000",
            "corner_radius": 8
          },
          "points": [
            [
              0.0,
              130.0
            ],
            [
              30.0,
              0.0
            ]
          ]
        }
      ]
    }
  ],
  "CardStock_stack_format": 10,
  "CardStock_stack_version": "0.99.7"
}
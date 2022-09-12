{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\n\nindicators = [oval_1, oval_2, oval_3, oval_4, oval_5]\nfields = [field_1, field_2, field_3, field_4, field_5]\nnums = [0, 0, 0, 0, 0]\nnum_guesses = 0\n\n# Set up field attributes to find next and previous fields\nfor i in range(len(fields)):\n   fields[i].next = fields[(i+1)%5] if i<4 else None\n   fields[i].prev = fields[(i-1)%5] if i>0 else None\n\ndef reset():\n   global num_guesses\n   \n   for i in range(5):\n      nums[i] = randint(0, 9)\n      indicators[i].fill_color = \"white\"\n      fields[i].text = 0\n   num_guesses = 0\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   fields[0].focus()\n   fields[0].select_all()\n\n\ndef check():\n   global num_guesses\n   \n   num_greens = 0\n   num_guesses += 1\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   \n   for i in range(5):\n      n = nums[i]\n      f = int(fields[i].text)\n      if f == n:\n         indicators[i].fill_color = \"green\"\n         num_greens += 1\n      elif f in nums:\n         indicators[i].fill_color = \"blue\"\n      else:\n         indicators[i].fill_color = \"red\"\n      if num_greens == 5:\n         alert(f\"You Won in {num_guesses} guesses!\")\n         reset()\n\nreset()\n",
        "on_key_press": "if key_name == \"Tab\":\n   for f in fields:\n      if f.has_focus:\n         f.select_all()\n\nelif key_name in [\"Backspace\", \"Left\"]:\n   for f in fields:\n      if f.has_focus:\n         if f.prev:\n            f.prev.focus()\n            f.prev.select_all()\n         else:\n            f.select_all()\n         break\n\nelif key_name == \"Right\":\n   for f in fields:\n      if f.has_focus:\n         if f.next:\n            f.next.focus()\n            f.next.select_all()\n         else:\n            f.select_all()\n         break\n         \n"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#F0F0F0"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "rect_1",
            "size": [
              472,
              187
            ],
            "position": [
              14.0,
              24.0
            ],
            "originalSize": [
              472,
              187
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#E0E0E0"
          },
          "points": [
            [
              0.0,
              187.0
            ],
            [
              472.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_changed": "if len(self.text) == 1:\n   field_2.focus()\n   field_2.select_all()",
            "on_text_enter": "guess.click()",
            "on_mouse_release": "self.select_all()"
          },
          "properties": {
            "name": "field_1",
            "size": [
              58,
              70
            ],
            "position": [
              57.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 44,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_1",
            "size": [
              44,
              44
            ],
            "position": [
              64.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_changed": "if len(self.text) == 1:\n   field_3.focus()\n   field_3.select_all()",
            "on_text_enter": "guess.click()",
            "on_mouse_release": "self.select_all()"
          },
          "properties": {
            "name": "field_2",
            "size": [
              58,
              70
            ],
            "position": [
              137.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 44,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_2",
            "size": [
              44,
              44
            ],
            "position": [
              144.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_changed": "if len(self.text) == 1:\n   field_4.focus()\n   field_4.select_all()",
            "on_text_enter": "guess.click()",
            "on_mouse_release": "self.select_all()"
          },
          "properties": {
            "name": "field_3",
            "size": [
              58,
              70
            ],
            "position": [
              217.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 44,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_3",
            "size": [
              44,
              44
            ],
            "position": [
              224.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_changed": "if len(self.text) == 1:\n   field_5.focus()\n   field_5.select_all()",
            "on_text_enter": "guess.click()",
            "on_mouse_release": "self.select_all()"
          },
          "properties": {
            "name": "field_4",
            "size": [
              58,
              70
            ],
            "position": [
              297.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 44,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_4",
            "size": [
              44,
              44
            ],
            "position": [
              304.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_changed": "if len(self.text) == 1:\n   field_1.focus()\n   field_1.select_all()",
            "on_text_enter": "guess.click()",
            "on_mouse_release": "self.select_all()"
          },
          "properties": {
            "name": "field_5",
            "size": [
              58,
              70
            ],
            "position": [
              377.0,
              336.0
            ],
            "text": "0",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 44,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_5",
            "size": [
              44,
              44
            ],
            "position": [
              384.0,
              417.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "check()\nfields[0].focus()\nfields[0].select_all()\n"
          },
          "properties": {
            "name": "guess",
            "size": [
              132,
              28
            ],
            "position": [
              293.0,
              273.0
            ],
            "title": "Guess",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_6",
            "size": [
              44,
              44
            ],
            "position": [
              32.0,
              156.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "green"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
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
              372,
              32
            ],
            "position": [
              91.0,
              159.0
            ],
            "text": "This number is in the correct spot",
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
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_7",
            "size": [
              44,
              44
            ],
            "position": [
              32.0,
              96.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "blue"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              372,
              32
            ],
            "position": [
              91.0,
              99.0
            ],
            "text": "This number is in the wrong spot",
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
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_8",
            "size": [
              44,
              44
            ],
            "position": [
              32.0,
              36.0
            ],
            "originalSize": [
              44,
              44
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "red"
          },
          "points": [
            [
              0.0,
              44.0
            ],
            [
              44.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              372,
              32
            ],
            "position": [
              91.0,
              39.0
            ],
            "text": "This number is not in the answer",
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
            "name": "num_guesses_label",
            "size": [
              194,
              28
            ],
            "position": [
              262.0,
              240.0
            ],
            "text": "Num Guesses: 0",
            "alignment": "Center",
            "text_color": "#666666",
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
            "on_click": "alert(\"The goal of Mastermind is to guess the secret 5-digit number.  enter \"\n\"your guesses for each digit, and click Guess.  Then each digit will be color \"\n\"coded according to whether it is the correct number in the correct spot, \"\n\"a correct number but in the wrong spot, or a wrong digit that's not in the \"\n\"secret number at all.  Then adjust your digits and click Guess again!\")"
          },
          "properties": {
            "name": "help_button",
            "size": [
              55,
              29
            ],
            "position": [
              3.0,
              470.0
            ],
            "title": "Help",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      640
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "from random import randint\n\nwordlist = ['adult', 'agile', 'alarm', 'aloft', 'amber', 'angel', 'arrow', 'bacon', 'bagel', 'basis', 'begin', 'board', 'bride', 'brink', 'carry', 'chain', 'chart', 'cheat', 'chewy', 'clerk', 'close', 'color', 'cover', 'creed', 'cruel', 'cycle', 'death', 'decay', 'ditch', 'dream', 'drift', 'drink', 'evoke', 'fader', 'favor', 'fence', 'flock', 'frank', 'ghost', 'glide', 'grain', 'graze', 'guest', 'handy', 'hardy', 'heart', 'hotel', 'ideal', 'jewel', 'large', 'learn', 'lease', 'major', 'mayor', 'medal', 'miner', 'money', 'motel', 'nerve', 'noble', 'north', 'orbit', 'order', 'paint', 'peace', 'plain', 'pound', 'press', 'price', 'prize', 'proof', 'punch', 'queen', 'quiet', 'ratio', 'rebel', 'refer', 'reign', 'relax', 'round', 'rumor', 'scarf', 'shelf', 'short', 'shout', 'slice', 'smell', 'snail', 'spare', 'speed', 'sport', 'stamp', 'steep', 'store', 'stork', 'strap', 'suite', 'swear', 'swing', 'swipe', 'sword', 'teach', 'tease', 'theft', 'tract', 'trick', 'virus', 'waste', 'water', 'weave', 'zebra']\n\nstr_alpha = \"\"\nstr_alpha_yes = \"\"\nstr_alpha_no = \"\"\n\nindicators = [oval_1, oval_2, oval_3, oval_4, oval_5]\nfields = [field_1, field_2, field_3, field_4, field_5]\nhints = [field_hint_1, field_hint_2, field_hint_3, field_hint_4, field_hint_5]\n\nfor i in range(len(fields)):\n   fields[i].next = fields[(i+1)%5] if i<4 else None\n   fields[i].prev = fields[(i-1)%5] if i>0 else None\n\nchars = ['', '', '', '', '']\nnum_guesses = 0\n\ndef reset():\n   global num_guesses, str_alpha, str_alpha_yes, str_alpha_no\n   \n   word = wordlist[randint(0, len(wordlist))]\n   for i in range(5):\n      chars[i] = word[i].upper()\n      indicators[i].fill_color = \"white\"\n      fields[i].text = ''\n      hints[i].text = ''\n      hints[i].text_color = \"blue\"\n   num_guesses = 0\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   fields[0].focus()\n   fields[0].select_all()\n   \n   str_alpha = \"abcdefghijklmnopqrstuvwxyz\".upper()\n   str_alpha_yes = \"\"\n   str_alpha_no = \"\"\n   update_alpha()\n   \n\ndef load_en_words():\n   words = set()\n   try:\n      f = open(\"/usr/share/dict/words\", 'r')\n      for l in f:\n         words.add(l.strip().upper())\n      return words\n   except:\n      return None\n\n\ndef check():\n   global num_guesses, str_alpha, str_alpha_yes, str_alpha_no\n   \n   word = ''.join([f.text for f in fields])\n   if english_words_set and word not in english_words_set:\n      alert(\"Sorry, I don't know that word.\")\n      return\n   num_greens = 0\n   num_guesses += 1\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   \n   for i in range(5):\n      f = fields[i].text\n      if f in str_alpha:\n         str_alpha = str_alpha.replace(f, \"\")\n         if f in chars:\n            str_alpha_yes += f\n         else:\n            str_alpha_no += f\n         update_alpha()\n   \n   remaining = [c for c in chars]\n   for i in range(5):\n      n = chars[i]\n      f = fields[i].text\n      if f == n:\n         indicators[i].fill_color = \"green\"\n         hints[i].text = f\n         hints[i].text_color = \"green\"\n         num_greens += 1\n         remaining.remove(f)\n   for i in range(5):\n      n = chars[i]\n      f = fields[i].text\n      if f != n:\n         if f in remaining:\n            indicators[i].fill_color = \"blue\"\n            if hints[i].text_color != \"green\" and f not in hints[i].text:\n               hints[i].text += f\n               hints[i].text_color = \"blue\"\n            remaining.remove(f)\n         else:\n            indicators[i].fill_color = \"red\"\n\n   if num_greens == 5:\n      alert(f\"You Won in {num_guesses} guesses!\")\n      reset()\n\ndef update_alpha():\n   alpha_unknown.text = str_alpha\n   alpha_yes.text = str_alpha_yes\n   alpha_no.text = str_alpha_no\n\n\nenglish_words_set = load_en_words()\nreset()",
        "on_key_press": "if key_name == \"Tab\":\n   for f in fields:\n      if f.has_focus:\n         f.select_all()\n\nelif key_name in [\"Backspace\", \"Left\"]:\n   for f in fields:\n      if f.has_focus:\n         if f.prev:\n            f.prev.focus()\n            f.prev.select_all()\n         else:\n            f.select_all()\n         break\n\nelif key_name == \"Right\":\n   for f in fields:\n      if f.has_focus:\n         if f.next:\n            f.next.focus()\n            f.next.select_all()\n         else:\n            f.select_all()\n         break"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#F0F0F0"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {
            "on_text_changed": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.focus()\n   self.next.select_all()",
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
              60.0,
              479.0
            ],
            "text": "",
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
              67.0,
              560.0
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
            "on_text_changed": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.focus()\n   self.next.select_all()",
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
              140.0,
              479.0
            ],
            "text": "",
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
              147.0,
              560.0
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
            "on_text_changed": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.focus()\n   self.next.select_all()",
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
              220.0,
              479.0
            ],
            "text": "",
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
              227.0,
              560.0
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
            "on_text_changed": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.focus()\n   self.next.select_all()",
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
              300.0,
              479.0
            ],
            "text": "",
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
              307.0,
              560.0
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
            "on_text_changed": "if len(self.text):\n   self.text = self.text[0].upper()\n   if self.next:\n      self.next.focus()\n      self.next.select_all()\n   else:\n      self.select_all()",
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
              380.0,
              479.0
            ],
            "text": "",
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
              387.0,
              560.0
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
            "on_click": "alert(\"The goal of Wordel is to guess the secret 5-letter word.  enter \"\n\"your guesses for each letter, and click Guess.  Then each letter will be color \"\n\"coded according to whether it is the correct letter in the correct spot, \"\n\"a correct letter but in the wrong spot, or a wrong letter that's not in the \"\n\"secret word at all.  Then adjust your letters and click Guess again!\")"
          },
          "properties": {
            "name": "help_button",
            "size": [
              55,
              29
            ],
            "position": [
              6.0,
              608.0
            ],
            "title": "Help",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "check()\nfields[0].focus()\nfields[0].select_all()"
          },
          "properties": {
            "name": "guess",
            "size": [
              131,
              27
            ],
            "position": [
              295.0,
              394.0
            ],
            "title": "Guess",
            "style": "Border",
            "is_selected": false,
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
              27
            ],
            "position": [
              265.0,
              359.0
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "alpha_unknown",
            "size": [
              362,
              31
            ],
            "position": [
              23.0,
              318.0
            ],
            "text": "abcdefghijklmnopqrstuvwxyz",
            "alignment": "Left",
            "text_color": "#7F7F7F",
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
            "name": "alpha_no",
            "size": [
              362,
              31
            ],
            "position": [
              23.0,
              236.0
            ],
            "text": "abcdefghijklmnopqrstuvwxyz",
            "alignment": "Left",
            "text_color": "#FB0207",
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
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "rect_1",
            "size": [
              472,
              187
            ],
            "position": [
              17.0,
              22.0
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
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "oval_6",
            "size": [
              44,
              44
            ],
            "position": [
              35.0,
              154.0
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
              94.0,
              157.0
            ],
            "text": "This letter is in the correct spot",
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
              35.0,
              94.0
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
              94.0,
              97.0
            ],
            "text": "This letter is in the wrong spot",
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
              35.0,
              34.0
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
              94.0,
              37.0
            ],
            "text": "This letter is not in the answer",
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
            "name": "field_hint_1",
            "size": [
              58,
              26
            ],
            "position": [
              60.0,
              442.0
            ],
            "text": "",
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "field_hint_2",
            "size": [
              58,
              26
            ],
            "position": [
              140.0,
              442.0
            ],
            "text": "",
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "field_hint_3",
            "size": [
              58,
              26
            ],
            "position": [
              220.0,
              442.0
            ],
            "text": "",
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "field_hint_4",
            "size": [
              58,
              26
            ],
            "position": [
              300.0,
              442.0
            ],
            "text": "",
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
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "alpha_yes",
            "size": [
              362,
              31
            ],
            "position": [
              23.0,
              276.0
            ],
            "text": "abcdefghijklmnopqrstuvwxyz",
            "alignment": "Left",
            "text_color": "blue",
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
            "name": "field_hint_5",
            "size": [
              58,
              26
            ],
            "position": [
              381.0,
              442.0
            ],
            "text": "",
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
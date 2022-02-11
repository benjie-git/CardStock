{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      650
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "from random import randint\n\nwordlist = ['adult', 'agile', 'alarm', 'aloft', 'amber', 'angel', 'arrow', 'bacon', 'bagel', 'basis', 'begin', 'board', 'bride', 'brink', 'carry', 'chain', 'chart', 'cheat', 'chewy', 'clerk', 'close', 'color', 'cover', 'creed', 'cruel', 'cycle', 'death', 'decay', 'ditch', 'dream', 'drift', 'drink', 'evoke', 'fader', 'favor', 'fence', 'flock', 'frank', 'ghost', 'glide', 'grain', 'graze', 'guest', 'handy', 'hardy', 'heart', 'hotel', 'ideal', 'jewel', 'large', 'learn', 'lease', 'major', 'mayor', 'medal', 'miner', 'money', 'motel', 'nerve', 'noble', 'north', 'orbit', 'order', 'paint', 'peace', 'plain', 'pound', 'press', 'price', 'prize', 'proof', 'punch', 'queen', 'quiet', 'ratio', 'rebel', 'refer', 'reign', 'relax', 'round', 'rumor', 'scarf', 'shelf', 'short', 'shout', 'slice', 'smell', 'snail', 'spare', 'speed', 'sport', 'stamp', 'steep', 'store', 'stork', 'strap', 'suite', 'swear', 'swing', 'swipe', 'sword', 'teach', 'tease', 'theft', 'tract', 'trick', 'virus', 'waste', 'water', 'weave', 'zebra']\n\nstr_alpha = \"\"\nstr_alpha_yes = \"\"\nstr_alpha_no = \"\"\n\nindicators = [oval_1, oval_2, oval_3, oval_4, oval_5]\nfields = [field_1, field_2, field_3, field_4, field_5]\nhints = [field_hint_1, field_hint_2, field_hint_3, field_hint_4, field_hint_5]\n\nfor i in range(len(fields)):\n   fields[i].next = fields[(i+1)%5] if i<4 else None\n   fields[i].prev = fields[(i-1)%5] if i>0 else None\n\nchars = ['', '', '', '', '']\nnum_guesses = 0\n\ndef reset():\n   global num_guesses, str_alpha, str_alpha_yes, str_alpha_no\n   \n   word = wordlist[randint(0, len(wordlist))]\n   for i in range(5):\n      chars[i] = word[i].upper()\n      indicators[i].fillColor = \"white\"\n      fields[i].text = ''\n      hints[i].text = ''\n      hints[i].textColor = \"blue\"\n   num_guesses = 0\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   fields[0].Focus()\n   fields[0].SelectAll()\n   \n   str_alpha = \"abcdefghijklmnopqrstuvwxyz\".upper()\n   str_alpha_yes = \"\"\n   str_alpha_no = \"\"\n   update_alpha()\n   \n\n\ndef load_en_words():\n   words = set()\n   try:\n      f = open(\"/usr/share/dict/words\", 'r')\n      for l in f:\n         words.add(l.strip().upper())\n      return words\n   except:\n      return None\n\n\ndef check():\n   global num_guesses, str_alpha, str_alpha_yes, str_alpha_no\n   \n   word = ''.join([f.text for f in fields])\n   if english_words_set and word not in english_words_set:\n      Alert(\"Sorry, I don't know that word.\")\n      return\n   num_greens = 0\n   num_guesses += 1\n   num_guesses_label.text = \"Num Guesses: \" + str(num_guesses)\n   \n   for i in range(5):\n      f = fields[i].text\n      if f in str_alpha:\n         str_alpha = str_alpha.replace(f, \"\")\n         if f in chars:\n            str_alpha_yes += f\n         else:\n            str_alpha_no += f\n         update_alpha()\n   \n   remaining = [c for c in chars]\n   for i in range(5):\n      n = chars[i]\n      f = fields[i].text\n      if f == n:\n         indicators[i].fillColor = \"green\"\n         hints[i].text = f\n         hints[i].textColor = \"green\"\n         num_greens += 1\n         remaining.remove(f)\n   for i in range(5):\n      n = chars[i]\n      f = fields[i].text\n      if f != n:\n         if f in remaining:\n            indicators[i].fillColor = \"blue\"\n            if hints[i].textColor != \"green\" and f not in hints[i].text:\n               hints[i].text += f\n               hints[i].textColor = \"blue\"\n            remaining.remove(f)\n         else:\n            indicators[i].fillColor = \"red\"\n\n   if num_greens == 5:\n      Alert(f\"You Won in {num_guesses} guesses!\")\n      reset()\n\ndef update_alpha():\n   alpha_unknown.text = str_alpha\n   alpha_yes.text = str_alpha_yes\n   alpha_no.text = str_alpha_no\n\n\nenglish_words_set = load_en_words()\nreset()\n",
        "OnKeyDown": "if keyName == \"Tab\":\n   for f in fields:\n      if f.hasFocus:\n         f.SelectAll()\n\nelif keyName in [\"Backspace\", \"Left\"]:\n   for f in fields:\n      if f.hasFocus:\n         if f.prev:\n            f.prev.Focus()\n            f.prev.SelectAll()\n         else:\n            f.SelectAll()\n         break\n\nelif keyName == \"Right\":\n   for f in fields:\n      if f.hasFocus:\n         if f.next:\n            f.next.Focus()\n            f.next.SelectAll()\n         else:\n            f.SelectAll()\n         break\n"
      },
      "properties": {
        "name": "card_1",
        "fillColor": "#F0F0F0"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {
            "OnTextChanged": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.Focus()\n   self.next.SelectAll()",
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "isEditable": true,
            "isMultiline": false
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "white"
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
            "OnTextChanged": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.Focus()\n   self.next.SelectAll()",
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "isEditable": true,
            "isMultiline": false
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "white"
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
            "OnTextChanged": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.Focus()\n   self.next.SelectAll()",
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "isEditable": true,
            "isMultiline": false
          }
        },
        {
          "type": "oval",
          "handlers": {
            "OnMouseEnter": "zzz=1"
          },
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "white"
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
            "OnTextChanged": "if len(self.text):\n   self.text = self.text[0].upper()\n   self.next.Focus()\n   self.next.SelectAll()",
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "isEditable": true,
            "isMultiline": false
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "white"
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
            "OnTextChanged": "if len(self.text):\n   self.text = self.text[0].upper()\n   if self.next:\n      self.next.Focus()\n      self.next.SelectAll()\n   else:\n      self.SelectAll()",
            "OnTextEnter": "guess.Click()",
            "OnMouseUp": "self.SelectAll()"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 44,
            "isEditable": true,
            "isMultiline": false
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "white"
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
            "OnClick": "Alert(\"The goal of Wordel is to guess the secret 5-letter word.  Enter \"\n\"your guesses for each letter, and click Guess.  Then each letter will be color \"\n\"coded according to whether it is the correct letter in the correct spot, \"\n\"a correct letter but in the wrong spot, or a wrong letter that's not in the \"\n\"secret word at all.  Then adjust your letters and click Guess again!\")"
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
            "hasBorder": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "check()\nfields[0].Focus()\nfields[0].SelectAll()\n"
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
            "hasBorder": true
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
            "textColor": "#666666",
            "font": "Default",
            "fontSize": 14,
            "canAutoShrink": true,
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
            "textColor": "#7F7F7F",
            "font": "Default",
            "fontSize": 18,
            "canAutoShrink": true,
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
            "textColor": "#FB0207",
            "font": "Default",
            "fontSize": 18,
            "canAutoShrink": true,
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
            "penColor": "black",
            "penThickness": 2,
            "rotation": 0.0,
            "fillColor": "#E0E0E0"
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "green"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 18,
            "canAutoShrink": true,
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "blue"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 18,
            "canAutoShrink": true,
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
            "penColor": "black",
            "penThickness": 4,
            "rotation": 0.0,
            "fillColor": "red"
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 18,
            "canAutoShrink": true,
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
            "textColor": "#666666",
            "font": "Default",
            "fontSize": 14,
            "canAutoShrink": true,
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
            "textColor": "#666666",
            "font": "Default",
            "fontSize": 14,
            "canAutoShrink": true,
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
            "textColor": "#666666",
            "font": "Default",
            "fontSize": 14,
            "canAutoShrink": true,
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
            "textColor": "#666666",
            "font": "Default",
            "fontSize": 14,
            "canAutoShrink": true,
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
            "textColor": "blue",
            "font": "Default",
            "fontSize": 18,
            "canAutoShrink": true,
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
            "textColor": "#666666",
            "font": "Default",
            "fontSize": 14,
            "canAutoShrink": true,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 3,
  "CardStock_stack_version": "0.9.8"
}
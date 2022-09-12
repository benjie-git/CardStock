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
        "on_setup": "from random import randint\n"
      },
      "properties": {
        "name": "home",
        "fill_color": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"minus\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              253.0
            ],
            "title": "-",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"plus\")"
          },
          "properties": {
            "name": "button_2",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              333.0
            ],
            "title": "+",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"times\")"
          },
          "properties": {
            "name": "button_3",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              173.0
            ],
            "title": "*",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"divide\")"
          },
          "properties": {
            "name": "button_4",
            "size": [
              84,
              21
            ],
            "position": [
              278.0,
              93.0
            ],
            "title": "\u00f7",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              280,
              129
            ],
            "position": [
              54.0,
              331.0
            ],
            "text": "Choose a Math Operation to Practice",
            "alignment": "Left",
            "text_color": "red",
            "font": "Default",
            "font_size": 24,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_show_card": "label_1.text = randint(0,100)\nlabel_2.text = randint(0,100)\n\nanswer.text = \"\"\nanswer.focus()\n"
      },
      "properties": {
        "name": "plus",
        "fill_color": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              467.0
            ],
            "title": "Home",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 + num2:\n   lastCardName = \"plus\"\n   goto_card(\"correct\")\nelse:\n   alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              276.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              31,
              32
            ],
            "position": [
              209.0,
              315.0
            ],
            "text": "+",
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
            "name": "label_2",
            "size": [
              64,
              30
            ],
            "position": [
              238.0,
              311.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
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
            "name": "label_1",
            "size": [
              64,
              30
            ],
            "position": [
              238.0,
              347.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_show_card": "num1 = randint(0,100)\nnum2 = randint(0,num1)\nlabel_1.text = num1\nlabel_2.text = num2\n\nanswer.text = \"\"\nanswer.focus()\n"
      },
      "properties": {
        "name": "minus",
        "fill_color": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              467.0
            ],
            "title": "Home",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 - num2:\n   lastCardName = \"minus\"\n   goto_card(\"correct\")\nelse:\n   alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              275.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              317.0
            ],
            "text": "-",
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
            "name": "label_2",
            "size": [
              60,
              30
            ],
            "position": [
              242.0,
              311.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
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
            "name": "label_1",
            "size": [
              60,
              28
            ],
            "position": [
              242.0,
              349.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_show_card": "label_1.text = randint(0,100)\nlabel_2.text = randint(0,100)\n\nanswer.text = \"\"\nanswer.focus()\n"
      },
      "properties": {
        "name": "minus_1",
        "fill_color": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              467.0
            ],
            "title": "Home",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 - num2:\n   lastCardName = \"minus\"\n   goto_card(\"correct\")\nelse:\n   alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              275.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              317.0
            ],
            "text": "-",
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
            "name": "label_2",
            "size": [
              60,
              30
            ],
            "position": [
              242.0,
              311.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
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
            "name": "label_1",
            "size": [
              60,
              28
            ],
            "position": [
              242.0,
              349.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_show_card": "label_1.text = randint(1,13)\nlabel_2.text = randint(0,13)\n\nanswer.text = \"\"\nanswer.focus()\n"
      },
      "properties": {
        "name": "times",
        "fill_color": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              467.0
            ],
            "title": "Home",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 * num2:\n   lastCardName = \"times\"\n   goto_card(\"correct\")\nelse:\n   alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              275.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              317.0
            ],
            "text": "X",
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
            "name": "label_2",
            "size": [
              61,
              30
            ],
            "position": [
              241.0,
              311.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
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
            "name": "label_1",
            "size": [
              60,
              29
            ],
            "position": [
              242.0,
              348.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_show_card": "a = randint(1,12)\nb = a * randint(1,12)\nlabel_1.text = b\nlabel_2.text = a\n\nanswer.text = \"\"\nanswer.focus()\n"
      },
      "properties": {
        "name": "divide",
        "fill_color": "#DDCCBB"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_card(\"home\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              11.0,
              467.0
            ],
            "title": "Home",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "num1 = int(label_1.text)\nnum2 = int(label_2.text)\nansNum = int(answer.text)\n\nif ansNum == num1 / num2:\n   lastCardName = \"divide\"\n   goto_card(\"correct\")\nelse:\n   alert(\"Hmmm.. Not quite right.  Try again!\")\n   self.text = \"\"\n"
          },
          "properties": {
            "name": "answer",
            "size": [
              105,
              22
            ],
            "position": [
              198.0,
              275.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "op",
            "size": [
              30,
              25
            ],
            "position": [
              213.0,
              317.0
            ],
            "text": "\u00f7",
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
            "name": "label_2",
            "size": [
              60,
              29
            ],
            "position": [
              242.0,
              312.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
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
            "name": "label_1",
            "size": [
              60,
              28
            ],
            "position": [
              242.0,
              349.0
            ],
            "text": "0",
            "alignment": "Right",
            "text_color": "black",
            "font": "Default",
            "font_size": 16,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {
        "on_show_card": "play_sound(\"yay.wav\")\nwait(2)\ngoto_card(lastCardName)\n"
      },
      "properties": {
        "name": "correct",
        "fill_color": "#FFFFDD"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              396,
              64
            ],
            "position": [
              41.0,
              378.0
            ],
            "text": "Good Job!!!",
            "alignment": "Center",
            "text_color": "red",
            "font": "Serif",
            "font_size": 40,
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
            "name": "label_2",
            "size": [
              405,
              85
            ],
            "position": [
              38.0,
              298.0
            ],
            "text": "You did it!",
            "alignment": "Center",
            "text_color": "green",
            "font": "Default",
            "font_size": 35,
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
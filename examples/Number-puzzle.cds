{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      603,
      250
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "import random\n\nlabels = [label_1, label_2, label_3, label_4, label_5,\n   label_6, label_7, label_8, label_9]\n\ndef reset():\n   digits = \"123456789\"\n\n   digitList = list(digits)\n   random.shuffle(digitList)\n   numberStr = ''.join(digitList)\n\n   for i in range(9):\n      labels[i].text = numberStr[i]\n\ndef swap(num):\n   str = [label.text for label in labels[:num]]\n   for i in range(num):\n      labels[i].text = str[num-i-1]\n   \n   if ''.join([label.text for label in labels]) == \"123456789\":\n      play_sound(\"yay.wav\")\n      wait(2)\n      reset()\n\nreset()"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {
            "on_mouse_press": "swap(2)"
          },
          "properties": {
            "name": "label_2",
            "size": [
              58,
              60
            ],
            "position": [
              90.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
          "handlers": {
            "on_mouse_press": "swap(3)"
          },
          "properties": {
            "name": "label_3",
            "size": [
              58,
              60
            ],
            "position": [
              150.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
          "handlers": {
            "on_mouse_press": "swap(4)"
          },
          "properties": {
            "name": "label_4",
            "size": [
              58,
              60
            ],
            "position": [
              210.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
          "handlers": {
            "on_mouse_press": "swap(5)"
          },
          "properties": {
            "name": "label_5",
            "size": [
              58,
              60
            ],
            "position": [
              270.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
          "handlers": {
            "on_mouse_press": "swap(6)"
          },
          "properties": {
            "name": "label_6",
            "size": [
              58,
              60
            ],
            "position": [
              330.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
          "handlers": {
            "on_mouse_press": "swap(7)"
          },
          "properties": {
            "name": "label_7",
            "size": [
              58,
              60
            ],
            "position": [
              390.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
          "handlers": {
            "on_mouse_press": "swap(8)"
          },
          "properties": {
            "name": "label_8",
            "size": [
              58,
              60
            ],
            "position": [
              450.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
          "handlers": {
            "on_mouse_press": "swap(9)"
          },
          "properties": {
            "name": "label_9",
            "size": [
              58,
              60
            ],
            "position": [
              510.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
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
            "name": "label_10",
            "size": [
              485,
              38
            ],
            "position": [
              59.0,
              191.0
            ],
            "text": "Reorder the numbers from 1-9",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 24,
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
            "name": "label_11",
            "size": [
              563,
              28
            ],
            "position": [
              23.0,
              152.0
            ],
            "text": "Click a number to flip it, along with all numbers to its left.",
            "alignment": "Center",
            "text_color": "#626262",
            "font": "Default",
            "font_size": 15,
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
              58,
              60
            ],
            "position": [
              30.0,
              52.0
            ],
            "text": "1",
            "alignment": "Center",
            "text_color": "black",
            "font": "Mono",
            "font_size": 40,
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
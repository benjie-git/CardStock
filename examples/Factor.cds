{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      495
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "import math\n\ndef factor(n):\n   # Test for -1\n   if n < 0:\n      output.text += \"-1\\n\"\n      factor(-n)\n      return\n\n   # Test for 0 or 1\n   if n <= 1:\n      return\n   \n   # Test for 2\n   if n % 2 == 0:\n      output.text += str(2) + \"\\n\"\n      factor(int(n/2))\n      return\n\n   # Test for 3+ odds\n   for d in range(3, n+1, 2):\n      if n % d == 0:\n         output.text += str(d) + \"\\n\"\n         factor(int(n/d))\n         return\n",
        "on_show_card": "field.focus()\n"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#DDEEDD"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "button.click()"
          },
          "properties": {
            "name": "field",
            "size": [
              150,
              24
            ],
            "position": [
              122.0,
              393.0
            ],
            "text": "",
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
          "type": "button",
          "handlers": {
            "on_click": "output.text = \"\"\n\ntry:\n   num = int(field.text)\n   factor(num)\nexcept:\n   pass\n\nfield.focus()"
          },
          "properties": {
            "name": "button",
            "size": [
              84,
              21
            ],
            "position": [
              286.0,
              394.0
            ],
            "title": "Find!",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "output",
            "size": [
              390,
              305
            ],
            "position": [
              52.0,
              54.0
            ],
            "text": "",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": false,
            "is_multiline": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              379,
              38
            ],
            "position": [
              57.0,
              428.0
            ],
            "text": "Enter a number to Prime Factor:",
            "alignment": "Center",
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
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
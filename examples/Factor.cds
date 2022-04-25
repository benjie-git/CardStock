{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      495
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "import math\n\ndef factor(n):\n   # Test for -1\n   if n < 0:\n      output.text += \"-1\\n\"\n      factor(-n)\n      return\n\n   # Test for 0 or 1\n   if n <= 1:\n      return\n   \n   # Test for 2\n   if n % 2 == 0:\n      output.text += str(2) + \"\\n\"\n      factor(int(n/2))\n      return\n\n   # Test for 3+ odds\n   for d in range(3, n+1, 2):\n      if n % d == 0:\n         output.text += str(d) + \"\\n\"\n         factor(int(n/d))\n         return\n",
        "OnShowCard": "field.Focus()\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#DDEEDD"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "button.Click()"
          },
          "properties": {
            "name": "field",
            "size": [
              105,
              22
            ],
            "position": [
              136.0,
              79.0
            ],
            "text": "",
            "alignment": "Right",
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "num = int(field.text)\noutput.text = \"\"\nfactor(num)\n"
          },
          "properties": {
            "name": "button",
            "size": [
              84,
              21
            ],
            "position": [
              261.0,
              80.0
            ],
            "title": "Find!",
            "border": true
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
              136.0
            ],
            "text": "",
            "alignment": "Left",
            "editable": false,
            "multiline": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              377,
              33
            ],
            "position": [
              58.0,
              34.0
            ],
            "text": "Enter a number to Prime Factor:",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 16
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.7"
}
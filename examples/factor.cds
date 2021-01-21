{
  "type": "stack",
  "handlers": {
    "OnStackStart": "import math\n"
  },
  "properties": {
    "name": "",
    "size": [
      500,
      495
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
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
            "OnTextEnter": "button.DoClick()"
          },
          "properties": {
            "name": "field",
            "size": [
              105,
              22
            ],
            "position": [
              136,
              79
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
            "OnClick": "num = int(field.GetText())\noutput.SetText(\"\")\n\ndef factor(n):\n   if n < 0:\n      output.AppendText(\"-1\\n\")\n      factor(-n)\n      return\n   if n <= 1: return\n   divisors = [2]\n   divisors.extend(range(3, n+1, 2))\n   for d in divisors:\n      if n % d == 0:\n         output.AppendText(str(d) + \"\\n\")\n         factor(int(n/d))\n         return\n\nfactor(num)\n"
          },
          "properties": {
            "name": "button",
            "size": [
              84,
              21
            ],
            "position": [
              261,
              80
            ],
            "title": "Find!"
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
              52,
              136
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
              295,
              35
            ],
            "position": [
              105,
              32
            ],
            "text": "Enter a number to Prime Factor:",
            "alignment": "Center",
            "textColor": "black",
            "font": "Helvetica",
            "fontSize": "18"
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
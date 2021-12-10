{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      603,
      250
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "import random\n\nlabels = [label_1, label_2, label_3, label_4, label_5,\n   label_6, label_7, label_8, label_9]\n\ndef reset():\n   digits = \"123456789\"\n\n   digitList = list(digits)\n   random.shuffle(digitList)\n   numberStr = ''.join(digitList)\n\n   for i in range(9):\n      labels[i].text = numberStr[i]\n\ndef swap(num):\n   str = [label.text for label in labels[:num]]\n   for i in range(num):\n      labels[i].text = str[num-i-1]\n   \n   if ''.join([label.text for label in labels]) == \"123456789\":\n      PlaySound(\"yay.wav\")\n      Wait(2)\n      reset()\n\nreset()"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(2)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(3)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(4)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(5)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(6)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(7)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(8)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnMouseDown": "swap(9)"
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
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
            "textColor": "black",
            "font": "Default",
            "fontSize": 24
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
            "textColor": "#626262",
            "font": "Default",
            "fontSize": 15
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
            "textColor": "black",
            "font": "Mono",
            "fontSize": 40
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.9"
}
{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "# Requires installing pyserial\nimport serial\n\nser = None"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#BFBFBF"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {
            "OnIdle": "if ser:\n   bytes = ser.read(1024)\n   if len(bytes):\n      self.text += bytes.decode(\"utf-8\")"
          },
          "properties": {
            "name": "receiveField",
            "size": [
              390,
              331
            ],
            "position": [
              55.0,
              111.0
            ],
            "text": "",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": false,
            "multiline": true
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "if ser:\n   ser.write(self.text.encode(\"utf-8\"))\n   self.text = \"\""
          },
          "properties": {
            "name": "sendField",
            "size": [
              391,
              30
            ],
            "position": [
              55.0,
              441.0
            ],
            "text": "",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "ser = serial.Serial(devField.text, timeout=0)\nsendField.Focus()"
          },
          "properties": {
            "name": "connect",
            "size": [
              88,
              20
            ],
            "position": [
              328.0,
              31.0
            ],
            "title": "Connect",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "connect.Click()"
          },
          "properties": {
            "name": "devField",
            "size": [
              264,
              29
            ],
            "position": [
              56.0,
              26.0
            ],
            "text": "/dev/ttyUSB0",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.8.4"
}
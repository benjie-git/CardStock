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
        "on_setup": "# A minimal example of using pyserial to talk over a serial port.\n# May require installing pyserial, if you're not running a prebuilt CardStock app.\nimport serial\nser = None"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#BFBFBF"
      },
      "childModels": [
        {
          "type": "textfield",
          "handlers": {
            "on_periodic": "if ser:\n   bytes = ser.read(1024)\n   if len(bytes):\n      self.text += bytes.decode(\"utf-8\")"
          },
          "properties": {
            "name": "receiveField",
            "size": [
              390,
              331
            ],
            "position": [
              55.0,
              58.0
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
          "type": "textfield",
          "handlers": {
            "on_text_enter": "if ser:\n   ser.write(self.text.encode(\"utf-8\"))\n   self.text = \"\""
          },
          "properties": {
            "name": "sendField",
            "size": [
              391,
              30
            ],
            "position": [
              55.0,
              29.0
            ],
            "text": "",
            "alignment": "Left",
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
            "on_click": "ser = serial.Serial(devField.text, timeout=0)\nsendField.focus()"
          },
          "properties": {
            "name": "connect",
            "size": [
              88,
              20
            ],
            "position": [
              328.0,
              449.0
            ],
            "title": "Connect",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "connect.click()"
          },
          "properties": {
            "name": "devField",
            "size": [
              264,
              29
            ],
            "position": [
              56.0,
              445.0
            ],
            "text": "/dev/ttyUSB0",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "is_editable": true,
            "is_multiline": false
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
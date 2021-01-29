{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "import requests\nimport json\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#AABBCC"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "result = requests.get('https://geek-jokes.sameerkumar.website/api?format=json')\ndict = json.loads(result.text)\nfield_1.text = dict[\"joke\"]\n"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              187,
              71
            ],
            "title": "Get it",
            "border": true
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field_1",
            "size": [
              244,
              173
            ],
            "position": [
              106,
              144
            ],
            "text": "Want to hear a joke?",
            "alignment": "Left",
            "editable": true,
            "multiline": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1
}
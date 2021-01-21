{
  "type": "stack",
  "handlers": {},
  "properties": {
    "name": "",
    "size": [
      500,
      500
    ]
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnShowCard": "import requests\nimport json\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#AABBCC"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "r = requests.get('https://geek-jokes.sameerkumar.website/api?format=json')\nd = json.loads(r.text)\nfield_1.SetText(d[\"joke\"])"
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
            "title": "Get it"
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
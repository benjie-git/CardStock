{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      463,
      381
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "OnSetup": "# requires you to have the python requests package installed\n# run: pip install requests\nimport requests\nimport json\n"
      },
      "properties": {
        "name": "card_1",
        "bgColor": "#AABBCC"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "field_1.text = \"Loading...\"\nresult = requests.get('https://geek-jokes.sameerkumar.website/api?format=json')\ndict = json.loads(result.text)\nfield_1.text = dict[\"joke\"]\n"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              187.0,
              71.0
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
              106.0,
              144.0
            ],
            "text": "Want to hear a joke?",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": false,
            "multiline": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.8"
}
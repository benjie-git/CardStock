{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      463,
      381
    ],
    "can_save": false,
    "can_resize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {
        "on_setup": "# A minimal example showing how to use the requests API in CardStock\nimport requests\nimport json"
      },
      "properties": {
        "name": "card_1",
        "fill_color": "#AABBCC"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "on_click": "# Show loading while we wait for the API result.\nfield_1.text = \"Loading...\"\n\n# Make an API hit to a public joke-serving API.\nresult = requests.get('https://geek-jokes.sameerkumar.website/api?format=json')\n\n# When the result comes back, parse it as json,\ndict = json.loads(result.text)\n# and display the \"joke\" field from the resulting dictionary.\nfield_1.text = dict[\"joke\"]"
          },
          "properties": {
            "name": "button_1",
            "size": [
              84,
              21
            ],
            "position": [
              187.0,
              289.0
            ],
            "title": "Get it",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
              64.0
            ],
            "text": "Want to hear a joke?",
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
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
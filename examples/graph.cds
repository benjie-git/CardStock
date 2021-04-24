{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      691,
      387
    ],
    "canSave": false,
    "canResize": false
  },
  "cards": [
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "card_1",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "items = [float(l) for l in field.text.split('\\n') if len(l)]\nlow = min(items)\nhigh = max(items)\nnum = len(items)\n\npos = graph_frame.position\ns = graph_frame.size\n\nxStep = (s.width-2)/(num-1)\nyStep = (s.height-2)/(high-low)\n\npoints = []\nfor i in range(len(items)):\n   points.append((xStep*i+pos.x, yStep*(items[i]-low)+pos.y))\n\nfor obj in card.children:\n   if obj.name == \"line_1\":\n      obj.Delete()\nline = card.AddLine(points, \"line_1\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              72,
              28
            ],
            "position": [
              127.0,
              347.0
            ],
            "title": "Graph It",
            "border": true
          }
        },
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "graph_frame",
            "size": [
              568,
              329
            ],
            "position": [
              115.0,
              10.0
            ],
            "originalSize": [
              428,
              221
            ],
            "penColor": "grey",
            "penThickness": 2,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              221.0
            ],
            [
              428.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "field",
            "size": [
              102,
              378
            ],
            "position": [
              4.0,
              6.0
            ],
            "text": "1\n1.1\n1.2\n1.4\n1.7\n2.3\n3.5\n4.5\n4.9\n5.1\n5.2\n5.3\n5.4\n5.45\n5.47\n5.45\n5.4\n5.3\n5.2\n5.1\n4.9\n4.5\n3.5\n2.3\n1.7\n1.4\n1.2\n1.1\n1\n",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": true
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.8.12"
}
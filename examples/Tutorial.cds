{
  "type": "stack",
  "handlers": {},
  "properties": {
    "size": [
      500,
      500
    ],
    "canSave": false,
    "canResize": true
  },
  "cards": [
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "welcome",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_5",
            "size": [
              240,
              40
            ],
            "position": [
              116.0,
              447.0
            ],
            "text": "(Later, when you run the stack, this button will take you to the next card.)",
            "alignment": "Right",
            "textColor": "black",
            "font": "Default",
            "fontSize": 9
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              351,
              38
            ],
            "position": [
              79.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_4",
            "size": [
              350,
              38
            ],
            "position": [
              28.0,
              91.0
            ],
            "text": "A CardStock program is called a stack.  And each page of your program is called a card.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "OnSetup": "self.Hide()"
          },
          "properties": {
            "name": "label_6",
            "size": [
              408,
              83
            ],
            "position": [
              30.0,
              204.0
            ],
            "text": "Here in the Designer, you can move to\nthe next card by clicking the \"Next Card\" \nbutton in the top right of this window...",
            "alignment": "Left",
            "textColor": "red",
            "font": "Default",
            "fontSize": 14
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "labels",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              351,
              38
            ],
            "position": [
              79.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              330,
              66
            ],
            "position": [
              34.0,
              92.0
            ],
            "text": "You can draw objects like buttons,\ntext fields, text labels, and shapes\nonto your cards using the tools up here.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_6",
            "size": [
              105,
              97
            ],
            "position": [
              372.0,
              44.0
            ],
            "originalSize": [
              115,
              88
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              88.0
            ],
            [
              115.0,
              0.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_7",
            "size": [
              23,
              21
            ],
            "position": [
              471.0,
              33.0
            ],
            "originalSize": [
              23,
              21
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              7.0,
              0.0
            ],
            [
              13.0,
              0.0
            ],
            [
              19.0,
              1.0
            ],
            [
              23.0,
              4.0
            ],
            [
              21.0,
              8.0
            ],
            [
              17.0,
              11.0
            ],
            [
              15.0,
              16.0
            ],
            [
              13.0,
              21.0
            ],
            [
              9.0,
              19.0
            ],
            [
              6.0,
              15.0
            ],
            [
              5.0,
              9.0
            ],
            [
              2.0,
              5.0
            ],
            [
              0.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              336,
              85
            ],
            "position": [
              34.0,
              212.0
            ],
            "text": "For example, this is a Text Label.  It shows text, but is not editable when you run the stack.  But in the Designer, you can double click it to edit the text.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "fields",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              351,
              38
            ],
            "position": [
              79.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              330,
              66
            ],
            "position": [
              34.0,
              92.0
            ],
            "text": "You can draw objects like buttons,\ntext fields, text labels, and shapes\nonto your cards using the tools up here.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_6",
            "size": [
              105,
              97
            ],
            "position": [
              372.0,
              44.0
            ],
            "originalSize": [
              115,
              88
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              88.0
            ],
            [
              115.0,
              0.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_7",
            "size": [
              23,
              21
            ],
            "position": [
              471.0,
              33.0
            ],
            "originalSize": [
              23,
              21
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              7.0,
              0.0
            ],
            [
              13.0,
              0.0
            ],
            [
              19.0,
              1.0
            ],
            [
              23.0,
              4.0
            ],
            [
              21.0,
              8.0
            ],
            [
              17.0,
              11.0
            ],
            [
              15.0,
              16.0
            ],
            [
              13.0,
              21.0
            ],
            [
              9.0,
              19.0
            ],
            [
              6.0,
              15.0
            ],
            [
              5.0,
              9.0
            ],
            [
              2.0,
              5.0
            ],
            [
              0.0,
              0.0
            ]
          ]
        },
        {
          "type": "textfield",
          "handlers": {
            "OnTextEnter": "self.text = \"You pressed enter.\""
          },
          "properties": {
            "name": "field_1",
            "size": [
              222,
              29
            ],
            "position": [
              73.0,
              269.0
            ],
            "text": "Edit me!  I'm a Text Field.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12,
            "editable": true,
            "multiline": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              400,
              45
            ],
            "position": [
              34.0,
              192.0
            ],
            "text": "And below is a Text Field.  It lets users of your stack enter and edit text, that your stack can use.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "buttons",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              351,
              38
            ],
            "position": [
              79.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              330,
              66
            ],
            "position": [
              34.0,
              92.0
            ],
            "text": "You can draw objects like buttons,\ntext fields, text labels, and shapes\nonto your cards using the tools up here.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_6",
            "size": [
              105,
              97
            ],
            "position": [
              372.0,
              44.0
            ],
            "originalSize": [
              115,
              88
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              88.0
            ],
            [
              115.0,
              0.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_7",
            "size": [
              23,
              21
            ],
            "position": [
              471.0,
              33.0
            ],
            "originalSize": [
              23,
              21
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              7.0,
              0.0
            ],
            [
              13.0,
              0.0
            ],
            [
              19.0,
              1.0
            ],
            [
              23.0,
              4.0
            ],
            [
              21.0,
              8.0
            ],
            [
              17.0,
              11.0
            ],
            [
              15.0,
              16.0
            ],
            [
              13.0,
              21.0
            ],
            [
              9.0,
              19.0
            ],
            [
              6.0,
              15.0
            ],
            [
              5.0,
              9.0
            ],
            [
              2.0,
              5.0
            ],
            [
              0.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              400,
              45
            ],
            "position": [
              34.0,
              192.0
            ],
            "text": "Buttons let your program do something when they are clicked.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "card.bgColor = \"#DDFFEE\""
          },
          "properties": {
            "name": "button_1",
            "size": [
              150,
              27
            ],
            "position": [
              108.0,
              262.0
            ],
            "title": "I am a Button",
            "border": true
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "images",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              351,
              38
            ],
            "position": [
              79.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              330,
              66
            ],
            "position": [
              34.0,
              92.0
            ],
            "text": "You can draw objects like buttons,\ntext fields, text labels, and shapes\nonto your cards using the tools up here.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_6",
            "size": [
              105,
              97
            ],
            "position": [
              372.0,
              44.0
            ],
            "originalSize": [
              115,
              88
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              88.0
            ],
            [
              115.0,
              0.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_7",
            "size": [
              23,
              21
            ],
            "position": [
              471.0,
              33.0
            ],
            "originalSize": [
              23,
              21
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              7.0,
              0.0
            ],
            [
              13.0,
              0.0
            ],
            [
              19.0,
              1.0
            ],
            [
              23.0,
              4.0
            ],
            [
              21.0,
              8.0
            ],
            [
              17.0,
              11.0
            ],
            [
              15.0,
              16.0
            ],
            [
              13.0,
              21.0
            ],
            [
              9.0,
              19.0
            ],
            [
              6.0,
              15.0
            ],
            [
              5.0,
              9.0
            ],
            [
              2.0,
              5.0
            ],
            [
              0.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              400,
              45
            ],
            "position": [
              34.0,
              192.0
            ],
            "text": "Image objects can show an image from a file, and you can also draw shapes.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "image",
          "handlers": {},
          "properties": {
            "name": "image_1",
            "size": [
              103,
              129
            ],
            "position": [
              62.0,
              270.0
            ],
            "file": "ship-on.png",
            "fit": "Center",
            "rotation": 0,
            "xFlipped": false,
            "yFlipped": false
          }
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              108,
              99
            ],
            "position": [
              211.0,
              276.0
            ],
            "originalSize": [
              60,
              55
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "white",
            "cornerRadius": 12
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              60.0,
              55.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_5",
            "size": [
              56,
              63
            ],
            "position": [
              237.0,
              295.0
            ],
            "originalSize": [
              134,
              190
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              72.0,
              43.0
            ],
            [
              74.0,
              38.0
            ],
            [
              76.0,
              34.0
            ],
            [
              79.0,
              31.0
            ],
            [
              82.0,
              27.0
            ],
            [
              85.0,
              24.0
            ],
            [
              88.0,
              20.0
            ],
            [
              92.0,
              17.0
            ],
            [
              95.0,
              14.0
            ],
            [
              99.0,
              12.0
            ],
            [
              105.0,
              11.0
            ],
            [
              112.0,
              11.0
            ],
            [
              116.0,
              13.0
            ],
            [
              119.0,
              16.0
            ],
            [
              122.0,
              19.0
            ],
            [
              125.0,
              22.0
            ],
            [
              127.0,
              27.0
            ],
            [
              129.0,
              32.0
            ],
            [
              131.0,
              37.0
            ],
            [
              132.0,
              43.0
            ],
            [
              133.0,
              48.0
            ],
            [
              134.0,
              54.0
            ],
            [
              134.0,
              61.0
            ],
            [
              134.0,
              68.0
            ],
            [
              134.0,
              74.0
            ],
            [
              132.0,
              79.0
            ],
            [
              131.0,
              82.0
            ],
            [
              129.0,
              85.0
            ],
            [
              127.0,
              89.0
            ],
            [
              124.0,
              93.0
            ],
            [
              122.0,
              97.0
            ],
            [
              120.0,
              101.0
            ],
            [
              117.0,
              105.0
            ],
            [
              116.0,
              107.0
            ],
            [
              114.0,
              111.0
            ],
            [
              112.0,
              114.0
            ],
            [
              110.0,
              118.0
            ],
            [
              108.0,
              122.0
            ],
            [
              105.0,
              126.0
            ],
            [
              102.0,
              130.0
            ],
            [
              100.0,
              135.0
            ],
            [
              97.0,
              139.0
            ],
            [
              94.0,
              143.0
            ],
            [
              92.0,
              147.0
            ],
            [
              90.0,
              151.0
            ],
            [
              87.0,
              154.0
            ],
            [
              84.0,
              158.0
            ],
            [
              82.0,
              162.0
            ],
            [
              79.0,
              166.0
            ],
            [
              76.0,
              170.0
            ],
            [
              74.0,
              175.0
            ],
            [
              72.0,
              178.0
            ],
            [
              69.0,
              182.0
            ],
            [
              66.0,
              186.0
            ],
            [
              63.0,
              190.0
            ],
            [
              60.0,
              186.0
            ],
            [
              56.0,
              183.0
            ],
            [
              53.0,
              180.0
            ],
            [
              50.0,
              176.0
            ],
            [
              47.0,
              173.0
            ],
            [
              44.0,
              169.0
            ],
            [
              41.0,
              165.0
            ],
            [
              38.0,
              161.0
            ],
            [
              35.0,
              157.0
            ],
            [
              32.0,
              153.0
            ],
            [
              30.0,
              148.0
            ],
            [
              27.0,
              144.0
            ],
            [
              25.0,
              139.0
            ],
            [
              23.0,
              135.0
            ],
            [
              21.0,
              132.0
            ],
            [
              19.0,
              127.0
            ],
            [
              17.0,
              124.0
            ],
            [
              16.0,
              121.0
            ],
            [
              14.0,
              118.0
            ],
            [
              12.0,
              113.0
            ],
            [
              11.0,
              108.0
            ],
            [
              9.0,
              103.0
            ],
            [
              7.0,
              98.0
            ],
            [
              6.0,
              92.0
            ],
            [
              5.0,
              88.0
            ],
            [
              4.0,
              83.0
            ],
            [
              3.0,
              78.0
            ],
            [
              2.0,
              72.0
            ],
            [
              1.0,
              66.0
            ],
            [
              1.0,
              59.0
            ],
            [
              0.0,
              55.0
            ],
            [
              0.0,
              49.0
            ],
            [
              0.0,
              44.0
            ],
            [
              0.0,
              39.0
            ],
            [
              0.0,
              32.0
            ],
            [
              0.0,
              25.0
            ],
            [
              2.0,
              20.0
            ],
            [
              4.0,
              16.0
            ],
            [
              6.0,
              12.0
            ],
            [
              8.0,
              9.0
            ],
            [
              11.0,
              6.0
            ],
            [
              14.0,
              2.0
            ],
            [
              20.0,
              1.0
            ],
            [
              26.0,
              0.0
            ],
            [
              33.0,
              0.0
            ],
            [
              39.0,
              1.0
            ],
            [
              44.0,
              2.0
            ],
            [
              48.0,
              4.0
            ],
            [
              52.0,
              6.0
            ],
            [
              56.0,
              8.0
            ],
            [
              60.0,
              11.0
            ],
            [
              63.0,
              14.0
            ],
            [
              67.0,
              17.0
            ],
            [
              69.0,
              21.0
            ],
            [
              71.0,
              26.0
            ],
            [
              72.0,
              32.0
            ],
            [
              73.0,
              38.0
            ],
            [
              74.0,
              39.0
            ]
          ]
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              65,
              112
            ],
            "position": [
              358.0,
              272.0
            ],
            "originalSize": [
              125,
              55
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "white"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              125.0,
              55.0
            ]
          ]
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "property_editor",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              351,
              38
            ],
            "position": [
              79.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              360,
              66
            ],
            "position": [
              24.0,
              74.0
            ],
            "text": "Whenever you have the Hand tool selected, you'll see the Property Editor here.  It lets you edit various aspects of your objects.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "image",
          "handlers": {
            "OnMouseDown": "SoundPlay(\"puff.wav\")"
          },
          "properties": {
            "name": "image_1",
            "size": [
              103,
              129
            ],
            "position": [
              62.0,
              270.0
            ],
            "file": "ship-on.png",
            "fit": "Center",
            "rotation": 30,
            "xFlipped": false,
            "yFlipped": false
          }
        },
        {
          "type": "roundrect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              108,
              99
            ],
            "position": [
              211.0,
              276.0
            ],
            "originalSize": [
              60,
              55
            ],
            "penColor": "#000000",
            "penThickness": 4,
            "fillColor": "#FF9BB4",
            "cornerRadius": 12
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              60.0,
              55.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_5",
            "size": [
              56,
              63
            ],
            "position": [
              237.0,
              295.0
            ],
            "originalSize": [
              134,
              190
            ],
            "penColor": "red",
            "penThickness": 12
          },
          "points": [
            [
              72.0,
              43.0
            ],
            [
              74.0,
              38.0
            ],
            [
              76.0,
              34.0
            ],
            [
              79.0,
              31.0
            ],
            [
              82.0,
              27.0
            ],
            [
              85.0,
              24.0
            ],
            [
              88.0,
              20.0
            ],
            [
              92.0,
              17.0
            ],
            [
              95.0,
              14.0
            ],
            [
              99.0,
              12.0
            ],
            [
              105.0,
              11.0
            ],
            [
              112.0,
              11.0
            ],
            [
              116.0,
              13.0
            ],
            [
              119.0,
              16.0
            ],
            [
              122.0,
              19.0
            ],
            [
              125.0,
              22.0
            ],
            [
              127.0,
              27.0
            ],
            [
              129.0,
              32.0
            ],
            [
              131.0,
              37.0
            ],
            [
              132.0,
              43.0
            ],
            [
              133.0,
              48.0
            ],
            [
              134.0,
              54.0
            ],
            [
              134.0,
              61.0
            ],
            [
              134.0,
              68.0
            ],
            [
              134.0,
              74.0
            ],
            [
              132.0,
              79.0
            ],
            [
              131.0,
              82.0
            ],
            [
              129.0,
              85.0
            ],
            [
              127.0,
              89.0
            ],
            [
              124.0,
              93.0
            ],
            [
              122.0,
              97.0
            ],
            [
              120.0,
              101.0
            ],
            [
              117.0,
              105.0
            ],
            [
              116.0,
              107.0
            ],
            [
              114.0,
              111.0
            ],
            [
              112.0,
              114.0
            ],
            [
              110.0,
              118.0
            ],
            [
              108.0,
              122.0
            ],
            [
              105.0,
              126.0
            ],
            [
              102.0,
              130.0
            ],
            [
              100.0,
              135.0
            ],
            [
              97.0,
              139.0
            ],
            [
              94.0,
              143.0
            ],
            [
              92.0,
              147.0
            ],
            [
              90.0,
              151.0
            ],
            [
              87.0,
              154.0
            ],
            [
              84.0,
              158.0
            ],
            [
              82.0,
              162.0
            ],
            [
              79.0,
              166.0
            ],
            [
              76.0,
              170.0
            ],
            [
              74.0,
              175.0
            ],
            [
              72.0,
              178.0
            ],
            [
              69.0,
              182.0
            ],
            [
              66.0,
              186.0
            ],
            [
              63.0,
              190.0
            ],
            [
              60.0,
              186.0
            ],
            [
              56.0,
              183.0
            ],
            [
              53.0,
              180.0
            ],
            [
              50.0,
              176.0
            ],
            [
              47.0,
              173.0
            ],
            [
              44.0,
              169.0
            ],
            [
              41.0,
              165.0
            ],
            [
              38.0,
              161.0
            ],
            [
              35.0,
              157.0
            ],
            [
              32.0,
              153.0
            ],
            [
              30.0,
              148.0
            ],
            [
              27.0,
              144.0
            ],
            [
              25.0,
              139.0
            ],
            [
              23.0,
              135.0
            ],
            [
              21.0,
              132.0
            ],
            [
              19.0,
              127.0
            ],
            [
              17.0,
              124.0
            ],
            [
              16.0,
              121.0
            ],
            [
              14.0,
              118.0
            ],
            [
              12.0,
              113.0
            ],
            [
              11.0,
              108.0
            ],
            [
              9.0,
              103.0
            ],
            [
              7.0,
              98.0
            ],
            [
              6.0,
              92.0
            ],
            [
              5.0,
              88.0
            ],
            [
              4.0,
              83.0
            ],
            [
              3.0,
              78.0
            ],
            [
              2.0,
              72.0
            ],
            [
              1.0,
              66.0
            ],
            [
              1.0,
              59.0
            ],
            [
              0.0,
              55.0
            ],
            [
              0.0,
              49.0
            ],
            [
              0.0,
              44.0
            ],
            [
              0.0,
              39.0
            ],
            [
              0.0,
              32.0
            ],
            [
              0.0,
              25.0
            ],
            [
              2.0,
              20.0
            ],
            [
              4.0,
              16.0
            ],
            [
              6.0,
              12.0
            ],
            [
              8.0,
              9.0
            ],
            [
              11.0,
              6.0
            ],
            [
              14.0,
              2.0
            ],
            [
              20.0,
              1.0
            ],
            [
              26.0,
              0.0
            ],
            [
              33.0,
              0.0
            ],
            [
              39.0,
              1.0
            ],
            [
              44.0,
              2.0
            ],
            [
              48.0,
              4.0
            ],
            [
              52.0,
              6.0
            ],
            [
              56.0,
              8.0
            ],
            [
              60.0,
              11.0
            ],
            [
              63.0,
              14.0
            ],
            [
              67.0,
              17.0
            ],
            [
              69.0,
              21.0
            ],
            [
              71.0,
              26.0
            ],
            [
              72.0,
              32.0
            ],
            [
              73.0,
              38.0
            ],
            [
              74.0,
              39.0
            ]
          ]
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              65,
              112
            ],
            "position": [
              358.0,
              272.0
            ],
            "originalSize": [
              125,
              55
            ],
            "penColor": "black",
            "penThickness": 4,
            "fillColor": "#85DF6E"
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              125.0,
              55.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              470,
              103
            ],
            "position": [
              24.0,
              154.0
            ],
            "text": "Here, we've changed the some of the objects' properties.  Try clicking each object to explore its properties, and edit them yourself!  Note that when you click on a property, you'll get a desciption of that property right below the Property Editor.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "group_1",
            "size": [
              102,
              26
            ],
            "position": [
              391.0,
              81.0
            ]
          },
          "childModels": [
            {
              "type": "line",
              "handlers": {},
              "properties": {
                "name": "shape_1",
                "size": [
                  81,
                  2
                ],
                "position": [
                  0.0,
                  13.0
                ],
                "originalSize": [
                  82,
                  2
                ],
                "penColor": "black",
                "penThickness": 4
              },
              "points": [
                [
                  0.0,
                  0.0
                ],
                [
                  82.0,
                  0.0
                ]
              ]
            },
            {
              "type": "line",
              "handlers": {},
              "properties": {
                "name": "shape_4",
                "size": [
                  2,
                  22
                ],
                "position": [
                  82.0,
                  2.0
                ],
                "originalSize": [
                  2,
                  21
                ],
                "penColor": "black",
                "penThickness": 4
              },
              "points": [
                [
                  0.0,
                  0.0
                ],
                [
                  1.0,
                  21.0
                ]
              ]
            },
            {
              "type": "line",
              "handlers": {},
              "properties": {
                "name": "shape_6",
                "size": [
                  18,
                  9
                ],
                "position": [
                  83.0,
                  0.0
                ],
                "originalSize": [
                  19,
                  9
                ],
                "penColor": "black",
                "penThickness": 4
              },
              "points": [
                [
                  0.0,
                  0.0
                ],
                [
                  19.0,
                  9.0
                ]
              ]
            },
            {
              "type": "line",
              "handlers": {},
              "properties": {
                "name": "shape_7",
                "size": [
                  18,
                  16
                ],
                "position": [
                  83.0,
                  9.0
                ],
                "originalSize": [
                  19,
                  15
                ],
                "penColor": "black",
                "penThickness": 4
              },
              "points": [
                [
                  19.0,
                  0.0
                ],
                [
                  0.0,
                  15.0
                ]
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "try_it",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              449,
              42
            ],
            "position": [
              24.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              359,
              48
            ],
            "position": [
              24.0,
              74.0
            ],
            "text": "Try adding your own objects below, and editing their properties yourself!",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "code_editor",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              449,
              42
            ],
            "position": [
              24.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              351,
              51
            ],
            "position": [
              18.0,
              75.0
            ],
            "text": "Whenever you have the Hand tool selected, you'll see the Code Editor down here.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "Alert(\"Hello, this is an Alert.\")"
          },
          "properties": {
            "name": "button_1",
            "size": [
              124,
              30
            ],
            "position": [
              56.0,
              182.0
            ],
            "title": "Click Me!",
            "border": true
          }
        },
        {
          "type": "button",
          "handlers": {
            "OnClick": "GotoNextCard()"
          },
          "properties": {
            "name": "button_2",
            "size": [
              118,
              39
            ],
            "position": [
              363.0,
              447.0
            ],
            "title": "Next Card  =>",
            "border": true
          }
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              296,
              137
            ],
            "position": [
              169.0,
              148.0
            ],
            "originalSize": [
              312,
              142
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              0.0
            ],
            [
              312.0,
              142.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              27,
              25
            ],
            "position": [
              462.0,
              276.0
            ],
            "originalSize": [
              21,
              30
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              13.0,
              2.0
            ],
            [
              14.0,
              8.0
            ],
            [
              16.0,
              13.0
            ],
            [
              17.0,
              18.0
            ],
            [
              19.0,
              23.0
            ],
            [
              21.0,
              28.0
            ],
            [
              16.0,
              30.0
            ],
            [
              10.0,
              29.0
            ],
            [
              4.0,
              28.0
            ],
            [
              0.0,
              25.0
            ],
            [
              2.0,
              20.0
            ],
            [
              3.0,
              14.0
            ],
            [
              6.0,
              10.0
            ],
            [
              8.0,
              5.0
            ],
            [
              11.0,
              1.0
            ],
            [
              13.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              467,
              98
            ],
            "position": [
              23.0,
              341.0
            ],
            "text": "This code is run when the currently chosen event happens.  The above button has code in its OnClick() event, and will run whenever the button is clicked.  You can change which event's code you're editing using the event picker just above your code.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_5",
            "size": [
              311,
              43
            ],
            "position": [
              23.0,
              269.0
            ],
            "text": "Select an object to see the code that will run when its events are triggered.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "run",
        "bgColor": "white"
      },
      "childModels": [
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              327,
              38
            ],
            "position": [
              84.0,
              16.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "textColor": "black",
            "font": "Default",
            "fontSize": 18
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              319,
              44
            ],
            "position": [
              110.0,
              97.0
            ],
            "text": "When you're ready to test your stack, Click the Run button up here.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "line",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              50,
              84
            ],
            "position": [
              47.0,
              37.0
            ],
            "originalSize": [
              50,
              84
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              50.0,
              84.0
            ],
            [
              0.0,
              0.0
            ]
          ]
        },
        {
          "type": "pen",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              28,
              30
            ],
            "position": [
              33.0,
              14.0
            ],
            "originalSize": [
              28,
              30
            ],
            "penColor": "#000000",
            "penThickness": 4
          },
          "points": [
            [
              0.0,
              28.0
            ],
            [
              0.0,
              21.0
            ],
            [
              0.0,
              14.0
            ],
            [
              0.0,
              7.0
            ],
            [
              0.0,
              0.0
            ],
            [
              4.0,
              3.0
            ],
            [
              9.0,
              5.0
            ],
            [
              14.0,
              7.0
            ],
            [
              20.0,
              8.0
            ],
            [
              24.0,
              11.0
            ],
            [
              28.0,
              14.0
            ],
            [
              26.0,
              18.0
            ],
            [
              21.0,
              20.0
            ],
            [
              16.0,
              22.0
            ],
            [
              12.0,
              25.0
            ],
            [
              8.0,
              27.0
            ],
            [
              4.0,
              30.0
            ],
            [
              3.0,
              29.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              398,
              51
            ],
            "position": [
              34.0,
              281.0
            ],
            "text": "For more info on how CardStock works, check out the Manual in the Help menu.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_4",
            "size": [
              398,
              49
            ],
            "position": [
              34.0,
              346.0
            ],
            "text": "For more info on writing CardStock code, check out the Reference Guide in the Help menu.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_5",
            "size": [
              336,
              53
            ],
            "position": [
              34.0,
              409.0
            ],
            "text": "You can also explore lots more CardStock code in the example CardStock stacks.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_6",
            "size": [
              386,
              44
            ],
            "position": [
              92.0,
              153.0
            ],
            "text": "When you're done running your stack, close the Viewer window to return to the Designer.",
            "alignment": "Left",
            "textColor": "black",
            "font": "Default",
            "fontSize": 12
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 1,
  "CardStock_stack_version": "0.8"
}
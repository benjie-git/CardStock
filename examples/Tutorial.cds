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
              14.0
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
              282,
              41
            ],
            "position": [
              74.0,
              13.0
            ],
            "text": "(Later, when you run the stack, this button\n will take you to the next card.)",
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
              446.0
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
              356,
              47
            ],
            "position": [
              28.0,
              362.0
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
              213.0
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
              14.0
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
              446.0
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
              342.0
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
              359.0
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
              0.0
            ],
            [
              115.0,
              88.0
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
              446.0
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
              21.0
            ],
            [
              7.0,
              21.0
            ],
            [
              13.0,
              21.0
            ],
            [
              19.0,
              20.0
            ],
            [
              23.0,
              17.0
            ],
            [
              21.0,
              13.0
            ],
            [
              17.0,
              10.0
            ],
            [
              15.0,
              5.0
            ],
            [
              13.0,
              0.0
            ],
            [
              9.0,
              2.0
            ],
            [
              6.0,
              6.0
            ],
            [
              5.0,
              12.0
            ],
            [
              2.0,
              16.0
            ],
            [
              0.0,
              21.0
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
              203.0
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
              14.0
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
              446.0
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
              342.0
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
              359.0
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
              0.0
            ],
            [
              115.0,
              88.0
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
              446.0
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
              21.0
            ],
            [
              7.0,
              21.0
            ],
            [
              13.0,
              21.0
            ],
            [
              19.0,
              20.0
            ],
            [
              23.0,
              17.0
            ],
            [
              21.0,
              13.0
            ],
            [
              17.0,
              10.0
            ],
            [
              15.0,
              5.0
            ],
            [
              13.0,
              0.0
            ],
            [
              9.0,
              2.0
            ],
            [
              6.0,
              6.0
            ],
            [
              5.0,
              12.0
            ],
            [
              2.0,
              16.0
            ],
            [
              0.0,
              21.0
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
              202.0
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
              263.0
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
              14.0
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
              446.0
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
              342.0
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
              359.0
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
              0.0
            ],
            [
              115.0,
              88.0
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
              446.0
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
              21.0
            ],
            [
              7.0,
              21.0
            ],
            [
              13.0,
              21.0
            ],
            [
              19.0,
              20.0
            ],
            [
              23.0,
              17.0
            ],
            [
              21.0,
              13.0
            ],
            [
              17.0,
              10.0
            ],
            [
              15.0,
              5.0
            ],
            [
              13.0,
              0.0
            ],
            [
              9.0,
              2.0
            ],
            [
              6.0,
              6.0
            ],
            [
              5.0,
              12.0
            ],
            [
              2.0,
              16.0
            ],
            [
              0.0,
              21.0
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
              263.0
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
              211.0
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
              14.0
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
              446.0
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
              342.0
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
              359.0
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
              0.0
            ],
            [
              115.0,
              88.0
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
              446.0
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
              21.0
            ],
            [
              7.0,
              21.0
            ],
            [
              13.0,
              21.0
            ],
            [
              19.0,
              20.0
            ],
            [
              23.0,
              17.0
            ],
            [
              21.0,
              13.0
            ],
            [
              17.0,
              10.0
            ],
            [
              15.0,
              5.0
            ],
            [
              13.0,
              0.0
            ],
            [
              9.0,
              2.0
            ],
            [
              6.0,
              6.0
            ],
            [
              5.0,
              12.0
            ],
            [
              2.0,
              16.0
            ],
            [
              0.0,
              21.0
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
              263.0
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
              101.0
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
              125.0
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
              142.0
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
              147.0
            ],
            [
              74.0,
              152.0
            ],
            [
              76.0,
              156.0
            ],
            [
              79.0,
              159.0
            ],
            [
              82.0,
              163.0
            ],
            [
              85.0,
              166.0
            ],
            [
              88.0,
              170.0
            ],
            [
              92.0,
              173.0
            ],
            [
              95.0,
              176.0
            ],
            [
              99.0,
              178.0
            ],
            [
              105.0,
              179.0
            ],
            [
              112.0,
              179.0
            ],
            [
              116.0,
              177.0
            ],
            [
              119.0,
              174.0
            ],
            [
              122.0,
              171.0
            ],
            [
              125.0,
              168.0
            ],
            [
              127.0,
              163.0
            ],
            [
              129.0,
              158.0
            ],
            [
              131.0,
              153.0
            ],
            [
              132.0,
              147.0
            ],
            [
              133.0,
              142.0
            ],
            [
              134.0,
              136.0
            ],
            [
              134.0,
              129.0
            ],
            [
              134.0,
              122.0
            ],
            [
              134.0,
              116.0
            ],
            [
              132.0,
              111.0
            ],
            [
              131.0,
              108.0
            ],
            [
              129.0,
              105.0
            ],
            [
              127.0,
              101.0
            ],
            [
              124.0,
              97.0
            ],
            [
              122.0,
              93.0
            ],
            [
              120.0,
              89.0
            ],
            [
              117.0,
              85.0
            ],
            [
              116.0,
              83.0
            ],
            [
              114.0,
              79.0
            ],
            [
              112.0,
              76.0
            ],
            [
              110.0,
              72.0
            ],
            [
              108.0,
              68.0
            ],
            [
              105.0,
              64.0
            ],
            [
              102.0,
              60.0
            ],
            [
              100.0,
              55.0
            ],
            [
              97.0,
              51.0
            ],
            [
              94.0,
              47.0
            ],
            [
              92.0,
              43.0
            ],
            [
              90.0,
              39.0
            ],
            [
              87.0,
              36.0
            ],
            [
              84.0,
              32.0
            ],
            [
              82.0,
              28.0
            ],
            [
              79.0,
              24.0
            ],
            [
              76.0,
              20.0
            ],
            [
              74.0,
              15.0
            ],
            [
              72.0,
              12.0
            ],
            [
              69.0,
              8.0
            ],
            [
              66.0,
              4.0
            ],
            [
              63.0,
              0.0
            ],
            [
              60.0,
              4.0
            ],
            [
              56.0,
              7.0
            ],
            [
              53.0,
              10.0
            ],
            [
              50.0,
              14.0
            ],
            [
              47.0,
              17.0
            ],
            [
              44.0,
              21.0
            ],
            [
              41.0,
              25.0
            ],
            [
              38.0,
              29.0
            ],
            [
              35.0,
              33.0
            ],
            [
              32.0,
              37.0
            ],
            [
              30.0,
              42.0
            ],
            [
              27.0,
              46.0
            ],
            [
              25.0,
              51.0
            ],
            [
              23.0,
              55.0
            ],
            [
              21.0,
              58.0
            ],
            [
              19.0,
              63.0
            ],
            [
              17.0,
              66.0
            ],
            [
              16.0,
              69.0
            ],
            [
              14.0,
              72.0
            ],
            [
              12.0,
              77.0
            ],
            [
              11.0,
              82.0
            ],
            [
              9.0,
              87.0
            ],
            [
              7.0,
              92.0
            ],
            [
              6.0,
              98.0
            ],
            [
              5.0,
              102.0
            ],
            [
              4.0,
              107.0
            ],
            [
              3.0,
              112.0
            ],
            [
              2.0,
              118.0
            ],
            [
              1.0,
              124.0
            ],
            [
              1.0,
              131.0
            ],
            [
              0.0,
              135.0
            ],
            [
              0.0,
              141.0
            ],
            [
              0.0,
              146.0
            ],
            [
              0.0,
              151.0
            ],
            [
              0.0,
              158.0
            ],
            [
              0.0,
              165.0
            ],
            [
              2.0,
              170.0
            ],
            [
              4.0,
              174.0
            ],
            [
              6.0,
              178.0
            ],
            [
              8.0,
              181.0
            ],
            [
              11.0,
              184.0
            ],
            [
              14.0,
              188.0
            ],
            [
              20.0,
              189.0
            ],
            [
              26.0,
              190.0
            ],
            [
              33.0,
              190.0
            ],
            [
              39.0,
              189.0
            ],
            [
              44.0,
              188.0
            ],
            [
              48.0,
              186.0
            ],
            [
              52.0,
              184.0
            ],
            [
              56.0,
              182.0
            ],
            [
              60.0,
              179.0
            ],
            [
              63.0,
              176.0
            ],
            [
              67.0,
              173.0
            ],
            [
              69.0,
              169.0
            ],
            [
              71.0,
              164.0
            ],
            [
              72.0,
              158.0
            ],
            [
              73.0,
              152.0
            ],
            [
              74.0,
              151.0
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
              116.0
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
              14.0
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
              446.0
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
              360.0
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
              101.0
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
              125.0
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
              142.0
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
              147.0
            ],
            [
              74.0,
              152.0
            ],
            [
              76.0,
              156.0
            ],
            [
              79.0,
              159.0
            ],
            [
              82.0,
              163.0
            ],
            [
              85.0,
              166.0
            ],
            [
              88.0,
              170.0
            ],
            [
              92.0,
              173.0
            ],
            [
              95.0,
              176.0
            ],
            [
              99.0,
              178.0
            ],
            [
              105.0,
              179.0
            ],
            [
              112.0,
              179.0
            ],
            [
              116.0,
              177.0
            ],
            [
              119.0,
              174.0
            ],
            [
              122.0,
              171.0
            ],
            [
              125.0,
              168.0
            ],
            [
              127.0,
              163.0
            ],
            [
              129.0,
              158.0
            ],
            [
              131.0,
              153.0
            ],
            [
              132.0,
              147.0
            ],
            [
              133.0,
              142.0
            ],
            [
              134.0,
              136.0
            ],
            [
              134.0,
              129.0
            ],
            [
              134.0,
              122.0
            ],
            [
              134.0,
              116.0
            ],
            [
              132.0,
              111.0
            ],
            [
              131.0,
              108.0
            ],
            [
              129.0,
              105.0
            ],
            [
              127.0,
              101.0
            ],
            [
              124.0,
              97.0
            ],
            [
              122.0,
              93.0
            ],
            [
              120.0,
              89.0
            ],
            [
              117.0,
              85.0
            ],
            [
              116.0,
              83.0
            ],
            [
              114.0,
              79.0
            ],
            [
              112.0,
              76.0
            ],
            [
              110.0,
              72.0
            ],
            [
              108.0,
              68.0
            ],
            [
              105.0,
              64.0
            ],
            [
              102.0,
              60.0
            ],
            [
              100.0,
              55.0
            ],
            [
              97.0,
              51.0
            ],
            [
              94.0,
              47.0
            ],
            [
              92.0,
              43.0
            ],
            [
              90.0,
              39.0
            ],
            [
              87.0,
              36.0
            ],
            [
              84.0,
              32.0
            ],
            [
              82.0,
              28.0
            ],
            [
              79.0,
              24.0
            ],
            [
              76.0,
              20.0
            ],
            [
              74.0,
              15.0
            ],
            [
              72.0,
              12.0
            ],
            [
              69.0,
              8.0
            ],
            [
              66.0,
              4.0
            ],
            [
              63.0,
              0.0
            ],
            [
              60.0,
              4.0
            ],
            [
              56.0,
              7.0
            ],
            [
              53.0,
              10.0
            ],
            [
              50.0,
              14.0
            ],
            [
              47.0,
              17.0
            ],
            [
              44.0,
              21.0
            ],
            [
              41.0,
              25.0
            ],
            [
              38.0,
              29.0
            ],
            [
              35.0,
              33.0
            ],
            [
              32.0,
              37.0
            ],
            [
              30.0,
              42.0
            ],
            [
              27.0,
              46.0
            ],
            [
              25.0,
              51.0
            ],
            [
              23.0,
              55.0
            ],
            [
              21.0,
              58.0
            ],
            [
              19.0,
              63.0
            ],
            [
              17.0,
              66.0
            ],
            [
              16.0,
              69.0
            ],
            [
              14.0,
              72.0
            ],
            [
              12.0,
              77.0
            ],
            [
              11.0,
              82.0
            ],
            [
              9.0,
              87.0
            ],
            [
              7.0,
              92.0
            ],
            [
              6.0,
              98.0
            ],
            [
              5.0,
              102.0
            ],
            [
              4.0,
              107.0
            ],
            [
              3.0,
              112.0
            ],
            [
              2.0,
              118.0
            ],
            [
              1.0,
              124.0
            ],
            [
              1.0,
              131.0
            ],
            [
              0.0,
              135.0
            ],
            [
              0.0,
              141.0
            ],
            [
              0.0,
              146.0
            ],
            [
              0.0,
              151.0
            ],
            [
              0.0,
              158.0
            ],
            [
              0.0,
              165.0
            ],
            [
              2.0,
              170.0
            ],
            [
              4.0,
              174.0
            ],
            [
              6.0,
              178.0
            ],
            [
              8.0,
              181.0
            ],
            [
              11.0,
              184.0
            ],
            [
              14.0,
              188.0
            ],
            [
              20.0,
              189.0
            ],
            [
              26.0,
              190.0
            ],
            [
              33.0,
              190.0
            ],
            [
              39.0,
              189.0
            ],
            [
              44.0,
              188.0
            ],
            [
              48.0,
              186.0
            ],
            [
              52.0,
              184.0
            ],
            [
              56.0,
              182.0
            ],
            [
              60.0,
              179.0
            ],
            [
              63.0,
              176.0
            ],
            [
              67.0,
              173.0
            ],
            [
              69.0,
              169.0
            ],
            [
              71.0,
              164.0
            ],
            [
              72.0,
              158.0
            ],
            [
              73.0,
              152.0
            ],
            [
              74.0,
              151.0
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
              116.0
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
              438,
              105
            ],
            "position": [
              24.0,
              241.0
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
              393.0
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
                  11.0
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
                  2.0
                ],
                [
                  82.0,
                  2.0
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
                  21.0
                ],
                [
                  1.0,
                  0.0
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
                  17.0
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
                  9.0
                ],
                [
                  19.0,
                  0.0
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
                  1.0
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
                  15.0
                ],
                [
                  0.0,
                  0.0
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
              14.0
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
              442.0
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
              378.0
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
              442.0
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
              374.0
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
              288.0
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
              14.0
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
              215.0
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
              142.0
            ],
            [
              312.0,
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
              27,
              25
            ],
            "position": [
              462.0,
              199.0
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
              28.0
            ],
            [
              14.0,
              22.0
            ],
            [
              16.0,
              17.0
            ],
            [
              17.0,
              12.0
            ],
            [
              19.0,
              7.0
            ],
            [
              21.0,
              2.0
            ],
            [
              16.0,
              0.0
            ],
            [
              10.0,
              1.0
            ],
            [
              4.0,
              2.0
            ],
            [
              0.0,
              5.0
            ],
            [
              2.0,
              10.0
            ],
            [
              3.0,
              16.0
            ],
            [
              6.0,
              20.0
            ],
            [
              8.0,
              25.0
            ],
            [
              11.0,
              29.0
            ],
            [
              13.0,
              30.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              446,
              101
            ],
            "position": [
              23.0,
              58.0
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
              188.0
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
              446.0
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
              359.0
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
              379.0
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
              0.0
            ],
            [
              0.0,
              84.0
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
              456.0
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
              2.0
            ],
            [
              0.0,
              9.0
            ],
            [
              0.0,
              16.0
            ],
            [
              0.0,
              23.0
            ],
            [
              0.0,
              30.0
            ],
            [
              4.0,
              27.0
            ],
            [
              9.0,
              25.0
            ],
            [
              14.0,
              23.0
            ],
            [
              20.0,
              22.0
            ],
            [
              24.0,
              19.0
            ],
            [
              28.0,
              16.0
            ],
            [
              26.0,
              12.0
            ],
            [
              21.0,
              10.0
            ],
            [
              16.0,
              8.0
            ],
            [
              12.0,
              5.0
            ],
            [
              8.0,
              3.0
            ],
            [
              4.0,
              0.0
            ],
            [
              3.0,
              1.0
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
              168.0
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
              105.0
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
              38.0
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
              303.0
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
  "CardStock_stack_format": 2,
  "CardStock_stack_version": "0.8.12"
}
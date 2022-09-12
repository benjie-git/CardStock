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
      "handlers": {},
      "properties": {
        "name": "welcome",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              431,
              70
            ],
            "position": [
              37.0,
              422.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "on_setup": "# Make this text black when we run the stack,\n# and update the text.\nself.text_color = \"black\"\nself.text = \"Now that you're running the stack, this button will take you to the next card.\"\n"
          },
          "properties": {
            "name": "label_5",
            "size": [
              282,
              41
            ],
            "position": [
              202.0,
              56.0
            ],
            "text": "(Later, when you run the stack, this button\n will take you to the next card.)",
            "alignment": "Right",
            "text_color": "#A0A0A0",
            "font": "Default",
            "font_size": 11,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              406,
              49
            ],
            "position": [
              48.0,
              435.0
            ],
            "text": "Welcome to CardStock!",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_4",
            "size": [
              400,
              45
            ],
            "position": [
              28.0,
              244.0
            ],
            "text": "A CardStock program is called a stack.  And each page of your program is called a card.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_2",
            "size": [
              400,
              66
            ],
            "position": [
              28.0,
              323.0
            ],
            "text": "CardStock lets you build programs by drawing them out, and then adding bits of code right where you need them.  Then you can click Run to try it out.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {
            "on_setup": "# Make this label disappear when we run the stack\nself.hide()"
          },
          "properties": {
            "name": "label_6",
            "size": [
              400,
              68
            ],
            "position": [
              28.0,
              149.0
            ],
            "text": "Here in the Designer, you can move to the next card by clicking the \"Next Card\" button in the top right of this window.  Try it!",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "labels",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              351,
              40
            ],
            "position": [
              79.0,
              444.0
            ],
            "text": "Objects",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
            "text": "You can draw objects like buttons,\ntext fields, shapes, and text labels\nonto your cards using the tools up here.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
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
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
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
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_1",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
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
            "text": "For example, this is a Text Label object.  It shows text, but is not editable by the user when you run the stack.  But in the Designer, you can double click it to edit its text.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "fields",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              77.0,
              439.0
            ],
            "text": "Objects",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {
            "on_text_enter": "self.text = \"You pressed enter.\""
          },
          "properties": {
            "name": "field_1",
            "size": [
              222,
              29
            ],
            "position": [
              73.0,
              282.0
            ],
            "text": "Edit me!  I'm a Text Field.",
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
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_1",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              426,
              47
            ],
            "position": [
              34.0,
              342.0
            ],
            "text": "And below is a Text Field.  Users of your stack can enter and edit text in them, and your code can get that text and use it.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "buttons",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
              343.0
            ],
            "text": "Buttons let your stack perform actions when they are clicked, once your stack is running.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              77.0,
              439.0
            ],
            "text": "Objects",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_3",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "card.fill_color = \"#DDFFEE\""
          },
          "properties": {
            "name": "button_1",
            "size": [
              150,
              27
            ],
            "position": [
              108.0,
              271.0
            ],
            "title": "I am a Button",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "images",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
              343.0
            ],
            "text": "Image objects can show an image from a file, and you can also draw shapes.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
            "rotation": 0.0,
            "xFlipped": false,
            "yFlipped": false
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              77.0,
              439.0
            ],
            "text": "Objects",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_1",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
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
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "white"
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
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "group_1",
            "size": [
              107,
              98
            ],
            "position": [
              211.0,
              125.0
            ],
            "rotation": 0.0
          },
          "childModels": [
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
                  0.0,
                  0.0
                ],
                "originalSize": [
                  60,
                  55
                ],
                "pen_color": "#000000",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "white",
                "corner_radius": 12
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
                  26.0,
                  17.0
                ],
                "originalSize": [
                  134,
                  190
                ],
                "pen_color": "#000000",
                "pen_thickness": 4,
                "rotation": 0.0
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
            }
          ]
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "property_editor",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_8",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "image",
          "handlers": {
            "on_mouse_press": "play_sound(\"puff.wav\")"
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
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              65,
              112
            ],
            "position": [
              360.0,
              109.0
            ],
            "originalSize": [
              125,
              55
            ],
            "pen_color": "black",
            "pen_thickness": 4,
            "rotation": 23.4,
            "fill_color": "#85DF6E"
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
            "text": "Here, we've changed some of the objects' properties.  Try clicking each object to explore its properties, and edit them yourself!  Note that when you click on a property, you'll get a desciption of that property right below the Property Editor, in the Context Help area.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              79.0,
              439.0
            ],
            "text": "Properties",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_1",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
            ],
            "rotation": 0.0
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
                "pen_color": "black",
                "pen_thickness": 4,
                "rotation": 0.0
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
                "pen_color": "black",
                "pen_thickness": 4,
                "rotation": 0.0
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
                "pen_color": "black",
                "pen_thickness": 4,
                "rotation": 0.0
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
                "pen_color": "black",
                "pen_thickness": 4,
                "rotation": 0.0
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
        },
        {
          "type": "group",
          "handlers": {},
          "properties": {
            "name": "group_2",
            "size": [
              107,
              98
            ],
            "position": [
              204.0,
              81.0
            ],
            "rotation": 346.4
          },
          "childModels": [
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
                  0.0,
                  0.0
                ],
                "originalSize": [
                  60,
                  55
                ],
                "pen_color": "#000000",
                "pen_thickness": 4,
                "rotation": 0.0,
                "fill_color": "#FF9BB4",
                "corner_radius": 12
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
                  26.0,
                  17.0
                ],
                "originalSize": [
                  134,
                  190
                ],
                "pen_color": "red",
                "pen_thickness": 12,
                "rotation": 0.0
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
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_2",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              79.0,
              439.0
            ],
            "text": "Properties",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "polygon",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              449,
              177
            ],
            "position": [
              22.0,
              247.0
            ],
            "originalSize": [
              296,
              242
            ],
            "pen_color": "#FB0207",
            "pen_thickness": 4,
            "rotation": 0.0,
            "fill_color": "#E6E7EA"
          },
          "points": [
            [
              118.0,
              193.0
            ],
            [
              159.0,
              242.0
            ],
            [
              174.0,
              190.0
            ],
            [
              256.0,
              219.0
            ],
            [
              225.0,
              152.0
            ],
            [
              296.0,
              152.0
            ],
            [
              255.0,
              101.0
            ],
            [
              292.0,
              57.0
            ],
            [
              223.0,
              67.0
            ],
            [
              225.0,
              0.0
            ],
            [
              181.0,
              48.0
            ],
            [
              136.0,
              1.0
            ],
            [
              134.0,
              61.0
            ],
            [
              67.0,
              22.0
            ],
            [
              89.0,
              85.0
            ],
            [
              30.0,
              78.0
            ],
            [
              77.0,
              136.0
            ],
            [
              0.0,
              162.0
            ],
            [
              61.0,
              177.0
            ],
            [
              75.0,
              242.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_1",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              216,
              63
            ],
            "position": [
              143.0,
              313.0
            ],
            "text": "Try drawing out your own\nobjects below, and editing\ntheir properties yourself!",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "code_editor",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
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
            "text": "Whenever you have the Hand tool selected, you'll also see the Code Editor down here.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "alert(\"Hello, this is an alert.\")"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
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
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
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
              456,
              116
            ],
            "position": [
              23.0,
              59.0
            ],
            "text": "This code is run when the currently chosen event happens.  The above button has code in its on_click() event, which will run whenever this button is clicked.  Each type of object can respond to a different set of events.  For any selected object, you can see all of the events that already have code in them, and you can add more events by clicking the \"+ Add Event\" button.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              79.0,
              439.0
            ],
            "text": "Code Editor",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_3",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_5",
            "size": [
              315,
              60
            ],
            "position": [
              23.0,
              198.0
            ],
            "text": "Select an object to see the code that will run when its events are triggered.  Try clicking on the button above.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "code_1",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "number_field.text = int(number_field.text)+1"
          },
          "properties": {
            "name": "add_button",
            "size": [
              124,
              30
            ],
            "position": [
              335.0,
              386.0
            ],
            "title": "Add One",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              450,
              243
            ],
            "position": [
              29.0,
              75.0
            ],
            "text": "This button does the following when clicked:\n- It takes the text from the above field, using number_field.text,\n- converts it to a number (an integer), using int(),\n- adds 1 to it, (+1)\n- and sets that new number as the new text for number_field.\n\nClick the button to select it, and see this code, and how it fits together.  Later, when you Run the stack, you'll be able to see this code work.\n\n\nTry adding a second button that will double the number instead of adding 1!",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              79.0,
              439.0
            ],
            "text": "Event Code",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_3",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textfield",
          "handlers": {},
          "properties": {
            "name": "number_field",
            "size": [
              104,
              26
            ],
            "position": [
              217.0,
              388.0
            ],
            "text": "1",
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
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "code_2",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_1",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "# Animate the ball to a point on the left over 1 second,\n# and then back to the right over 1 more second.\n# This queues up both animations to happen one after another,\n# since they are animating the same property.\nball.animate_position(1, [  0, 325])\nball.animate_position(1, [440, 325])\n\n# If you also add animations for a different property, for\n# example ball.animate_fill_color(1, \"blue\"), this will\n# run simultaneously with ball's position animations."
          },
          "properties": {
            "name": "animate_button",
            "size": [
              124,
              30
            ],
            "position": [
              361.0,
              395.0
            ],
            "title": "Animate",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_next_card()"
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
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_3",
            "size": [
              436,
              242
            ],
            "position": [
              29.0,
              56.0
            ],
            "text": "This button animates the ball to move across the screen and back.\n\nNote that the circle has its name property set to \"ball\".  So the code in the button can perform actions on the ball object by name.\n\nCan you make the ball also animate its fill_color to blue and back to red, from the same button click?",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              354,
              45
            ],
            "position": [
              79.0,
              439.0
            ],
            "text": "Event Code",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_3",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
          }
        },
        {
          "type": "oval",
          "handlers": {},
          "properties": {
            "name": "ball",
            "size": [
              54,
              54
            ],
            "position": [
              440.0,
              325.0
            ],
            "originalSize": [
              54,
              54
            ],
            "pen_color": "black",
            "pen_thickness": 1,
            "rotation": 0.0,
            "fill_color": "#E62332"
          },
          "points": [
            [
              0.0,
              54.0
            ],
            [
              54.0,
              0.0
            ]
          ]
        }
      ]
    },
    {
      "type": "card",
      "handlers": {},
      "properties": {
        "name": "run",
        "fill_color": "white"
      },
      "childModels": [
        {
          "type": "rect",
          "handlers": {},
          "properties": {
            "name": "shape_3",
            "size": [
              359,
              55
            ],
            "position": [
              76.0,
              436.0
            ],
            "originalSize": [
              431,
              70
            ],
            "pen_color": "black",
            "pen_thickness": 2,
            "rotation": 0.0,
            "fill_color": "#ADCEA2"
          },
          "points": [
            [
              0.0,
              70.0
            ],
            [
              431.0,
              0.0
            ]
          ]
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_1",
            "size": [
              343,
              43
            ],
            "position": [
              84.0,
              442.0
            ],
            "text": "Run Your Stack!",
            "alignment": "Center",
            "text_color": "black",
            "font": "Default",
            "font_size": 25,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
            "text": "When you're ready to test your stack, Click the Run Stack button up here.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
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
            "pen_color": "#000000",
            "pen_thickness": 4,
            "rotation": 0.0
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
              188.0
            ],
            "text": "For more info on how CardStock works, check out the Manual in the Help menu.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
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
              125.0
            ],
            "text": "For more info on writing CardStock code, check out the Reference Guide in the Help menu.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "textlabel",
          "handlers": {},
          "properties": {
            "name": "label_5",
            "size": [
              336,
              46
            ],
            "position": [
              34.0,
              65.0
            ],
            "text": "You can also explore lots more CardStock code in the example CardStock stacks.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        },
        {
          "type": "button",
          "handlers": {
            "on_click": "goto_previous_card()"
          },
          "properties": {
            "name": "button_1",
            "size": [
              118,
              39
            ],
            "position": [
              20.0,
              14.0
            ],
            "title": "<= Prev Card",
            "style": "Border",
            "is_selected": false,
            "rotation": 0.0
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
            "text": "When you're done running your stack, close the Viewer window to return here, to the Designer.",
            "alignment": "Left",
            "text_color": "black",
            "font": "Default",
            "font_size": 12,
            "is_bold": false,
            "is_italic": false,
            "is_underlined": false,
            "can_auto_shrink": true,
            "rotation": 0.0
          }
        }
      ]
    }
  ],
  "CardStock_stack_format": 6,
  "CardStock_stack_version": "0.99.1"
}
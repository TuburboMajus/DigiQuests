def get_pattern(letter):
    patterns = {
        'A': [
            "  ###  ",
            " #   # ",
            "#     #",
            "#######",
            "#     #",
            "#     #",
            "#     #"
        ],
        'B': [
            "###### ",
            "#     #",
            "#     #",
            "###### ",
            "#     #",
            "#     #",
            "###### "
        ],
        'C': [
            " ##### ",
            "#     #",
            "#      ",
            "#      ",
            "#      ",
            "#     #",
            " ##### "
        ],
        'D': [
            "###### ",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            "###### "
        ],
        'E': [
            "#######",
            "#      ",
            "#      ",
            "###### ",
            "#      ",
            "#      ",
            "#######"
        ],
        'F': [
            "#######",
            "#      ",
            "#      ",
            "#####  ",
            "#      ",
            "#      ",
            "#      "
        ],
        'G': [
            " ##### ",
            "#     #",
            "#      ",
            "#  ### ",
            "#     #",
            "#     #",
            " ##### "
        ],
        'H': [
            "#     #",
            "#     #",
            "#     #",
            "#######",
            "#     #",
            "#     #",
            "#     #"
        ],
        'I': [
            "#######",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   ",
            "#######"
        ],
        'J': [
            "#######",
            "    #  ",
            "    #  ",
            "    #  ",
            "    #  ",
            "#   #  ",
            " ###   "
        ],
        'K': [
            "#    # ",
            "#   #  ",
            "#  #   ",
            "###    ",
            "#  #   ",
            "#   #  ",
            "#    # "
        ],
        'L': [
            "#      ",
            "#      ",
            "#      ",
            "#      ",
            "#      ",
            "#      ",
            "#######"
        ],
        'M': [
            "#     #",
            "##   ##",
            "# # # #",
            "#  #  #",
            "#     #",
            "#     #",
            "#     #"
        ],
        'N': [
            "#     #",
            "##    #",
            "# #   #",
            "#  #  #",
            "#   # #",
            "#    ##",
            "#     #"
        ],
        'O': [
            " ##### ",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            " ##### "
        ],
        'P': [
            "###### ",
            "#     #",
            "#     #",
            "###### ",
            "#      ",
            "#      ",
            "#      "
        ],
        'Q': [
            " ##### ",
            "#     #",
            "#     #",
            "#  #  #",
            "#   ## ",
            "#    # ",
            " #### #"
        ],
        'R': [
            "###### ",
            "#     #",
            "#     #",
            "###### ",
            "#  #   ",
            "#   #  ",
            "#    # "
        ],
        'S': [
            " ######",
            "#      ",
            "#      ",
            " ##### ",
            "      #",
            "      #",
            "###### "
        ],
        'T': [
            "#######",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   "
        ],
        'U': [
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            " ##### "
        ],
        'V': [
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            " #   # ",
            "  # #  ",
            "   #   "
        ],
        'W': [
            "#     #",
            "#     #",
            "#     #",
            "#  #  #",
            "#  #  #",
            "#  #  #",
            " ## ## "
        ],
        'X': [
            "#     #",
            " #   # ",
            "  # #  ",
            "   #   ",
            "  # #  ",
            " #   # ",
            "#     #"
        ],
        'Y': [
            "#     #",
            " #   # ",
            "  # #  ",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   "
        ],
        'Z': [
            "#######",
            "     # ",
            "    #  ",
            "   #   ",
            "  #    ",
            " #     ",
            "#######"
        ],
        '1': [
            "  ###  ",
            " # ##  ",
            "#   #  ",
            "    #  ",
            "    #  ",
            "    #  ",
            "#######"
        ],
        '2': [
            " ##### ",
            "#     #",
            "      #",
            " ##### ",
            "#      ",
            "#      ",
            "#######"
        ],
        '3': [
            " ##### ",
            "#     #",
            "      #",
            " ##### ",
            "      #",
            "#     #",
            " ##### "
        ],
        '4': [
            "#      ",
            "#    # ",
            "#    # ",
            "#######",
            "     # ",
            "     # ",
            "     # "
        ],
        '5': [
            "#######",
            "#      ",
            "#      ",
            " ##### ",
            "      #",
            "#     #",
            " ##### "
        ],
        '6': [
            " ##### ",
            "#      ",
            "#      ",
            " ##### ",
            "#     #",
            "#     #",
            " ##### "
        ],
        '7': [
            "#######",
            "     # ",
            "    #  ",
            "   #   ",
            "  #    ",
            " #     ",
            "#      "
        ],
        '8': [
            " ##### ",
            "#     #",
            "#     #",
            " ##### ",
            "#     #",
            "#     #",
            " ##### "
        ],
        '9': [
            " ##### ",
            "#     #",
            "#     #",
            " ######",
            "      #",
            "#     #",
            " ##### "
        ],
        '0': [
            " ##### ",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            "#     #",
            " ##### "
        ],
        '?': [
            " ####  ",
            "#    # ",
            "    #  ",
            "   #   ",
            "  #    ",
            "       ",
            "  #    "
        ],
        '!': [
            "  #    ",
            "  #    ",
            "  #    ",
            "  #    ",
            "  #    ",
            "       ",
            "  #    "
        ],
        ':': [
            "       ",
            "   #   ",
            "       ",
            "       ",
            "   #   ",
            "       ",
            "       "
        ],
        ';': [
            "   #   ",
            "   #   ",
            "       ",
            "       ",
            "   #   ",
            "   #   ",
            "   #   "
        ],
        '#': [
            " # # # ",
            " # # # ",
            "#######",
            " # # # ",
            "#######",
            " # # # ",
            " # # # "
        ],
        '@': [
            " ##### ",
            "#     #",
            "# ### #",
            "# # # #",
            "# # # #",
            "#     #",
            " ##### "
        ],
        '$': [
            "  ###  ",
            " #   # ",
            " ##### ",
            "  #   #",
            " ##### ",
            " #   # ",
            "  ###  "
        ],
        '%': [
            "#    # ",
            " #  #  ",
            "  ##   ",
            "  ##   ",
            " #  #  ",
            "#    # ",
            "       "
        ],
        '&': [
            "  ###  ",
            " #   # ",
            " #   # ",
            "  ###  ",
            " # # # ",
            "#  # # ",
            "  ## # "
        ],
        '^': [
            "   #   ",
            "  # #  ",
            " #   # ",
            "       ",
            "       ",
            "       ",
            "       "
        ],
        '*': [
            "       ",
            "  # #  ",
            "   #   ",
            "#######",
            "   #   ",
            "  # #  ",
            "       "
        ],
        '~': [
            "       ",
            "       ",
            "       ",
            " ### # ",
            "#     #",
            "       ",
            "       "
        ],
        '`': [
            "  #    ",
            "   #   ",
            "       ",
            "       ",
            "       ",
            "       ",
            "       "
        ],
        '|': [
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   ",
            "   #   "
        ],
        '\\': [
            "#      ",
            " #     ",
            "  #    ",
            "   #   ",
            "    #  ",
            "     # ",
            "      #"
        ],
        '/': [
            "      #",
            "     # ",
            "    #  ",
            "   #   ",
            "  #    ",
            " #     ",
            "#      "
        ],
        '-': [
            "       ",
            "       ",
            "       ",
            "#####  ",
            "       ",
            "       ",
            "       "
        ],
        '_': [
            "       ",
            "       ",
            "       ",
            "       ",
            "       ",
            "       ",
            "#######"
        ],
        '+': [
            "       ",
            "   #   ",
            "   #   ",
            " ##### ",
            "   #   ",
            "   #   ",
            "       "
        ],
        '=': [
            "       ",
            "       ",
            "#######",
            "       ",
            "#######",
            "       ",
            "       "
        ],
        '<': [
            "    #  ",
            "   #   ",
            "  #    ",
            " #     ",
            "  #    ",
            "   #   ",
            "    #  "
        ],
        '>': [
            " #     ",
            "  #    ",
            "   #   ",
            "    #  ",
            "   #   ",
            "  #    ",
            " #     "
        ],
        '[': [
            "  ###  ",
            "  #    ",
            "  #    ",
            "  #    ",
            "  #    ",
            "  #    ",
            "  ###  "
        ],
        ']': [
            "  ###  ",
            "    #  ",
            "    #  ",
            "    #  ",
            "    #  ",
            "    #  ",
            "  ###  "
        ],
        '{': [
            "   ##  ",
            "  #    ",
            "  #    ",
            " ##    ",
            "  #    ",
            "  #    ",
            "   ##  "
        ],
        '}': [
            "  ##   ",
            "    #  ",
            "    #  ",
            "    ## ",
            "    #  ",
            "    #  ",
            "  ##   "
        ],
        '(': [
            "   ##  ",
            "  #    ",
            " #     ",
            " #     ",
            " #     ",
            "  #    ",
            "   ##  "
        ],
        ')': [
            "  ##   ",
            "    #  ",
            "     # ",
            "     # ",
            "     # ",
            "    #  ",
            "  ##   "
        ],
        '{': [
            "   ##  ",
            "  #    ",
            "  #    ",
            " ##    ",
            "  #    ",
            "  #    ",
            "   ##  "
        ],
        '}': [
            "  ##   ",
            "    #  ",
            "    #  ",
            "    ## ",
            "    #  ",
            "    #  ",
            "  ##   "
        ],
        '<': [
            "    #  ",
            "   #   ",
            "  #    ",
            " #     ",
            "  #    ",
            "   #   ",
            "    #  "
        ],
        '>': [
            "  #    ",
            "   #   ",
            "    #  ",
            "     # ",
            "    #  ",
            "   #   ",
            "  #    "
        ],
        ',': [
            "       ",
            "       ",
            "       ",
            "       ",
            "   ##  ",
            "   ##  ",
            "  ##   "
        ],
        '.': [
            "       ",
            "       ",
            "       ",
            "       ",
            "       ",
            "       ",
            "   ##  "
        ],
        ':': [
            "   ##  ",
            "   ##  ",
            "       ",
            "       ",
            "   ##  ",
            "   ##  ",
            "       "
        ],
    }
    return patterns.get(letter, [""] * 7)

def print_pattern(word):
    patterns = [get_pattern(letter.upper()) for letter in word]
    max = 0
    for i in range(7):
        line = "".join([pattern[i] for pattern in patterns])
        print(line)
        if len(line) > max:
            max = len(line)
    return max


print("\n")
width = print_pattern("DigiQuest")
print()
print("#"*width)
print()
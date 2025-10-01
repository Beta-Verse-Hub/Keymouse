# Keymouse (Keyboard-to-Mouse Controller)

This project allows you to control your mouse cursor using the keyboard.

## Dependencies
The python code uses the following libraries and modules :
- pynput (*)
- keyboard (*)
- threading
- json
- time
- sys

(*) = The modules/libraries which aren't pre-installed.

To download the non-pre-installed modules/libraries:
```bash
pip install pynput keyboard
```

## Controls

The controls can be changed in the control_keys.json
The default configuration is like this:

| Action       | Key(s)               |
|--------------|----------------------|
| Toggle Combo | PrintScreen + Insert |
| Move Up      | ↑                    |
| Move Down    | ↓                    |
| Move Left    | ←                    |
| Move Right   | →                    |
| Left Click   | Z                    |
| Middle Click | X                    |
| Right Click  | C                    |
| Scroll Up    | W                    |
| Scroll Down  | S                    |
| Scroll Left  | A                    |
| Scroll Right | D                    |
| Change Speed | 1,2,3,4,5,6,7,8,9&0  |
| Exit program | Esc                  |


## How to use

1. Download the zip file from the releases section.
2. Unzip the zip file and keep the program in this format in one folder (the order doesn't matter).
.
├── Keymouse.exe         # Main executable file
├── control keys.json    # JSON file with key mappings
├── LICENCE              # The Licence
└── README.md            # Project documentation
3. Run the executable file.
4. Toggle between keyboard mode and mouse mode with a key combo.
5. Control mouse movement using assigned keys.
6. Perform left, middle, and right clicks from the keyboard.
7. Scroll up, down, left, right with keys.
8. Adjustable cursor and scroll speed (1–10 levels).
   **Note: The speed manipulation depends upon the last action, so if the last action was scroll then you can change the scroll speed and if the last action was moving the cursor then you can change the cursor speed**
9. Press the exit key, **when in mouse mode**, to quit the program.

## Notes

- This script suppresses keyboard input in mouse mode (so keystrokes won’t reach other apps while active).
- Run with admin privileges on Windows if some stuff doesn't work.
- Works best on Windows; it hasn't been tested in macOS and Linux.
- **Do not update the keys in the control_keys.json file until you know what you are doing!**

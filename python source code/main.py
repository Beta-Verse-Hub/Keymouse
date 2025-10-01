# Importing modules
from pynput import keyboard, mouse
import threading
import keyboard as kb
import json
import time
import sys



# GLOBAL VARIABLES

# Running variable
running = True

# Speeds
min_mouse_speed = 3
max_mouse_speed = 7
scroll_speed = 2
mouse_speed = min_mouse_speed
speed_change_mode = "cursor"

# Mouse parameters
mouseCon = mouse.Controller()
mouse_mode = False

# Pressed key variables
pressed = set()
pressed_lock = threading.Lock()

# Listeners
non_supp_listener = None
supp_listener = None

# Toggle variables
last_toggle_time = 0.0
TOGGLE_DELAY = 0.3
toggle_pressed = False

# Control keys
control_keys = {}



# FUNCTIONS

# JSON functions

def get_control_keys():
    """
    Loads the control keys mappings from the control keys JSON file.

    This function reads the control key mappings from the control keys JSON file and stores them in the control_keys dictionary.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global control_keys

    with open("control keys.json", "r") as f:
        control_keys = json.load(f)


# Utility functions

def name_from_key(key):
    """
    Returns a string name for a given key.

    This function takes a key (either a KeyCode or a Key) and returns a string name for that key.

    For KeyCode, it returns the lowercase character of the key if it has one, or a string representation of the key otherwise.

    For Key, it returns the lowercase name of the key.

    For any other type of key, it returns a generic string representation of the key, converted to lowercase.

    Parameters
    ----------
    key : KeyCode or Key
        The key to get the name from

    Returns
    -------
    str
        The string name for the given key
    """
    # If it's a KeyCode (alphanumeric, symbols)
    if isinstance(key, keyboard.KeyCode):
        if key.char is not None:
            return key.char.lower()
        return str(key)
    
    # If it's a Key (special key: arrows, esc, insert, etc.)
    if isinstance(key, keyboard.Key):
        return key.name.lower()

    return str(key).lower()  # Generic fallback


def key_present(pressed_keys, wanted_keys):
    """
    Checks if a certain key or key starting with a certain string is present in a set of currently pressed keys.

    Parameters
    ----------
    pressed_keys : set
        A set of currently pressed keys.
    wanted_keys : str or pynput.keyboard.Key
        The key or key starting with a certain string to look for.

    Returns
    -------
    bool
        True if the key or key starting with a certain string is present, False otherwise.
    """
    for k in pressed_keys:
        if k == wanted_keys or k.startswith(wanted_keys):
            return True
    return False


def toggle_combo_present(pressed_keys):
    """
    Checks if the toggle combo is present in a set of currently pressed keys.

    Parameters
    ----------
    pressed_keys : set
        A set of currently pressed keys.

    Returns
    -------
    bool
        True if the toggle combo is present, False otherwise.
    """
    a = control_keys["toggle combo 1st button"] in pressed_keys
    b = control_keys["toggle combo 2nd button"] in pressed_keys
    return a and b


# Listener Callbacks

def on_press_common(key):
    """
    A common callback for the on_press event of both the suppressed and non-suppressed listeners.

    This callback is responsible for adding the name of the pressed key to the set of currently pressed keys.

    Parameters
    ----------
    key : pynput.keyboard.Key
        The key that was pressed.

    Returns
    -------
    None
    """
    n = name_from_key(key)
    with pressed_lock:
        pressed.add(n)


def on_release_common(key):
    """
    A common callback for the on_release event of both the suppressed and non-suppressed listeners.

    This callback is responsible for removing the name of the released key from the set of currently pressed keys.

    Parameters
    ----------
    key : pynput.keyboard.Key
        The key that was released.

    Returns
    -------
    None
    """
    n = name_from_key(key)
    with pressed_lock:
        pressed.discard(n)


# Suppressed callbacks

def on_press_supp(key):
    """
    The callback for the on_press event of the suppressed listener.

    This callback is responsible for adding the name of the pressed key to the set of currently pressed keys.

    Additionally, it checks if the mouse mode is not enabled and, if so, presses the key using keyboard.press.

    It also checks if the toggle combo is present in the set of currently pressed keys and, if so, exits mouse mode.

    Parameters
    ----------
    key : pynput.keyboard.Key
        The key that was pressed.

    Returns
    -------
    None
    """
    global pressed_keys
    on_press_common(key)

    with pressed_lock:
        pressed_keys = set(pressed)

    if not mouse_mode:
        kb.press(key)

    if toggle_combo_present(pressed_keys):
        exit_mouse_mode()


def on_release_supp(key):
    """
    The callback for the on_release event of the suppressed listener.

    This function is responsible for releasing the pressed key from the set of currently pressed keys.

    Additionally, it checks if the mouse mode is not enabled and, if so, releases the key using keyboard.release.

    Parameters
    ----------
    key : pynput.keyboard.Key
        The key that was released.

    Returns
    -------
    None
    """
    on_release_common(key)

    if not mouse_mode:
        kb.release(key)


# Listeners

def start_supp_listener():
    """
    Starts the suppressed listener if it is not already running.

    The suppressed listener is responsible for capturing keyboard events while in mouse mode and exiting mouse mode when the PrintScreen + insert combination is pressed.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global supp_listener

    if supp_listener is None:
        supp_listener = keyboard.Listener(on_press=on_press_supp, on_release=on_release_supp, daemon = True, suppress=True)
        supp_listener.start()


def stop_supp_listener():
    """
    Stops the suppressed listener if it is running.

    The suppressed listener is responsible for capturing keyboard events while in mouse mode and exiting mouse mode when the PrintScreen + insert combination is pressed.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global supp_listener

    if supp_listener is not None:
        supp_listener.stop()
        supp_listener = None


# App exit

def exit_app():
    """
    Exits the application.

    Stops the suppressed listener, sets the running flag to False, and exits the application using sys.exit(0).

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global running
    stop_supp_listener()
    running = False
    sys.exit(0)


# Mode switching

def enter_mouse_mode():
    """
    Enters mouse mode.

    Clears the set of currently pressed keys to avoid sticky keys, starts the suppressed listener, and sets the mouse_mode flag to True.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global mouse_mode

    with pressed_lock:
        pressed.clear()

    start_supp_listener()

    mouse_mode = True
    print("Entered mouse mode")


def exit_mouse_mode():
    """
    Exits mouse mode.

    Clears the set of currently pressed keys to avoid sticky keys, stops the suppressed listener, and sets the mouse_mode flag to False.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global mouse_mode

    with pressed_lock:
        pressed.clear()

    stop_supp_listener()

    mouse_mode = False
    print("Exited mouse mode")


# Mouse control loop

def mouse_control_loop():
    """
    Main loop for mouse control.

    Toggles mouse mode with PrintScreen + insert combination, exits the application with the exit key, and toggles mouse speed with the number keys (1-10).

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global mouse_speed, scroll_speed, speed_change_mode, running, last_toggle_time, TOGGLE_DELAY, toggle_pressed, control_keys

    print(f"Started. Toggle mouse mode with {control_keys["toggle combo 1st button"]} + {control_keys["toggle combo 2nd button"]}.")

    while running:

        time.sleep(0.01)

        keys_down = kb.is_pressed(control_keys["toggle combo 1st button"]) and kb.is_pressed(control_keys["toggle combo 2nd button"])

        if keys_down and not toggle_pressed:
            if time.time() - last_toggle_time > TOGGLE_DELAY:
                if mouse_mode:
                    exit_mouse_mode()
                else:
                    enter_mouse_mode()
                last_toggle_time = time.time()
            toggle_pressed = True
        elif not keys_down:
            toggle_pressed = False

        if not mouse_mode:
            continue

        with pressed_lock:
            pressed_keys = set(pressed)

        # Detect exiting key
        if key_present(pressed_keys, control_keys["exit"]) and mouse_mode:
            exit_app()

        # Toggle mouse speed
        for i in range(1, 11):
            if key_present(pressed_keys, control_keys[f"speed {i}"]):
                if speed_change_mode == "cursor":
                    mouse_speed = i
                    print(f"Cursor speed: {mouse_speed}")
                elif speed_change_mode == "scroll":
                    scroll_speed = i
                    print(f"Scroll speed: {scroll_speed}")

                while key_present(pressed_keys, control_keys[f"speed {i}"]):
                    time.sleep(0.01)
                    with pressed_lock:
                        pressed_keys = set(pressed)

        # Movement keys
        if key_present(pressed_keys, control_keys["move up"]):
            mouseCon.move(0, -mouse_speed)
            speed_change_mode = "cursor"

        if key_present(pressed_keys, control_keys["move down"]):
            mouseCon.move(0, mouse_speed)
            speed_change_mode = "cursor"

        if key_present(pressed_keys, control_keys["move left"]):
            mouseCon.move(-mouse_speed, 0)
            speed_change_mode = "cursor"

        if key_present(pressed_keys, control_keys["move right"]):
            mouseCon.move(mouse_speed, 0)
            speed_change_mode = "cursor"

        # Mouse clicks
        if control_keys["left click"] in pressed_keys: # Left
            mouseCon.click(mouse.Button.left)
            while control_keys["left click"] in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if control_keys["middle click"] in pressed_keys: # Middle
            mouseCon.click(mouse.Button.middle)
            while control_keys["middle click"] in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if control_keys["right click"] in pressed_keys: # Right
            mouseCon.click(mouse.Button.right)
            while control_keys["right click"] in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        # Scroll
        if control_keys["scroll up"] in pressed_keys: # Up
            mouseCon.scroll(0, scroll_speed)
            speed_change_mode = "scroll"
            while control_keys["scroll up"] in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if control_keys["scroll down"] in pressed_keys: # Down
            mouseCon.scroll(0, -scroll_speed)
            speed_change_mode = "scroll"
            while control_keys["scroll down"] in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if control_keys["scroll left"] in pressed_keys: # Left
            mouseCon.scroll(-scroll_speed, 0)
            speed_change_mode = "scroll"
            while control_keys["scroll left"] in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if control_keys["scroll right"] in pressed_keys: # Right
            mouseCon.scroll(scroll_speed, 0)
            speed_change_mode = "scroll"
            while control_keys["scroll right"] in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

# MAIN
if __name__ == "__main__":
    # Get Control Keys
    get_control_keys()

    # Mouse controller loop
    mouse_control_loop()

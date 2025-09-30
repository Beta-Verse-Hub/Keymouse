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

# Mouse parameters
mouseCon = mouse.Controller()
mouse_mode = False
mouse_speed = min_mouse_speed

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



# FUNCTIONS

# Utility functions
def name_from_key(key):
    """
    Returns the name of a key object as a lowercase string.

    For alphanumeric keys, this is the character itself (e.g. "a" or "A" become "a").
    For other keys, this is the name of the key (e.g. "ctrl" or "insert").

    Parameters
    ----------
    key : pynput.keyboard.Key
        The key object to get the name from.

    Returns
    -------
    str
        The lowercase name of the key.
    """
    # If it's a KeyCode (alphanumeric, symbols)
    if isinstance(key, keyboard.KeyCode):
        if key.char is not None:
            return key.char.lower()
        return str(key)
    
    # If it's a Key (special key: arrows, esc, insert, etc.)
    if isinstance(key, keyboard.Key):
        return key.name.lower()

    return str(key).lower()  # generic fallback


def key_present(pressed_keys, wanted_keys):
    """
    Checks if a given key is present in a set of currently pressed keys.

    Parameters
    ----------
    pressed_keys : set
        A set of currently pressed keys.
    wanted_keys : str
        The key to search for.

    Returns
    -------
    bool
        True if the key is present, False otherwise.
    """
    for k in pressed_keys:
        if k == wanted_keys or k.startswith(wanted_keys):
            return True
    return False


def toggle_combo_present(pressed_keys):
    """
    Checks if both the PrintScreen and insert keys are present in the given set of pressed keys.

    Parameters
    ----------
    pressed_keys : set
        A set of currently pressed keys.

    Returns
    -------
    bool
        True if both keys are present, False otherwise.
    """
    ps_names = ("print_screen", "print screen", "printscreen", "prt_sc")
    insert_names = ("insert",)
    return any(name in pressed_keys for name in ps_names) and any(name in pressed_keys for name in insert_names)


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

    This function is responsible for adding the name of the pressed key to the set of currently pressed keys.

    Additionally, it checks if both the PrintScreen and insert keys are present and, if so, exits the suppressed mode by calling exit_mouse_mode in a separate thread.

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

    This function is responsible for removing the name of the released key from the set of currently pressed keys.

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

    This function is responsible for stopping the non-suppressed and suppressed listeners and exiting the application.

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

    Clears the set of currently pressed keys to avoid sticky keys, stops the non-suppressed listener, starts the suppressed listener, and sets the mouse_mode flag to True.

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

    Clears the set of currently pressed keys to avoid sticky keys, stops the suppressed listener, starts the non-suppressed listener, and sets the mouse_mode flag to False.

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
    A loop that listens to keyboard events and controls the mouse accordingly.

    This loop is responsible for detecting the exiting key (ESC) and exiting the application if mouse mode is enabled.
    It also detects the toggling of mouse speed using the ALT key and prints the current mouse speed.

    Furthermore, it detects movement keys (UP, DOWN, LEFT, RIGHT), mouse clicks (Z, X, C), and scroll keys (W, S, A, D) and moves the mouse accordingly.
    It also prevents sticky keys by waiting for the key to be released before continuing.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global mouse_speed, running, last_toggle_time, TOGGLE_DELAY, toggle_pressed

    print("Started. Toggle mouse mode with PrintScreen + insert.")

    while running:

        time.sleep(0.01)

        keys_down = kb.is_pressed("print screen") and kb.is_pressed("insert")

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
        if key_present(pressed_keys, "esc") and mouse_mode:
            exit_app()

        # Toggle mouse speed
        if any(k.startswith("alt") for k in pressed_keys):

            mouse_speed = max_mouse_speed if mouse_speed == min_mouse_speed else min_mouse_speed
            print("mouse_speed:", mouse_speed)

            while any(k.startswith("alt") for k in pressed_keys):
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        # Movement keys
        if "up" in pressed_keys:    mouseCon.move(0, -mouse_speed)
        if "down" in pressed_keys:  mouseCon.move(0, mouse_speed)
        if "left" in pressed_keys:  mouseCon.move(-mouse_speed, 0)
        if "right" in pressed_keys: mouseCon.move(mouse_speed, 0)

        # Mouse clicks
        if "z" in pressed_keys: # Left
            mouseCon.click(mouse.Button.left)
            while "z" in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if "x" in pressed_keys: # Middle
            mouseCon.click(mouse.Button.middle)
            while "x" in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if "c" in pressed_keys: # Right
            mouseCon.click(mouse.Button.right)
            while "c" in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        # Scroll
        if "w" in pressed_keys: # Up
            mouseCon.scroll(0, scroll_speed)
            while "w" in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if "s" in pressed_keys: # Down
            mouseCon.scroll(0, -scroll_speed)
            while "s" in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if "a" in pressed_keys: # Left
            mouseCon.scroll(-scroll_speed, 0)
            while "a" in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

        if "d" in pressed_keys: # Right
            mouseCon.scroll(scroll_speed, 0)
            while "d" in pressed_keys:
                time.sleep(0.01)
                with pressed_lock:
                    pressed_keys = set(pressed)

# MAIN
if __name__ == "__main__":
    # Mouse controller loop
    mouse_control_loop()

# Importing important libraries
import pynput.mouse as mouse
import pynput.keyboard as keyboard
import threading
from time import sleep



# Defining global variables
mouseCon = mouse.Controller()
keyboardCon = keyboard.Controller()
previous_keys = []



# Defining functions
def listen():
    """
    Starts a keyboard listener in a separate thread and waits for it to finish.

    This function starts a keyboard listener with the on_press and on_release
    functions as the event handlers. It then waits for the listener to finish

    in a separate thread.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def on_press(key):
    """
    Handles the event when a key is pressed.

    This function is called when a key is pressed. It appends the key to the
    previous_keys list and prints the key.

    Global Variables
    ----------------
    mouseCon : pynput.mouse.Controller
        The mouse controller object.
    keyboardCon : pynput.keyboard.Controller
        The keyboard controller object.
    previous_keys : list
        The list of previous keys pressed.

    Parameters
    ----------
    key : pynput.keyboard.Key
        The key that was pressed.
    
    Returns
    -------
    None
    """
    global mouseCon, keyboardCon, previous_keys
    previous_keys.append(key)
    print(key)


def on_release(key):
    """
    Handles the event when a key is released.

    This function is called when a key is released. It checks if the previous key
    pressed was the shift key and the control key. If so, it prints a message
    indicating that the water bucket has been released and resets the list of
    previous keys. If the previous key was not the shift key, it resets the list of
    previous keys.

    Global Variables
    -----------------
    mouseCon : pynput.mouse.Controller
        The mouse controller object.
    keyboardCon : pynput.keyboard.Controller
        The keyboard controller object.
    previous_keys : list
        The list of previous keys pressed.

    Parameters
    ----------
    key : pynput.keyboard.Key
        The key that was released.

    Returns
    -------
    None
    """
    global mouseCon, keyboardCon, previous_keys
    if previous_keys == [keyboard.Key.shift, keyboard.Key.ctrl_l]:
        print("Water bucket RELEASE!")
        previous_keys = []
    elif not previous_keys == [keyboard.Key.shift]:
        previous_keys = []


# Defining threads
listeningThread = threading.Thread(target=listen, args=())
listeningThread.start()

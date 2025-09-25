# Importing important libraries
import pynput.mouse as mouse
from keyboard import is_pressed, block_key, unblock_key, release
import threading
import tkinter
from time import sleep



# Defining global variables
mouseCon = mouse.Controller()
mouse_mode = False
min_mouse_speed = 3
max_mouse_speed = 7
mouse_speed = min_mouse_speed
scroll_speed = 2



# Defining functions
def block_keys(state: bool):
    """
    Blocks all keys on the keyboard if state is True, or unblocks them if state is False.

    :param state: A boolean indicating whether to block or unblock the keys.
    :type state: bool
    """
    keys = (
        [chr(c) for c in range(32, 127)]   # space to ~
        + ["up", "down", "left", "right",
           "shift", "ctrl", "alt",
           "caps lock", "tab", "enter", "backspace"]
    )

    for k in keys:
        try:
            if state:
                block_key(k)
            else:
                unblock_key(k)
        except:
            pass

def listen():
    """
    Listens for keyboard events and controls the mouse accordingly.

    Keys and their corresponding actions are as follows:
    - shift + ctrl: toggle mouse mode
    - alt: toggle mouse speed
    - up/down/left/right: moves the mouse in the respective direction
    - z/x/c: performs a left/middle/right click respectively
    - s/w: scrolls the mouse down/up respectively
    - a/d: scrolls the mouse left/right respectively

    The function will terminate when the "esc" key is pressed.
    """
    global mouseCon, mouse_mode, mouse_speed

    while not(is_pressed("esc") and mouse_mode):

        if is_pressed("print screen") and is_pressed("F12"):

            if mouse_mode:
                mouse_mode = False
                block_keys(False)
            else:
                mouse_mode = True
                block_keys(True)

            release("print screen")
            release("F12")

            print(f"Mouse mode: {mouse_mode}")

            while is_pressed("print screen") and is_pressed("F12"):
                sleep(0.01)

        if not mouse_mode:
            continue

        if is_pressed("print screen") and is_pressed("F12"):
            continue

        if is_pressed("esc"):
            break

        if is_pressed("alt"):
            if mouse_speed == min_mouse_speed:
                mouse_speed = max_mouse_speed
            else:
                mouse_speed = min_mouse_speed

            print(f"mouse_speed: {mouse_speed}")

            while is_pressed("alt"):
                sleep(0.01)

        if is_pressed("up"):
            mouseCon.move(0,-mouse_speed)

        if is_pressed("down"):
            mouseCon.move(0,mouse_speed)

        if is_pressed("left"):
            mouseCon.move(-mouse_speed,0)

        if is_pressed("right"):
            mouseCon.move(mouse_speed,0)
        
        if is_pressed("z"):
            mouseCon.click(mouse.Button.left)
            while is_pressed("z"):
                sleep(0.01)
        
        if is_pressed("x"):
            mouseCon.click(mouse.Button.middle)
            while is_pressed("x"):
                sleep(0.01)
        
        if is_pressed("c"):
            mouseCon.click(mouse.Button.right)
            while is_pressed("c"):
                sleep(0.01)
        
        if is_pressed("s"):
            mouseCon.scroll(0,-scroll_speed)
            while is_pressed("s"):
                sleep(0.01)
        
        if is_pressed("w"):
            mouseCon.scroll(0,scroll_speed)
            while is_pressed("w"):
                sleep(0.01)
        
        if is_pressed("a"):
            mouseCon.scroll(-scroll_speed,0)
            while is_pressed("a"):
                sleep(0.01)
        
        if is_pressed("d"):
            mouseCon.scroll(scroll_speed,0)
            while is_pressed("d"):
                sleep(0.01)

        sleep(0.01)


if __name__ == "__main__":
    # Defining threads
    # TkinterThread = threading.Thread(target=Tkinter_loop, args=())
    # TkinterThread.start()

    listeningThread = threading.Thread(target=listen, args=())
    listeningThread.start()

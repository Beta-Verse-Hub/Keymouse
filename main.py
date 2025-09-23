# Importing important libraries
import pynput.mouse as mouse
from keyboard import is_pressed, on_press, wait
import threading
import tkinter
from time import sleep



# Defining global variables
mouseCon = mouse.Controller()
mouse_mode = False
speed = 3



# Defining functions
def listen():
    """
    Listens for keyboard inputs to control the mouse.

    It checks for the following keyboard inputs:

    - Shift + Ctrl: Toggle mouse mode
    - Alt: Toggle speed between 1 and 3
    - Up, Down, Left, Right: Move the mouse in the respective direction
    - Ctrl + Shift + Esc: Quit the program

    It continues to listen until the program is quit.
    """
    global mouseCon, mouse_mode, speed

    while not(is_pressed("esc")):

        if is_pressed("shift") and is_pressed("ctrl"):

            if mouse_mode:
                mouse_mode = False
            else:
                mouse_mode = True

            print(f"Mouse mode: {mouse_mode}")

            while is_pressed("shift") and is_pressed("ctrl"):
                sleep(0.01)

        if not mouse_mode:
            continue

        wait(["up", "down", "left", "right", "ctrl", "shift", "esc", "alt"])

        if is_pressed("ctrl") and is_pressed("shift"):
            continue

        if is_pressed("esc"):
            break

        if is_pressed("alt"):
            if speed == 1:
                speed = 7
            else:
                speed = 3

            print(f"Speed: {speed}")

            while is_pressed("alt"):
                sleep(0.01)

        if is_pressed("up"):
            mouseCon.move(0,-speed)

        if is_pressed("down"):
            mouseCon.move(0,speed)

        if is_pressed("left"):
            mouseCon.move(-speed,0)

        if is_pressed("right"):
            mouseCon.move(speed,0)

        sleep(0.01)


if __name__ == "__main__":
    # Defining threads
    # TkinterThread = threading.Thread(target=Tkinter_loop, args=())
    # TkinterThread.start()

    listeningThread = threading.Thread(target=listen, args=())
    listeningThread.start()

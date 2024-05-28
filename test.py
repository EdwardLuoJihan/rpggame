import pyautogui
import time
import keyboard
import pyscreeze

on = True

while True:
    if keyboard.is_pressed('b'):
        if on:
            on = False
            print("Click off")
        else:
            on = True
            print("Click on")
        time.sleep(1)
    if on:
        pyautogui.moveTo(1805, 969)
        pyautogui.leftClick()
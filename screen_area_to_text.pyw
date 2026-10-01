import os
import sys
import time
import subprocess
import shutil
import tkinter as tk
from PIL import ImageGrab
import pyperclip
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------           
# Screen Area OCR Tool
# -----------------------------

def select_area():
    """Let the user drag a rectangle over the screen."""
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.25)
    root.attributes("-topmost", True)
    root.configure(bg="black")

    canvas = tk.Canvas(root, cursor="cross", bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    start_x = start_y = None
    rectangle = None
    result = None

    def mouse_down(event):
        nonlocal start_x, start_y, rectangle
        start_x, start_y = event.x, event.y
        rectangle = canvas.create_rectangle(
            start_x, start_y, start_x, start_y,
            outline="red", width=2
        )

    def mouse_move(event):
        if rectangle is not None:
            canvas.coords(rectangle, start_x, start_y, event.x, event.y)

    def mouse_up(event):
        nonlocal result
        x1, x2 = sorted((start_x, event.x))
        y1, y2 = sorted((start_y, event.y))

        if x2 - x1 > 2 and y2 - y1 > 2:
            result = (x1, y1, x2, y2)

        root.destroy()

    def cancel(event):
        root.destroy()

    canvas.bind("<ButtonPress-1>", mouse_down)
    canvas.bind("<B1-Motion>", mouse_move)
    canvas.bind("<ButtonRelease-1>", mouse_up)
    root.bind("<Escape>", cancel)

    root.mainloop()
    return result


def main():
    print("=== Screen Area → Text ===")
    print()
    print("Drag a box around the text you want to capture.")

    area = select_area()

    if not area:
        print("No area selected. Exiting.")
        return

    screenshot_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "_temporary_ocr_screenshot.png"
    )

    try:
        # Take the screenshot.
        screenshot = ImageGrab.grab(bbox=area)
        screenshot.save(screenshot_path)

        print("Screenshot taken. Converting to text...")

        # OCR the screenshot.
        text = pytesseract.image_to_string(screenshot).strip()


        if not text:
            print("\nNo text was detected.")
            return

        
        print("\n========== DETECTED TEXT ==========")
        print(text)
        print("===================================\n")


        # Put the OCR result into the clipboard.
        pyperclip.copy(text)

        print("The text has been copied to your clipboard.")
        print("You can now paste it anywhere with Ctrl+V.")

    finally:
        # Always remove the temporary screenshot.
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
                print("Temporary screenshot deleted.")
            except PermissionError:
                print("Could not delete the screenshot because another program is using it.")


if __name__ == "__main__":
    main()

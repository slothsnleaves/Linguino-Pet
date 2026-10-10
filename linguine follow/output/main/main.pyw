import sys
import os

# 1. SUPPRESS THE COLOURED PYGAME BANNER TEXT
# This environment variable MUST be set BEFORE importing pygame to hide the text
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import math
import ctypes
import tkinter as tk
from tkinter import filedialog, ttk
import pygame

# Global variable to hold the path once selected
selected_image_path = None

def open_file_picker():
    """Opens the file picker and updates the UI label."""
    global selected_image_path
    path = filedialog.askopenfilename(
        title="Select your Linguino PNG",
        filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
)
    if path:
        selected_image_path = path
        file_label.config(text=os.path.basename(path), foreground="#2ecc71")
        launch_btn.config(state="normal")

def start_pet():
    """Closes the setup window and continues execution."""
    root.quit()

# 2. CREATE A SLEEK CONTROL PANEL STARTUP WINDOW
root = tk.Tk()
root.title("Linguine Desktop Setup")
root.geometry("340x180")
root.resizable(False, False)
root.configure(bg="#1e1e24")

# Custom Title Label
title_lbl = tk.Label(root, text="🐾 Linguine Desktop Pet", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#1e1e24")
title_lbl.pack(pady=15)

# Selected File Label Indicator
file_label = tk.Label(root, text="No pet asset selected", font=("Segoe UI", 9, "italic"), fg="#a0a0a0", bg="#1e1e24")
file_label.pack(pady=2)

# Button Panel Layout
btn_frame = tk.Frame(root, bg="#1e1e24")
btn_frame.pack(pady=15)

browse_btn = tk.Button(btn_frame, text="Browse PNG", command=open_file_picker, width=12, bg="#2f3136", fg="white", font=("Segoe UI", 10), relief="flat")
browse_btn.grid(row=0, column=0, padx=10)

launch_btn = tk.Button(btn_frame, text="Launch Pet", command=start_pet, state="disabled", width=12, bg="#007acc", fg="white", font=("Segoe UI", 10, "bold"), relief="flat")
launch_btn.grid(row=0, column=1, padx=10)

# Start the Tkinter UI event loop
root.mainloop()

# Cleanly destroy the Tkinter window once users press "Launch Pet"
root.destroy()

# Exit cleanly if they closed the window without picking a file
if not selected_image_path:
    sys.exit()

# 3. INITIALIZE PYGAME (Now completely silent!)
pygame.init()

CAT_WIDTH, CAT_HEIGHT = 90, 90  
PET_SPEED = 3                   

screen = pygame.display.set_mode((CAT_WIDTH, CAT_HEIGHT), pygame.NOFRAME)
clock = pygame.time.Clock()

try:
    original_image = pygame.image.load(selected_image_path).convert_alpha()
except pygame.error:
    sys.exit()

# Process left and right visual directions
image_right = pygame.transform.scale(original_image, (CAT_WIDTH, CAT_HEIGHT))
image_left = pygame.transform.flip(image_right, True, False)
current_image = image_right

# Set up graphics surface
screen.fill((255, 0, 255))
pygame.display.flip()
pygame.event.pump()

hwnd = pygame.display.get_wm_info()["window"]
GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, WS_EX_TOPMOST | WS_EX_TRANSPARENT | WS_EX_LAYERED)
ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0xFF00FF, 0, 0x00000001)

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

pt = POINT()
ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))

current_x = pt.x - (CAT_WIDTH // 2)
current_y = pt.y - (CAT_HEIGHT // 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    target_x = pt.x - (CAT_WIDTH // 2)
    target_y = pt.y - (CAT_HEIGHT // 2)

    dx = target_x - current_x
    dy = target_y - current_y
    distance = math.hypot(dx, dy)

    if distance > 5:
        ratio = PET_SPEED / distance
        if ratio >= 1.0:
            current_x = target_x
            current_y = target_y
        else:
            current_x += dx * ratio
            current_y += dy * ratio

        if dx > 1:
            current_image = image_right
        elif dx < -1:
            current_image = image_left

    pygame.display.set_window_position((int(current_x), int(current_y)))
    screen.fill((255, 0, 255)) 
    screen.blit(current_image, (0, 0)) 
    pygame.display.flip()
    clock.tick(60) 

pygame.quit()
sys.exit()

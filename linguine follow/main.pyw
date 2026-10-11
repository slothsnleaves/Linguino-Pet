import sys
import os

# 1. SUPPRESS THE COLOURED PYGAME BANNER TEXT
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import math
import ctypes
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pygame
import random
import subprocess

# Global variable to hold the path once selected
selected_image_path = None

# Check if an image path was passed as a command-line argument (meaning this is a spawned twin)
if len(sys.argv) > 1:
    selected_image_path = sys.argv[1]
else:
    def open_file_picker():
        """Opens the file picker and updates the UI label during startup."""
        global selected_image_path
        path = filedialog.askopenfilename(
            title="Select your PNG :)",
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
    root.title("friend setup :)")
    root.geometry("340x180")
    root.resizable(False, False)
    root.configure(bg="#1e1e24")

    # Custom Title Label
    title_lbl = tk.Label(root, text="🐾 friend setup :)", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#1e1e24")
    title_lbl.pack(pady=15)

    # Selected File Label Indicator
    file_label = tk.Label(root, text="No asset selected", font=("Segoe UI", 9, "italic"), fg="#a0a0a0", bg="#1e1e24")
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

# Exit cleanly if no file was picked
if not selected_image_path:
    sys.exit()

# 3. INITIALIZE PYGAME (Now completely silent!)
pygame.init()

CAT_WIDTH, CAT_HEIGHT = 90, 90  
PET_SPEED = 2                 

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

user32 = ctypes.windll.user32

# Setup proper ctypes prototypes for 64-bit safety & native menu commands
user32.SetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long]
user32.SetWindowLongW.restype = ctypes.c_long

user32.SetWindowPos.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, 
    ctypes.c_int, ctypes.c_int, 
    ctypes.c_int, ctypes.c_int, 
    ctypes.c_uint
]

user32.CreatePopupMenu.restype = ctypes.c_void_p
user32.AppendMenuW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_wchar_p]
user32.AppendMenuW.restype = ctypes.c_bool
user32.TrackPopupMenu.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
user32.TrackPopupMenu.restype = ctypes.c_int
user32.DestroyMenu.argtypes = [ctypes.c_void_p]
user32.DestroyMenu.restype = ctypes.c_bool
user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
user32.SetForegroundWindow.restype = ctypes.c_bool

user32.SetWindowLongW(hwnd, GWL_EXSTYLE, WS_EX_TOPMOST | WS_EX_TRANSPARENT | WS_EX_LAYERED)
user32.SetLayeredWindowAttributes(hwnd, 0xFF00FF, 0, 0x00000001)

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

pt = POINT()
user32.GetCursorPos(ctypes.byref(pt))

current_x = pt.x - (CAT_WIDTH // 2)
current_y = pt.y - (CAT_HEIGHT // 2)

# Win32 Constants
HWND_TOPMOST = ctypes.c_void_p(-1)
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
VK_RBUTTON = 0x02

# Menu Constants
TPM_RETURNCMD = 0x0100
TPM_RIGHTBUTTON = 0x0002
MF_STRING = 0x0000
MF_SEPARATOR = 0x0800

right_click_handled = False

def show_context_menu():
    """Builds and displays a native Win32 right-click popup menu."""
    h_menu = user32.CreatePopupMenu()
    user32.AppendMenuW(h_menu, MF_STRING, 1, "🐾 Say Hello")
    user32.AppendMenuW(h_menu, MF_STRING, 3, "👥 Spawn Twin")
    user32.AppendMenuW(h_menu, MF_STRING, 4, "🎨 Change Linguine")
    user32.AppendMenuW(h_menu, MF_STRING, 5, "🔧 Twin Squared")
    user32.AppendMenuW(h_menu, MF_STRING, 7, "⚠️ Information")
    user32.AppendMenuW(h_menu, MF_STRING, 8, "⏰ Time")
    user32.AppendMenuW(h_menu, MF_SEPARATOR, 0, None)
    user32.AppendMenuW(h_menu, MF_STRING, 2, "❌ Exit me")
    user32.AppendMenuW(h_menu, MF_STRING, 6, "🔄 CRASH Twin PC")

    pt_menu = POINT()
    user32.GetCursorPos(ctypes.byref(pt_menu))

    # Required so the menu dismisses properly when clicking outside of it
    user32.SetForegroundWindow(hwnd)

    # TrackPopupMenu returns the ID of the chosen menu item
    cmd = user32.TrackPopupMenu(
        h_menu,
        TPM_RETURNCMD | TPM_RIGHTBUTTON,
        pt_menu.x,
        pt_menu.y,
        0,
        hwnd,
        None
    )
    user32.DestroyMenu(h_menu)

    global running, current_image, image_right, image_left
    if cmd == 1:
        random_message = [
            'ayup mush ya alright ya want a pack o irn bru fro corna shop',
            'hola maricon',
            'miaw miaw miaw miaw miaw (mate im a cat fuck you expect wanna scrap mate)'
        ]
        messagebox.showinfo("Linguino", random.choice(random_message))
    elif cmd == 2:
        messagebox.showinfo("Warning", "NO DONT KILL ME PLEAWSEASEASEASEAWEDQWARFQAEFEWSAGWSRHGYWGHGYWEIGFHNWUEAGFHVNUWSEBNGIUWESBGIWESBI")
        running = False
    elif cmd == 3:
        # Spawn a brand new pet process with a newly chosen asset via file picker
        temp_root = tk.Tk()
        temp_root.withdraw()
        new_path = filedialog.askopenfilename(
            title="Select your twin's PNG :)",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        temp_root.destroy()

        if new_path:
            subprocess.Popen([sys.executable, __file__, new_path])
    elif cmd == 4:
        # Change current pet's asset in-place
        temp_root = tk.Tk()
        temp_root.withdraw()
        new_path = filedialog.askopenfilename(
            title="Select your new PNG :)",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        temp_root.destroy()

        if new_path:
            try:
                new_original = pygame.image.load(new_path).convert_alpha()
                image_right = pygame.transform.scale(new_original, (CAT_WIDTH, CAT_HEIGHT))
                image_left = pygame.transform.flip(image_right, True, False)
                current_image = image_right
            except pygame.error:
                messagebox.showerror("Error", "Could not load the selected image.")
    elif cmd == 5:
        # Twin Squared: Spawns an exact clone of the current pet using the same asset path instantly
        if selected_image_path:
            subprocess.Popen([sys.executable, __file__, selected_image_path])
            
    elif cmd == 6:
        # Summon 1000 clones of the current pet to crash the twin's PC.
        messagebox.showwarning("Warning", "This will spawn 1000 clones of the pet and may crash your PC. Proceed with caution.")
        messagebox.showwarning("Warning", "If you wish to proceed, click OK. Otherwise, close this application immediately.")
        messagebox.showwarning("Warning", "This action is irreversible. Click OK to continue or close the application to cancel.")
        messagebox.showwarning("Warning", "ARE YOU SURE YOU WANT TO PROCEED? This will spawn 1000 clones of the pet and WILL crash your PC.")
        messagebox.showwarning("Warning", "Okay, this is your last chance. Click OK to spawn 1000 clones of the pet and crash your PC, or close the application to cancel.")
        messagebox.showwarning("Warning", "Mk. I know its all fun and games but are you 100 percent sure you want to crash your PC with twin?")
        messagebox.showwarning("Warning", "Okay, have fun.")
        if selected_image_path:
            for _ in range(1000):
                subprocess.Popen([sys.executable, __file__, selected_image_path])
                
    elif cmd == 7:
        random_message = [
                    'poo poo',
                    'pee pee',
                    'wee wee',
                    'woo woo',
                    'sup m8 wan a pint o gravey'
                ]
        messagebox.showinfo("Information", random.choice(random_message))
        
    elif cmd == 8:
        messagebox.showinfo("Time", "check the bottom right you absolute waffel")
        

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    user32.GetCursorPos(ctypes.byref(pt))
    
    # Check if user is right-clicking while hovering over the pet
    is_rclick_down = (user32.GetAsyncKeyState(VK_RBUTTON) & 0x8000) != 0
    is_over_pet = (
        current_x <= pt.x <= current_x + CAT_WIDTH and
        current_y <= pt.y <= current_y + CAT_HEIGHT
    )

    if is_rclick_down and is_over_pet and not right_click_handled:
        right_click_handled = True
        show_context_menu()
    elif not is_rclick_down:
        right_click_handled = False

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
            

    # Keeps the window permanently locked as topmost on every frame
    user32.SetWindowPos(
        hwnd, 
        HWND_TOPMOST, 
        int(current_x), 
        int(current_y), 
        CAT_WIDTH, 
        CAT_HEIGHT, 
        SWP_NOSIZE | SWP_NOACTIVATE
    )

    screen.fill((255, 0, 255)) 
    screen.blit(current_image, (0, 0)) 
    pygame.display.flip()
    clock.tick(60) 

pygame.quit()
sys.exit()
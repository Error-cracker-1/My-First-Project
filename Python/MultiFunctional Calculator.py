import math
import tkinter as tk
import webbrowser
from tkinter import messagebox


# Constants
THEMES = {
    "dark": {
        "background": "#1e1e1e",
        "text": "white",
        "entry_background": "#2b2b2b",
        "button_background": "#333333",
    },
    "light": {
        "background": "#f5f5f5",
        "text": "black",
        "entry_background": "white",
        "button_background": "#e0e0e0",
    },
}

GITHUB_URL = "https://github.com/Error-cracker-1/My-First-Project"


# Global state variables
current_theme = "dark"
labels = []
entries = []
buttons = []


def get_numbers():
    """Return both entry values as floats for two-number operations."""
    return float(entry1.get()), float(entry2.get())


def add():
    """Perform addition of two numbers from entry fields."""
    try:
        num1, num2 = get_numbers()
        result = num1 + num2
        messagebox.showinfo("Result", f"The sum is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")


def subtract():
    """Perform subtraction of two numbers from entry fields."""
    try:
        num1, num2 = get_numbers()
        result = num1 - num2
        messagebox.showinfo("Result", f"The difference is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")


def multiply():
    """Perform multiplication of two numbers from entry fields."""
    try:
        num1, num2 = get_numbers()
        result = num1 * num2
        messagebox.showinfo("Result", f"The product is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")


def divide():
    """Perform division of two numbers from entry fields, handling division by zero."""
    try:
        num1, num2 = get_numbers()
        if num2 == 0:
            messagebox.showerror("Error", "Cannot divide by zero.")
            return
        result = num1 / num2
        messagebox.showinfo("Result", f"The quotient is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")


def exponentiate():
    """Calculate the power of one number raised to another."""
    try:
        num1, num2 = get_numbers()
        result = math.pow(num1, num2)
        messagebox.showinfo(
            "Result",
            f"The result of {num1} raised to the power of {num2} is: {result}",
        )
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")


def square_root():
    """Calculate the square root of the first number, handling negative input."""
    try:
        num = float(entry1.get())
        if num < 0:
            messagebox.showerror(
                "Error",
                "Cannot calculate square root of a negative number.",
            )
            return
        result = math.sqrt(num)
        messagebox.showinfo("Result", f"The square root of {num} is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")


def open_github():
    """Open the project's GitHub page in a web browser."""
    webbrowser.open(GITHUB_URL)


def apply_theme():
    """Apply the selected theme to every visible widget."""
    theme = THEMES[current_theme]

    window.configure(bg=theme["background"])
    canvas.configure(bg=theme["background"], highlightthickness=0)
    scrollable_frame.configure(bg=theme["background"])

    for label in labels:
        label.configure(bg=theme["background"], fg=theme["text"])

    for entry in entries:
        entry.configure(
            bg=theme["entry_background"],
            fg=theme["text"],
            insertbackground=theme["text"],
            relief=tk.FLAT,
        )

    for button in buttons:
        button.configure(
            bg=theme["button_background"],
            fg=theme["text"],
            activebackground=theme["entry_background"],
            activeforeground=theme["text"],
            relief=tk.FLAT,
        )

    next_theme_name = "Light" if current_theme == "dark" else "Dark"
    theme_button.configure(text=f"Switch to {next_theme_name} Mode")


def toggle_theme():
    """Switch between dark mode and light mode."""
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    apply_theme()


def update_scroll_region(event=None):
    """Keep the canvas scroll area synced with the content frame size."""
    canvas.configure(scrollregion=canvas.bbox("all"))


def resize_content_frame(event):
    """Match the inner frame width to the canvas width for a clean layout."""
    canvas.itemconfigure(content_window, width=event.width)


def scroll_with_mouse(event):
    """Support mouse wheel scrolling on Windows, macOS, and Linux."""
    # event.num is for Linux/macOS; event.delta is for Windows
    if getattr(event, "num", None) == 4:  # Mouse wheel up (Linux/macOS)
        canvas.yview_scroll(-1, "units")
    elif getattr(event, "num", None) == 5:  # Mouse wheel down (Linux/macOS)
        canvas.yview_scroll(1, "units")
    elif event.delta:  # Mouse wheel (Windows)
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def create_label(text, row):
    """Create a themed label widget and add it to the global labels list."""
    label = tk.Label(scrollable_frame, text=text, font=("Arial", 11))
    label.grid(row=row, column=0, sticky="ew", padx=24, pady=(10, 4))
    labels.append(label)
    return label


def create_entry(row):
    """Create a themed entry widget and add it to the global entries list."""
    entry = tk.Entry(scrollable_frame, font=("Arial", 12), justify="center")
    entry.grid(row=row, column=0, sticky="ew", padx=24, pady=(0, 10), ipady=6)
    entries.append(entry)
    return entry


def create_button(text, command, row):
    """Create a themed button widget and add it to the global buttons list."""
    button = tk.Button(
        scrollable_frame,
        text=text,
        command=command,
        font=("Arial", 11),
        cursor="hand2",
    )
    button.grid(row=row, column=0, sticky="ew", padx=24, pady=6, ipady=6)
    buttons.append(button)
    return button


# Root window setup
window = tk.Tk()
window.title("MultiFunctional Calculator")
window.geometry("380x500")
window.minsize(320, 360)

# Scrollable root layout: only canvas and scrollbar are packed in root
canvas = tk.Canvas(window, borderwidth=0)
scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# All app content lives inside this frame, which is embedded in the canvas
scrollable_frame = tk.Frame(canvas)
content_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
scrollable_frame.columnconfigure(0, weight=1)

# Input fields
create_label("Number 1:", 0)
entry1 = create_entry(1)
create_label("Number 2:", 2)
entry2 = create_entry(3)

# Calculator actions
create_button("Add (+)", add, 4)
create_button("Subtract (-)", subtract, 5)
create_button("Multiply (*)", multiply, 6)
create_button("Divide (∻)", divide, 7)
create_button("Power (aⁿ)", exponentiate, 8)
create_button("Square Root (√)", square_root, 9)

# Utility actions
theme_button = create_button("", toggle_theme, 10)  # Text for this button is set by apply_theme
create_button("Support", open_github, 11)

# Keep scrolling behavior responsive as the window or content changes
scrollable_frame.bind("<Configure>", update_scroll_region)
canvas.bind("<Configure>", resize_content_frame)
canvas.bind_all("<MouseWheel>", scroll_with_mouse)  # For Windows
canvas.bind_all("<Button-4>", scroll_with_mouse)    # For Linux/macOS scroll up
canvas.bind_all("<Button-5>", scroll_with_mouse)    # For Linux/macOS scroll down

# Apply initial theme and start the application
apply_theme()
window.mainloop()
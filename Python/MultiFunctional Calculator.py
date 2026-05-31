import tkinter as tk
import math
import webbrowser
from tkinter import messagebox

def add():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 + num2
        messagebox.showinfo("Result", f"The sum is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
def subtract():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 - num2
        messagebox.showinfo("Result", f"The difference is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")

def multiply():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 * num2
        messagebox.showinfo("Result", f"The product is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
def divide():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        if num2 == 0:
            messagebox.showerror("Error", "Cannot divide by zero.")
            return
        result = num1 / num2
        messagebox.showinfo("Result", f"The quotient is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
def exponentiate():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = math.pow(num1, num2)
        messagebox.showinfo("Result", f"The result of {num1} raised to the power of {num2} is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")
def square_root():
    try:
        num = float(entry1.get())
        if num < 0:
            messagebox.showerror("Error", "Cannot calculate square root of a negative number.")
            return
        result = math.sqrt(num)
        messagebox.showinfo("Result", f"The square root of {num} is: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")
def open_github():
    webbrowser.open("https://github.com/Error-cracker-1/My-First-Project")


window = tk.Tk()
window.title("MultiFunctional Calculator")
window.geometry("350x400")
label1 = tk.Label(window, text="Number 1:")
label1.pack(pady=5)
entry1 = tk.Entry(window)
entry1.pack(pady=5)
label2 = tk.Label(window, text="Number 2:")
label2.pack(pady=5)
entry2 = tk.Entry(window)
entry2.pack(pady=5)
button_add = tk.Button(window, text="Add (+)", command=add)
button_add.pack(pady=7)
button_subtract = tk.Button(window, text="Subtract (-)", command=subtract)
button_subtract.pack(pady=7)
button_multiply = tk.Button(window, text="Multiply (*)", command=multiply)
button_multiply.pack(pady=7)
button_divide = tk.Button(window, text="Divide (∻)", command=divide)
button_divide.pack(pady=7)
button_exponentiate = tk.Button(window, text="Power (aⁿ)", command=exponentiate)
button_exponentiate.pack(pady=7)
button_square_root = tk.Button(window, text="Square Root (√)", command=square_root)
button_square_root.pack(pady=7)
button_github = tk.Button(window, text="Support", command=open_github)
button_github.pack(pady=5)
window.mainloop()

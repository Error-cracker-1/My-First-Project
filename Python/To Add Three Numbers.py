"""
This script calculates the sum of three numbers provided by the user.
"""

print("Welcome to the Simple Calculator for Adding Three Numbers")

x = float(input("Enter first number: "))
y = float(input("Enter second number: "))
z = float(input("Enter third number: "))

# Calculate the sum of the three numbers
total = x + y + z

print("The sum is:", total)

# Keep the console window open until the user presses Enter
input("Press Enter to Exit")
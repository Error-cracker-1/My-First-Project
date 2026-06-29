# This script calculates the area of a rectangle based on user input for its width and length.

print("Welcome to the Rectangle Area Calculator!")


# Prompt the user to enter the width and length, and convert them to floating-point numbers.
width = float(input("Enter the width of the rectangle: "))
length = float(input("Enter the length of the rectangle: "))

# Calculate the area of the rectangle.
area = length * width

# Display the calculated area to the user.
print(f"The area of the rectangle is: {area}")

# Keep the console window open until the user presses Enter, allowing them to see the result.
input("Press Enter to Exit")
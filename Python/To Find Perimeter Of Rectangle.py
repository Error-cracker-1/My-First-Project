# This script calculates the perimeter of a rectangle.
# It prompts the user for the length and width (or breadth)
# and then displays the calculated perimeter.


print("Welcome to the Rectangle Perimeter Calculator!")
length = float(input("Enter length: "))
width = float(input("Enter width/Breadth: "))
perimeter = 2 * (length + width)
print("The perimeter of the rectangle is:", perimeter)

input("Press Enter to Exit")
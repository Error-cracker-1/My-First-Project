"""
This script prompts the user to enter three numbers
and then calculates and displays their product.
"""

# Display a welcome message to the user.
print("Welcome to the Multiplier!")

# Prompt the user to enter three numbers and convert them to floating-point numbers.
first_number = float(input("Enter first number: "))
second_number = float(input("Enter second number: "))
third_number = float(input("Enter third number: "))

# Calculate the product of the three numbers.
product = first_number * second_number * third_number

# Display the calculated product to the user.
print("The result is:", product)

# Pause the script to allow the user to view the output before the console closes.
input("Press Enter to Exit")
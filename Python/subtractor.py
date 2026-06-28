"""
A simple Python script to perform subtraction of two numbers provided by the user.
It includes robust input handling to ensure valid numeric input.
"""

def get_float_input(prompt_message):
    """
    Prompts the user to enter a number and robustly handles non-numeric input.

    Args:
        prompt_message (str): The message to display to the user.

    Returns:
        float: The validated floating-point number entered by the user.
    """
    while True:
        user_input = input(prompt_message)
        try:
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    """
    Main function to run the simple subtractor program.
    It welcomes the user, gets two numbers, performs subtraction,
    and displays the result.
    """
    print("Welcome to the Simple Subtractor!")

    num1 = get_float_input("Enter first number: ")
    num2 = get_float_input("Enter second number: ")

    result = num1 - num2
    print(f"The result is: {result}")

    input("Press Enter to Exit")

if __name__ == "__main__":
    main()
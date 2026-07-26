# Welcome message for the user.
print("Welcome to the Even and Odd Number Finder!")

# Loop to ensure valid input is received.
while True:
    try:
        # Prompt the user to enter a number.
        # Convert input to a float to allow for decimal numbers.
        # The program will handle both integer and non-integer inputs.
        num_str = input("Enter a number: ")
        num = float(num_str)

        # Even and odd concepts are traditionally defined for integers.
        # First, check if the entered number is a whole number.
        if num.is_integer():
            # If it's an integer, determine if it's even or odd.
            # Convert to an integer type for the modulo operation,
            # as it's the standard practice for even/odd checks.
            if int(num) % 2 == 0:
                print(f"{num} is an even number.")
            else:
                print(f"{num} is an odd number.")
        else:
            # If the number is not a whole number (e.g., 3.14),
            # it is neither even nor odd by standard definitions.
            print(f"{num} is neither even nor odd, as it is not an integer.")

        # Exit the loop if input is valid and processed successfully.
        break

    except ValueError:
        # Handle cases where the input string cannot be converted to a float.
        # This occurs for non-numeric input (e.g., "hello").
        print(f"'{num_str}' is not a valid number. Please enter a numerical value.")
    except Exception as e:
        # Catch any other unexpected errors that might occur.
        print(f"An unexpected error occurred: {e}")
        # Exit on unexpected error to prevent infinite loops.
        break

# Keep the console window open until the user presses Enter,
# allowing them to see the output before the script closes.
input("\nPress Enter to Exit")
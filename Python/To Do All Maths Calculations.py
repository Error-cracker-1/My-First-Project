def add(a: float, b: float) -> float:
    """Adds two numbers and returns their sum."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtracts the second number from the first and returns the difference."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiplies two numbers and returns their product."""
    return a * b

def divide(a: float, b: float) -> float | str:
    """
    Divides the first number by the second.
    Returns the quotient or an error message if the divisor is zero.
    """
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b

if __name__ == "__main__":
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
    
    print(f"Add: {num1} + {num2} = {add(num1, num2)}")
    print(f"Subtract: {num1} - {num2} = {subtract(num1, num2)}")
    print(f"Multiply: {num1} * {num2} = {multiply(num1, num2)}")
    print(f"Divide: {num1} / {num2} = {divide(num1, num2)}")
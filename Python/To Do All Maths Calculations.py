def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract two numbers"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide two numbers"""
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
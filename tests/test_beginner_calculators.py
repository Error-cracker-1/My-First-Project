import io
import runpy
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "Python"


def run_script(filename, inputs):
    output = io.StringIO()
    values = iter(inputs)
    with patch("builtins.input", side_effect=lambda _prompt: next(values)):
        with redirect_stdout(output):
            runpy.run_path(str(PYTHON_DIR / filename), run_name="__main__")
    return output.getvalue()


def test_add_three_numbers():
    output = run_script("To Add Three Numbers.py", ["1.5", "2", "3.5", ""])
    assert "The sum is: 7.0" in output


def test_multiply_three_numbers():
    output = run_script("To Multiply Three Numbers.py", ["2", "3", "4", ""])
    assert "The result is: 24.0" in output


def test_rectangle_area():
    output = run_script("To Find Area of Rectangle.py", ["5", "4", ""])
    assert "The area of the rectangle is: 20.0" in output


def test_rectangle_perimeter():
    output = run_script("To Find Perimeter Of Rectangle.py", ["5", "4", ""])
    assert "The perimeter of the rectangle is: 18.0" in output


def test_even_number():
    output = run_script("To Find Even And Odd Numbers.py", ["8", ""])
    assert "8.0 is an even number." in output


def test_odd_number():
    output = run_script("To Find Even And Odd Numbers.py", ["7", ""])
    assert "7.0 is an odd number." in output


def test_non_integer_number():
    output = run_script("To Find Even And Odd Numbers.py", ["3.14", ""])
    assert "3.14 is neither even nor odd" in output


def test_invalid_number_then_valid_even_number():
    output = run_script("To Find Even And Odd Numbers.py", ["not-a-number", "6", ""])
    assert "'not-a-number' is not a valid number." in output
    assert "6.0 is an even number." in output

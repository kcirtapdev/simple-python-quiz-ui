# Simple Python Quiz UI

I made this project as a way to teach simple Python and coding logic to some of my friends. It works by parsing the json file containing all of the lessons. 
This project uses PyQt6, make sure to install via pip if you plan to modify.

`python -m pip install PyQt6`

## Use

You can build your own lessons and then build a executable via pyinstaller, just make sure to attach the json.

`pyinstaller --onefile --noconsole --add-data "lessons.json:." your_script.py`

## Building Lessons

Open the json file in this repo to see some examples I made, you can modify them and make your own lessons. 

Things to consider:
- check() will be replaced with print() and you can check if it meets your desired results.
- You can set multiple correct solutions by assigning a parameter to a list.
- You can name lessons, but it will only save in order what lessons are complete, if you plan to add to an existing quiz just make sure to add it to the end.


Here is an example of a Fibonacci Sequence Generator lesson that is also part of this code.
```json
{
      "lesson_name": "Fibonacci Sequence Generator",
      "code_lines": [
        ["# Fibonacci Sequence Generator"],
        ["# The Fibonacci sequence is a series of numbers where"],
        ["# each number is the sum of the two preceding ones."],
        ["# It starts with 0 and 1, and follows this pattern: 0, 1, 1, 2, 3, 5, 8, ..."],
        ["# This function returns the nth Fibonacci number using recursion."],
        ["def fibonacci(", "parameter", "):"],
        ["    # The base case: The first two numbers in the sequence are themselves"],
        ["    if ", "base_case", ":"],
        ["        return ", "return_value"],
        ["    # Recursively sum the two previous Fibonacci numbers"],
        ["    return fibonacci(", "recursive_call_1", ") + fibonacci(", "recursive_call_2", ")"],
        ["# Example usage"],
        ["print(fibonacci(", "input_value", "))"]
      ],
      "drop_area_keys": ["parameter", "base_case", "return_value", "recursive_call_1", "recursive_call_2", "input_value"],
      "correct_answers": {
        "parameter": "n",
        "base_case": "n <= 1",
        "return_value": "n",
        "recursive_call_1": ["n - 1", "n - 2"],
        "recursive_call_2": ["n - 2", "n - 1"],
        "input_value": "5"
      },
      "bank_items": [
        "n",
        "n <= 1",
        "n",
        "n - 1",
        "n - 2",
        "5",
        "n >= 1",
        "n + 1",
        "fibonacci(n + 2)",
        "None"
      ],
      "desired_result": "5"
    },
```

"""Enter your own parentheses. The main classes are in main.py."""

from main import Logger, LogLevel, ParenthesesValidator


def main():
    Logger.set_level(LogLevel.TRACE)
    Logger.set_format("[%l] %n: %m")
    validator = ParenthesesValidator()

    print("Lab 1: Parentheses Validator")
    print("Enter parentheses, for example (()). Enter q to exit.")

    while True:
        try:
            text = input("\nYour input: ")
        except (EOFError, KeyboardInterrupt):
            print("\nProgram closed.")
            break

        if text.lower() == "q":
            break

        valid = validator.isValid(text)
        if valid:
            print("Result: valid parentheses.")
        else:
            print("Result: invalid input. See the ERROR message for the reason.")


if __name__ == "__main__":
    main()

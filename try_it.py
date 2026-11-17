"""Run the Lab 1 parentheses check with the refactored logger."""

from main import Formatter, Logger, LogLevel, ParenthesesValidator


def main():
    Logger.set_level(LogLevel.TRACE)
    validator = ParenthesesValidator()
    validator.logger.formatter = Formatter("[%l] %n: %m")

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

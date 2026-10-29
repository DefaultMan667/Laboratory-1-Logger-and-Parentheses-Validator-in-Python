"""Lab 1: Logger and Parentheses Validator. Python 3, standard library only."""

from datetime import datetime
from enum import IntEnum
import random
import re


class LogLevel(IntEnum):
    TRACE = 10
    INFO = 20
    WARN = 30
    ERROR = 40


class Logger:
    # Class attributes: changing these settings affects every logger object.
    level = LogLevel.INFO
    format = "[%t] [%l] %n: %m"

    _random_messages = {
        LogLevel.TRACE: ("Following the steps", "Checking the details"),
        LogLevel.INFO: ("Operation completed", "Here is your result"),
        LogLevel.WARN: ("Please check this", "Something unexpected happened"),
        LogLevel.ERROR: ("Operation failed", "Invalid input detected"),
    }

    def __init__(self, name: str):
        # Instance attribute: each object has its own name.
        self.name = name

    @classmethod
    def set_level(cls, level: LogLevel):
        if not isinstance(level, LogLevel):
            raise ValueError("level must be a LogLevel value")
        cls.level = level

    @classmethod
    def set_format(cls, format_string: str):
        if not isinstance(format_string, str):
            raise TypeError("format must be a string")
        cls.format = format_string

    def log(self, level: LogLevel, message: str):
        if level < Logger.level:
            return

        values = {
            "%t": datetime.now().strftime("%H:%M:%S"),
            "%m": message,
            "%n": self.name,
            "%l": level.name,
        }
        if "%r" in Logger.format:
            values["%r"] = random.choice(self._random_messages[level])

        # Replace placeholders in the template only, preserving message contents.
        output = re.sub(r"%[tmnlr]", lambda match: values[match.group()], Logger.format)
        print(output)

    def trace(self, message: str):
        self.log(LogLevel.TRACE, message)

    def info(self, message: str):
        self.log(LogLevel.INFO, message)

    def warn(self, message: str):
        self.log(LogLevel.WARN, message)

    def error(self, message: str):
        self.log(LogLevel.ERROR, message)


class ParenthesesValidator:
    def __init__(self):
        self.logger = Logger("Parentheses")

    def isValid(self, input: str) -> bool:
        balance = 0
        reason = ""

        for position, character in enumerate(input, start=1):
            if character == "(":
                balance += 1
                self.logger.trace(f"Opening parenthesis at position {position}")
            elif character == ")":
                if balance == 0:
                    reason = f"closing parenthesis without an opening at position {position}"
                    self.logger.warn(reason)
                    break
                balance -= 1
                self.logger.info(f"Matching pair found at position {position}")
            else:
                # Explicit policy: this program accepts only '(' and ')'.
                reason = f"unexpected character {character!r} at position {position}"
                break

        if not reason and balance != 0:
            reason = f"unclosed opening parentheses: {balance}"

        valid = not reason
        self.logger.info(f"Validation result for {input!r}: {str(valid).lower()}")
        if not valid:
            self.logger.error(f"Invalid input {input!r}: {reason}")
        return valid


def main():
    validator = ParenthesesValidator()
    required_cases = ["()", ")((()))", "(", "(())((()())())"]

    print("=== Required test cases, TRACE level ===")
    Logger.set_level(LogLevel.TRACE)
    Logger.set_format("[%t] [%l] %n: %m")
    for text in required_cases:
        validator.isValid(text)
        print()

    print("=== INFO level: TRACE messages are hidden ===")
    Logger.set_level(LogLevel.INFO)
    Logger.set_format("[%l] %m")
    validator.isValid("()")

    print("\n=== Shared settings and individual names ===")
    first = Logger("First")
    second = Logger("Second")
    Logger.set_format("%n: [%l] %m")
    Logger.set_level(LogLevel.ERROR)
    first.info("This message is hidden")
    second.info("This message is also hidden")
    first.error("Visible error from First")
    second.error("Visible error from Second")

    print("\n=== Bonus: random phrases for each level ===")
    Logger.set_level(LogLevel.TRACE)
    Logger.set_format("[%l] %m | %r")
    for level in LogLevel:
        first.log(level, "Example message")


if __name__ == "__main__":
    main()

"""Lab 2 Part A: the logger and the Lab 1 parentheses validator."""

from datetime import datetime
from enum import IntEnum
import random


class LogLevel(IntEnum):
    TRACE = 10
    INFO = 20
    WARN = 30
    ERROR = 40


class Formatter:
    """Build a log line without printing it."""

    _random_messages = {
        LogLevel.TRACE: ("Following the steps", "Checking the details"),
        LogLevel.INFO: ("Operation completed", "Here is your result"),
        LogLevel.WARN: ("Please check this", "Something unexpected happened"),
        LogLevel.ERROR: ("Operation failed", "Invalid input detected"),
    }

    def __init__(self, format_string="[%t] [%l] %n: %m"):
        # Each formatter stores its own format.
        self.set_format(format_string)

    def set_format(self, format_string):
        if not isinstance(format_string, str):
            raise TypeError("format must be a string")
        self.format_string = format_string

    def format_message(self, message, *args):
        """Bonus: replace each single % with the next argument. %% means %."""
        result = []
        index = 0
        argument = 0
        while index < len(message):
            if message[index] != "%":
                result.append(message[index])
            elif index + 1 < len(message) and message[index + 1] == "%":
                result.append("%")
                index += 1
            elif argument < len(args):
                result.append(str(args[argument]))
                argument += 1
            else:
                # Missing arguments leave the original percent sign in place.
                result.append("%")
            index += 1
        if argument < len(args):
            raise ValueError("more arguments than message placeholders")
        return "".join(result)

    def format(self, level, name, message, *args):
        message = self.format_message(message, *args)
        values = {
            "%t": datetime.now().strftime("%H:%M:%S"),
            "%l": level.name,
            "%n": name,
            "%m": message,
        }
        if "%r" in self.format_string:
            values["%r"] = random.choice(self._random_messages[level])
        result = ""
        index = 0
        while index < len(self.format_string):
            token = self.format_string[index:index + 2]
            if token in values:
                result += values[token]
                index += 2
            else:
                result += self.format_string[index]
                index += 1
        return result


class ConsoleSink:
    """Deliver a finished log line to the console."""

    def write(self, line):
        print(line)


class Logger:
    level = LogLevel.INFO

    def __init__(self, name, formatter=None, sink=None):
        self.name = name
        if formatter is None and sink is None:
            # Composition: this logger creates its own parts.
            self.formatter = Formatter()
            self.sink = ConsoleSink()
        elif formatter is not None and sink is not None:
            # Aggregation: these parts can also serve other loggers.
            self.formatter = formatter
            self.sink = sink
        else:
            raise ValueError("provide both formatter and sink, or neither")

    @classmethod
    def set_level(cls, level):
        if not isinstance(level, LogLevel):
            raise ValueError("level must be a LogLevel value")
        Logger.level = level

    def log(self, level, message, *args):
        if level < Logger.level:
            return
        line = self.formatter.format(level, self.name, message, *args)
        self.sink.write(line)

    def trace(self, message, *args):
        self.log(LogLevel.TRACE, message, *args)

    def info(self, message, *args):
        self.log(LogLevel.INFO, message, *args)

    def warn(self, message, *args):
        self.log(LogLevel.WARN, message, *args)

    def error(self, message, *args):
        self.log(LogLevel.ERROR, message, *args)


class ParenthesesValidator:
    def __init__(self, logger=None):
        if logger is None:
            self.logger = Logger("Parentheses")
        else:
            self.logger = logger

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
                reason = f"unexpected character {character!r} at position {position}"
                break
        if not reason and balance != 0:
            reason = f"unclosed opening parentheses: {balance}"
        valid = not reason
        self.logger.info(f"Validation result for {input!r}: {str(valid).lower()}")
        if not valid:
            self.logger.error(f"Invalid input {input!r}: {reason}")
        return valid

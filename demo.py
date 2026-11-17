"""Examples for the logger and the display shop. Run: python demo.py."""

from pathlib import Path

from main import ConsoleSink, Formatter, Logger, LogLevel, ParenthesesValidator
from shop import CommandReader, Display, DisplayManager


def logger_demo():
    Logger.set_level(LogLevel.TRACE)
    print("=== Formatter alone ===")
    formatter = Formatter("[%l] %n: %m")
    print(formatter.format(LogLevel.INFO, "Example", "Ratio is 100%n"))
    formatter.set_format("%n: %m")
    print(formatter.format(LogLevel.INFO, "Example", "Another format"))

    print("\n=== Composition ===")
    own = Logger("OwnParts")
    own.info("This logger created its formatter and sink")

    print("\n=== Aggregation ===")
    shared = Formatter("[%l] %n: %m")
    console = ConsoleSink()
    first = Logger("First", shared, console)
    second = Logger("Second", shared, console)
    first.info("Both loggers share one formatter and one sink")
    shared.set_format("%n: %m")
    first.info("The shared format changed")
    second.info("The same change affects this logger")
    special = Logger("Special", Formatter("%l >> %m"), console)
    special.info("This logger has a different formatter")

    print("\n=== Lab 1 still works ===")
    validator = ParenthesesValidator(Logger("Parentheses", shared, console))
    for text in ["()", ")((()))", "(", "(())((()())())"]:
        validator.isValid(text)

    print("\n=== Shared minimum level ===")
    Logger.set_level(LogLevel.ERROR)
    first.info("This INFO message stays hidden")
    second.error("This ERROR message appears")

    print("\n=== Bonus examples ===")
    Logger.set_level(LogLevel.TRACE)
    shared.set_format("[%l] %n: %m | %r")
    first.info("Pair found at % and %", 3, 7)
    first.info("Progress: % (100%% total)", 50)


def shop_demo(formatter, sink):
    first = Display("Dell-U2723QE", 3840, 2160, 163.0, formatter, sink)
    second = Display("LG-27GP850", 2560, 1440, 108.8, formatter, sink)
    third = Display("Samsung-Odyssey-G5", 2560, 1440, 93.0, formatter, sink)
    bob = DisplayManager("Bob", formatter, sink)
    alice = DisplayManager("Alice", formatter, sink)
    for display in (first, second, third):
        bob.assignDisplay(display)
    alice.assignDisplay(first)
    bob.assist()
    bought = bob.buyDisplay(first)
    print(f"Returned object is the original Dell: {bought is first}")
    print(f"Alice still has the original Dell: {alice.assignedDisplays[0] is first}")
    alice.assist()


def file_demo(path, formatter, sink):
    reader = CommandReader(Logger("Reader", formatter, sink))
    lines = reader.read(path)
    if lines is None:
        return
    for number, line in enumerate(lines, start=1):
        print(f"{number}: {line}")


def main():
    previous_level = Logger.level
    try:
        logger_demo()
        formatter = Formatter("[%l] %n: %m")
        sink = ConsoleSink()
        print("\n=== Display shop ===")
        shop_demo(formatter, sink)
        print("\n=== File lines ===")
        file_demo(Path(__file__).resolve().parent / "shop-monday.txt", formatter, sink)
    finally:
        Logger.set_level(previous_level)


if __name__ == "__main__":
    main()

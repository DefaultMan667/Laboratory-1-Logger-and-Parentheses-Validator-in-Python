"""Lab 2 Track 1: read commands and run a display shop."""

import math
from pathlib import Path

from main import ConsoleSink, Formatter, Logger, LogLevel


LEVELS = {"TRACE": LogLevel.TRACE, "INFO": LogLevel.INFO,
          "WARN": LogLevel.WARN, "ERROR": LogLevel.ERROR}


class Display:
    def __init__(self, model, width, height, ppi, formatter=None, sink=None):
        if not model:
            raise ValueError("display model must not be empty")
        if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
            raise ValueError("width and height must be positive integers")
        if isinstance(ppi, bool) or not math.isfinite(ppi) or ppi <= 0:
            raise ValueError("ppi must be a positive finite number")
        self.model = model
        self.width = width
        self.height = height
        self.ppi = float(ppi)
        if not math.isfinite(self.diagonal_inches()):
            raise ValueError("display size is too large")
        # The display creates its logger. The logger receives the shared parts.
        self.logger = Logger(f"Display:{model}", formatter, sink)
        self.logger.trace(f"Display {self.description()} created")

    def diagonal_inches(self):
        return math.sqrt(self.width ** 2 + self.height ** 2) / self.ppi

    def description(self):
        return f'{self.model} ({self.diagonal_inches():.1f}", {self.ppi:g} ppi)'

    def compareSize(self, other):
        difference = self.diagonal_inches() - other.diagonal_inches()
        if difference > 0:
            relation = "is bigger than"
        elif difference < 0:
            relation = "is smaller than"
        else:
            relation = "has the same diagonal as"
        return (f'{self.model} ({self.diagonal_inches():.1f}") {relation} '
                f'{other.model} ({other.diagonal_inches():.1f}")')

    def compareSharpness(self, other):
        difference = self.ppi - other.ppi
        if difference > 0:
            relation = "is sharper than"
        elif difference < 0:
            relation = "is less sharp than"
        else:
            relation = "has the same sharpness as"
        return f"{self.model} ({self.ppi:g} ppi) {relation} {other.model} ({other.ppi:g} ppi)"

    def compareWithMonitor(self, other):
        size_text = self.compareSize(other)
        sharpness_text = self.compareSharpness(other)
        size = self.diagonal_inches() - other.diagonal_inches()
        sharpness = self.ppi - other.ppi
        if size == 0 and sharpness == 0:
            verdict = "Both models have the same size and sharpness"
        elif size >= 0 and sharpness >= 0:
            verdict = f"{self.model} is at least as large and as sharp"
        elif size <= 0 and sharpness <= 0:
            verdict = f"{other.model} is at least as large and as sharp"
        else:
            verdict = "One model is larger, and the other has a higher pixel density"
        return f"{size_text}. {sharpness_text}. Verdict: {verdict}."


class DisplayManager:
    def __init__(self, name, formatter=None, sink=None):
        if not name:
            raise ValueError("manager name must not be empty")
        self.name = name
        self.assignedDisplays = []
        self.logger = Logger(f"Manager:{name}", formatter, sink)
        self.logger.trace(f"Manager {name} created")

    def assignDisplay(self, display):
        if display in self.assignedDisplays:
            self.logger.warn(f"{display.model} is already assigned to {self.name}")
            return
        # Store the same object. Do not create a copy of the display.
        self.assignedDisplays.append(display)
        self.logger.trace(f"{display.model} assigned to {self.name}")

    def assist(self):
        if not self.assignedDisplays:
            self.logger.warn(f"{self.name} has no displays to compare")
            return
        if len(self.assignedDisplays) == 1:
            self.logger.info(f"{self.name} has one display: {self.assignedDisplays[0].description()}")
            return
        self.logger.info(f"{self.name} compares the assigned displays")
        for index in range(len(self.assignedDisplays) - 1):
            result = self.assignedDisplays[index].compareWithMonitor(self.assignedDisplays[index + 1])
            self.logger.info(result)

    def buyDisplay(self, display):
        if display not in self.assignedDisplays:
            raise ValueError(f"{display.model} is not assigned to {self.name}")
        self.assignedDisplays.remove(display)
        self.logger.info(f"{self.name} sold {display.model}")
        if not self.assignedDisplays:
            self.logger.warn(f"{self.name} has no displays left")
        return display


class CommandReader:
    def __init__(self, logger):
        self.logger = logger

    def read(self, path):
        try:
            with open(path, "r", encoding="utf-8-sig") as file:
                return file.read().splitlines()
        except (OSError, UnicodeError, ValueError) as error:
            self.logger.error(f"Cannot read {path!s}: {error}")
            return None


def find_manager(managers, name):
    for manager in managers:
        if manager.name == name:
            return manager
    raise ValueError(f"manager {name!r} does not exist")


def find_display(displays, model):
    for display in displays:
        if display.model == model:
            return display
    raise ValueError(f"display {model!r} does not exist")


def parse_command(line, line_number, managers, displays, formatter, sink, logger):
    words = line.split()
    if not words or words[0].startswith("#"):
        return
    command = words[0]
    word_counts = {"MANAGER": 2, "DISPLAY": 5, "ASSIGN": 3,
                   "COMPARE": 3, "ASSIST": 2, "BUY": 3}
    try:
        if command not in word_counts:
            raise ValueError(f"unknown command {command!r}; commands are case-sensitive")
        expected = word_counts[command]
        if len(words) != expected:
            raise ValueError(f"{command} needs {expected - 1} argument(s), got {len(words) - 1}")

        if command == "MANAGER":
            name = words[1]
            for manager in managers:
                if manager.name == name:
                    logger.warn(f"Line {line_number}: manager {name!r} already exists; skipped")
                    return
            managers.append(DisplayManager(name, formatter, sink))
        elif command == "DISPLAY":
            model = words[1]
            for display in displays:
                if display.model == model:
                    logger.warn(f"Line {line_number}: display {model!r} already exists; skipped")
                    return
            try:
                width, height, ppi = int(words[2]), int(words[3]), float(words[4])
            except ValueError:
                raise ValueError("DISPLAY needs integer width and height, and a numeric ppi")
            displays.append(Display(model, width, height, ppi, formatter, sink))
        elif command == "ASSIGN":
            display = find_display(displays, words[1])
            manager = find_manager(managers, words[2])
            if display in manager.assignedDisplays:
                logger.warn(f"Line {line_number}: {display.model} is already assigned to {manager.name}; skipped")
            else:
                manager.assignDisplay(display)
        elif command == "COMPARE":
            first = find_display(displays, words[1])
            second = find_display(displays, words[2])
            logger.info(first.compareWithMonitor(second))
        elif command == "ASSIST":
            manager = find_manager(managers, words[1])
            if not manager.assignedDisplays:
                logger.warn(f"Line {line_number}: {manager.name} has no displays to compare")
            else:
                manager.assist()
        elif command == "BUY":
            display = find_display(displays, words[1])
            manager = find_manager(managers, words[2])
            manager.buyDisplay(display)
    except (ValueError, OverflowError) as error:
        logger.error(f"Line {line_number}: {error}")


def run_file(path, formatter, sink):
    logger = Logger("Parser", formatter, sink)
    reader = CommandReader(Logger("Reader", formatter, sink))
    lines = reader.read(path)
    if lines is None:
        return None
    managers = []
    displays = []
    for number, line in enumerate(lines, start=1):
        parse_command(line, number, managers, displays, formatter, sink, logger)
    return managers, displays


def menu():
    from try_it import main as parentheses_demo

    folder = Path(__file__).resolve().parent
    files = {"1": "shop-monday.txt", "2": "shop-tuesday.txt", "3": "shop-extra.txt"}
    while True:
        print("\nLab 2: Display Shop")
        print("1. Monday commands\n2. Tuesday commands with errors\n3. Extra checks")
        print("4. Lab 1 parentheses\n5. Exit")
        try:
            choice = input("Choose 1-5: ").strip()
            if choice == "5":
                return
            if choice not in files and choice != "4":
                print("Please choose a number from 1 to 5.")
                continue
            if choice == "4":
                parentheses_demo()
            else:
                level = input("Log level TRACE, INFO, WARN or ERROR [TRACE]: ").strip().upper()
                if level == "":
                    level = "TRACE"
                if level not in LEVELS:
                    print("Unknown log level.")
                    continue
                Logger.set_level(LEVELS[level])
                formatter = Formatter("[%l] %n: %m")
                sink = ConsoleSink()
                run_file(folder / files[choice], formatter, sink)
            input("\nPress Enter to return to the menu.")
        except (EOFError, KeyboardInterrupt):
            print("\nProgram closed.")
            return


if __name__ == "__main__":
    menu()

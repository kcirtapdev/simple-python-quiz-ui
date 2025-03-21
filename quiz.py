import json
import sys
import io
import re
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QMessageBox, QSizePolicy, QGridLayout, QInputDialog, QDialog, QTextEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QFont

SALT = "no_cheating_allowed"

def encrypt_text(text, salt=SALT):
    key = salt
    cipher = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))
    return cipher.encode("utf-8").hex()

def decrypt_text(hex_text, salt=SALT):
    try:
        cipher = bytes.fromhex(hex_text).decode("utf-8")
    except Exception:
        return None
    key = salt
    plain = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(cipher))
    return plain

def save_progress(progress, filename="progress.txt"):
    data = json.dumps(progress)
    enc = encrypt_text(data)
    with open(filename, "w") as f:
        f.write(enc)

def load_progress(filename="progress.txt"):
    try:
        with open(filename, "r") as f:
            enc = f.read()
        dec = decrypt_text(enc)
        if dec is None:
            return None
        return json.loads(dec)
    except Exception:
        return None

def highlight_code_line(line):
    light_blue_keywords = {
        "def", "if", "for", "while", "return", "print", "in", "import", "from", "class",
        "else", "elif", "try", "except", "finally", "with", "as", "pass", "break",
        "continue", "lambda", "yield", "not", "and", "or", "is", "None", "True", "False",
        "global", "nonlocal", "assert", "del", "raise"
    }

    built_in_functions = {
        "abs", "dict", "help", "min", "setattr", "all", "dir", "hex", "next", "slice", "any",
        "divmod", "id", "object", "sorted", "ascii", "enumerate", "input", "oct", "staticmethod",
        "bin", "eval", "int", "open", "str", "bool", "exec", "isinstance", "ord", "sum", "bytearray",
        "filter", "issubclass", "pow", "super", "bytes", "float", "iter", "print", "tuple", "callable",
        "format", "len", "property", "type", "chr", "frozenset", "list", "range", "vars", "classmethod",
        "getattr", "locals", "repr", "zip", "compile", "globals", "map", "reversed", "__import__", "complex",
        "hasattr", "max", "round", "delattr", "hash", "memoryview", "set"
    }

    number_pattern = r"(\b\d+(\.\d+)?\b)"
    string_pattern = r"(['\"])(?:\\.|(?!\1).)*\1"
    comment_pattern = r"(^#.*$)"
    identifier_pattern = r"\b[a-zA-Z_]\w*\b"

    leading_whitespace_match = re.match(r"(\s*)", line)
    leading_whitespace = leading_whitespace_match.group(0) if leading_whitespace_match else ""

    formatted_whitespace = leading_whitespace.replace(" ", "&nbsp;").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
    whitespace_span = f"<span style='white-space: pre;'>{formatted_whitespace}</span>"

    comment_match = re.match(comment_pattern, line.strip())
    if comment_match:
        return whitespace_span + f"<span style='color: green;'>{line.strip()}</span>"
    def highlight_match(match):
        token = match.group(0)
        if token in light_blue_keywords:
            return f"<span style='color: #6699FF; font-weight: bold;'>{token}</span>"
        elif token in built_in_functions:
            return f"<span style='color: teal;'>{token}</span>"
        elif re.match(number_pattern, token):
            return f"<span style='color: purple;'>{token}</span>"
        elif re.match(string_pattern, token):
            return f"<span style='color: orange;'>{token}</span>"
        else:
            return token

    highlighted_code = re.sub(identifier_pattern, highlight_match, line.strip())

    return whitespace_span + highlighted_code

class DraggableLabel(QLabel):
    def __init__(self, key, text="[DROP]", parent=None):
        super().__init__(text, parent)
        self.key = key
        self.setStyleSheet("border: 1px solid black; padding: 2px; background-color: lightgray; color: black;")
        self.setFont(QFont("Courier", 10))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.drag_start_position = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        previous_text = self.text()
        new_text = event.mimeData().text()
        if previous_text and previous_text != "[DROP]":
            main_window.return_to_bank(previous_text)
        self.setText(new_text)
        self.adjustSize()
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.text() != "[DROP]":
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.text() != "[DROP]":
            if (event.pos() - self.drag_start_position).manhattanLength() >= QApplication.startDragDistance():
                drag = QDrag(self)
                mimeData = QMimeData()
                current_text = self.text()
                mimeData.setText(current_text)
                drag.setMimeData(mimeData)
                self.setText("[DROP]")
                self.adjustSize()
                result = drag.exec(Qt.DropAction.MoveAction)
                if result != Qt.DropAction.MoveAction:
                    main_window.return_to_bank(current_text)
        super().mouseMoveEvent(event)

class DraggableBankItem(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("border: 2px solid blue; padding: 5px; background-color: white; color: black;")
        self.setFont(QFont("Courier", 10))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.drag_start_position = None
        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if (event.pos() - self.drag_start_position).manhattanLength() >= QApplication.startDragDistance():
                drag = QDrag(self)
                mimeData = QMimeData()
                mimeData.setText(self.text())
                drag.setMimeData(mimeData)
                result = drag.exec(Qt.DropAction.MoveAction)
                if result == Qt.DropAction.MoveAction:
                    self.deleteLater()
                    QTimer.singleShot(0, main_window.update_bank_layout)
        super().mouseMoveEvent(event)

class RunOutputDialog(QDialog):
    def __init__(self, output, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Code Output")
        layout = QVBoxLayout(self)
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setText(output)
        layout.addWidget(self.output_edit)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        self.setLayout(layout)

class DragDropLesson(QWidget):
    lessonCompleted = pyqtSignal()
    
    def __init__(self, code_lines, drop_area_keys, correct_answers, bank_items, desired_result, manager, parent=None):
        super().__init__(parent)
        global main_window
        main_window = self
        self.manager = manager
        self.correct_answers = correct_answers
        self.bank_items_data = bank_items
        self.code_lines_data = code_lines
        self.drop_area_keys = drop_area_keys
        self.desired_result = desired_result
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        prompt = QLabel("Drag the correct elements into the code to complete the lesson:")
        prompt.setFont(QFont("Arial", 11))
        layout.addWidget(prompt)
        
        self.code_layout = QVBoxLayout()
        self.code_layout.setSpacing(2)
        self.drop_areas = {}
        for key in self.drop_area_keys:
            self.drop_areas[key] = DraggableLabel(key)
        
        for line in self.code_lines_data:
            h_layout = QHBoxLayout()
            for part in line:
                if isinstance(part, str) and part in self.drop_area_keys:
                    h_layout.addWidget(self.drop_areas[part])
                else:
                    highlighted = highlight_code_line(part)
                    lbl = QLabel(highlighted)
                    lbl.setTextFormat(Qt.TextFormat.RichText)
                    lbl.setFont(QFont("Courier", 10))
                    lbl.setStyleSheet("margin: 0px; padding: 0px;")
                    h_layout.addWidget(lbl)
            h_layout.addStretch()
            self.code_layout.addLayout(h_layout)
        
        code_frame = QFrame()
        code_frame.setLayout(self.code_layout)
        code_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout.addWidget(code_frame)
        
        self.word_bank = QFrame()
        self.word_bank_layout = QGridLayout()
        self.word_bank_layout.setSpacing(10)
        self.word_bank_layout.setContentsMargins(5, 5, 5, 5)
        self.word_bank.setLayout(self.word_bank_layout)
        layout.addWidget(self.word_bank)
        
        for index, item in enumerate(self.bank_items_data):
            bank_item = DraggableBankItem(item)
            row = index // 5
            col = index % 5
            self.word_bank_layout.addWidget(bank_item, row, col)
        
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_code)
        layout.addWidget(self.run_button)
        
        self.setLayout(layout)
        self.adjustSize()

    def update_bank_layout(self):
        items = []
        count = self.word_bank_layout.count()
        for i in range(count):
            widget = self.word_bank_layout.itemAt(i).widget()
            if widget:
                items.append(widget)
        while self.word_bank_layout.count():
            item = self.word_bank_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        for index, widget in enumerate(items):
            row = index // 5
            col = index % 5
            self.word_bank_layout.addWidget(widget, row, col)
            widget.adjustSize()
        self.adjustSize()
    
    def return_to_bank(self, text):
        bank_item = DraggableBankItem(text)
        count = self.word_bank_layout.count()
        row = count // 5
        col = count % 5
        self.word_bank_layout.addWidget(bank_item, row, col)
        bank_item.adjustSize()
        self.update_bank_layout()
    
    def show_answers(self):
        if self.manager.progress.get("solved", {}).get(str(self.manager.current_index), False):
            for key, answer in self.correct_answers.items():
                display = answer[0] if isinstance(answer, list) else answer
                self.drop_areas[key].setText(display)
                self.drop_areas[key].adjustSize()
            answers_used = set(answer[0] if isinstance(answer, list) else answer for answer in self.correct_answers.values())
            count = self.word_bank_layout.count()
            items_to_remove = []
            for i in range(count):
                widget = self.word_bank_layout.itemAt(i).widget()
                if widget and widget.text() in answers_used:
                    items_to_remove.append(widget)
            for widget in items_to_remove:
                self.word_bank_layout.removeWidget(widget)
                widget.deleteLater()
            self.update_bank_layout()
        else:
            QMessageBox.information(self, "Not Solved", "You must complete the lesson before viewing the answers.")

    def run_code(self):
        for key, drop_area in self.drop_areas.items():
            if drop_area.text() == "[DROP]":
                QMessageBox.warning(self, "Incomplete", "Please fill in all drop areas before running the code.")
                return
        
        code_str = ""
        for line in self.code_lines_data:
            line_str = ""
            for part in line:
                if isinstance(part, str) and part in self.drop_area_keys:
                    line_str += self.drop_areas[part].text()
                else:
                    line_str += part
            code_str += line_str + "\n"
        
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            exec_globals = {"check": lambda val: print(val)}
            exec(code_str, exec_globals)
            output = sys.stdout.getvalue()
        except Exception as e:
            output = "Error: " + str(e)
        finally:
            sys.stdout = old_stdout

        dialog = RunOutputDialog(output, self)
        dialog.exec()

        if output.strip() == self.desired_result.strip():
            QMessageBox.information(self, "Success", "Congratulations! The code produced the desired result.")
            self.run_button.setEnabled(False)
            self.lessonCompleted.emit()
        else:
            QMessageBox.warning(self, "Incorrect", "The output did not match the desired result.\n\nExpected:\n" +
                                self.desired_result + "\n\nGot:\n" + output)

class LessonManager(QWidget):
    def __init__(self, lessons, parent=None):
        super().__init__(parent)
        self.lessons = lessons
        self.current_index = 0
        self.progress = load_progress() or {"highest_unlocked": 1, "solved": {}}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Amazing code")
        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setFixedSize(self.sizeHint())
    
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        top_bar = QHBoxLayout()
        self.select_button = QPushButton("Select Lesson")
        self.select_button.clicked.connect(self.select_lesson)
        top_bar.addWidget(self.select_button)
        
        self.show_answers_button = QPushButton("Show Answers")
        self.show_answers_button.clicked.connect(self.show_answers)
        top_bar.addWidget(self.show_answers_button)
        top_bar.addStretch()
        self.main_layout.addLayout(top_bar)
        
        self.lesson_container = QVBoxLayout()
        self.main_layout.addLayout(self.lesson_container)
        
        self.next_button = QPushButton("Next Lesson")
        self.next_button.clicked.connect(self.next_lesson)
        self.next_button.setVisible(False)
        self.main_layout.addWidget(self.next_button)
        
        self.load_current_lesson()
        self.adjustSize()

    def load_current_lesson(self):
        self.next_button.setVisible(False)
        while self.lesson_container.count():
            item = self.lesson_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        if self.current_index < len(self.lessons):
            lesson_config = self.lessons[self.current_index]
            self.lesson_widget = DragDropLesson(
                lesson_config["code_lines"],
                lesson_config["drop_area_keys"],
                lesson_config["correct_answers"],
                lesson_config["bank_items"],
                lesson_config["desired_result"],
                manager=self
            )
            self.lesson_widget.lessonCompleted.connect(self.on_lesson_completed)
            self.lesson_container.addWidget(self.lesson_widget)
        else:
            self.lesson_container.addWidget(QLabel("All lessons completed! Good job!"))
            self.next_button.setVisible(False)

    def on_lesson_completed(self):
        self.progress["solved"][str(self.current_index)] = True
        if self.current_index + 1 > self.progress.get("highest_unlocked", 1) - 1 and self.current_index + 1 < len(self.lessons):
            self.progress["highest_unlocked"] = self.current_index + 2
        save_progress(self.progress)
        self.next_button.setVisible(True)

    def next_lesson(self):
        self.next_button.setVisible(False)
        self.current_index += 1
        self.load_current_lesson()
        self.adjustSize()

    def select_lesson(self):
        highest = self.progress.get("highest_unlocked", 1)
        available = [f"Lesson {i}: {self.lessons[i - 1]['lesson_name']}" for i in range(1, highest + 1)]
        item, ok = QInputDialog.getItem(self, "Select Lesson", "Choose a lesson:", available, 0, False)
        if ok and item:
            selected_index = int(item.split()[1][:-1]) - 1
            self.current_index = selected_index
            self.next_button.setVisible(False)
            self.load_current_lesson()

    def show_answers(self):
        self.lesson_widget.show_answers()


def load_lessons_from_json(file_path="lessons.json"):
    try:
        with open(file_path, "r") as f:
            lessons = json.load(f)
        return lessons
    except Exception as e:
        print("Error loading lessons:", e)
        return []

lesson1 = {
    "lesson_name" : "Automated Cooking Timer",
    "code_lines": [
        ["# Automated Cooking Timer"],
        ["# When cooking, we often need to set a timer and wait"],
        ["# until the timer reaches zero before taking the food out."],
        ["def start_timer(", "parameter", "):"],
        ["    while ", "condition", ":"],
        ["        print('Time remaining:', ", "output", ")"],
        ["        ", "decrement"],
        ["    print('Time is up! Remove the food.')"],
        ["# Example usage"],
        ["start_timer(", "input_value", ")"]
    ],
    "drop_area_keys": ["parameter", "condition", "output", "decrement", "input_value"],
    "correct_answers": {
        "parameter": "seconds",
        "condition": "seconds > 0",
        "output": "seconds",
        "decrement": "seconds -= 1",
        "input_value": "10"
    },
    "bank_items": ["seconds", "seconds > 0", "seconds", "seconds -= 1", "10", "seconds >= 0", "None", "while True", "stop()", "exit"],
    "desired_result": "\n".join([
        "Time remaining: 10",
        "Time remaining: 9",
        "Time remaining: 8",
        "Time remaining: 7",
        "Time remaining: 6",
        "Time remaining: 5",
        "Time remaining: 4",
        "Time remaining: 3",
        "Time remaining: 2",
        "Time remaining: 1",
        "Time is up! Remove the food."
    ])
}

lesson2 = {
    "lesson_name" : "Customer Support Ticket System",
    "code_lines": [
        ["# Customer Support Ticket System"],
        ["# Companies process multiple support tickets every day."],
        ["# This function processes a list of customer tickets in order."],
        ["def process_tickets(", "parameter", "):"],
        ["    for ticket in ", "loop_variable", ":"],
        ["        print('Processing ticket:', ", "output", ")"],
        ["    print('All tickets have been processed.')"],
        ["# Example usage"],
        ["support_tickets = ['Refund Request', 'Technical Issue', 'Account Login Help']"],
        ["process_tickets(", "input_value", ")"]
    ],
    "drop_area_keys": ["parameter", "loop_variable", "output", "input_value"],
    "correct_answers": {
        "parameter": "tickets",
        "loop_variable": "tickets",
        "output": "ticket",
        "input_value": "support_tickets"
    },
    "bank_items": ["tickets", "tickets", "ticket", "support_tickets", "None", "while True", "stop()", "ticket_list", "customer_tickets"],
    "desired_result": "\n".join([
        "Processing ticket: Refund Request",
        "Processing ticket: Technical Issue",
        "Processing ticket: Account Login Help",
        "All tickets have been processed."
    ])
}

lesson3 = {
    "lesson_name" : "Water Level Control Code",
    "code_lines": [
        ["# Water Level Control Code"],
        ["# This code controls the water level in a tank"],
        ["# and lowers it based on the amount specified."],
        ["# The water level is decreased in a loop until it reaches the threshold."],
        ["# Complete the code by dragging the correct items into the drop areas."],
        ["threshold = 500"],
        ["water_level = 1000"],
        [""],
        ["def lower_water_level(", "param", "):"],
        ["    global water_level"],
        ["    for i in range(0, amount):"],
        ["        ", "loop_condition"],
        [""],
        ["lower_water_level(", "input_value", ")"],
        [""],
        ["check(water_level ", "comparison", " threshold)"]
    ],
    "drop_area_keys": ["param", "loop_condition", "input_value", "comparison"],
    "correct_answers": {
        "param": "amount",
        "loop_condition": "water_level -= 1",
        "input_value": "501",
        "comparison": "<="
    },
    "bank_items": ["amount", "water_level -= 1", "501", "<=", "==", ">", "++", "null", "if", "for"],
    "desired_result": "True"
}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    lessons = load_lessons_from_json("lessons.json")
    if not lessons:
        lessons = [lesson1, lesson2]
    manager = LessonManager(lessons)
    manager.show()
    sys.exit(app.exec())
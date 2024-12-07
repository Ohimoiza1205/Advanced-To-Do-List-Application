import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHBoxLayout
)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt


class AdvancedToDoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced To-Do List App")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        layout = QVBoxLayout()

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.filter_tasks)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Table for tasks
        self.task_table = QTableWidget(self)
        self.task_table.setColumnCount(3)  # Task Name, Completion, Timestamp
        self.task_table.setHorizontalHeaderLabels(["Task", "Completed", "Timestamp"])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.task_table)

        # Input for new tasks
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter a new task")
        layout.addWidget(self.task_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task", self)
        self.add_button.clicked.connect(self.add_task)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Task", self)
        self.delete_button.clicked.connect(self.delete_task)
        button_layout.addWidget(self.delete_button)

        self.complete_button = QPushButton("Mark as Complete", self)
        self.complete_button.clicked.connect(self.mark_complete)
        button_layout.addWidget(self.complete_button)

        layout.addLayout(button_layout)

        # Set up the central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initialize database
        self.setup_database()

    def setup_database(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("advanced_tasks.db")
        if not self.db.open():
            print("Error: Unable to open database")
            return

        query = QSqlQuery()
        query.exec_(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "task TEXT, completed BOOLEAN, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        self.load_tasks()

    def load_tasks(self):
        query = QSqlQuery("SELECT id, task, completed, timestamp FROM tasks")
        self.task_table.setRowCount(0)
        while query.next():
            row_position = self.task_table.rowCount()
            self.task_table.insertRow(row_position)

            task_id = query.value(0)
            task_name = query.value(1)
            completed = "Yes" if query.value(2) else "No"
            timestamp = query.value(3)

            self.task_table.setItem(row_position, 0, QTableWidgetItem(task_name))
            self.task_table.setItem(row_position, 1, QTableWidgetItem(completed))
            self.task_table.setItem(row_position, 2, QTableWidgetItem(timestamp))

    def add_task(self):
        task_text = self.task_input.text()
        if task_text:
            query = QSqlQuery()
            query.prepare("INSERT INTO tasks (task, completed) VALUES (?, ?)")
            query.addBindValue(task_text)
            query.addBindValue(False)  # Task starts as incomplete
            if query.exec_():
                self.task_input.clear()
                self.load_tasks()

    def delete_task(self):
        selected_row = self.task_table.currentRow()
        if selected_row >= 0:
            task_name = self.task_table.item(selected_row, 0).text()
            query = QSqlQuery()
            query.prepare("DELETE FROM tasks WHERE task = ?")
            query.addBindValue(task_name)
            if query.exec_():
                self.load_tasks()

    def mark_complete(self):
        selected_row = self.task_table.currentRow()
        if selected_row >= 0:
            task_name = self.task_table.item(selected_row, 0).text()
            query = QSqlQuery()
            query.prepare("UPDATE tasks SET completed = ? WHERE task = ?")
            query.addBindValue(True)  # Mark as completed
            query.addBindValue(task_name)
            if query.exec_():
                self.load_tasks()

    def filter_tasks(self):
        search_text = self.search_input.text()
        query = QSqlQuery(
            "SELECT id, task, completed, timestamp FROM tasks WHERE task LIKE ?"
        )
        query.addBindValue(f"%{search_text}%")
        self.task_table.setRowCount(0)
        while query.next():
            row_position = self.task_table.rowCount()
            self.task_table.insertRow(row_position)

            task_id = query.value(0)
            task_name = query.value(1)
            completed = "Yes" if query.value(2) else "No"
            timestamp = query.value(3)

            self.task_table.setItem(row_position, 0, QTableWidgetItem(task_name))
            self.task_table.setItem(row_position, 1, QTableWidgetItem(completed))
            self.task_table.setItem(row_position, 2, QTableWidgetItem(timestamp))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedToDoApp()
    window.show()
    sys.exit(app.exec_())

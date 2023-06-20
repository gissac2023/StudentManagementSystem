import time

from PyQt6.QtWidgets import QApplication, QLabel, \
    QWidget, QLineEdit, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, \
    QStatusBar, QGridLayout, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import sqlite3


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.cursor = None
        self.connection = None
        self.database_file = database_file

    def connect(self):
        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()
        return self.connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 800)
        # Add Menu Bar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Search")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About Action", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)  # only for macos
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        search_menu_item.addAction(search_action)
        search_action.setMenuRole(QAction.MenuRole.NoRole)
        # Add Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        # add toolbars
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        # detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    def cell_clicked(self):
        edit_button = QPushButton("Edit Button")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete Button")
        delete_button.clicked.connect(self.delete)
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        # print(list(result))
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

        # self.table

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        search = SerachDB()
        search.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This is app was created while learning Python.
        Feel free to modify this app for your use.
        """
        self.setText(content)


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        yes.clicked.connect(self.delete_student)
        no = QPushButton("No")
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

    def delete_student(self):
        index = student_management_system.table.currentRow()
        student_id = student_management_system.table.item(index, 0).text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        student_management_system.load_data()

        self.close()
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        # add name widget
        layout = QVBoxLayout()
        # get student name from selected row
        index = student_management_system.table.currentRow()
        student_name = student_management_system.table.item(index, 1).text()
        # get id from row
        self.student_id = student_management_system.table.item(index, 0).text()
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)
        # get course name from selected row
        course_name = student_management_system.table.item(index, 2).text()
        self.course_box = QComboBox()
        course = ['DevOps', 'AWS', 'Jenkins']
        self.course_box.addItems(course)
        self.course_box.setCurrentText(course_name)
        layout.addWidget(self.course_box)
        # get current number
        current_nr = student_management_system.table.item(index, 3).text()
        self.phone_nr = QLineEdit(current_nr)
        # self.phone_nr.setPlaceholderText("Phone Number")
        layout.addWidget(self.phone_nr)

        submit_button = QPushButton("Update")
        submit_button.clicked.connect(self.update_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET Name = ?, Course = ?, Mobile = ? WHERE Id = ?",
                       (self.student_name.text(),
                        self.course_box.itemText(self.course_box.currentIndex()),
                        self.phone_nr.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # refresh the table
        student_management_system.load_data()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert New Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        # add name widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)
        # add ComboBox for course
        self.course_box = QComboBox()
        course = ['DevOps', 'AWS', 'Jenkins']
        self.course_box.addItems(course)
        layout.addWidget(self.course_box)
        # add phone number widget
        self.phone_nr = QLineEdit()
        self.phone_nr.setPlaceholderText("Phone Number")
        layout.addWidget(self.phone_nr)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_box.itemText(self.course_box.currentIndex())
        mobile = self.phone_nr.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        student_management_system.load_data()


class SerachDB(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.search_content_edit = QLineEdit()
        self.search_content_edit.setPlaceholderText("Enter the name you want to search")
        layout.addWidget(self.search_content_edit)
        self.submit_button = QPushButton("Search")
        self.submit_button.clicked.connect(self.search)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def search(self):
        name = self.search_content_edit.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        print(rows)
        items = student_management_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            student_management_system.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
student_management_system = MainWindow()
student_management_system.load_data()
student_management_system.show()
sys.exit(app.exec())

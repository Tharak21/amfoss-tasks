import sys
import mysql.connector
import csv
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QGridLayout, 
    QTextEdit, QSizePolicy, QLineEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CineScope – Dashboard")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: #121212; color: white; padding: 20px;")
        self.column_mapping = {
        "title": "Series_Title",
        "year": "Released_Year", 
        "genre": "Genre",
        "rating": "IMDB_Rating",
        "director": "Director",
        "stars": "Star1, Star2, Star3"  
    }
        
        # Initialize database variables
        self.db_connection = None
        self.cursor = None
        self.search_mode = "title"   # Default search mode
        self.selected_columns = ["title", "year", "genre", "rating", "director"]
        self.search_button_list = []  # To track button references
        self.column_button_list = []  # To track column button references
        print("ROws selected",self.search_button_list)
        print("Column button selected:",self.column_button_list)
        
        self.init_ui()
        self.open_connection()  # Co>nnect to database when app starts

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Header
        header = QLabel("🎬 Cinescope")
        header.setFont(QFont("Arial", 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(80)
        main_layout.addWidget(header)

        split_layout = QHBoxLayout()

        # Left Panel
        left_container = QVBoxLayout()
        left_container.setSpacing(10)
        left_container.setAlignment(Qt.AlignTop)

        # Search buttons
        search_heading = QLabel("Search By")
        search_heading.setFont(QFont("Arial", 18, QFont.Bold))
        left_container.addWidget(search_heading)

        search_buttons = [
            ("Genre", "genre"),  
            ("Year", "year"),
            ("Rating", "rating"),
            ("Director", "director"),
            ("Actor", "actor"),
        ]
        
        self.column_search={}
        search_grid = QGridLayout()
        for index, (label, mode) in enumerate(search_buttons):
            btn = QPushButton(label)
            btn.setStyleSheet(self.get_button_style(False))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, m=mode: self.set_search_mode(m))
            row, col = divmod(index, 2)
            search_grid.addWidget(btn, row, col)
            self.column_search[mode]=btn
        left_container.addLayout(search_grid)

        # Column selection
        column_heading = QLabel("Select Columns")
        column_heading.setFont(QFont("Arial", 18, QFont.Bold))
        left_container.addWidget(column_heading)

        column_buttons = [
            ("Title", "title"),
            ("Year", "year"),
            ("Genre", "genre"),
            ("Rating", "rating"),
            ("Director", "director"),
            ("Stars", "stars"),
        ]
        self.column_buttons={}
        column_grid = QGridLayout()
        for index, (label, col) in enumerate(column_buttons):
            btn = QPushButton(label)
            btn.setStyleSheet(self.get_button_style(False))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda _, c=col: self.toggle_column(c))
            row, col_ind = divmod(index, 2)
            column_grid.addWidget(btn, row, col_ind)
            self.column_buttons[col]=btn
        left_container.addLayout(column_grid)

        # Search input
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter search term")
        self.query_input.setStyleSheet("background-color: #1e1e1e; color: white; padding: 5px; border: 1px solid #444;")
        left_container.addWidget(self.query_input)

        # Action buttons
        action_layout = QHBoxLayout()
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("background-color: #e50914; color: white; padding: 6px; border-radius: 5px;")
        search_btn.clicked.connect(self.execute_search)
        action_layout.addWidget(search_btn)

        export_btn = QPushButton("Export CSV")
        export_btn.setStyleSheet("background-color: #1f1f1f; color: white; padding: 6px; border-radius: 5px;")
        export_btn.clicked.connect(self.export_csv)
        action_layout.addWidget(export_btn)
        left_container.addLayout(action_layout)

        # Right Panel
        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(10)

        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                color: white;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #ffcc00;
                color: black;
                padding: 4px;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Output console
        self.output_console = QTextEdit()
        self.output_console.setPlaceholderText("Results will appear here...")
        self.output_console.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #444;
                padding: 5px;
            }
        """)
        self.output_console.setFixedHeight(100)

        right_side_layout.addWidget(self.table)
        right_side_layout.addWidget(self.output_console)

        split_layout.addLayout(left_container, 2)
        split_layout.addLayout(right_side_layout, 8)
        main_layout.addLayout(split_layout)
        self.setLayout(main_layout)

    def get_button_style(self, is_selected):
        if is_selected:
            return """
                QPushButton {
                    background-color: #3399ff;
                    border: 1px solid #ff9900;
                    border-radius: 3px;
                    padding: 6px;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #1f1f1f;
                    border: 1px solid #333;
                    border-radius: 3px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #333;
                }
            """

    def open_connection(self):
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="thmarvel",
                database="cinescope"
            )
            self.cursor = self.db_connection.cursor()
            self.output_console.append("Database connected successfully")
            return True
        except mysql.connector.Error as err:
            self.output_console.append(f"Database connection failed: {err}")
            return False

    def set_search_mode(self, mode):
        self.search_mode = mode
        self.output_console.append(f"Search mode set to: {mode}")
        for m, btn in self.column_search.items():
            btn.setStyleSheet(self.get_button_style(m == mode))


    def toggle_column(self, column):
        print("Toggle request for column:", column)
        self.output_console.append(f"Column toggled: {column}")
        if column in self.column_button_list:
            self.column_button_list.remove(column)
            self.column_buttons[column].setStyleSheet(self.get_button_style(False))
        else:
            self.column_button_list.append(column)
            self.column_buttons[column].setStyleSheet(self.get_button_style(True))


    def execute_search(self):
        if not self.cursor:
            self.output_console.append("Database not connected")
            return
        
            
        search_term = self.query_input.text()
        if not search_term:
            self.output_console.append("Please enter a search term")
            return
        db_columns = []
        for col in self.column_button_list:
            mapped = self.column_mapping[col]
            if "," in mapped:
                db_columns.extend([c.strip() for c in mapped.split(",")])
            else:
                db_columns.append(mapped)
        column_str=",".join(db_columns)
        
        
        try:
            # Queries 
            if self.search_mode == "genre":
                query = f"SELECT {column_str} FROM movies1 WHERE Genre LIKE %s"
            elif self.search_mode == "year":
                query = f"SELECT {column_str} FROM movies1 WHERE Released_Year = %s"
            elif self.search_mode == "rating":
                query = f"SELECT {column_str} FROM movies1 WHERE IMDB_Rating >= %s"
            elif self.search_mode == "director":
                query = f"SELECT {column_str} FROM movies1 WHERE Director LIKE %s"
            elif self.search_mode == "actor":
                query = f"SELECT {column_str} FROM movies1 WHERE Star1 LIKE %s OR Star2 LIKE %s OR Star3 LIKE %s"
            else:  # Default to title search
                query = f"SELECT {column_str} FROM movies1 WHERE Series_Title LIKE %s"
            
            # Execute query
            if self.search_mode == "actor":
                search_value = f"%{search_term}%"
                self.cursor.execute(query, (search_value, search_value, search_value))
            elif self.search_mode in ["genre", "director"]:
                self.cursor.execute(query, (f"%{search_term}%",))
            else:
                self.cursor.execute(query, (search_term,))
            
            results = self.cursor.fetchall()
            self.display_results(results)
            self.output_console.append(f"Found {len(results)} movies")
            
        except mysql.connector.Error as err:
            self.output_console.append(f"Search failed: {err}")

    def display_results(self, results):
        if not results:
            self.table.setRowCount(0)
            return

        # Expand columns
        db_columns = []
        for col in self.column_button_list:
            mapped = self.column_mapping[col]
            if "," in mapped:
                db_columns.extend([c.strip() for c in mapped.split(",")])
            else:
                db_columns.append(mapped)

        # Build headers list for the table
        headers = []
        for col in self.column_button_list:
            if col == "stars":
                headers.extend(["Star1", "Star2", "Star3"])
            else:
                headers.append(col.capitalize())

        self.table.setColumnCount(len(db_columns))
        self.table.setRowCount(len(results))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setVisible(True)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setVisible(True)
        


        header = self.table.horizontalHeader()
        header.setStyleSheet("""
        QHeaderView::section {
        background-color: #ffcc00;
        color: black;
        padding: 4px;
        font-weight: bold;
    }
""")



        # Add to table
        for row_ind, row_data in enumerate(results):
            for col_ind, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.table.setItem(row_ind, col_ind, item)

        self.table.resizeColumnsToContents()

    def export_csv(self):
        self.output_console.append("Exporting to CSV...")
        with open("result.csv", "w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            
            headers = []
            for c in range(self.table.columnCount()):
                headers.append(self.table.horizontalHeaderItem(c).text())
            writer.writerow(headers)

            # Write table data row by row
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

        self.output_console.append("Exported results to result.csv")

    def closeEvent(self, event):
        # Close all databases
        if self.cursor:
            self.cursor.close()
        if self.db_connection:
            self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())
    
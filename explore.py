import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QListWidget, QLabel, QComboBox
)
from PyQt5.QtCore import Qt
from googlesearch import search

class MoodleSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Moodle LMS Website Finder")
        self.setGeometry(200, 200, 600, 400)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Input field for search query
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter a search term (e.g., 'Moodle LMS')")
        self.layout.addWidget(self.search_input)

        # Dropdown for country selection
        self.country_selector = QComboBox(self)
        self.country_selector.addItem("All Countries", "")
        self.country_selector.addItem("United States", "us")
        self.country_selector.addItem("United Kingdom", "uk")
        self.country_selector.addItem("Canada", "ca")
        self.country_selector.addItem("Australia", "au")
        self.country_selector.addItem("India", "in")
        self.country_selector.addItem("Germany", "de")
        self.country_selector.addItem("France", "fr")
        self.country_selector.addItem("United Arab Emirates", "ae")
        self.country_selector.addItem("Saudi Arabia", "sa")
        self.country_selector.addItem("Oman", "om")
        self.country_selector.addItem("Qatar", "qa")
        self.country_selector.addItem("Kuwait", "kw")
        self.country_selector.addItem("Bahrain", "bh")
        self.layout.addWidget(self.country_selector)

        # Search button
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.perform_search)
        self.layout.addWidget(self.search_button)

        # Label to display status or instructions
        self.status_label = QLabel("Enter a search query and click 'Search'", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # List widget to display search results
        self.results_list = QListWidget(self)
        self.layout.addWidget(self.results_list)

    def perform_search(self):
        # Get query from input field
        query = self.search_input.text().strip()
        country_code = self.country_selector.currentData()

        if not query:
            self.status_label.setText("Please enter a valid search query.")
            return

        self.status_label.setText("Searching...")
        self.results_list.clear()

        try:
            # Add country-specific restriction if specified
            if country_code:
                query += f" cr:{country_code}"

            # Perform Google search
            results = list(search(query, num_results=10))

            if results:
                self.results_list.addItems(results)
                self.status_label.setText(f"Found {len(results)} result(s).")
            else:
                self.status_label.setText("No results found.")

        except Exception as e:
            self.status_label.setText("An error occurred. Please try again later.")
            print(f"Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoodleSearchApp()
    window.show()
    sys.exit(app.exec_())

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QListWidget, QLabel, QComboBox, QCheckBox  # Added QCheckBox here
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from googlesearch import search

# Configure logging
logging.basicConfig(level=logging.ERROR)

class SearchThread(QThread):
    """Thread to perform the Google search in the background."""
    search_finished = pyqtSignal(list, str)  # Signal to emit search results and status

    def __init__(self, query, country_code, search_in_domains=False):
        super().__init__()
        self.query = query
        self.country_code = country_code
        self.search_in_domains = search_in_domains

    def run(self):
        try:
            if self.country_code:
                self.query += f" cr:{self.country_code}"

            # If search_in_domains is True, search within specific domains
            if self.search_in_domains:
                domains = ["site:ae", "site:sa", "site:om"]
                results = []
                for domain in domains:
                    domain_query = f"{self.query} {domain}"
                    domain_results = list(search(domain_query, num_results=10))
                    results.extend(domain_results)
            else:
                results = list(search(self.query, num_results=10))

            self.search_finished.emit(results, f"Found {len(results)} result(s).")
        except Exception as e:
            logging.error(f"Search error: {e}")
            self.search_finished.emit([], "An error occurred. Please try again later.")

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

        # Checkbox to search within specific domains (ae, sa, om)
        self.domain_checkbox = QCheckBox("Search within UAE, Saudi Arabia, and Oman domains", self)
        self.layout.addWidget(self.domain_checkbox)

        # Search button
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.perform_search)
        self.layout.addWidget(self.search_button)

        # Clear button
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear_results)
        self.layout.addWidget(self.clear_button)

        # Label to display status or instructions
        self.status_label = QLabel("Enter a search query and click 'Search'", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # List widget to display search results
        self.results_list = QListWidget(self)
        self.layout.addWidget(self.results_list)

        # Thread for search
        self.search_thread = None

    def perform_search(self):
        """Perform a Google search based on the user's input."""
        query = self.search_input.text().strip()
        country_code = self.country_selector.currentData()
        search_in_domains = self.domain_checkbox.isChecked()

        if not query:
            self.status_label.setText("Please enter a valid search query.")
            return

        self.status_label.setText("Searching...")
        self.results_list.clear()
        self.search_button.setEnabled(False)  # Disable search button during search

        # Start the search in a separate thread
        self.search_thread = SearchThread(query, country_code, search_in_domains)
        self.search_thread.search_finished.connect(self.update_results)
        self.search_thread.start()

    def update_results(self, results, status):
        """Update the UI with search results and status."""
        if results:
            self.results_list.addItems(results)
        self.status_label.setText(status)
        self.search_button.setEnabled(True)  # Re-enable search button

    def clear_results(self):
        """Clear the search input and results."""
        self.search_input.clear()
        self.results_list.clear()
        self.status_label.setText("Enter a search query and click 'Search'")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoodleSearchApp()
    window.show()
    sys.exit(app.exec_())
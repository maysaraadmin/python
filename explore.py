import sys
import logging
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLineEdit, QListWidget, QLabel, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from googlesearch import search

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="moodle_search.log"
)

# Dictionary of country codes, full names, and their national domains
COUNTRY_DATA = {
    "us": {"name": "United States", "domain": "site:us"},
    "uk": {"name": "United Kingdom", "domain": "site:uk"},
    "ca": {"name": "Canada", "domain": "site:ca"},
    "au": {"name": "Australia", "domain": "site:au"},
    "in": {"name": "India", "domain": "site:in"},
    "de": {"name": "Germany", "domain": "site:de"},
    "fr": {"name": "France", "domain": "site:fr"},
    "ae": {"name": "United Arab Emirates", "domain": "site:ae"},
    "sa": {"name": "Saudi Arabia", "domain": "site:sa"},
    "om": {"name": "Oman", "domain": "site:om"},
    "qa": {"name": "Qatar", "domain": "site:qa"},
    "kw": {"name": "Kuwait", "domain": "site:kw"},
    "bh": {"name": "Bahrain", "domain": "site:bh"},
    # Add more countries as needed
}

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
            results = []
            if self.search_in_domains:
                if self.country_code:
                    # Search within the selected country's domain
                    domain = COUNTRY_DATA[self.country_code]["domain"]
                    query = f"{self.query} {domain}"
                    results = list(search(query, num_results=10))
                else:
                    # Search within all country domains
                    for code, data in COUNTRY_DATA.items():
                        query = f"{self.query} {data['domain']}"
                        results.extend(list(search(query, num_results=10)))
            else:
                # Perform a general search
                query = self.query
                if self.country_code:
                    query += f" cr:{self.country_code}"
                results = list(search(query, num_results=10))

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
        self.search_input.setToolTip("Enter a search term, e.g., 'Moodle LMS'")
        self.layout.addWidget(self.search_input)

        # Dropdown for country selection
        self.country_selector = QComboBox(self)
        self.country_selector.addItem("All Countries", "")
        for code, data in COUNTRY_DATA.items():
            self.country_selector.addItem(data["name"], code)
        self.country_selector.setToolTip("Select a country to filter results")
        self.layout.addWidget(self.country_selector)

        # Checkbox to search within specific domains
        self.domain_checkbox = QCheckBox("Search within national domains", self)
        self.domain_checkbox.setToolTip("Search within national domains for more specific results")
        self.layout.addWidget(self.domain_checkbox)

        # Search button
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setToolTip("Start the search")
        self.layout.addWidget(self.search_button)

        # Clear button
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setToolTip("Clear the search results")
        self.layout.addWidget(self.clear_button)

        # Label to display status or instructions
        self.status_label = QLabel("Enter a search query and click 'Search'", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # List widget to display search results
        self.results_list = QListWidget(self)
        self.results_list.itemDoubleClicked.connect(self.open_url)
        self.layout.addWidget(self.results_list)

        # Thread for search
        self.search_thread = None

    def perform_search(self):
        """Perform a Google search based on the user's input."""
        if self.search_thread and self.search_thread.isRunning():
            self.status_label.setText("A search is already in progress.")
            return

        query = self.search_input.text().strip()
        country_code = self.country_selector.currentData()
        search_in_domains = self.domain_checkbox.isChecked()

        if not query:
            self.status_label.setText("Please enter a valid search query.")
            return

        if len(query) > 200:
            self.status_label.setText("Search query is too long. Please shorten it.")
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
            self.status_label.setText(f"Found {len(results)} result(s).")
        else:
            self.status_label.setText("No results found. Please refine your search.")
        self.search_button.setEnabled(True)  # Re-enable search button

    def clear_results(self):
        """Clear the search input and results."""
        self.search_input.clear()
        self.results_list.clear()
        self.status_label.setText("Enter a search query and click 'Search'")

    def open_url(self, item):
        """Open the selected URL in the default web browser."""
        url = item.text()
        webbrowser.open(url)

    def closeEvent(self, event):
        """Ensure the search thread is terminated when the window is closed."""
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.quit()
            self.search_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoodleSearchApp()
    window.show()
    sys.exit(app.exec_())
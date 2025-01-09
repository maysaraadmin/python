import sys
import random
import logging
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QTextEdit
from googlesearch import search  # Import the Google Search function

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class JobSearchThread(QThread):
    results_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, job_titles, parent=None):
        super().__init__(parent)
        self.job_titles = job_titles

    def run(self):
        for job_title in self.job_titles:
            try:
                self.results_ready.emit(f"Searching for '{job_title}' jobs on Google...\n")
                
                # Perform Google search
                search_results = search(
                    f"{job_title} jobs",  # Search query as the first positional argument
                    stop=10,  # Stop after fetching 10 results
                    pause=2.0  # Delay between requests (in seconds)
                )

                if not search_results:
                    self.results_ready.emit(f"No jobs found for '{job_title}'.\n")
                    continue

                for result in search_results:
                    self.results_ready.emit(f"Link: {result}\n")
                    self.results_ready.emit("-" * 50 + "\n")

            except Exception as e:
                logging.error(f"Error fetching jobs for '{job_title}': {e}")
                self.error_occurred.emit(f"Error fetching jobs for '{job_title}': {e}\n")


class JobSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Job Search for Moodle and LMS Administrators")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Job titles
        self.job_titles = [
            "Moodle Administrator",
            "Moodle Developer",
            "Learning Management System Administrator",
            "Learning System Administrator",
            "LMS Administrator"
        ]

        # Job titles list
        self.job_title_label = QLabel("Job Titles:")
        self.job_title_list = QListWidget()
        self.job_title_list.addItems(self.job_titles)
        layout.addWidget(self.job_title_label)
        layout.addWidget(self.job_title_list)

        # Add new job title
        self.new_job_title_label = QLabel("Add New Job Title:")
        self.new_job_title_input = QLineEdit()
        self.add_job_title_button = QPushButton("Add Job Title")
        self.add_job_title_button.clicked.connect(self.add_job_title)
        layout.addWidget(self.new_job_title_label)
        layout.addWidget(self.new_job_title_input)
        layout.addWidget(self.add_job_title_button)

        # Search button
        self.search_button = QPushButton("Search Jobs")
        self.search_button.clicked.connect(self.search_jobs)
        layout.addWidget(self.search_button)

        # Results display
        self.results_label = QLabel("Search Results:")
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_label)
        layout.addWidget(self.results_display)

        # Set layout
        self.setLayout(layout)

    def add_job_title(self):
        new_title = self.new_job_title_input.text().strip()
        if new_title and new_title not in self.job_titles:
            self.job_titles.append(new_title)
            self.job_title_list.addItem(new_title)
            self.new_job_title_input.clear()
        elif not new_title:
            QMessageBox.warning(self, "Warning", "Please enter a valid job title.")
        else:
            QMessageBox.warning(self, "Warning", "This job title already exists.")

    def search_jobs(self):
        selected_job_titles = [item.text() for item in self.job_title_list.selectedItems()]
        if not selected_job_titles:
            QMessageBox.warning(self, "Warning", "Please select at least one job title.")
            return

        # Clear previous results
        self.results_display.clear()

        # Start search in a separate thread
        self.thread = JobSearchThread(selected_job_titles)
        self.thread.results_ready.connect(self.update_results)
        self.thread.error_occurred.connect(self.show_error)
        self.thread.start()

    def update_results(self, text):
        self.results_display.append(text)

    def show_error(self, error_message):
        self.results_display.append(error_message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobSearchApp()
    window.show()
    sys.exit(app.exec_())
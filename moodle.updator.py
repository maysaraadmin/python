import sys
import os
import shutil
import subprocess
import requests
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QMessageBox
)

class MoodleUpgradeManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moodle Upgrade Manager")
        self.setGeometry(100, 100, 600, 600)

        # Moodle Path
        self.moodle_path_label = QLabel("Moodle Code Path:", self)
        self.moodle_path_input = QLineEdit(self)
        self.browse_moodle_code_button = QPushButton("Browse", self)
        self.browse_moodle_code_button.clicked.connect(self.browse_moodle_code_path)

        # Moodle Data Directory
        self.data_path_label = QLabel("Moodle Data Path:", self)
        self.data_path_input = QLineEdit(self)
        self.browse_data_button = QPushButton("Browse", self)
        self.browse_data_button.clicked.connect(self.browse_data_path)

        # Database Details
        self.db_ip_label = QLabel("Database IP Address:", self)
        self.db_ip_input = QLineEdit(self)

        self.db_name_label = QLabel("Database Name:", self)
        self.db_name_input = QLineEdit(self)

        self.db_port_label = QLabel("Database Port:", self)
        self.db_port_input = QLineEdit(self)
        self.db_port_input.setText("3306")  # Default MySQL port

        self.db_user_label = QLabel("Database Username:", self)
        self.db_user_input = QLineEdit(self)

        self.db_password_label = QLabel("Database Password:", self)
        self.db_password_input = QLineEdit(self)
        self.db_password_input.setEchoMode(QLineEdit.Password)

        self.test_connection_button = QPushButton("Test Database Connection", self)
        self.test_connection_button.clicked.connect(self.test_database_connection)

        # Upgrade URL
        self.upgrade_url_label = QLabel("Moodle Update URL:", self)
        self.upgrade_url_input = QLineEdit(self)

        # Upgrade Button
        self.upgrade_button = QPushButton("Start Upgrade", self)
        self.upgrade_button.clicked.connect(self.start_upgrade)

        # Log Display
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.moodle_path_label)
        layout.addWidget(self.moodle_path_input)
        layout.addWidget(self.browse_moodle_code_button)

        layout.addWidget(self.data_path_label)
        layout.addWidget(self.data_path_input)
        layout.addWidget(self.browse_data_button)

        layout.addWidget(self.db_ip_label)
        layout.addWidget(self.db_ip_input)
        layout.addWidget(self.db_name_label)
        layout.addWidget(self.db_name_input)
        layout.addWidget(self.db_port_label)
        layout.addWidget(self.db_port_input)
        layout.addWidget(self.db_user_label)
        layout.addWidget(self.db_user_input)
        layout.addWidget(self.db_password_label)
        layout.addWidget(self.db_password_input)
        layout.addWidget(self.test_connection_button)

        layout.addWidget(self.upgrade_url_label)
        layout.addWidget(self.upgrade_url_input)
        layout.addWidget(self.upgrade_button)
        layout.addWidget(self.log_display)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def log_message(self, message):
        """Log messages to the QTextEdit log display."""
        self.log_display.append(message)

    def browse_moodle_code_path(self):
        """Browse and select Moodle code directory."""
        moodle_path = QFileDialog.getExistingDirectory(self, "Select Moodle Code Directory")
        if moodle_path:
            self.moodle_path_input.setText(moodle_path)

    def browse_data_path(self):
        """Browse and select Moodle data directory."""
        data_path = QFileDialog.getExistingDirectory(self, "Select Moodle Data Directory")
        if data_path:
            self.data_path_input.setText(data_path)

    def test_database_connection(self):
        """Test the connection to the database."""
        db_ip = self.db_ip_input.text()
        db_name = self.db_name_input.text()
        db_port = self.db_port_input.text()
        db_user = self.db_user_input.text()
        db_password = self.db_password_input.text()

        try:
            self.log_message("Testing database connection...")
            connection = mysql.connector.connect(
                host=db_ip,
                database=db_name,
                user=db_user,
                password=db_password,
                port=int(db_port)
            )
            if connection.is_connected():
                self.log_message("Database connection successful.")
                QMessageBox.information(self, "Success", "Database connection successful.")
                connection.close()
        except mysql.connector.Error as e:
            self.log_message(f"Database connection failed: {e}")
            QMessageBox.critical(self, "Error", f"Database connection failed: {e}")

    def start_upgrade(self):
        """Handle Moodle upgrade process."""
        moodle_path = self.moodle_path_input.text()
        data_path = self.data_path_input.text()
        upgrade_url = self.upgrade_url_input.text()

        if not moodle_path or not os.path.exists(moodle_path):
            QMessageBox.critical(self, "Error", "Invalid Moodle code path.")
            return
        if not data_path or not os.path.exists(data_path):
            QMessageBox.critical(self, "Error", "Invalid Moodle data path.")
            return
        if not upgrade_url:
            QMessageBox.critical(self, "Error", "Please enter the Moodle update URL.")
            return

        try:
            self.log_message("Starting Moodle upgrade...")
            self.backup_moodle(moodle_path, data_path)
            zip_file = self.download_update(upgrade_url)
            self.replace_moodle_files(moodle_path, zip_file)
            self.run_database_upgrade(moodle_path)
            self.log_message("Moodle upgrade completed successfully.")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Upgrade failed: {str(e)}")

    def backup_moodle(self, moodle_path, data_path):
        """Backup the existing Moodle code and data directories."""
        self.log_message("Backing up Moodle directories...")

        def ignore_patterns(directory, contents):
            """Ignore specified patterns during backup."""
            return ['.git', '__pycache__']

        for path, name in [(moodle_path, "code"), (data_path, "data")]:
            backup_path = f"{path}_backup"
            try:
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.copytree(path, backup_path, ignore=shutil.ignore_patterns(*ignore_patterns(path, [])))
                self.log_message(f"Backup of {name} directory completed at {backup_path}.")
            except PermissionError as e:
                self.log_message(f"Permission error while backing up {name}: {e}")
                raise Exception(f"Access denied during backup of {name}. Please check permissions.")
            except Exception as e:
                self.log_message(f"Unexpected error while backing up {name}: {e}")
                raise Exception(f"Failed to backup {name}: {e}")

    def download_update(self, url):
        """Download the Moodle update package."""
        self.log_message("Downloading Moodle update...")
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception("Failed to download update.")

        zip_file = "moodle_update.zip"
        with open(zip_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        self.log_message(f"Downloaded update to {zip_file}.")
        return zip_file

    def replace_moodle_files(self, moodle_path, zip_file):
        """Replace existing Moodle files with the new version."""
        self.log_message("Extracting and replacing Moodle files...")
        extract_path = "moodle_temp"
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

        shutil.unpack_archive(zip_file, extract_path)
        for item in os.listdir(extract_path):
            s = os.path.join(extract_path, item)
            d = os.path.join(moodle_path, item)
            if os.path.exists(d):
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.remove(d)
            shutil.move(s, d)
        shutil.rmtree(extract_path)
        os.remove(zip_file)
        self.log_message("Files replaced successfully.")

    def run_database_upgrade(self, moodle_path):
        """Run Moodle's CLI script to upgrade the database."""
        self.log_message("Running database upgrade script...")
        script_path = os.path.join(moodle_path, "admin", "cli", "upgrade.php")
        if not os.path.exists(script_path):
            raise Exception("CLI upgrade script not found.")
        result = subprocess.run(
            ["php", script_path, "--non-interactive"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"Database upgrade failed: {result.stderr}")
        self.log_message(result.stdout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoodleUpgradeManager()
    window.show()
    sys.exit(app.exec_())

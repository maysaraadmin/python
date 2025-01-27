import sqlite3
import json
import requests
from lxml import html
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load credentials
def load_credentials(file_path):
    with open(file_path) as auth_data:
        return json.loads(auth_data.read())

# Initialize database
def init_db():
    conn = sqlite3.connect("person_data.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS persons (
        uid INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        laddr TEXT,
        paddr TEXT,
        aadhar TEXT,
        phone TEXT
    )
    """)
    conn.commit()
    return conn

# Scrape profile data
def scrape_profile(session, profile_id):
    response = session.get(f"https://lms.example.edu.in/user/profile.php?id={profile_id}")
    if response.status_code != 200:
        logging.warning(f"Failed to fetch profile ID {profile_id}")
        return None

    dom = html.fromstring(response.text)

    def get_text(selector, default=""):
        try:
            return dom.cssselect(selector)[0].text.strip()
        except IndexError:
            return default

    name = get_text(".fullname > span:nth-child(1)")
    if not name:  # Skip if name is missing
        return None

    laddr = get_text("li.contentnode:nth-child(3) > dl:nth-child(1) > dd:nth-child(2) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(1)", "")
    paddr = get_text(".custom_field_CorrespondenceAddressPermanent > dl:nth-child(1) > dd:nth-child(2)", "")
    aadhar = get_text(".custom_field_AaadharNo > dl:nth-child(1) > dd:nth-child(2)", "")
    phone = get_text(".custom_field_ContactNumber > dl:nth-child(1) > dd:nth-child(2)", "")

    return {
        "uid": profile_id,
        "name": name,
        "laddr": laddr,
        "paddr": paddr,
        "aadhar": aadhar,
        "phone": phone,
    }

# Save data to database
def save_to_db(conn, person):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO persons (uid, name, laddr, paddr, aadhar, phone) 
    VALUES (?, ?, ?, ?, ?, ?)
    """, (person["uid"], person["name"], person["laddr"], person["paddr"], person["aadhar"], person["phone"]))
    conn.commit()

# Main script
def main():
    credentials = load_credentials("userpass.json")
    session = requests.Session()

    # Login
    login_page = session.get("https://lms.example.edu.in/")
    dom = html.fromstring(login_page.text)
    login_token = dom.cssselect("#pre-login-form > input:nth-child(1)")[0].get("value")

    login_data = {
        "logintoken": login_token,
        "username": credentials["username"],
        "password": credentials["password"],
    }

    response = session.post("https://lms.example.edu.in/login/index.php", data=login_data)
    if response.status_code != 200:
        logging.error("Login failed")
        return

    # Initialize database
    conn = init_db()

    # Scrape profiles
    for profile_id in range(15000, 26200):
        logging.info(f"Scraping profile ID: {profile_id}")
        person = scrape_profile(session, profile_id)
        if person:
            save_to_db(conn, person)
            logging.info(f"Saved: {person}")
        time.sleep(1)  # Be respectful with delays

    conn.close()

if __name__ == "__main__":
    main()

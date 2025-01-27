import tkinter as tk
from tkinter import messagebox
import requests
import base64
import certifi
import os

# Set the SSL certificate path to the certifi bundle
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# PayPal API endpoints (Live environment)
PAYPAL_API_BASE = "https://api.paypal.com"  # Live PayPal API endpoint
AUTH_URL = f"{PAYPAL_API_BASE}/v1/oauth2/token"

class PayPalAPITester:
    def __init__(self, root):
        self.root = root
        self.root.title("PayPal API Key Tester")

        # Create and place the labels and entry widgets
        tk.Label(root, text="API Key:").grid(row=0, column=0, padx=10, pady=10)
        self.api_key_entry = tk.Entry(root, width=40)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(root, text="API Secret:").grid(row=1, column=0, padx=10, pady=10)
        self.api_secret_entry = tk.Entry(root, width=40, show="*")
        self.api_secret_entry.grid(row=1, column=1, padx=10, pady=10)

        # Create and place the test button
        self.test_button = tk.Button(root, text="Test API Key", command=self.test_api_key)
        self.test_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Status label to show the result
        self.status_label = tk.Label(root, text="", fg="black")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)

    def test_api_key(self):
        api_key = self.api_key_entry.get()
        api_secret = self.api_secret_entry.get()

        if not api_key or not api_secret:
            self.status_label.config(text="Please enter both API Key and API Secret.", fg="red")
            return

        # Encode the API key and secret for Basic Auth
        auth_string = f"{api_key}:{api_secret}"
        auth_bytes = auth_string.encode("ascii")
        base64_auth = base64.b64encode(auth_bytes).decode("ascii")

        headers = {
            "Authorization": f"Basic {base64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        try:
            response = requests.post(AUTH_URL, headers=headers, data=data)
            response.raise_for_status()  # Raise an error for bad status codes

            # If the request is successful, the API key and secret are valid
            response_data = response.json()
            access_token = response_data.get("access_token", "N/A")
            token_type = response_data.get("token_type", "N/A")

            self.status_label.config(
                text=f"Success! API Key and Secret are working.\nAccess Token: {access_token}\nToken Type: {token_type}",
                fg="green"
            )

        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP errors (e.g., 401 Unauthorized)
            error_message = f"HTTP Error: {http_err}\n"
            if response.status_code == 401:
                error_message += "Invalid API Key or Secret."
            else:
                error_message += f"Status Code: {response.status_code}\nResponse: {response.text}"
            self.status_label.config(text=error_message, fg="red")

        except requests.exceptions.ConnectionError:
            # Handle connection errors (e.g., no internet)
            self.status_label.config(text="Connection Error: Unable to connect to PayPal API.", fg="red")

        except requests.exceptions.RequestException as err:
            # Handle other request errors
            self.status_label.config(text=f"Request Error: {err}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = PayPalAPITester(root)
    root.mainloop()
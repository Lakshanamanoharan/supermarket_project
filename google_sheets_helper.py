import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import json

def create_order_sheet(order_number: str, cart: list, delivery_mode: str, delivery_address: str):
    """
    Creates a new Google Sheet named with the order number and writes cart details to it.
    Requires a 'credentials.json' service account file in the project directory.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    if not os.path.exists(credentials_path):
        print("Warning: credentials.json not found. Cannot write to Google Sheets.")
        # Return a dummy link for testing without breaking the flow
        return "https://docs.google.com/spreadsheets/d/dummy-link-if-no-credentials"
        
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Create a new spreadsheet
        sheet_title = f"Order #{order_number} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        spreadsheet = client.create(sheet_title)
        
        # Share the spreadsheet so anyone with link can view (or specifically with an email)
        spreadsheet.share(None, role='reader', type='anyone')
        
        # Get the first sheet
        worksheet = spreadsheet.sheet1
        
        # Prepare data
        headers = ["Product Name", "Quantity", "Price", "Total Price"]
        rows = [headers]
        
        grand_total = 0
        for item in cart:
            total_price = item["quantity"] * item["price"]
            grand_total += total_price
            rows.append([
                item["product"],
                item["quantity"],
                item["price"],
                total_price
            ])
            
        # Add empty row
        rows.append(["", "", "", ""])
        
        # Add totals and delivery Info
        rows.append(["GRAND TOTAL", "", "", grand_total])
        rows.append(["Delivery Mode", delivery_mode, "", ""])
        if delivery_mode == "delivery":
            rows.append(["Delivery Address", delivery_address, "", ""])
            
        worksheet.update('A1', rows)
        
        return spreadsheet.url
        
    except Exception as e:
        print(f"Failed to create Google Sheet: {str(e)}")
        return "Error creating sheet"

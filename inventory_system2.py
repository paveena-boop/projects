import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/paveenasingh/Downloads/sf-inventory-450807-81e3839fcf88.json", scope)
client = gspread.authorize(creds)

client = gspread.authorize(creds)

# Open the Google Sheets
user_master_sheet = client.open("borrowingdatabase").worksheet("user_master")
item_master_sheet = client.open("borrowingdatabase").worksheet("item_master")
transactions_sheet = client.open("borrowingdatabase").worksheet("transactions")

# Load data from Google Sheets into DataFrames
user_master = pd.DataFrame(user_master_sheet.get_all_records())
item_master = pd.DataFrame(item_master_sheet.get_all_records())
transactions = pd.DataFrame(transactions_sheet.get_all_records())

def save_data():
    user_master_sheet.update([user_master.columns.values.tolist()] + user_master.values.tolist())
    item_master_sheet.update([item_master.columns.values.tolist()] + item_master.values.tolist())
    transactions_sheet.update([transactions.columns.values.tolist()] + transactions.values.tolist())

def scan_user():
    user_id = input("Enter user ID: ")
    user_id = int(user_id)
    if user_id not in user_master['user_id'].values:
        user_name = input("Enter user name: ")
        user_master.loc[len(user_master)] = [user_id, user_name]
        save_data()
    return user_id

def scan_item():
    item_id = input("Enter item ID: ")
    item_id = int(item_id)
    if item_id not in item_master['item_id'].values:
        item_name = input("Enter item name: ")
        total_stock = int(input("Enter item quantity: "))
        current_stock = total_stock
        item_master.loc[len(item_master)] = [item_id, item_name, total_stock, current_stock]
        save_data()
    return item_id

def log_transaction(user_id, item_id, action):
    global transactions

     # If transactions DataFrame is empty, initialize columns
    if transactions.empty:
        transactions = pd.DataFrame(columns=['transaction_id', 'user_id', 'item_id', 'timestamp', 'action'])
        
    transaction_id = len(transactions) + 1
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    transactions.loc[len(transactions)] = [transaction_id, user_id, item_id, timestamp, action]
    save_data()

def borrow_item():
    user_id = scan_user()
    item_id = scan_item()
    item_id = int(item_id)
    # Debug print to check the item_master DataFrame
    print("Item Master DataFrame:\n", item_master)
    if 'current_stock' not in item_master.columns:
        print("Error: 'current_stock' column not found in item_master DataFrame")
        return
    item_quantity = item_master.loc[item_master['item_id'] == item_id, 'current_stock'].values[0]
    if item_quantity > 0:
        item_master.loc[item_master['item_id'] == item_id, 'current_stock'] -= 1
        log_transaction(user_id, item_id, 'borrow')
        print(f"Item {item_id} borrowed by user {user_id}.")
    else:
        print(f"Item {item_id} is out of stock.")

def return_item():
    user_id = scan_user()
    item_id = scan_item()
    item_id = int(item_id)
    item_master.loc[item_master['item_id'] == item_id, 'current_stock'] += 1
    log_transaction(user_id, item_id, 'return')
    print(f"Item {item_id} returned by user {user_id}.")

def view_data():
    print("User Master:")
    if user_master.empty:
        print("Nothing to display")
    else:
        print(user_master)
    
    print("\nItem Master:")
    if item_master.empty:
        print("Nothing to display")
    else:
        print(item_master)
    
    print("\nTransactions:")
    if transactions.empty:
        print("Nothing to display")
    else:
        print(transactions)

def view_borrowed_items():
    if transactions.empty:
        print("Nothing to display")
        return
    
    # Get the latest transaction for each item
    latest_transactions = transactions.loc[transactions.groupby('item_id')['timestamp'].idxmax()]
    # Filter for items that are currently borrowed
    borrowed_items_ids = latest_transactions[latest_transactions['action'] == 'borrow']['item_id']
    borrowed_items = item_master[item_master['item_id'].isin(borrowed_items_ids)]
    
    if borrowed_items.empty:
        print("Nothing to display")
    else:
        print("Currently Borrowed Items:")
        print(borrowed_items)

def view_items_in_stock():
    if item_master.empty:
        print("Nothing to display")
    else:
        in_stock_items = item_master[item_master['current_stock'] > 0]
        if in_stock_items.empty:
            print("Nothing to display")
        else:
            print("Items in Stock:")
            print(in_stock_items)

# Main loop
while True:
    print("\n1. Borrow Item")
    print("2. Return Item")
    print("3. View Data")
    print("4. View Borrowed Items")
    print("5. View Items in Stock")
    print("6. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        borrow_item()
    elif choice == '2':
        return_item()
    elif choice == '3':
        view_data()
    elif choice == '4':
        view_borrowed_items()
    elif choice == '5':
        view_items_in_stock()
    elif choice == '6':
        break
    else:
        print("Invalid choice. Please try again.")
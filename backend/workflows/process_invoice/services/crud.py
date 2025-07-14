import json
import os

FILE_PATH = "storage.json"

# Helper: Load data
def load_data():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

# Helper: Save data
def save_data(data):
    with open(FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

# CREATE
def create_item(item):
    data = load_data()
    if any(existing['vendor_name'] == item['vendor_name'] for existing in data):
        raise ValueError(f"Item with vendor_name '{item['vendor_name']}' already exists.")
    data.append(item)
    save_data(data)
    return item

# READ
def read_item(vendor_name=None):
    data = load_data()
    if vendor_name is None:
        return data
    return next((item for item in data if item['vendor_name'] == vendor_name), None)

# UPDATE
def update_item(vendor_name, updated_fields):
    data = load_data()
    for item in data:
        if item['vendor_name'] == vendor_name:
            item.update(updated_fields)
            save_data(data)
            return item
    return None

# DELETE
def delete_item(vendor_name):
    data = load_data()
    new_data = [item for item in data if item['vendor_name'] != vendor_name]
    if len(new_data) == len(data):
        return False  # No item deleted
    save_data(new_data)
    return True

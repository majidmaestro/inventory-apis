import requests

BASE_URL = "http://127.0.0.1:5000"


# Show all items in the inventory
def view_inventory():
    response = requests.get(f"{BASE_URL}/inventory")
    items = response.json()

    if not items:
        print("Inventory is empty.")
        return

    for item in items:
        print(f"ID {item['id']}: {item['name']} ({item['brand']}) - "
              f"KES {item['price']}, qty: {item['quantity']}")


# Ask for item details and add a new item
def add_item():
    barcode = input("Barcode: ")
    name = input("Name: ")
    brand = input("Brand: ")
    price = input("Price: ")
    quantity = input("Quantity: ")

    payload = {
        "barcode": barcode,
        "name": name,
        "brand": brand,
        "price": float(price),
        "quantity": int(quantity)
    }

    response = requests.post(f"{BASE_URL}/inventory", json=payload)

    if response.status_code == 201:
        print("Item added:", response.json())
    else:
        print("Error:", response.json())


# Update the price or quantity of an item
def update_item():
    item_id = input("ID of item to update: ")
    print("Leave blank to skip a field.")

    price = input("New price: ")
    quantity = input("New quantity: ")

    payload = {}

    if price:
        payload["price"] = float(price)

    if quantity:
        payload["quantity"] = int(quantity)

    response = requests.patch(
        f"{BASE_URL}/inventory/{item_id}", json=payload
    )

    if response.status_code == 200:
        print("Item updated:", response.json())
    else:
        print("Error:", response.json())


# Delete an item using its ID
def delete_item():
    item_id = input("ID of item to delete: ")
    response = requests.delete(f"{BASE_URL}/inventory/{item_id}")

    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print("Error:", response.json())


# Search OpenFoodFacts by barcode or product name
def find_on_api():
    choice = input("Search by (1) barcode or (2) name? ")

    if choice == "1":
        barcode = input("Barcode: ")
        response = requests.get(f"{BASE_URL}/external/{barcode}")
    else:
        name = input("Product name: ")
        response = requests.get(
            f"{BASE_URL}/external/search", params={"name": name}
        )

    if response.status_code == 200:
        print("Found:", response.json())
    else:
        print("Error:", response.json())


# Display the menu and handle the user's choice
def main():
    while True:
        print("\n--- Inventory CLI ---")
        print("1. View inventory")
        print("2. Add item")
        print("3. Update item")
        print("4. Delete item")
        print("5. Find item on OpenFoodFacts")
        print("6. Quit")

        choice = input("Choose an option: ")

        if choice == "1":
            view_inventory()
        elif choice == "2":
            add_item()
        elif choice == "3":
            update_item()
        elif choice == "4":
            delete_item()
        elif choice == "5":
            find_on_api()
        elif choice == "6":
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()

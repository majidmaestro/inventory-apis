from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Sample inventory items
inventory = [
    {"id": 1, "barcode": 20304567, "name": "Almond milk", "price": 250, "quantity": 67, "brand": "brookside"},
    {"id": 2, "barcode": 20304667, "name": "bread", "price": 450, "quantity": 89, "brand": "Super Loaf"}
]

next_id = 3


# Find an item using its ID
def get_item(item_id):
    item_id = int(item_id)
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


# Get all inventory items
@app.route("/inventory", methods=["GET"])
def list_inventory():
    return jsonify(inventory)


# Get one item by ID
@app.route("/inventory/<id>", methods=["GET"])
def get_single_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


# Add a new item
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json()

    required_fields = ["barcode", "name", "price", "quantity", "brand"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    new_item = {
        "id": next_id,
        "barcode": data["barcode"],
        "name": data["name"],
        "price": data["price"],
        "quantity": data["quantity"],
        "brand": data["brand"]
    }
    inventory.append(new_item)
    next_id += 1

    return jsonify(new_item), 201


# Update an item's details
@app.route("/inventory/<id>", methods=["PATCH"])
def update_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    for key in ["barcode", "name", "price", "quantity", "brand"]:
        if key in data:
            item[key] = data[key]

    return jsonify(item)


# Delete an item
@app.route("/inventory/<id>", methods=["DELETE"])
def delete_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item {id} deleted"})


# Look up a product using its barcode on OpenFoodFacts
@app.route("/external/<barcode>", methods=["GET"])
def lookup_external_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    headers = {"User-Agent": "InventoryApp/1.0 (student project)"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Could not reach OpenFoodFacts"}), 502

    data = response.json()
    if data.get("status") == 0:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    product = data["product"]
    result = {
        "barcode": barcode,
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", "Unknown"),
        "ingredients": product.get("ingredients_text", "Not available")
    }
    return jsonify(result)


# Search OpenFoodFacts using a product name
@app.route("/external/search", methods=["GET"])
def search_external_product():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Please provide a 'name' query parameter"}), 400

    url = "https://world.openfoodfacts.org/cgi/search.pl"
    headers = {"User-Agent": "InventoryApp/1.0 (student project)"}
    params = {
        "search_terms": name,
        "search_simple": 1,
        "json": 1,
        "page_size": 1
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Could not reach OpenFoodFacts"}), 502

    data = response.json()
    products = data.get("products", [])
    if not products:
        return jsonify({"error": f"No product found matching '{name}'"}), 404

    product = products[0]
    result = {
        "barcode": product.get("code", "Unknown"),
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", "Unknown"),
        "ingredients": product.get("ingredients_text", "Not available")
    }
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)

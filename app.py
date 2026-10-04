from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# ---------------------------------------------------------------------
# In-memory "database" — a simple list of dictionaries.
# In a real system this would be an actual database (that comes later
# in the course, Week 3-4 with SQL/SQLAlchemy). For now this array
# simulates storage, as the brief asks for.
# ---------------------------------------------------------------------
inventory = [
    {"id": 1, "barcode": 20304567, "name": "Almond milk", "price": 250, "quantity": 67, "brand": "brookside"},
    {"id": 2, "barcode": 20304667, "name": "bread", "price": 450, "quantity": 89, "brand": "Super Loaf"}
]

# Keeps track of the next id to assign when a new item is created.
# Starts at 3 because ids 1 and 2 are already used above.
next_id = 3


# ---------------------------------------------------------------------
# Helper function: find one item in `inventory` by its id.
# Returns the dictionary if found, or None if no item matches.
# `id` arrives from the URL as a string, so we convert it to int
# before comparing against item["id"], which is stored as a real int.
# ---------------------------------------------------------------------
def get_item(item_id):
    item_id = int(item_id)
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


# ---------------------------------------------------------------------
# GET /inventory
# Returns the full list of inventory items as JSON.
# ---------------------------------------------------------------------
@app.route("/inventory", methods=["GET"])
def list_inventory():
    return jsonify(inventory)


# ---------------------------------------------------------------------
# GET /inventory/<id>
# Returns a single item by id, or a 404 JSON error if not found.
# ---------------------------------------------------------------------
@app.route("/inventory/<id>", methods=["GET"])
def get_single_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


# ---------------------------------------------------------------------
# POST /inventory
# Adds a new item to inventory. Expects a JSON body like:
# {"barcode": 123, "name": "Eggs", "price": 300, "quantity": 20, "brand": "Kenchic"}
# The id is assigned automatically — the client never supplies it.
# ---------------------------------------------------------------------
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json()

    # Basic validation: make sure the required fields were actually sent.
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

    return jsonify(new_item), 201  # 201 = "Created", the correct REST status for POST


# ---------------------------------------------------------------------
# PATCH /inventory/<id>
# Updates one or more fields of an existing item. Expects a JSON body
# with only the fields that should change, e.g. {"price": 275}.
# ---------------------------------------------------------------------
@app.route("/inventory/<id>", methods=["PATCH"])
def update_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    # Only update fields that were actually sent, leave the rest untouched.
    for key in ["barcode", "name", "price", "quantity", "brand"]:
        if key in data:
            item[key] = data[key]

    return jsonify(item)


# ---------------------------------------------------------------------
# DELETE /inventory/<id>
# Removes an item from inventory by id.
# ---------------------------------------------------------------------
@app.route("/inventory/<id>", methods=["DELETE"])
def delete_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item {id} deleted"})


# ---------------------------------------------------------------------
# GET /external/<barcode>
# Looks up a product on the OpenFoodFacts API by barcode, and returns
# the relevant product details. Does NOT add it to inventory — that's
# a separate step the CLI/client decides to do with this data.
# ---------------------------------------------------------------------
@app.route("/external/<barcode>", methods=["GET"])
def lookup_external_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    # OpenFoodFacts requires a User-Agent header identifying the app;
    # requests without one are often rejected.
    headers = {"User-Agent": "InventoryApp/1.0 (student project)"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Could not reach OpenFoodFacts"}), 502

    data = response.json()

    # OpenFoodFacts returns status: 0 if the barcode wasn't found in their database.
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


# ---------------------------------------------------------------------
# GET /external/search?name=<product name>
# Searches OpenFoodFacts by product name (instead of exact barcode)
# and returns the top result. Uses a query parameter since searching
# by name is optional/flexible, unlike a barcode lookup which targets
# one specific product.
# ---------------------------------------------------------------------
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
        "page_size": 1  # only need the top match
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
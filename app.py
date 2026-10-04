from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# two starting items for demo purpose majorly.

inventory = [
    {"id": 1, "barcode": 20304567, "name": "Almond milk", "price": 250, "quantity": 67, "brand": "brookside"},
    {"id": 2, "barcode": 20304667, "name": "bread", "price": 450, "quantity": 89, "brand": "Super Loaf"}
]

# start at 3 since 1,2 is already taken.
next_id = 3

# 1. helper function
# helps to find an item by id in the inventory list. Returns the item dict if found, or None if not found.
# id comes in as text from the url, convert to number to compare.

def get_item(item_id):
    item_id = int(item_id)
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


# visit /inventory to see all items in inventory.
# and return it as json

@app.route("/inventory", methods=["GET"])
def list_inventory():
    return jsonify(inventory)

# if nothing is found return 404 error with error message 
# if something found return that one item as json


@app.route("/inventory/<id>", methods=["GET"])
def get_single_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


# request.get_json reads data that was sent in to create the item
# checks if all require fields are there, if not return 400(bad request) error with message
# if all good build new_dic. using next_id and add it to inventory status code is 201(created)
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


# find element by id 
# if not found return 404 error with message
# if found update the fields that were sent in, leave the rest untouched.
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


# find element by id 
# if not found return 404 error with message
# inventory.remove(item) removes item from list.
@app.route("/inventory/<id>", methods=["DELETE"])
def delete_item(id):
    item = get_item(id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item {id} deleted"})


# gets the product name from the query and searches OpenFoodFacts for a matching product.
# if a product is found, return its barcode, name, brand and ingredients; 
# otherwise return the appropriate error.
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


# gets the product name from the query and searches OpenFoodFacts for a matching product.
# if a product is found, return its barcode, name, brand and ingredients;
# otherwise return the appropriate error.
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
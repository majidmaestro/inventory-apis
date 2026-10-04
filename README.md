# Inventory Management System (Flask REST API)

A small REST API for managing retail inventory, built with Flask. Includes
integration with the OpenFoodFacts API to look up product details by
barcode, a CLI frontend, and a pytest test suite.

## Setup

```bash
git clone <your-repo-url>
cd inventory-apis
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the API

```bash
python app.py
```

The server starts at `http://127.0.0.1:5000`.

## Running the CLI

In a **second terminal** (with the API already running in the first):

```bash
source venv/bin/activate
python cli.py
```

Follow the on-screen menu to view, add, update, delete inventory items,
or look up a product on OpenFoodFacts by barcode.

## Running the tests

```bash
pytest
```

## API Endpoints

| Method | Endpoint              | Description                          |
|--------|------------------------|--------------------------------------|
| GET    | `/inventory`            | Get all inventory items              |
| GET    | `/inventory/<id>`       | Get a single item by id              |
| POST   | `/inventory`            | Add a new item                       |
| PATCH  | `/inventory/<id>`       | Update one or more fields of an item |
| DELETE | `/inventory/<id>`       | Delete an item by id                 |
| GET    | `/external/<barcode>`   | Look up a product on OpenFoodFacts   |

### Example: Add an item

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"barcode": 11111, "name": "Eggs", "brand": "Kenchic", "price": 300, "quantity": 20}'
```

### Example: Update an item

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 275}'
```

### Example: Look up a product externally

```bash
curl http://127.0.0.1:5000/external/3017620422003
```

## Data model

Each inventory item is stored as:

```json
{
  "id": 1,
  "barcode": 20304567,
  "name": "Almond milk",
  "brand": "brookside",
  "price": 250,
  "quantity": 67
}
```

`id` uniquely identifies the inventory record. `barcode` identifies the
underlying product and may repeat across records of the same product.
# Inventory Management System

This is a project I built for my Flask course. It's a REST API that lets
you manage a shop's inventory (add, view, update, delete items). It also
connects to the OpenFoodFacts API so you can look up real product info
by barcode or name. There's also a CLI tool to use it from the terminal
instead of a browser.

## What this project does

- Lets you add, view, update and delete inventory items through an API
- Lets you search OpenFoodFacts for a product by barcode or name
- Has a CLI menu so you can use all of this from the terminal
- Has tests written with pytest to check everything works

## Project files

- `app.py` - the Flask API, this is the main file
- `cli.py` - the command line tool that talks to the API
- `test_app.py` - the tests
- `requirements.txt` - list of packages needed
- `README.md` - this file

## How to set it up

1. Clone the repo:
```
git clone <your-repo-url>
cd inventory-apis
```

2. Make a virtual environment and activate it:
```
python3 -m venv venv
source venv/bin/activate
```
(On windows it would be `venv\Scripts\activate` instead)

3. Install what's needed:
```
pip install -r requirements.txt
```

## How to run it

Start the API first, and leave this terminal running:
```
python app.py
```

It should say something like `Running on http://127.0.0.1:5000`.

Then open a second terminal, activate the venv again, and run the CLI:
```
source venv/bin/activate
python cli.py
```

You'll get a menu where you can view inventory, add items, update them,
delete them, or search OpenFoodFacts.

## Running the tests

With the venv active:
```
pytest
```

## API endpoints

These are the routes the API has:

| Method | Route                     | What it does                    |
|--------|----------------------------|----------------------------------|
| GET    | /inventory                 | get all items                   |
| GET    | /inventory/<id>            | get one item by its id          |
| POST   | /inventory                 | add a new item                  |
| PATCH  | /inventory/<id>            | update an item                  |
| DELETE | /inventory/<id>            | delete an item                  |
| GET    | /external/<barcode>        | look up a product by barcode    |
| GET    | /external/search?name=X    | look up a product by name       |

### Example: adding an item

```
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"barcode": 11111, "name": "Eggs", "brand": "Kenchic", "price": 300, "quantity": 20}'
```

### Example: updating an item's price

```
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 275}'
```

### Example: looking up a product by barcode

```
curl http://127.0.0.1:5000/external/3017620422003
```

## What one inventory item looks like

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

I used two different fields on purpose - `id` and `barcode`. `id` is
unique to each record in my inventory, but `barcode` is the actual
product's barcode, so two records could have the same barcode if they're
the same product added at different times.

## Notes

- The inventory is just stored in a Python list in memory for now, so it
  resets every time the server restarts. A real version would use an
  actual database.
- The OpenFoodFacts API needs a User-Agent header or it blocks the
  request, so that's included when calling it.
- Sometimes the OpenFoodFacts search can fail if their server is down
  (I got a 503 once while testing) - that's on their end, not a bug here.
# Inventory Management System

## About

This is a Python inventory management system built using Flask.

It allows users to add, view, update and delete products. It also connects to the OpenFoodFacts API to search for product information using a barcode or product name.

The project has a command-line interface (CLI) that allows users to interact with the system.

## Features

* View all products
* View one product by ID
* Add new products
* Update product details
* Delete products
* Search OpenFoodFacts by barcode
* Search OpenFoodFacts by product name
* Test the API using pytest

## Requirements

* Python 3
* Flask
* Requests
* Pytest

## Installation

Clone the project and enter its directory.

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on Linux or WSL:

```bash
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask API:

```bash
python app.py
```

Open another terminal in the project directory and activate the virtual environment.

Then run the CLI:

```bash
python cli.py
```

Use the menu to choose what you want to do.

## API Routes

| Method | Route                        | Purpose                              |
| ------ | ---------------------------- | ------------------------------------ |
| GET    | `/inventory`                 | View all products                    |
| GET    | `/inventory/<id>`            | View one product                     |
| POST   | `/inventory`                 | Add a product                        |
| PATCH  | `/inventory/<id>`            | Update a product                     |
| DELETE | `/inventory/<id>`            | Delete a product                     |
| GET    | `/external/<barcode>`        | Search OpenFoodFacts by barcode      |
| GET    | `/external/search?name=milk` | Search OpenFoodFacts by product name |

## Running Tests

Run the tests with:

```bash
pytest -v
```

The tests check the inventory routes, adding and updating products, deleting products, and searching OpenFoodFacts.

The external API tests use mock responses so they do not need to contact OpenFoodFacts during those tests.

## Data Storage

The inventory is stored in a Python list while the application is running. The data is temporary and is not saved permanently.

## External API

This project uses OpenFoodFacts to retrieve product information.

Website: https://world.openfoodfacts.org/

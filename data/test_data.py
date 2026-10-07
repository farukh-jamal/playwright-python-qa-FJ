"""Inputs and expected values. Keep these separate from test actions.

Expected values are explicit, rather than calculated by the application under
test. This helps a test catch an incorrect application calculation.
"""

VALID_USER = {"username": "alex.demo", "password": "DemoPass123!"}
SECOND_USER = {"username": "jamie.demo", "password": "DemoPass456!"}

INVALID_LOGINS = [
    ("alex.demo", "wrong-password"),
    ("unknown.demo", "DemoPass123!"),
]

REQUIRED_LOGIN_CASES = [
    ("", "DemoPass123!"),
    ("alex.demo", ""),
    ("", ""),
]

PROTECTED_UI_PATHS = ["/products", "/cart", "/checkout"]

EXPECTED_PRODUCTS = [
    {"id": 1, "name": "Trail Backpack", "price_cents": 4500,
     "description": "A lightweight backpack for day trips.", "stock": 8},
    {"id": 2, "name": "Steel Water Bottle", "price_cents": 1800,
     "description": "A reusable bottle with a leakproof lid.", "stock": 10},
    {"id": 3, "name": "Desk Notebook", "price_cents": 1200,
     "description": "A lined notebook for everyday notes.", "stock": 6},
]

BACKPACK, BOTTLE, NOTEBOOK = EXPECTED_PRODUCTS

VALID_QUANTITIES = [(1, "$45.00"), (2, "$90.00"), (8, "$360.00")]
INVALID_UI_QUANTITIES = [
    (0, "Quantity must be a positive integer."),
    (-1, "Quantity must be a positive integer."),
    (9, "Requested quantity exceeds available stock."),
]
INVALID_API_QUANTITIES = [0, -1, 1.5, "2", True]

CART_TOTALS = {
    "empty": "$0.00",
    "backpack": "$45.00",
    "bottle": "$18.00",
    "two_backpacks": "$90.00",
    "backpack_and_bottle": "$63.00",
    "two_backpacks_and_bottle": "$108.00",
}

VALID_CUSTOMER = {
    "full_name": "Alex Morgan",
    "address": "42 Example Street",
    "city": "Toronto",
    "postal_code": "M5V 2T6",
    "email": "alex@example.test",
}

CHECKOUT_REQUIRED_FIELDS = [
    ("full_name", "Full name is required."),
    ("address", "Street address is required."),
    ("city", "City is required."),
    ("postal_code", "Postal code is required."),
    ("email", "Email is required."),
]

INVALID_CUSTOMER_FIELDS = [
    ("email", "invalid-email", "Enter a valid email address."),
    ("postal_code", "12345", "Enter a valid Canadian postal code."),
]

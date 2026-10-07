"""Local demo store. UI forms and the REST API share the same business rules.

Prices use integer cents to avoid floating point rounding. Data lives in memory
so pytest resets it without a database or external service.
"""

import json
import re
import secrets
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for


class StoreError(Exception):
    """A business rule rejection with an HTTP status and readable messages."""

    def __init__(self, messages: list[str], status: int = 422):
        self.messages = messages
        self.status = status
        super().__init__(messages[0])


def create_app() -> Flask:
    app = Flask(__name__)
    # A new signing key belongs to this process only. No secret is committed.
    app.secret_key = secrets.token_hex(32)
    seed_path = Path(__file__).resolve().parents[1] / "data" / "store_seed.json"
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    users = {user["username"]: user for user in seed["users"]}
    products = {product["id"]: product for product in seed["products"]}
    app.config["STORE"] = {"carts": {}, "orders": {}, "next_order_number": 1001}

    def store() -> dict:
        return app.config["STORE"]

    def current_cart() -> dict[int, int]:
        return store()["carts"].setdefault(session["username"], {})

    def cart_details() -> dict:
        items = []
        for product_id, quantity in current_cart().items():
            product = products[product_id]
            items.append({
                **product,
                "quantity": quantity,
                "line_total_cents": product["price_cents"] * quantity,
            })
        return {
            "items": items,
            "item_count": sum(item["quantity"] for item in items),
            "total_cents": sum(item["line_total_cents"] for item in items),
        }

    def authenticate(username: str, password: str) -> dict:
        if not username or not password:
            raise StoreError(["Username and password are required."])
        user = users.get(username)
        if user is None or not secrets.compare_digest(user["password"], password):
            raise StoreError(["Invalid username or password."], 401)
        session.clear()
        session["username"] = username
        return {"username": username, "full_name": user["full_name"]}

    def product_by_id(product_id: int) -> dict:
        if product_id not in products:
            raise StoreError(["Product not found."], 404)
        return products[product_id]

    def validate_quantity(product: dict, quantity: int) -> None:
        # bool is a Python int subclass, so check the exact type for JSON input.
        if type(quantity) is not int or quantity < 1:
            raise StoreError(["Quantity must be a positive integer."])
        if quantity > product["stock"]:
            raise StoreError(["Requested quantity exceeds available stock."], 409)

    def add_item(product_id: int, quantity: int) -> dict:
        product = product_by_id(product_id)
        validate_quantity(product, quantity)
        new_quantity = current_cart().get(product_id, 0) + quantity
        validate_quantity(product, new_quantity)
        current_cart()[product_id] = new_quantity
        return cart_details()

    def update_item(product_id: int, quantity: int) -> dict:
        product = product_by_id(product_id)
        if product_id not in current_cart():
            raise StoreError(["Product is not in your cart."], 404)
        validate_quantity(product, quantity)
        current_cart()[product_id] = quantity
        return cart_details()

    def remove_item(product_id: int) -> dict:
        if product_id not in current_cart():
            raise StoreError(["Product is not in your cart."], 404)
        del current_cart()[product_id]
        return cart_details()

    def place_order(customer: dict) -> dict:
        if not current_cart():
            raise StoreError(["Your cart is empty."], 400)
        labels = {
            "full_name": "Full name", "address": "Street address", "city": "City",
            "postal_code": "Postal code", "email": "Email",
        }
        cleaned = {}
        errors = []
        for field, label in labels.items():
            value = customer.get(field, "")
            cleaned[field] = value.strip() if isinstance(value, str) else ""
            if not cleaned[field]:
                errors.append(f"{label} is required.")
        if cleaned["email"] and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", cleaned["email"]):
            errors.append("Enter a valid email address.")
        if cleaned["postal_code"] and not re.fullmatch(
            r"[A-Z]\d[A-Z] ?\d[A-Z]\d", cleaned["postal_code"].upper()
        ):
            errors.append("Enter a valid Canadian postal code.")
        if errors:
            raise StoreError(errors)
        cart = cart_details()
        order_id = f"DEMO-{store()['next_order_number']}"
        store()["next_order_number"] += 1
        order = {"order_id": order_id, "username": session["username"],
                 "customer": cleaned, **cart}
        store()["orders"][order_id] = order
        current_cart().clear()
        return order

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "username" not in session:
                if request.path.startswith("/api/"):
                    raise StoreError(["Login is required."], 401)
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped

    def json_body() -> dict:
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            raise StoreError(["Send a JSON object."], 400)
        return body

    def form_quantity() -> int:
        try:
            return int(request.form.get("quantity", "1"))
        except ValueError:
            raise StoreError(["Quantity must be a positive integer."]) from None

    @app.template_filter("money")
    def money(cents: int) -> str:
        return f"${cents / 100:.2f}"

    @app.errorhandler(StoreError)
    def handle_store_error(error: StoreError):
        return jsonify({"error": error.messages[0], "errors": error.messages}), error.status

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ready"})

    @app.route("/", methods=["GET", "POST"])
    @app.route("/login", methods=["GET", "POST"])
    def login():
        errors = []
        if request.method == "POST":
            try:
                authenticate(request.form.get("username", ""), request.form.get("password", ""))
                return redirect(url_for("catalog"))
            except StoreError as error:
                errors = error.messages
        return render_template("login.html", errors=errors)

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/products")
    @login_required
    def catalog():
        return render_template("products.html", products=products.values(), errors=[])

    @app.get("/products/<int:product_id>")
    @login_required
    def product_detail(product_id: int):
        return render_template("product_detail.html", product=product_by_id(product_id), errors=[])

    @app.post("/cart/add/<int:product_id>")
    @login_required
    def cart_add(product_id: int):
        try:
            add_item(product_id, form_quantity())
            return redirect(url_for("cart"))
        except StoreError as error:
            return render_template("products.html", products=products.values(), errors=error.messages)

    @app.get("/cart")
    @login_required
    def cart():
        return render_template("cart.html", cart=cart_details(), errors=[])

    @app.post("/cart/update/<int:product_id>")
    @login_required
    def cart_update(product_id: int):
        try:
            update_item(product_id, form_quantity())
            return redirect(url_for("cart"))
        except StoreError as error:
            return render_template("cart.html", cart=cart_details(), errors=error.messages)

    @app.post("/cart/remove/<int:product_id>")
    @login_required
    def cart_remove(product_id: int):
        remove_item(product_id)
        return redirect(url_for("cart"))

    @app.route("/checkout", methods=["GET", "POST"])
    @login_required
    def checkout():
        if not current_cart():
            return redirect(url_for("cart"))
        errors = []
        if request.method == "POST":
            try:
                order = place_order(request.form.to_dict())
                return redirect(url_for("confirmation", order_id=order["order_id"]))
            except StoreError as error:
                errors = error.messages
        return render_template("checkout.html", cart=cart_details(), errors=errors,
                               customer=request.form)

    @app.get("/confirmation/<order_id>")
    @login_required
    def confirmation(order_id: str):
        order = store()["orders"].get(order_id)
        if order is None or order["username"] != session["username"]:
            raise StoreError(["Order not found."], 404)
        return render_template("confirmation.html", order=order, errors=[])

    @app.post("/api/login")
    def api_login():
        body = json_body()
        username, password = body.get("username", ""), body.get("password", "")
        if not isinstance(username, str) or not isinstance(password, str):
            raise StoreError(["Username and password must be text."])
        return jsonify({"user": authenticate(username, password)})

    @app.post("/api/logout")
    def api_logout():
        session.clear()
        return "", 204

    @app.get("/api/products")
    def api_products():
        return jsonify({"products": list(products.values())})

    @app.get("/api/products/<int:product_id>")
    def api_product(product_id: int):
        return jsonify({"product": product_by_id(product_id)})

    @app.get("/api/cart")
    @login_required
    def api_cart():
        return jsonify(cart_details())

    @app.post("/api/cart")
    @login_required
    def api_add_item():
        body = json_body()
        product_id = body.get("product_id")
        if type(product_id) is not int:
            raise StoreError(["Product ID must be an integer."])
        return jsonify(add_item(product_id, body.get("quantity", 1))), 201

    @app.patch("/api/cart/<int:product_id>")
    @login_required
    def api_update_item(product_id: int):
        return jsonify(update_item(product_id, json_body().get("quantity")))

    @app.delete("/api/cart/<int:product_id>")
    @login_required
    def api_remove_item(product_id: int):
        return jsonify(remove_item(product_id))

    @app.post("/api/checkout")
    @login_required
    def api_checkout():
        return jsonify(place_order(json_body())), 201

    return app


if __name__ == "__main__":
    # For manual exploration. Tests start their own server on an available port.
    create_app().run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

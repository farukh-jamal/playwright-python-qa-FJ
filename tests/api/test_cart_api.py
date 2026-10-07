import pytest
from playwright.sync_api import APIRequestContext

from data.test_data import BACKPACK, BOTTLE, INVALID_API_QUANTITIES, SECOND_USER

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
def test_api_add_products_calculates_total(authenticated_api: APIRequestContext) -> None:
    """Two backpacks plus a bottle must return HTTP 201 and 10800 cents."""
    first_response = authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"], "quantity": 2})
    assert first_response.status == 201
    assert first_response.json()["total_cents"] == 9000
    second_response = authenticated_api.post("/api/cart", data={"product_id": BOTTLE["id"], "quantity": 1})
    assert second_response.status == 201
    cart = second_response.json()
    assert len(cart["items"]) == 2
    assert cart["item_count"] == 3
    assert cart["total_cents"] == 10800
    assert [item["line_total_cents"] for item in cart["items"]] == [9000, 1800]


def test_api_update_quantity(authenticated_api: APIRequestContext) -> None:
    """PATCH must replace the quantity and return the recalculated cart."""
    setup_response = authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"]})
    assert setup_response.status == 201
    response = authenticated_api.patch(f"/api/cart/{BACKPACK['id']}", data={"quantity": 3})
    assert response.status == 200
    assert response.json()["items"][0]["quantity"] == 3
    assert response.json()["total_cents"] == 13500


def test_api_remove_product(authenticated_api: APIRequestContext) -> None:
    """DELETE must remove the cart line and return an empty cart."""
    assert authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"]}).status == 201
    response = authenticated_api.delete(f"/api/cart/{BACKPACK['id']}")
    assert response.status == 200
    assert response.json() == {"items": [], "item_count": 0, "total_cents": 0}


@pytest.mark.parametrize("quantity", INVALID_API_QUANTITIES,
                         ids=["zero", "negative", "decimal", "text", "boolean"])
def test_api_rejects_invalid_quantity(authenticated_api: APIRequestContext, quantity) -> None:
    """Invalid quantity types or values must return HTTP 422 without adding items."""
    response = authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"], "quantity": quantity})
    assert response.status == 422
    assert response.json()["error"] == "Quantity must be a positive integer."
    cart_response = authenticated_api.get("/api/cart")
    assert cart_response.status == 200
    assert cart_response.json()["item_count"] == 0
    assert cart_response.json()["total_cents"] == 0


def test_api_rejects_addition_above_stock(authenticated_api: APIRequestContext) -> None:
    """Adding beyond existing stock must return HTTP 409 and preserve the cart."""
    assert authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"], "quantity": 8}).status == 201
    response = authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"], "quantity": 1})
    assert response.status == 409
    assert response.json()["error"] == "Requested quantity exceeds available stock."
    cart = authenticated_api.get("/api/cart").json()
    assert cart["items"][0]["quantity"] == 8
    assert cart["total_cents"] == 36000


def test_api_rejects_unknown_product_in_cart(authenticated_api: APIRequestContext) -> None:
    """Adding an unknown product must return HTTP 404 without changing the cart."""
    response = authenticated_api.post("/api/cart", data={"product_id": 999, "quantity": 1})
    assert response.status == 404
    assert response.json()["error"] == "Product not found."
    assert authenticated_api.get("/api/cart").json()["items"] == []


def test_api_rejects_non_json_payload(authenticated_api: APIRequestContext) -> None:
    """A text body must return HTTP 400 rather than a server error."""
    response = authenticated_api.post("/api/cart", data="not-json",
                                      headers={"Content-Type": "text/plain"})
    assert response.status == 400
    assert response.json()["error"] == "Send a JSON object."


def test_api_users_have_separate_carts(authenticated_api: APIRequestContext) -> None:
    """Changing the logged-in user must not expose the first user's cart."""
    assert authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"]}).status == 201
    login_response = authenticated_api.post("/api/login", data=SECOND_USER)
    assert login_response.status == 200
    assert login_response.json()["user"]["username"] == SECOND_USER["username"]
    cart_response = authenticated_api.get("/api/cart")
    assert cart_response.status == 200
    assert cart_response.json() == {"items": [], "item_count": 0, "total_cents": 0}


@pytest.mark.parametrize("method,path", [("get", "/api/cart"), ("post", "/api/cart"),
                                        ("post", "/api/checkout")])
def test_api_protected_routes_require_login(api_client: APIRequestContext, method: str,
                                           path: str) -> None:
    """Protected operations must return HTTP 401 for a fresh anonymous client."""
    response = getattr(api_client, method)(path)
    assert response.status == 401
    assert response.json()["error"] == "Login is required."

import pytest
from playwright.sync_api import APIRequestContext

from data.test_data import BACKPACK, CHECKOUT_REQUIRED_FIELDS, INVALID_CUSTOMER_FIELDS, VALID_CUSTOMER

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
def test_api_successful_checkout(authenticated_api: APIRequestContext) -> None:
    """Checkout must return HTTP 201, the expected order, and an empty cart."""
    assert authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"], "quantity": 2}).status == 201
    response = authenticated_api.post("/api/checkout", data=VALID_CUSTOMER)
    assert response.status == 201
    order = response.json()
    assert order["order_id"] == "DEMO-1001"
    assert order["customer"] == VALID_CUSTOMER
    assert order["total_cents"] == 9000
    assert order["item_count"] == 2
    assert order["items"][0]["id"] == BACKPACK["id"]
    assert order["items"][0]["quantity"] == 2
    assert authenticated_api.get("/api/cart").json() == {
        "items": [], "item_count": 0, "total_cents": 0,
    }
    # A repeated submission must not create another order from an empty cart.
    repeat_response = authenticated_api.post("/api/checkout", data=VALID_CUSTOMER)
    assert repeat_response.status == 400
    assert repeat_response.json()["error"] == "Your cart is empty."


def test_api_checkout_rejects_empty_cart(authenticated_api: APIRequestContext) -> None:
    """An empty cart must return HTTP 400 and no order payload."""
    response = authenticated_api.post("/api/checkout", data=VALID_CUSTOMER)
    assert response.status == 400
    assert response.json()["error"] == "Your cart is empty."
    assert "order_id" not in response.json()


@pytest.mark.parametrize("field,error_message", CHECKOUT_REQUIRED_FIELDS,
                         ids=[case[0] for case in CHECKOUT_REQUIRED_FIELDS])
def test_api_checkout_requires_customer_fields(authenticated_api: APIRequestContext,
                                              field: str, error_message: str) -> None:
    """Missing customer fields must return HTTP 422 and preserve the cart."""
    assert authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"]}).status == 201
    response = authenticated_api.post("/api/checkout", data={**VALID_CUSTOMER, field: ""})
    assert response.status == 422
    assert response.json()["errors"] == [error_message]
    assert authenticated_api.get("/api/cart").json()["total_cents"] == 4500


@pytest.mark.parametrize("field,value,error_message", INVALID_CUSTOMER_FIELDS,
                         ids=["invalid-email", "invalid-postal-code"])
def test_api_checkout_rejects_invalid_format(authenticated_api: APIRequestContext, field: str,
                                            value: str, error_message: str) -> None:
    """Invalid contact formats must return HTTP 422 without creating an order."""
    assert authenticated_api.post("/api/cart", data={"product_id": BACKPACK["id"]}).status == 201
    response = authenticated_api.post("/api/checkout", data={**VALID_CUSTOMER, field: value})
    assert response.status == 422
    assert response.json()["error"] == error_message
    assert "order_id" not in response.json()
    assert authenticated_api.get("/api/cart").json()["item_count"] == 1

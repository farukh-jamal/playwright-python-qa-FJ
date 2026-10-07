import pytest
from playwright.sync_api import APIRequestContext

from data.test_data import EXPECTED_PRODUCTS, INVALID_LOGINS, REQUIRED_LOGIN_CASES, VALID_USER

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
def test_api_login_returns_public_user(api_client: APIRequestContext) -> None:
    """Valid login must return HTTP 200 and user identity without a password."""
    response = api_client.post("/api/login", data=VALID_USER)
    assert response.status == 200
    assert response.json() == {"user": {"username": "alex.demo", "full_name": "Alex Morgan"}}
    # APIRequestContext retains the session cookie from the login response.
    cart_response = api_client.get("/api/cart")
    assert cart_response.status == 200
    assert cart_response.json() == {"items": [], "item_count": 0, "total_cents": 0}


@pytest.mark.parametrize("username,password", INVALID_LOGINS,
                         ids=["wrong-password", "unknown-user"])
def test_api_invalid_login(api_client: APIRequestContext, username: str, password: str) -> None:
    """Invalid credentials must return HTTP 401 and leave the client anonymous."""
    response = api_client.post("/api/login", data={"username": username, "password": password})
    assert response.status == 401
    assert response.json()["error"] == "Invalid username or password."
    assert api_client.get("/api/cart").status == 401


@pytest.mark.parametrize("username,password", REQUIRED_LOGIN_CASES,
                         ids=["missing-username", "missing-password", "both-empty"])
def test_api_login_requires_credentials(api_client: APIRequestContext, username: str,
                                        password: str) -> None:
    """Missing credentials must return HTTP 422 with a validation message."""
    response = api_client.post("/api/login", data={"username": username, "password": password})
    assert response.status == 422
    assert response.json()["errors"] == ["Username and password are required."]


def test_api_logout_clears_session(authenticated_api: APIRequestContext) -> None:
    """Logout must return an empty HTTP 204 response and revoke cart access."""
    response = authenticated_api.post("/api/logout")
    assert response.status == 204
    assert response.body() == b""
    protected_response = authenticated_api.get("/api/cart")
    assert protected_response.status == 401
    assert protected_response.json()["error"] == "Login is required."


@pytest.mark.smoke
def test_api_catalog_matches_expected_products(api_client: APIRequestContext) -> None:
    """The public catalog must return HTTP 200 and all expected product fields."""
    response = api_client.get("/api/products")
    assert response.status == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["products"] == EXPECTED_PRODUCTS


@pytest.mark.parametrize("product", EXPECTED_PRODUCTS, ids=lambda product: product["name"])
def test_api_product_details(api_client: APIRequestContext, product: dict) -> None:
    """Each existing product must return its expected details with HTTP 200."""
    response = api_client.get(f"/api/products/{product['id']}")
    assert response.status == 200
    assert response.json() == {"product": product}


def test_api_unknown_product_returns_404(api_client: APIRequestContext) -> None:
    """An unknown ID must return HTTP 404 with a readable error."""
    response = api_client.get("/api/products/999")
    assert response.status == 404
    assert response.json()["error"] == "Product not found."

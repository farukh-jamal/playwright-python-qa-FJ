"""Shared setup and cleanup. The official plugin owns browser lifecycles."""

import json
from collections.abc import Iterator
from threading import Thread
from urllib.request import urlopen

import pytest
from flask import Flask
from playwright.sync_api import APIRequestContext, Page, Playwright, expect
from werkzeug.serving import make_server

from config.settings import settings
from data.test_data import BACKPACK, VALID_USER
from demo_store.app import create_app
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage


@pytest.fixture(scope="session")
def demo_app() -> Flask:
    """Build one local application per pytest run."""
    return create_app()


@pytest.fixture(scope="session")
def base_url(demo_app: Flask) -> Iterator[str]:
    """Start once, confirm HTTP readiness, and stop after the final test.

    Port zero asks the OS for a free port. make_server binds before the thread
    starts, so the health request waits for service without a polling loop.
    """
    server = make_server("127.0.0.1", 0, demo_app)
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    application_url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(
            f"{application_url}/api/health",
            timeout=settings.app_start_timeout_ms / 1000,
        ) as response:
            if response.status != 200 or json.load(response) != {"status": "ready"}:
                pytest.fail("The demo application did not return its readiness response.")
        yield application_url
    finally:
        # Cleanup still runs if readiness or a test fails.
        server.shutdown()
        server_thread.join(timeout=5)
        server.server_close()


@pytest.fixture(autouse=True)
def reset_application_data(demo_app: Flask) -> Iterator[None]:
    """Function scope resets server data before and after every test.

    A fresh browser context clears cookies, but does not clear server carts or
    orders. These two forms of isolation solve different problems.
    """
    state = demo_app.config["STORE"]
    state["carts"].clear()
    state["orders"].clear()
    state["next_order_number"] = 1001
    yield
    state["carts"].clear()
    state["orders"].clear()
    state["next_order_number"] = 1001


@pytest.fixture(scope="session", autouse=True)
def assertion_timeout() -> None:
    expect.set_options(timeout=settings.assertion_timeout_ms)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, base_url: str) -> dict:
    """Extend plugin settings and preserve its screenshot, trace, and video setup."""
    return {**browser_context_args, "base_url": base_url,
            "viewport": {"width": 1280, "height": 800}}


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    # page is the plugin's fresh page. Do not launch another browser here.
    page.set_default_timeout(settings.action_timeout_ms)
    return LoginPage(page)


@pytest.fixture
def logged_in_products(login_page: LoginPage, page: Page) -> ProductsPage:
    """Each requesting test performs its own login, without shared cookies."""
    login_page.open()
    login_page.login(**VALID_USER)
    return ProductsPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)


@pytest.fixture
def checkout_with_product(logged_in_products: ProductsPage, cart_page: CartPage,
                          checkout_page: CheckoutPage) -> CheckoutPage:
    logged_in_products.add_to_cart(BACKPACK["name"])
    cart_page.checkout()
    return checkout_page


@pytest.fixture
def api_client(playwright: Playwright, base_url: str) -> Iterator[APIRequestContext]:
    """A separate cookie jar per test. API tests do not launch a browser."""
    client = playwright.request.new_context(base_url=base_url)
    try:
        yield client
    finally:
        client.dispose()


@pytest.fixture
def authenticated_api(api_client: APIRequestContext) -> APIRequestContext:
    response = api_client.post("/api/login", data=VALID_USER)
    if response.status != 200:
        pytest.fail(f"API login setup failed: {response.status}, {response.text()}")
    return api_client

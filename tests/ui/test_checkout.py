import pytest
from playwright.sync_api import Page, expect

from data.test_data import (
    CART_TOTALS, CHECKOUT_REQUIRED_FIELDS, INVALID_CUSTOMER_FIELDS, VALID_CUSTOMER,
)
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.regression


@pytest.mark.parametrize("field,error_message", CHECKOUT_REQUIRED_FIELDS,
                         ids=[case[0] for case in CHECKOUT_REQUIRED_FIELDS])
def test_checkout_requires_each_customer_field(checkout_with_product: CheckoutPage,
                                               field: str, error_message: str) -> None:
    """Each missing customer field must block checkout with its own message."""
    customer = {**VALID_CUSTOMER, field: ""}
    checkout_with_product.fill_customer(customer)
    checkout_with_product.place_order()
    expect(checkout_with_product.error_message).to_have_text(error_message)
    expect(checkout_with_product.heading).to_be_visible()
    expect(checkout_with_product.confirmation_heading).to_have_count(0)


@pytest.mark.parametrize("field,value,error_message", INVALID_CUSTOMER_FIELDS,
                         ids=["invalid-email", "invalid-postal-code"])
def test_checkout_rejects_invalid_format(checkout_with_product: CheckoutPage, field: str,
                                         value: str, error_message: str) -> None:
    """Invalid email or postal code must block the order."""
    checkout_with_product.fill_customer({**VALID_CUSTOMER, field: value})
    checkout_with_product.place_order()
    expect(checkout_with_product.error_message).to_have_text(error_message)
    expect(checkout_with_product.heading).to_be_visible()


@pytest.mark.smoke
def test_successful_checkout_clears_cart(checkout_with_product: CheckoutPage,
                                         cart_page: CartPage) -> None:
    """Valid checkout must confirm an order, preserve its total, and empty the cart."""
    checkout_with_product.fill_customer(VALID_CUSTOMER)
    checkout_with_product.place_order()
    expect(checkout_with_product.confirmation_heading).to_be_visible()
    expect(checkout_with_product.order_number).to_have_text("DEMO-1001")
    expect(checkout_with_product.order_total).to_have_text(CART_TOTALS["backpack"])
    cart_page.open()
    expect(cart_page.empty_message).to_be_visible()
    expect(cart_page.total).to_have_text(CART_TOTALS["empty"])


def test_empty_cart_blocks_checkout(logged_in_products: ProductsPage, cart_page: CartPage,
                                   page: Page, base_url: str) -> None:
    """Direct checkout access with an empty cart must return to the cart."""
    page.goto("/checkout")
    expect(page).to_have_url(f"{base_url}/cart")
    expect(cart_page.empty_message).to_be_visible()
    expect(cart_page.checkout_link).to_have_count(0)

import pytest
from playwright.sync_api import expect

from data.test_data import (
    BACKPACK, BOTTLE, CART_TOTALS, EXPECTED_PRODUCTS,
    INVALID_UI_QUANTITIES, VALID_QUANTITIES,
)
from pages.cart_page import CartPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.regression


def test_new_user_cart_is_empty(logged_in_products: ProductsPage, cart_page: CartPage) -> None:
    """A fresh test must start with zero items and a zero total."""
    logged_in_products.open_cart()
    expect(cart_page.empty_message).to_be_visible()
    expect(cart_page.total).to_have_text(CART_TOTALS["empty"])
    expect(cart_page.item_count).to_have_text("0")


@pytest.mark.smoke
@pytest.mark.parametrize("product", EXPECTED_PRODUCTS, ids=lambda product: product["name"])
def test_add_product_to_cart(logged_in_products: ProductsPage, cart_page: CartPage,
                             product: dict) -> None:
    """Adding each product must create one cart line with the correct total."""
    logged_in_products.add_to_cart(product["name"])
    expect(cart_page.item(product["name"])).to_be_visible()
    expect(cart_page.quantity(product["name"])).to_have_value("1")
    expect(cart_page.item_count).to_have_text("1")
    expect(cart_page.total).to_have_text(f"${product['price_cents'] / 100:.2f}")


def test_adding_same_product_increments_quantity(logged_in_products: ProductsPage,
                                                cart_page: CartPage) -> None:
    """A second addition must update one line to quantity two."""
    logged_in_products.add_to_cart(BACKPACK["name"])
    cart_page.continue_shopping()
    logged_in_products.add_to_cart(BACKPACK["name"])
    expect(cart_page.item(BACKPACK["name"])).to_have_count(1)
    expect(cart_page.quantity(BACKPACK["name"])).to_have_value("2")
    expect(cart_page.total).to_have_text(CART_TOTALS["two_backpacks"])


def test_remove_only_product_empties_cart(logged_in_products: ProductsPage,
                                        cart_page: CartPage) -> None:
    """Removing the last item must show an empty cart and zero total."""
    logged_in_products.add_to_cart(BACKPACK["name"])
    cart_page.remove(BACKPACK["name"])
    expect(cart_page.item(BACKPACK["name"])).to_have_count(0)
    expect(cart_page.empty_message).to_be_visible()
    expect(cart_page.total).to_have_text(CART_TOTALS["empty"])


def test_remove_one_product_preserves_other_product(logged_in_products: ProductsPage,
                                                    cart_page: CartPage) -> None:
    """Removing one line must preserve the other line and its total."""
    logged_in_products.add_to_cart(BACKPACK["name"])
    cart_page.continue_shopping()
    logged_in_products.add_to_cart(BOTTLE["name"])
    cart_page.remove(BACKPACK["name"])
    expect(cart_page.item(BACKPACK["name"])).to_have_count(0)
    expect(cart_page.item(BOTTLE["name"])).to_be_visible()
    expect(cart_page.total).to_have_text(CART_TOTALS["bottle"])


@pytest.mark.parametrize("quantity,expected_total", VALID_QUANTITIES,
                         ids=["minimum", "two-items", "stock-boundary"])
def test_valid_quantity_updates_total(logged_in_products: ProductsPage, cart_page: CartPage,
                                      quantity: int, expected_total: str) -> None:
    """Accepted quantities must update the line, item count, and total."""
    logged_in_products.add_to_cart(BACKPACK["name"])
    cart_page.change_quantity(BACKPACK["name"], quantity)
    expect(cart_page.quantity(BACKPACK["name"])).to_have_value(str(quantity))
    expect(cart_page.item_count).to_have_text(str(quantity))
    expect(cart_page.total).to_have_text(expected_total)
    expect(cart_page.line_total(BACKPACK["name"])).to_have_text(expected_total)


@pytest.mark.parametrize("quantity,error_message", INVALID_UI_QUANTITIES,
                         ids=["zero", "negative", "over-stock"])
def test_invalid_quantity_preserves_cart(logged_in_products: ProductsPage, cart_page: CartPage,
                                         quantity: int, error_message: str) -> None:
    """Rejected quantities must show an error and preserve the original cart."""
    logged_in_products.add_to_cart(BACKPACK["name"])
    cart_page.change_quantity(BACKPACK["name"], quantity)
    expect(cart_page.error_message).to_have_text(error_message)
    expect(cart_page.quantity(BACKPACK["name"])).to_have_value("1")
    expect(cart_page.total).to_have_text(CART_TOTALS["backpack"])


def test_cart_total_for_multiple_products(logged_in_products: ProductsPage,
                                          cart_page: CartPage) -> None:
    """Two backpacks and one bottle must cost CAD 108.00 across two lines."""
    logged_in_products.add_to_cart(BACKPACK["name"])
    cart_page.change_quantity(BACKPACK["name"], 2)
    cart_page.continue_shopping()
    logged_in_products.add_to_cart(BOTTLE["name"])
    expect(cart_page.item_count).to_have_text("3")
    expect(cart_page.total).to_have_text(CART_TOTALS["two_backpacks_and_bottle"])

import pytest
from playwright.sync_api import expect

from data.test_data import EXPECTED_PRODUCTS
from pages.products_page import ProductsPage

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_catalog_lists_all_products(logged_in_products: ProductsPage) -> None:
    """The catalog must show every seeded product exactly once."""
    expect(logged_in_products.product_cards).to_have_count(len(EXPECTED_PRODUCTS))
    for product in EXPECTED_PRODUCTS:
        card = logged_in_products.product_card(product["name"])
        expect(card).to_be_visible()
        expect(card.get_by_text(product["description"], exact=True)).to_be_visible()


@pytest.mark.parametrize("product", EXPECTED_PRODUCTS, ids=lambda product: product["name"])
def test_product_details(logged_in_products: ProductsPage, product: dict) -> None:
    """Each details page must show its name, description, price, and stock."""
    logged_in_products.view_product(product["name"])
    expect(logged_in_products.detail_heading(product["name"])).to_be_visible()
    expect(logged_in_products.description(product["description"])).to_be_visible()
    expect(logged_in_products.detail_price).to_have_text(
        f"${product['price_cents'] / 100:.2f}"
    )
    expect(logged_in_products.stock(product["stock"])).to_be_visible()

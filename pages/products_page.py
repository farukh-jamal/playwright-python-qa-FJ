from playwright.sync_api import Locator, Page


class ProductsPage:
    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Products", exact=True)
        self.product_cards = page.get_by_role("article")
        self.error_message = page.get_by_role("alert")
        self.detail_price = page.get_by_label("Price", exact=True)

    def open(self) -> None:
        self.page.goto("/products")

    def product_card(self, product_name: str) -> Locator:
        # Scope the search to one named product instead of using a position.
        return self.page.get_by_role("article", name=product_name, exact=True)

    def view_product(self, product_name: str) -> None:
        self.page.get_by_role("link", name=product_name, exact=True).click()

    def detail_heading(self, product_name: str) -> Locator:
        return self.page.get_by_role("heading", name=product_name, exact=True)

    def description(self, description: str) -> Locator:
        return self.page.get_by_text(description, exact=True)

    def stock(self, quantity: int) -> Locator:
        return self.page.get_by_text(f"Available stock: {quantity}", exact=True)

    def add_to_cart(self, product_name: str) -> None:
        self.page.get_by_role("button", name=f"Add {product_name} to cart", exact=True).click()

    def open_cart(self) -> None:
        self.page.get_by_role("link", name="Cart", exact=True).click()

    def logout(self) -> None:
        self.page.get_by_role("button", name="Log out", exact=True).click()

from playwright.sync_api import Locator, Page


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Your cart", exact=True)
        self.total = page.get_by_role("status", name="Cart total", exact=True)
        self.item_count = page.get_by_role("status", name="Cart item count", exact=True)
        self.empty_message = page.get_by_text("Your cart is empty.", exact=True)
        self.error_message = page.get_by_role("alert")
        self.checkout_link = page.get_by_role("link", name="Checkout", exact=True)

    def open(self) -> None:
        self.page.goto("/cart")

    def item(self, product_name: str) -> Locator:
        return self.page.get_by_role("region", name=product_name, exact=True)

    def quantity(self, product_name: str) -> Locator:
        return self.page.get_by_label(f"Quantity for {product_name}", exact=True)

    def line_total(self, product_name: str) -> Locator:
        return self.item(product_name).get_by_label("Line total", exact=True)

    def change_quantity(self, product_name: str, quantity: int) -> None:
        self.quantity(product_name).fill(str(quantity))
        self.page.get_by_role("button", name=f"Update {product_name}", exact=True).click()

    def remove(self, product_name: str) -> None:
        self.page.get_by_role("button", name=f"Remove {product_name}", exact=True).click()

    def continue_shopping(self) -> None:
        self.page.get_by_role("link", name="Continue shopping", exact=True).click()

    def checkout(self) -> None:
        self.checkout_link.click()

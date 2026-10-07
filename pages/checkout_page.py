from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Checkout", exact=True)
        self.fields = {
            "full_name": page.get_by_label("Full name", exact=True),
            "address": page.get_by_label("Street address", exact=True),
            "city": page.get_by_label("City", exact=True),
            "postal_code": page.get_by_label("Postal code", exact=True),
            "email": page.get_by_label("Email", exact=True),
        }
        self.place_order_button = page.get_by_role("button", name="Place order", exact=True)
        self.error_message = page.get_by_role("alert")
        self.confirmation_heading = page.get_by_role("heading", name="Order confirmed", exact=True)
        self.order_number = page.get_by_role("status", name="Order number", exact=True)
        self.order_total = page.get_by_role("status", name="Order total", exact=True)

    def fill_customer(self, customer: dict[str, str]) -> None:
        for field_name, locator in self.fields.items():
            locator.fill(customer[field_name])

    def place_order(self) -> None:
        self.place_order_button.click()

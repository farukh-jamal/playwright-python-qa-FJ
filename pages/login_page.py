from playwright.sync_api import Page


class LoginPage:
    """One place for login locators and user actions."""

    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Login", exact=True)
        # Labels follow how a person identifies a form field.
        self.username_input = page.get_by_label("Username", exact=True)
        self.password_input = page.get_by_label("Password", exact=True)
        self.login_button = page.get_by_role("button", name="Log in", exact=True)
        self.error_message = page.get_by_role("alert")

    def open(self) -> None:
        self.page.goto("/login")

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

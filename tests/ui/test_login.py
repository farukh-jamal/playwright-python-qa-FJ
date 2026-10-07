import pytest
from playwright.sync_api import Page, expect

from data.test_data import INVALID_LOGINS, PROTECTED_UI_PATHS, REQUIRED_LOGIN_CASES, VALID_USER
from pages.login_page import LoginPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_successful_login(login_page: LoginPage, page: Page, base_url: str) -> None:
    """Valid credentials must open the product catalog."""
    # Arrange: navigate to the feature under test.
    login_page.open()
    # Act: the page object fills the form and clicks its button.
    login_page.login(**VALID_USER)
    # Assert: Playwright retries until the expected heading is visible.
    products_page = ProductsPage(page)
    expect(products_page.heading).to_be_visible()
    expect(page).to_have_url(f"{base_url}/products")


@pytest.mark.parametrize("username,password", INVALID_LOGINS,
                         ids=["wrong-password", "unknown-user"])
def test_invalid_login(login_page: LoginPage, username: str, password: str) -> None:
    """An unknown user or wrong password must leave the user at login."""
    login_page.open()
    login_page.login(username, password)
    expect(login_page.error_message).to_have_text("Invalid username or password.")
    expect(login_page.heading).to_be_visible()


@pytest.mark.parametrize("username,password", REQUIRED_LOGIN_CASES,
                         ids=["missing-username", "missing-password", "both-empty"])
def test_login_required_fields(login_page: LoginPage, username: str, password: str) -> None:
    """Missing credentials must show the required-field message."""
    login_page.open()
    login_page.login(username, password)
    expect(login_page.error_message).to_have_text("Username and password are required.")
    expect(login_page.heading).to_be_visible()


@pytest.mark.parametrize("protected_path", PROTECTED_UI_PATHS)
def test_anonymous_user_is_redirected_to_login(login_page: LoginPage, page: Page,
                                             protected_path: str, base_url: str) -> None:
    """Protected catalog, cart, and checkout routes must require login."""
    page.goto(protected_path)
    expect(login_page.heading).to_be_visible()
    expect(page).to_have_url(f"{base_url}/login")


@pytest.mark.smoke
def test_logout_blocks_protected_pages(logged_in_products: ProductsPage,
                                      login_page: LoginPage, page: Page) -> None:
    """Logout must remove authentication, including direct route access."""
    logged_in_products.logout()
    expect(login_page.heading).to_be_visible()
    page.goto("/products")
    expect(login_page.heading).to_be_visible()

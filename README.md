# Playwright Python QA Automation Portfolio

A QA automation portfolio project built with Playwright, Python, and pytest.

This project demonstrates automated UI testing, API testing, Page Object Model design, reusable pytest fixtures, test data management, and CI/CD concepts using a small local e-commerce application.

## Technologies

- Python
- Playwright
- pytest
- pytest-playwright
- REST API testing
- Page Object Model
- Git and GitHub
- GitLab CI/CD
- HTML and JUnit test reports

## Test Coverage

The automated test suite covers key e-commerce workflows.

### UI Tests

- User login
- Product catalog
- Shopping cart
- Checkout workflow

### API Tests

- Authentication
- Product APIs
- Cart APIs
- Checkout APIs

## Framework Design

The project uses the Page Object Model to separate page interactions from test logic.

The `pages` directory contains reusable page classes.

The `tests` directory contains UI and API test scenarios.

The `conftest.py` file contains shared pytest fixtures and test setup.

## Project Structure

```text
playwright-python-qa-FJ/
│
├── config/             # Test configuration
├── data/               # Test data
├── demo_store/         # Local demo e-commerce application
├── pages/              # Page Object Model classes
├── tests/
│   ├── api/            # API automated tests
│   └── ui/             # Playwright UI automated tests
├── conftest.py         # Shared pytest fixtures
├── pytest.ini          # pytest configuration
├── requirements.txt    # Python dependencies
├── .gitignore
├── .gitlab-ci.yml      # CI/CD pipeline configuration
└── README.md
```

## Setup

Clone the repository:

```bash
git clone https://github.com/farukh-jamal/playwright-python-qa-FJ.git
```

Move into the project directory:

```bash
cd playwright-python-qa-FJ
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Install the Playwright browser:

```bash
playwright install chromium
```

## Running the Tests

Run the complete test suite:

```bash
pytest
```

Run only UI tests:

```bash
pytest tests/ui
```

Run only API tests:

```bash
pytest tests/api
```

Run Playwright tests with the browser visible:

```bash
pytest tests/ui --headed
```

## Test Reports

The framework supports test reporting, including JUnit XML and HTML reports.

Example:

```bash
pytest --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html
```

## CI/CD

The repository includes a `.gitlab-ci.yml` configuration for automated test execution in a CI/CD pipeline.

The pipeline installs project dependencies and Playwright browser dependencies before executing the automated test suite.

## Purpose

I built this project as a QA automation portfolio to demonstrate practical experience with Python, Playwright, pytest, UI automation, API testing, Page Object Model design, test framework organization, and CI/CD.

## Author

Farukh Jamal

QA Automation Engineer
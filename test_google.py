# test_google.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_google_title(driver):
    driver.get("https://www.google.com")
    assert "Google" in driver.title

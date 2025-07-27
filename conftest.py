import os
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from pytest_html import extras

# Dossier screenshots
SCREENSHOTS_DIR = "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

@pytest.fixture(scope="function")
def driver():
    """Fixture Selenium Chrome WebDriver"""
    options = Options()
    options.add_argument("--headless")  # Enlève si tu veux voir le navigateur
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()  # Assure-toi que chromedriver est dans PATH

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook pytest pour capturer un screenshot à la fin de chaque test, même Passed.
    Ajoute la capture dans le rapport HTML pytest-html.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":  # Seulement après exécution du test

        # Vérifie si test utilise le fixture 'driver' Selenium
        driver = item.funcargs.get("driver", None)
        if driver and isinstance(driver, WebDriver):

            # Génère un nom de fichier unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_test_name = item.name.replace("/", "_").replace(":", "_").replace(" ", "_")
            filename = os.path.join(SCREENSHOTS_DIR, f"{safe_test_name}_{timestamp}.png")

            # Tente la capture d'écran
            try:
                driver.save_screenshot(filename)
            except Exception as e:
                print(f"[ERROR] Impossible de prendre screenshot : {e}")
            else:
                # Ajoute la capture au rapport HTML
                if hasattr(rep, "extra"):
                    rep.extra.append(extras.image(filename, mime_type="image/png"))

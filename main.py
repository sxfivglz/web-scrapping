import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
from scrapper import WebScraper

def main():
    # Cargar la configuración desde el archivo JSON
    with open('Indeed.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Iniciar el WebDriver según el navegador especificado en la configuración
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        # Iniciar el scraping con la configuración cargada
        scraper = WebScraper(driver)
        scraper.run(config)

    except Exception as e:
        print(f"Error durante la ejecución del scraper: {e}")

    finally:
        # Cerrar el WebDriver al finalizar
        driver.quit()

if __name__ == "__main__":
    main()

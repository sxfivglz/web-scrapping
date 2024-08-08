#main.py
import json
from selenium import webdriver
from scrapper import WebScraper
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    #config_files = ['Indeed.json']
    #config_files = ['Clima.json']
    #config_files =['SIAUTT.json']
    config_files = ['Adafruit.json']
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.maximize_window()

    password = os.getenv('siautt_credential')
    passwordAdafruit = os.getenv('adafruit_credential')

    try:
        for config_file in config_files:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            config['siautt_credential'] = password
            config['adafruit_credential'] = passwordAdafruit

            scraper = WebScraper(driver)
            scraper.run(config)
    except Exception as e:
        print(f"Error durante la ejecución del scraper: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

    '''
        def get_by_method(self, method):
        """Devuelve el tipo de selector de elementos basado en el método especificado."""
        method = method.lower()
        if method == 'id':
            return By.ID
        elif method == 'name':
            return By.NAME
        elif method in ['class_name', 'class']:
            return By.CLASS_NAME
        elif method in ['tag_name', 'tag']:
            return By.TAG_NAME
        elif method in ['link_text', 'link']:
            return By.LINK_TEXT
        elif method in ['partial_link_text', 'partial']:
            return By.PARTIAL_LINK_TEXT
        elif method in ['css_selector', 'css']:
            return By.CSS_SELECTOR
        elif method == 'xpath':
            return By.XPATH
    '''
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
    config_files =['SIAUTT.json']
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    driver.maximize_window()

    password = os.getenv('siautt_credential')

    try:
        for config_file in config_files:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            config['siautt_credential'] = password

            scraper = WebScraper(driver)
            scraper.run(config)
    except Exception as e:
        print(f"Error durante la ejecución del scraper: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

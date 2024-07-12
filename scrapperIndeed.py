from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
driver.maximize_window()


driver.get('https://mx.indeed.com/')
time.sleep(2)

search_job = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'text-input-what')))
search_job.send_keys('Desarrollador web')


search_location = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'text-input-where')))
search_location.send_keys('Torreón, Coah')
time.sleep(2)

search_location.send_keys(Keys.ARROW_DOWN)
search_location.send_keys(Keys.ENTER)
search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'yosegi-InlineWhatWhere-primaryButton')))
search_button.click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobsearch-JobCountAndSortPane-jobCount')))

results = driver.find_element(By.CLASS_NAME, 'jobsearch-JobCountAndSortPane-jobCount')
print(results.text)

cards = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'job_seen_beacon')))
data = []

for card in cards:
    try:
      
        ActionChains(driver).move_to_element(card).perform()
        card.click()
        
     
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobsearch-JobInfoHeader-title')))
        
        
        title = driver.find_element(By.CLASS_NAME, 'jobsearch-JobInfoHeader-title').text
        
        company = driver.find_element(By.CLASS_NAME, 'css-1ioi40n').text
        
        try:
            salary = driver.find_element(By.ID, 'salaryInfoAndJobType').text
        except NoSuchElementException:
            salary = "No salary information available"

        title = title.replace('\n- job post', '')
        print(title)
        print(company)
        print(salary)
        print("----------------------------------------------------")
        
        data.append({"Puesto": title, "Empresa": company, "Pago y horario": salary})
        
        driver.back()
        
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'job_seen_beacon')))
        cards = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')
    except (NoSuchElementException, ElementNotInteractableException) as e:
        print(f"Error interacting with card: {e}")
        continue
    time.sleep(2) 

driver.quit()

df = pd.DataFrame(data)
print(df)
df.to_csv('trabajos.csv', index=False)
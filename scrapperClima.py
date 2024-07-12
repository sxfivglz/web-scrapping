from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
import pandas as pd
import datetime

url = 'https://weather.com/'

driver = webdriver.Chrome()
driver.get(url)

try:
    search = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, 'LocationSearch_input'))
    )
    search.send_keys('Torreón, Coahuila')
    time.sleep(2)
    search.send_keys(Keys.ARROW_DOWN)
    search.send_keys(Keys.ENTER)
    time.sleep(2)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="WxuLocalsuiteNav-header-71dadf79-621d-43ff-9a1a-d99a39f16abe"]/div/nav/div/div[1]/a[3]/span'))
    ).click()
    time.sleep(2)
    resultados = driver.find_elements(By.CLASS_NAME, 'DailyForecast--DisclosureList--nosQS')
    for resultado in resultados:
        time.sleep(2)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'DaypartDetails--DayPartDetail--2XOOV'))
        ).click()
        #Obtener la información de cada uno de los elementos
         #Obtener la fecha
        #<h2 class="DailyContent--daypartName--3emSU"><span class="DailyContent--daypartDate--3VGlz">jue 11</span> | Día</h2>
        fecha = info[0].find_element(By.CLASS_NAME, 'DailyContent--daypartDate--3emSU').text
        #class="DaypartDetails--Content--2Yg3_ DaypartDetails--contentGrid--2_szQ"
        info = driver.find_elements(By.CLASS_NAME, 'DaypartDetails--contentGrid--2_szQ')
        #Obtener la temperatura por el día
        #<span data-testid="TemperatureValue" class="DailyContent--temp--1s3a7" dir="ltr">33<span class="DailyContent--degreeSymbol--EbEpi">°</span></span>
        temperaturaDia = info[0].find_element(By.CLASS_NAME, 'DailyContent--temp--1s3a7').text
        #Obtener la descripción del clima
        #<p data-testid="wxPhrase" class="DailyContent--narrative--3Ti6_">Cielo parcialmente cubierto. Máxima de 33 C. Vientos del NNE de 15 a 25 km/h.</p>
        descripcion = info[0].find_element(By.CLASS_NAME, 'DailyContent--narrative--3Ti6_').text
       #obtener la temperatura por la noche
       #<span data-testid="TemperatureValue" class="DailyContent--temp--1s3a7 DailyContent--tempN--33RmW" dir="ltr">21<span class="DailyContent--degreeSymbol--EbEpi">°</span></span>
        temperaturaNoche = info[1].find_element(By.CLASS_NAME, 'DailyContent--temp--1s3a7').text
        #Obtener la descripción del clima por la noche
        #<p data-testid="wxPhrase" class="DailyContent--narrative--3Ti6_">Cielo parcialmente cubierto. Mínima de 21 C. Vientos del NNE de 15 a 25 km/h.</p>
        descripcionNoche = info[1].find_element(By.CLASS_NAME, 'DailyContent--narrative--3Ti6_').text
        print(fecha, temperaturaDia, descripcion, temperaturaNoche, descripcionNoche)
except TimeoutException:
    print('La página tardó demasiado en cargar')
except ElementNotInteractableException:
    print('No se pudo interactuar con el elemento')
finally:
    driver.quit()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import time
from archivoJson import archivoJson
from archivoPandas import Pandas

class Scrapper(archivoJson):

    def __init__(self):
        super().__init__("Datos.json")
        self.filename = ""
        self.driver = None 
        self.options = None
        self.url=""
     

    def configurarNavegador(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--disable-extensions')

    def abrirNavegador(self):
        self.driver = webdriver.Chrome(options=self.options)

    def abrirPagina(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

    def leerConfiguracion(self):
        self.configurarNavegador()
        self.abrirNavegador()
        self.filename = 'configuracion.json'
        lista = self.obtenerDatosJson()
        link = lista['configuracion'][0]['URL']
        self.url = link
        self.abrirPagina()
        time.sleep(5)
        for item in lista['configuracion']:
            item_type = item.get('type')
            if item_type == 'TABLE':
                self.extraerDatosTablas(item['xpath'], item['file'])
                time.sleep(5)
            if item_type == 'OL' or item_type == 'UL':
                self.obtenerDatosListas(item['xpath'], item['file'])
                time.sleep(5)
            if item_type == 'DIV':
                self.obtenerDatosDiv(item['xpath'], item['file'])
                time.sleep(5)
            if item_type == 'A':
                self.clickLink(item['xpath'])
                time.sleep(5)
            if item_type == 'BUTTON':
                self.clickBoton(item['xpath'])
                time.sleep(5)
            if item_type == 'SELECT':
                self.valorSelect(item['xpath'], item['value'])
                time.sleep(5)
            if item_type == 'INPUT':
                self.valorInput(item['xpath'], item['value'])
                time.sleep(5)

    def extraerDatosTablas(self, xpath, filename):
        try:
            tabla = self.driver.find_element(By.XPATH, xpath)
            try:
                thead = tabla.find_elements(By.TAG_NAME, 'thead')
                headers =[header.text for header in thead[0].find_elements(By.TAG_NAME, 'th')]
            except NoSuchElementException:
                headers = None

            tbody = tabla.find_elements(By.TAG_NAME, 'tbody')
            rows = tbody[0].find_elements(By.TAG_NAME, 'tr')
            datos = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if headers:
                    row_data = {headers[i]: cells[i].text for i in range(len(cells))}
                else:
                    row_data = [cell.text for cell in cells]
                datos.append(row_data)

            datos_tabla = {
                "datos": datos,
            }
        except NoSuchElementException as e:
            print(f"Error: {e}")
            datos_tabla = {
                "datos": []
                }
            
        
        self.filename = f'{filename}.json'
        self.convertirJson(datos_tabla)
        excel = Pandas(self.obtenerDatosJson())
        Pandas.to_excel(excel)

    def obtenerDatosListas(self, xpath, filename):
            try:
                lista = self.driver.find_element(By.XPATH, xpath)
                items = lista.find_elements(By.TAG_NAME, 'li')
                datos = [item.text for item in items]
                self.filename = f'{filename}.json'
                self.convertirJson(datos)
                print(self.obtenerDatosJson())
                # pandas = Pandas(self.obtenerDatosJson())
                # excel = f'{filename}.xlsx'
                # pandas.to_excel(excel)
            except NoSuchElementException as e:
                print(f"Error: {e}")

    def obtenerDatosDiv(self, xpath, filename):
            try:
                datosDiv = self.driver.find_element(By.XPATH, xpath)
                items = datosDiv.find_elements(By.TAG_NAME, 'div')
                listaDatos = [item.text for item in items]
                self.filename = f'{filename}.json'
                self.convertirJson(listaDatos)
            except NoSuchElementException as e:
                print(f"Error: {e}")   
        
    def clickBoton(self, xpath):
            try:
                boton = self.driver.find_element(By.XPATH, xpath)
                boton.click()
            except NoSuchElementException as e:
                print(f"Error: {e}")

    def clickLink(self, xpath):
            try:
                a = self.driver.find_element(By.XPATH, xpath)
                url = a.get_attribute('href')
                self.driver.get(url)
                self.abrirPagina()
            except NoSuchElementException as e:
                print(f"Error: {e}")
        
    def valorSelect(self, xpath, valor):
            try:
                seleccionar_elemento = self.driver.find_element(By.XPATH, xpath)
                select = Select(seleccionar_elemento)
                select.select_by_value(valor)
            except NoSuchElementException as e:
                print(f"Error: {e}")

    def valorInput(self, xpath, valor):
            try:
                input_element = self.driver.find_element(By.XPATH, xpath)
                input_element(valor)
            except NoSuchElementException as e:
                print(f"Error: {e}")
    
    


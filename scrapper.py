from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import json
import time
import os

class WebScraper:
    def __init__(self, driver):
        self.driver = driver
        self.data = []

    def run_from_json(self, json_file):
        """Carga la configuración desde un archivo JSON y ejecuta el scraper."""
        with open(json_file, 'r') as f:
            config = json.load(f)
        self.run(config)

    def run(self, config):
        """Ejecuta el scraper basado en la configuración proporcionada."""
        try:
            start_url = config['start_url']
            self.driver.get(start_url)
            time.sleep(2)

            while True:
                for action in config['actions']:
                    self.execute_action(action)

                # Verificar si hay una siguiente página y hacer clic si existe
                next_page_button = self.find_next_page_button(config)
                if not next_page_button:
                    break

                # Hacer clic en el botón de la siguiente página
                next_page_button.click()
                time.sleep(2)  # Esperar a que cargue la nueva página

            filename = config['output']['filename']
            columns = config['output'].get('columns')
            self.guardar_datos(filename, columns)

        except Exception as e:
            print(f"Error durante la ejecución del scraper: {e}")

    def execute_action(self, action):
        """Ejecuta una acción basada en la configuración JSON."""
        try:
            if action['action'] == 'click':
                self.click_action(action)
            elif action['action'] == 'input':
                self.input_action(action)
            elif action['action'] == 'key_press':
                self.key_press_action(action)
            elif action['action'] == 'wait':
                self.wait_action(action)
            elif action['action'] == 'get_element_text':
                self.get_element_text_action(action)
            elif action['action'] == 'find_elements':
                self.find_elements_action(action)
            elif action['action'] == 'store_data':
                self.store_data(action)
            elif action['action'] == 'go_back':
                self.go_back_action()
            elif action['action'] == 'scroll':
                self.scroll_action(action)
            else:
                print(f"Acción no reconocida: {action['action']}")
        except Exception as e:
            print(f"Error en acción {action['action']}: {e}")

    def click_action(self, action):
        """Ejecuta la acción de clic en el elemento especificado."""
        print(f"Ejecutando acción 'click' en elemento {action['value']}")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((self.get_by_method(action['by']), action['value']))
            )
            element.click()
            time.sleep(action.get('wait', 1))
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
            print(f"Error en acción 'click': {e}")

    def input_action(self, action):
        """Ejecuta la acción de ingresar texto en el elemento especificado."""
        print(f"Ejecutando acción 'input' en elemento {action['value']}")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((self.get_by_method(action['by']), action['value']))
            )
            input_value = action['input_value']
            if action.get('hidden', False):
                input_value = os.getenv(input_value)
            element.send_keys(input_value)
            time.sleep(action.get('wait', 1))
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error en acción 'input': {e}")

    def key_press_action(self, action):
        """Ejecuta la acción de presionar una tecla en el elemento especificado."""
        print(f"Ejecutando acción 'key_press' en elemento {action['value']}")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((self.get_by_method(action['by']), action['value']))
            )
            element.send_keys(getattr(Keys, action['key']))
            time.sleep(action.get('wait', 1))
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error en acción 'key_press': {e}")

    def wait_action(self, action):
        """Ejecuta una espera basada en el valor de espera proporcionado."""
        print(f"Ejecutando acción 'wait' por {action['wait']} segundos")
        time.sleep(action['wait'])

    def get_element_text_action(self, action):
        """Obtiene el texto de un elemento y lo almacena si es necesario."""
        print(f"Ejecutando acción 'get_element_text' en elemento {action['value']}")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((self.get_by_method(action['by']), action['value']))
            )
            text = element.text.strip()
            if 'save_as' in action:
                self.data.append({action['save_as']: text})
            print(f"{action['save_as']}: {text}")
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error en acción 'get_element_text': {e}")

    def find_elements_action(self, action):
        """Encuentra elementos y ejecuta acciones en ellos según la configuración JSON."""
        print(f"Ejecutando acción 'find_elements' en elementos con selector {action['value']}")
        try:
            # Localizar todos los elementos basados en el método y valor proporcionado
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((self.get_by_method(action['by']), action['value']))
            )

            print(f"Se encontraron {len(elements)} elementos.")

            for element in elements:
                try:
                    row = {}
                    # Ejecutar acciones para cada elemento encontrado
                    for sub_action in action['actions']:
                        if sub_action['action'] == 'click':
                            print(f"Ejecutando acción 'click' en elemento {element}")
                            element.click()
                        
                        elif sub_action['action'] == 'get_element_text':
                            print(f"Ejecutando acción 'get_element_text' en elemento {element}")
                            text_element = WebDriverWait(self.driver, 10).until(
                                EC.visibility_of(element.find_element(self.get_by_method(sub_action['by']), sub_action['value']))
                            )
                            text = text_element.text.strip()
                            if 'save_as' in sub_action:
                                row[sub_action['save_as']] = text
                            print(f"{sub_action['save_as']}: {text}")
                        
                        elif sub_action['action'] == 'store_data':
                            for key, value in sub_action['data'].items():
                                if '{' in value and '}' in value:
                                    value = value.format(**row)
                                row[key] = value
                            print(f"Datos almacenados: {row}")
                        
                        elif sub_action['action'] == 'go_back':
                            self.go_back_action()
                        
                        elif sub_action['action'] == 'scroll':
                            self.scroll_action(sub_action)
                        
                        else:
                            print(f"Acción no reconocida: {sub_action['action']}")
                    
                    # Solo añadir datos si hay información en la fila
                    if any(row.values()):
                        self.data.append(row)
                        print(f"Datos añadidos a la lista: {row}")

                    time.sleep(action.get('wait', 1))  # Espera opcional

                except Exception as e:
                    print(f"Error procesando elemento: {e}")

        except TimeoutException as e:
            print(f"Tiempo de espera agotado al buscar elementos: {e}")
        except NoSuchElementException as e:
            print(f"No se encontraron elementos: {e}")
        except Exception as e:
            print(f"Error general al buscar elementos: {e}")

    def store_data(self, action):
        """Almacena datos basados en la configuración JSON."""
        print(f"Ejecutando acción 'store_data' con datos: {action['data']}")
        try:
            data_to_store = {}
            for key, value in action['data'].items():
                if '{' in value and '}' in value:
                    value = value.format(**self.data[-1] if self.data else {})
                data_to_store[key] = value
                print(f"{key}: {value}")
            if data_to_store not in self.data:
                self.data.append(data_to_store)
            print(f"Datos almacenados: {data_to_store}")
        except Exception as e:
            print(f"Error en acción 'store_data': {e}")

    def go_back_action(self):
        """Ejecuta la acción de regresar a la página anterior."""
        print("Ejecutando acción 'go_back'")
        try:
            self.driver.back()
            time.sleep(2)
        except Exception as e:
            print(f"Error en acción 'go_back': {e}")

    def scroll_action(self, action):
        """Ejecuta la acción de desplazamiento basado en el valor proporcionado."""
        print(f"Ejecutando acción 'scroll' con valor {action['value']}")
        try:
            if action['direction'] == 'down':
                self.driver.execute_script(f"window.scrollBy(0, {action['value']});")
            elif action['direction'] == 'up':
                self.driver.execute_script(f"window.scrollBy(0, -{action['value']});")
            time.sleep(action.get('wait', 1))
        except Exception as e:
            print(f"Error en acción 'scroll': {e}")

    def find_next_page_button(self, config):
        """Encuentra el botón de la siguiente página basado en la configuración JSON."""
        try:
            next_page_selector = config['next_page_selector']
            next_page_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((self.get_by_method(next_page_selector['by']), next_page_selector['value']))
            )
            return next_page_button
        except Exception as e:
            print(f"Error encontrando el botón de la siguiente página: {e}")
            return None

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

    def guardar_datos(self, filename, columns):
        """Guarda los datos en un archivo CSV basado en la configuración JSON."""
        print(f"Guardando datos en el archivo {filename}")
        try:
            df = pd.DataFrame(self.data)
            if columns:
                df = df[columns]
            df.to_excel(filename, index=False)
            print("Datos guardados exitosamente.")
        except Exception as e:
            print(f"Error guardando datos: {e}")

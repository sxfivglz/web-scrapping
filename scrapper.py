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
        with open(json_file, 'r') as f:
            config = json.load(f)
        self.run(config)

    def run(self, config):
        try:
            start_url = config['start_url']
            self.driver.get(start_url)
            time.sleep(2)

            for action in config['actions']:
                self.execute_action(action)

            filename = config['output']['filename']
            columns = config['output'].get('columns')
            self.guardar_datos(filename, columns)

        except Exception as e:
            print(f"Error durante la ejecución del scraper: {e}")

    def execute_action(self, action):
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
            else:
                print(f"Acción no reconocida: {action['action']}")
        except Exception as e:
            print(f"Error en acción {action['action']}: {e}")

    def click_action(self, action):
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
        print(f"Ejecutando acción 'wait' por {action['wait']} segundos")
        time.sleep(action['wait'])

    def get_element_text_action(self, action):
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
        print(f"Ejecutando acción 'find_elements' en elementos {action['value']}")
        try:
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((self.get_by_method(action['by']), action['value']))
            )

            for element in elements:
                try:
                    row = {}
                    for sub_action in action['actions']:
                        if sub_action['action'] == 'click':
                            print(f"Ejecutando acción 'click' en elemento {element}")
                            element.click()
                        elif sub_action['action'] == 'get_element_text':
                            print(f"Ejecutando acción 'get_element_text' en elemento {element}")
                            text_element = WebDriverWait(self.driver, 10).until(
                                EC.visibility_of_element_located((self.get_by_method(sub_action['by']), sub_action['value']))
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
                        else:
                            print(f"Acción no reconocida: {sub_action['action']}")
                    
                    # Solo añadir si la fila no está vacía
                    if any(row.values()):
                        self.data.append(row)
                        time.sleep(action.get('wait', 1))
                except Exception as e:
                    print(f"Error procesando elemento: {e}")

        except TimeoutException as e:
            print(f"Tiempo de espera agotado al buscar elementos: {e}")
        except NoSuchElementException as e:
            print(f"No se encontraron elementos: {e}")
        except Exception as e:
            print(f"Error general al buscar elementos: {e}")

    def store_data(self, action):
        print(f"Ejecutando acción 'store_data' con datos: {action['data']}")
        try:
            data_to_store = {}
            for key, value in action['data'].items():
                if '{' in value and '}' in value:
                    value = value.format(**self.data[-1])
                data_to_store[key] = value
                print(f"{key}: {value}")
            if data_to_store not in self.data:
                self.data.append(data_to_store)
            print(f"Datos almacenados: {data_to_store}")
        except Exception as e:
            print(f"Error en acción 'store_data': {e}")

    def go_back_action(self):
        print("Ejecutando acción 'go_back'")
        try:
            self.driver.back()
            time.sleep(2)  # Espera para asegurarse de que la navegación se complete
        except Exception as e:
            print(f"Error en acción 'go_back': {e}")

    def limpiar_datos(self, data):
        cleaned_data = []
        for item in data:
            cleaned_item = {key: (value.strip() if isinstance(value, str) else value) for key, value in item.items()}
            if any(cleaned_item.values()):  # Solo añadir si hay valores no vacíos
                cleaned_data.append(cleaned_item)
        return cleaned_data

    def guardar_datos(self, filename, columns):
        print(f"Ejecutando acción 'guardar_datos' para guardar en {filename}")
        try:
            if not self.data:
                print("No hay datos para guardar.")
                return

            # Limpiar datos antes de guardar
            self.data = self.limpiar_datos(self.data)
            filtered_data = [{key: item.get(key, "") for key in columns} for item in self.data]
            if filtered_data and not all(filtered_data[0].values()):  # Si la primera fila está vacía, eliminarla
                filtered_data.pop(0)
            print(f"Datos a guardar: {filtered_data}")

            if os.path.exists(filename):
                os.remove(filename)

            df = pd.DataFrame(filtered_data, columns=columns)
            #si una fila entera es vacía, se elimina
            df = df.dropna(how='all')
            if not df.empty:
                df.to_excel(filename, index=False)
                print(f"Datos guardados exitosamente en {filename}")
        except Exception as e:
            print(f"Error en acción 'guardar_datos': {e}")

    def get_by_method(self, method):
        if method == 'ID':
            return By.ID
        elif method == 'CLASS_NAME':
            return By.CLASS_NAME
        elif method == 'CSS_SELECTOR':
            return By.CSS_SELECTOR
        elif method == 'LINK_TEXT':
            return By.LINK_TEXT
        elif method == 'XPATH':
            return By.XPATH
        else:
            raise ValueError(f"Método no soportado: {method}")

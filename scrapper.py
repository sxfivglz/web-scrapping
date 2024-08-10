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
        self.data = {}

    def run(self, config):
        """Ejecuta el scraper basado en la configuración proporcionada."""
        try:
            start_url = config['start_url']
            self.driver.get(start_url)
            time.sleep(2)

            actions = config['actions']
            for action in actions:
                self.execute_action(action)

            # Guardar los datos obtenidos en los archivos especificados
            output_configs = config.get('output_configs', [])
            self.guardar_datos(output_configs)

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
            elif action['action'] == 'select':
                self.select_action(action)
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
                section = action.get('section', 'default')
                if section not in self.data:
                    self.data[section] = []
                self.data[section].append({action['save_as']: text})
            print(f"{action['save_as']}: {text}")
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error en acción 'get_element_text': {e}")

    def select_action(self, action):
        """Ejecuta la acción de seleccionar una opción en un elemento <select>."""
        print(f"Ejecutando acción 'select' en elemento {action['value']} con valor {action['input_value']}")
        try:
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((self.get_by_method(action['by']), action['value']))
            )
            from selenium.webdriver.support.ui import Select
            select_obj = Select(select_element)
            select_obj.select_by_visible_text(action['input_value'])
            time.sleep(action.get('wait', 1))
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
            print(f"Error en acción 'select': {e}")

    def find_elements_action(self, action):
        """Encuentra elementos y ejecuta acciones en ellos según la configuración JSON."""
        print(f"Ejecutando acción 'find_elements' en elementos con selector {action['value']}")
        try:
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((self.get_by_method(action['by']), action['value']))
            )

            print(f"Se encontraron {len(elements)} elementos.")

            section = action.get('section', 'default')
            if section not in self.data:
                self.data[section] = []

            for element in elements:
                try:
                    row = {}
                    for sub_action in action['columns']:
                        if sub_action['action'] == 'get_element_text':
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
                
                    if any(row.values()):
                        self.data[section].append(row)
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
        try:
            # Validar que 'data' exista en 'action' y que sea un diccionario
            if 'data' not in action or not isinstance(action['data'], dict):
                raise ValueError("El campo 'data' es requerido y debe ser un diccionario.")

            section = action.get('section', 'default')

            # Inicializar la sección si no existe
            if section not in self.data:
                self.data[section] = []

            # Crear el diccionario para almacenar los datos
            data_to_store = {}
            for key, value in action['data'].items():
                if '{' in value and '}' in value:
                    # Validar que la última entrada de la sección tiene los datos necesarios para formatear 'value'
                    try:
                        value = value.format(**self.data.get(section, [{}])[-1])
                    except KeyError as e:
                        raise KeyError(f"Falta la clave {e} en los datos almacenados en la sección '{section}'.")
                data_to_store[key] = value

            # Agregar el diccionario al almacenamiento de datos
            self.data[section].append(data_to_store)
            print(f"Datos almacenados en la sección '{section}': {data_to_store}")

        except ValueError as ve:
            print(f"Error en 'store_data': {ve}")
        except KeyError as ke:
            print(f"Error en 'store_data': {ke}")
        except Exception as e:
            print(f"Error general en 'store_data': {e}")

    def go_back_action(self):
        """Regresa a la página anterior en el navegador."""
        print("Regresando a la página anterior")
        self.driver.back()
        time.sleep(2)  # Espera para asegurarse de que la página se haya cargado

    def scroll_action(self, action):
        """Desplaza la página según la configuración."""
        try:
            scroll_type = action.get('type', 'down')
            amount = action.get('amount', 1000)
            print(f"Ejecutando acción 'scroll' {scroll_type} por {amount} píxeles")
            if scroll_type == 'down':
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif scroll_type == 'up':
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            elif scroll_type == 'left':
                self.driver.execute_script(f"window.scrollBy(-{amount}, 0);")
            elif scroll_type == 'right':
                self.driver.execute_script(f"window.scrollBy({amount}, 0);")
            else:
                print(f"Tipo de desplazamiento no reconocido: {scroll_type}")
            time.sleep(action.get('wait', 1))
        except Exception as e:
            print(f"Error en acción 'scroll': {e}")

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

    def guardar_datos(self, output_configs):
        """Guarda los datos recopilados en archivos Excel o CSV según la configuración."""
        # Validar que output_configs sea una lista
        if not isinstance(output_configs, list):
            print("Error: 'output_configs' debe ser una lista de configuraciones.")
            return

        for output_config in output_configs:
            # Validar que cada output_config sea un diccionario
            if not isinstance(output_config, dict):
                print(f"Error: Cada 'output_config' debe ser un diccionario, se encontró: {type(output_config).__name__}")
                continue

            section = output_config.get('section', 'default')
            filename = output_config.get('filename')
            file_format = output_config.get('format', 'excel')

            if section not in self.data:
                print(f"Sección '{section}' no encontrada. Datos no guardados.")
                continue

            # Validar si la sección tiene una lista de diccionarios o un diccionario anidado
            if isinstance(self.data[section], list):
                # Si es una lista de diccionarios, guardarla en Excel o CSV
                df = pd.DataFrame(self.data[section])
                if file_format == 'excel':
                    df.to_excel(f"{filename}.xlsx", index=False)
                elif file_format == 'csv':
                    df.to_csv(f"{filename}.csv", index=False)
                print(f"Datos guardados en '{filename}.{file_format}'")

            elif isinstance(self.data[section], dict):
                # Si es un diccionario anidado, se guarda cada subnivel en diferentes hojas de Excel
                with pd.ExcelWriter(f"{filename}.xlsx") as writer:
                    for key, value in self.data[section].items():
                        df = pd.DataFrame(value)
                        df.to_excel(writer, sheet_name=key, index=False)
                print(f"Datos guardados en '{filename}.xlsx' en hojas separadas por cada clave de '{section}'.")

            else:
                print(f"Formato de datos en la sección '{section}' no soportado para guardar.")


###########EL MERO BUENO############
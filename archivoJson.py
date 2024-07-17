import json

class archivoJson:
    def __init__(self,filename = ''):
        self.filename = filename
        
    def obtenerDatosJson(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data=json.load(file)
                return data
        except:
            return f"ocurrio un error al cargar el archivo"
        
    def convertirJson(self, data):
        try:
            with open(self.filename, 'w', encoding='utf-8') as data_json:
                json.dump(data, data_json, ensure_ascii=False, indent=4)
        except Exception as e:
            return f"Ocurrió un error al convertir a JSON: {e}"
        
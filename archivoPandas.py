import pandas as pd

class Pandas:
    
    def __init__(self,data):
        self.data = data
        
    def _normalize_data(self):
        if isinstance(self.data, dict) and 'data' in self.data:
            data_list = self.data['data']
            if isinstance(data_list, list):
                if all(isinstance(item, dict) for item in data_list):
                    return pd.json_normalize(data_list)
                elif all(isinstance(item, list) for item in data_list):
                    headers = data_list[0]
                    data = data_list[1:]
                    max_columns = len(headers)
                    adjusted_data = [row[:max_columns] for row in data]
                    return pd.DataFrame(adjusted_data, columns=headers)
                
        return pd.DataFrame()

    def to_excel(self, file_path):
        df = self._normalize_data()
        df.to_excel(file_path, index=False)
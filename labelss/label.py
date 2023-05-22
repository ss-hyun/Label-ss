import json
import xmltodict
import warnings
import re
from pathlib import Path
from .utils import verify_path


def get_real_data(str):
    try:
        try:
            return int(str)
        except ValueError:
            return float(str)
    except ValueError:
        if str.lower() == 'true': return True
        if str.lower() == 'false': return False
        if str.lower() == 'none': return None
        if str.lower() == 'null': return None
        return str


class Label():    
    def __init__(self, label_path, data_path, meta=False, label=None):
        verify_path(label_path.parent)
        verify_path(data_path.parent if data_path.is_file() else data_path)
        self.label_path = label_path
        self.data_path = data_path
        self.meta = meta
        self.label = label
        
        # # Change an existing label with a new label format
        # if isinstance(label, Label):
        #     self.label_path, self.label = self.convert()
        # Get a new label from a file
        if label is None:
            if not label_path.exists():
                raise LabelError(f"Invalid label file path: {label_path}") 
            
            self.label = self.parse(self.get_raw())

    def get_raw(self):
        raise LabelFunctionError("Funtion <get_raw> is not defined.")
        
    def verify(self):
        raise LabelFunctionError("Funtion <verify> is not defined.")
    
    def save(self):
        raise LabelFunctionError("Funtion <save> is not defined.")
    
    def convert(self):
        raise LabelFunctionError("Funtion <convert> is not defined.")
    
    def print(self, print_data=True):
        print(f"Label Path: {self.label_path}")
        print(f"Data Path: {self.data_path}")
        print(f"Meta Data Flag: {self.meta}")
        if print_data:
            print("Label Data:")
            print(json.dumps(self.label, indent='\t'))
    
    def extract_label_list(self, location = [], name_loc = ['name'], label_path = ""):
        if not self.meta:
            raise LabelError("This label is not meta label. It is impossible to extract label list.")
        
        labels = self.label
        for loc in location:
            labels = labels[loc]
        
        if not label_path:
            label_path = self.data_path
        
        result = []
        for label in labels:
            name = label
            for loc in name_loc:
                name = name[loc]
            
            result.append(
                JSON(
                    label_path=Path(re.sub('(.jpg)|(.png)', '.json', str(label_path/name))),
                    data_path=(label_path/name),
                    label=label
                )   
            )
        
        return result
        
    def parse(self, raw_data):
        if isinstance(raw_data, dict):
            result = {}
            for key, value in raw_data.items():
                result[key] = self.parse(value)
            return result
        if isinstance(raw_data, list):
            result = []
            for value in raw_data:
                result.append(self.parse(value))
            return result
        if isinstance(raw_data, str):
            return get_real_data(raw_data)
        if isinstance(raw_data, (int, float, bool)) or raw_data is None:
            return raw_data
        
        raise LabelError(f"Invalid label data. {raw_data}")


class LabelError(Exception):
    pass


class LabelFunctionError(LabelError):
    pass


class XML(Label):
    
    def get_raw(self):
        with self.label_path.open('r') as f:
            return xmltodict.parse(f.read())        

    def verify(self):
        warnings.warn("There is no label reliability verification system.")
    
    def save(self):
        self.verify()
        with open(str(self.label_path).replace('.xml', '.json'), 'w') as f:
            json.dump(self.label, f, indent='\t')
  
    
class JSON(Label):
        
    def get_raw(self):
        with open(self.label_path, 'r') as f:
            return json.load(f)

    def verify(self):
        warnings.warn("There is no label reliability verification system.")
    
    def save(self):
        self.verify()
        if self.label_path.exists() and self.meta:
            self.label_path.rename(self.label_path/".origin")
        with self.label_path.open('w') as f:
            json.dump(self.label, f, indent='\t')

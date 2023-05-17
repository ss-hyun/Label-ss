import os
import json
import xmltodict
import warnings


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
    def __init__(self, path):
        if not os.path.isfile(path):
            raise LabelError("Invalid label file path.") 
        
        self.path = path
        self.label = self.parse(self.get_raw())

    def get_raw(self):
        raise LabelFunctionError("Funtion <get_raw> required!")
        
    def verify(self):
        raise LabelFunctionError("Funtion <verify> required!")
    
    def save(self):
        raise LabelFunctionError("Funtion <save> required!")
        
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
        if raw_data is None:
            return raw_data
        
        raise LabelError("Invalid label data.")


class LabelError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class LabelFunctionError(LabelError):
    def __init__(self, msg):
        super().__init__(msg)


class XML(Label):
    
    def get_raw(self):
        with open(self.path, 'r') as f:
            return xmltodict.parse(f.read())        

    def verify(self):
        warnings.warn("There is no label reliability verification system.")
    
    def save(self):
        self.verify()
        with open(self.path.replace('.xml', '.json'), 'w') as f:
            json.dump(self.label, f, indent='\t')
  
    
class JSON(Label):
        
    def get_raw(self):
        with open(self.path, 'r') as f:
            return json.load(f)

    def verify(self):
        warnings.warn("There is no label reliability verification system.")
    
    def save(self):
        self.verify()
        os.rename(self.path, self.path + ".origin")
        with open(self.path, 'w') as f:
            json.dump(self.label, f, indent='\t')
    

class MyLabel(XML):
    
    def __init__(self, path):
        super().__init__(path)
        # self.image_dir = os.path.join("..", self.label['annotations']['meta']['task']['name'])
        self.image_dir = os.path.join(os.path.dirname(path), '..', self.label['annotations']['meta']['task']['name'])
    
    def verify(self):
        removable = []
        for idx, image in enumerate(self.label['annotations']['image']):
            # Image path check
            if not os.path.isdir(self.image_dir):
                raise LabelError(f"Image directory '{self.image_dir}' not exists.")
            if not os.path.isfile(os.path.join(self.image_dir, image['@name'])):
                # Check for invalid image extensions
                if not os.path.isfile(os.path.join(self.image_dir, image['@name'].replace('.png', '.jpg'))):
                    warnings.warn(f"File '{image['@name']}' not exists. File data is removed from the label.")
                    removable.append(image)
                else:
                    # Image extension is different from the known extension
                    self.label['annotations']['image'][idx]['@name'] = image['@name'].replace('.png', '.jpg')
        
            # Label check
            for box in image['box']:
                if box['@label'] not in [l['name'] for l in self.label['annotations']['meta']['task']['labels']['label']]:
                    raise LabelError(f"Invalid label name '{box['@label']}'")
        
        for image in removable:
            self.label['annotations']['image'].remove(image)
        
        # Meta data check
        if self.label['annotations']['meta']['task']['size'] != len(self.label['annotations']['image']):
            warnings.warn(f"Invalid label size 'meta data info: {self.label['annotations']['meta']['task']['size']}', 'real images len: {len(self.label['annotations']['image'])}'")
            self.label['annotations']['meta']['task']['size'] = len(self.label['annotations']['image'])
    

if __name__ == "__main__":
    
    file_name = "test/meta-labels/Suwon_CH01_20200720_1700_MON_9m_NH_highway_TW5_sunny_FHD.xml"
        
    MyLabel(file_name).save()

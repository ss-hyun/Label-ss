import os
import xmltodict
from pathlib import Path
from .label import XML, LabelError
from .labelme import LabelMe
from .yolov8 import CarYolov8Label
from .utils import pixel2ratio, xyxy2xywh


class AIhubCCTV(XML):
    
    def __init__(self, working_dir, label_path):
        os.chdir(working_dir)
        super(XML, self).__init__(label_path, (label_path.parent.parent/label_path.name.replace('.xml', '')), meta=True)
        self.verify()
        self.img_labels = self.extract_label_list(location=['annotations', 'image'], name_loc=['@name'])
    
    
    def verify(self):
        removable = []
        for idx, image in enumerate(self.label['annotations']['image']):
            # Image path check
            if not self.data_path.exists():
                raise LabelError(f"Image directory '{self.data_path}' not exists.")
            if not (self.data_path/image['@name']).exists():
                # Check for invalid image extensions
                if not (self.data_path/image['@name'].replace('.png', '.jpg')).exists():
                    self.warn(f"File '{image['@name']}' not exists. File data is removed from the label.")
                    removable.append(image)
                else:
                    # Image extension is different from the known extension
                    self.label['annotations']['image'][idx]['@name'] = image['@name'].replace('.png', '.jpg')
        
            # Label check
            if not isinstance(image['box'], list):
                self.label['annotations']['image'][idx]['box'] = image['box'] = [image['box']]
            for box in image['box']:
                if box['@label'] not in [l['name'] for l in self.label['annotations']['meta']['task']['labels']['label']]:
                    raise LabelError(f"Invalid label name '{box['@label']}'")
        
        for image in removable:
            self.label['annotations']['image'].remove(image)
        
        # Meta data check
        if self.label['annotations']['meta']['task']['size'] != len(self.label['annotations']['image']):
            self.warn(f"Invalid label size 'meta data info: {self.label['annotations']['meta']['task']['size']}', 'real images len: {len(self.label['annotations']['image'])}'")
            self.label['annotations']['meta']['task']['size'] = len(self.label['annotations']['image'])


    def save_labelme(self):
        for img_label in self.img_labels:
            label = {
                "version" : "5.1.1",
                "flags" : {},
                "imagePath" : img_label.label['@name'],
                "imageData" : None,
                "imageHeight" : img_label.label['@height'],
                "imageWidth" : img_label.label['@width'],
                "shapes" : []
            }
            
            for box in img_label.label['box']:
                label['shapes'].append(
                    {
                        "label" : box['@label'],
                        "points" : [[box['@xtl'], box['@ytl']], [box['@xbr'], box['@ybr']]],
                        "group_id" : None,
                        "shape_type" : "rectangle",
                        "flags" : {}
                    }
                )
            
            LabelMe(label_path=img_label.label_path
                    , data_path=img_label.data_path
                    , label=label).save()    
    
    def save_yolov8(self, path_save_flag='w'):
        for img_label in self.img_labels:
            label = []
            
            for box in img_label.label['box']:
                label.append(
                    [   
                        str(CarYolov8Label.cls[box['@label']])
                        , *pixel2ratio(
                            *xyxy2xywh(
                                box['@xtl'], box['@ytl'], box['@xbr'], box['@ybr']
                            )
                            , img_label.label['@width']
                            , img_label.label['@height']
                        )
                    ]
                )
            
            CarYolov8Label(label_path=Path(img_label.label_path.as_posix().replace('images', 'labels').replace('.json', '.txt'))
                    , data_path=img_label.data_path
                    , label=label).save() 
        

class AIhubCrossRoad(XML):
    
    def __init__(self, working_dir, label_path):
        os.chdir(working_dir)
        super(XML, self).__init__(label_path, Path(str(label_path.absolute()).replace('labels','images').replace('.xml', '')), meta=True)
        self.verify()
        self.img_labels = self.extract_label_list(location=['annotations', 'image'], name_loc=['@name'])
        
    def get_raw(self):
        with self.label_path.open('r', encoding='UTF-8') as f:
            return xmltodict.parse(f.read())     
    
    def verify(self):
        removable = []

        if not isinstance(self.label['annotations']['image'], list):
            self.label['annotations']['image'] = [self.label['annotations']['image']]
        for idx, image in enumerate(self.label['annotations']['image']):
            if not (self.data_path/image['@name']).exists():
                # Check for invalid image extensions
                if not (self.data_path/image['@name'].replace('.jpg', '.png')).exists():
                    self.warn(f"File '{image['@name']}' not exists. File data is removed from the label.")
                    removable.append(image)
                else:
                    # Image extension is different from the known extension
                    self.label['annotations']['image'][idx]['@name'] = image['@name'].replace('.jpg', '.png')
        
            # Label check
            if 'box' not in image:
                image_path = self.data_path/image['@name']
                self.warn(f"Image doesn't have box : {image_path}")
                if image_path.exists():
                    labelme = LabelMe(label_path=Path(str(image_path).replace('.jpg', '.json'))
                            , data_path=image_path, label=self.labelme_label(image))
                    os.renames(image_path, str(image_path).replace('images', 'invalid'))
                    labelme.save()
                    os.renames(labelme.label_path, str(labelme.label_path).replace('images', 'invalid'))
                removable.append(image)
                continue
            
            if not isinstance(image['box'], list):
                self.label['annotations']['image'][idx]['box'] = image['box'] = [image['box']]
            for box in image['box']:
                if box['@label'] not in [l['name'] for l in self.label['annotations']['meta']['task']['labels']['label']]:
                    raise LabelError(f"Invalid label name '{box['@label']}'")
        
        for image in removable:
            self.label['annotations']['image'].remove(image)
        
        # Meta data check
        if self.label['annotations']['meta']['task']['size'] != len(self.label['annotations']['image']):
            self.warn(f"Invalid label size 'meta data info: {self.label['annotations']['meta']['task']['size']}', 'real images len: {len(self.label['annotations']['image'])}'")
            self.label['annotations']['meta']['task']['size'] = len(self.label['annotations']['image'])

    def labelme_label(self, raw_label):
        label = {
            "version" : "5.1.1",
            "flags" : {},
            "imagePath" : raw_label['@name'],
            "imageData" : None,
            "imageHeight" : raw_label['@height'],
            "imageWidth" : raw_label['@width'],
            "shapes" : []
        }
        
        if 'box' in raw_label:
            for box in raw_label['box']:
                label['shapes'].append(
                    {
                        "label" : box['@label'],
                        "points" : [[box['@xtl'], box['@ytl']], [box['@xbr'], box['@ybr']]],
                        "group_id" : None,
                        "shape_type" : "rectangle",
                        "flags" : {}
                    }
                )
        
        return label 

    def save_labelme(self):
        for img_label in self.img_labels:
            LabelMe(label_path=img_label.label_path
                    , data_path=img_label.data_path
                    , label=self.labelme_label(img_label.label)).save()    
    
    def save_yolov8(self):
        for img_label in self.img_labels:
            label = []
            
            for box in img_label.label['box']:
                if self.mig_class(box['@label']):
                    label.append(
                        [   
                            self.mig_class(box['@label'])
                            , *pixel2ratio(
                                *xyxy2xywh(
                                    box['@xtl'], box['@ytl'], box['@xbr'], box['@ybr']
                                )
                                , img_label.label['@width']
                                , img_label.label['@height']
                            )
                        ]
                    )
            
            if label:
                CarYolov8Label(label_path=Path(img_label.label_path.as_posix().replace('images', 'labels').replace('.json', '.txt'))
                        , data_path=img_label.data_path
                        , label=label).save() 
            else:
                os.renames(img_label.label_path, str(img_label.label_path).replace('images', 'invalid'))
                os.renames(img_label.data_path, str(img_label.data_path).replace('images', 'invalid'))
                self.warn(f"All classes are invalid: {img_label.label_path}")
                
                
    def mig_class(self, cls):
        if 'car' in cls: return str(CarYolov8Label.cls['car'])
        elif 'bus' in cls: return str(CarYolov8Label.cls['bus'])
        elif 'truck' in cls: return str(CarYolov8Label.cls['truck'])
        return None
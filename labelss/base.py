import os
import warnings
from pathlib import Path
from .label import XML, JSON, LabelError
from .labelme import LabelMe
from .yolov8 import Yolov8Label
from .utils import pixel2ratio, xyxy2xywh


class MyLabel(XML):
    
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
                    warnings.warn(f"File '{image['@name']}' not exists. File data is removed from the label.")
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
            warnings.warn(f"Invalid label size 'meta data info: {self.label['annotations']['meta']['task']['size']}', 'real images len: {len(self.label['annotations']['image'])}'")
            self.label['annotations']['meta']['task']['size'] = len(self.label['annotations']['image'])

        
        # self.label['annotations']['meta']['task']['name'] : label name이 잘 기록되었는지 확인

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
        img_path_info = []
        label_path_info = []
        for img_label in self.img_labels:
            label = []
            
            for box in img_label.label['box']:
                label.append(
                    [   
                        str(Yolov8Label.cls[box['@label']])
                        , *pixel2ratio(
                            *xyxy2xywh(
                                box['@xtl'], box['@ytl'], box['@xbr'], box['@ybr']
                            )
                            , img_label.label['@width']
                            , img_label.label['@height']
                        )
                    ]
                )
            
            img_path_info.append(img_label.data_path.as_posix())
            label_path_info.append(img_label.label_path.as_posix().replace('images', 'labels').replace('.json', '.txt'))
            
            Yolov8Label(label_path=Path(label_path_info[-1])
                    , data_path=img_label.data_path
                    , label=label).save() 
        
        with (self.data_path.parent/"path_info.txt").open(path_save_flag) as f:
            f.write('\n'.join(img_path_info))
            # print("Images path_info.txt saved.")  
        
        with open(str(self.data_path.parent/"path_info.txt").replace('images', 'labels'), path_save_flag) as f:
            f.write('\n'.join(label_path_info))
            # print("Labels path_info.txt saved.")  

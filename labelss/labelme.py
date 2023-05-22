from .formatted import FormattedLabel

class LabelMe(FormattedLabel):
    
    def __init__(self, label_path='', data_path='', label=None):
        self.label_format = {
            "version" : "5.1.1",
            "flags" : {},
            "shapes" : [
                {
                    "label" : "",
                    "points" : [[0.0,0.0],[0.0,0.0]],
                    "group_id" : None,
                    "shape_type" : "rectangle",
                    "flags" : {}
                }
            ],
            "imagePath" : "",
            "imageData" : None,
            "imageHeight" : 0,
            "imageWidth" : 0
        }
        super(FormattedLabel, self).__init__(label_path, data_path, label=label)

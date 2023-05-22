from .label import JSON, LabelError


def compare_format(standard, label):
    if isinstance(standard, dict):
        for key, value in standard.items():
            compare_format(value, label[key])
    if isinstance(standard, list):
        for value in label:
            compare_format(standard[0], value)
    if not isinstance(standard, type(label)):
        raise LabelError(f"Invalid label format: {standard}/{label}")


class FormattedLabel(JSON):
    def __init__(self, label_path='', data_path='', label=None):
        if not (label_path or label):
            raise LabelError(f"Invalid label format. 'label_path' or 'label' must be set.")
        
        super(JSON, self).__init__(label_path, data_path, label=label)
        self.verify()
    
    def verify(self):
        try:
            if not self.label_format:
                raise LabelError("Invalid label format. 'label_format' is not empty.")
        except AttributeError:
            raise LabelError("Invalid label format. Class that inherits FormatedLabel has 'label_format' attribute.")
        
        if not isinstance(self.label_format, dict) and not isinstance(self.label_format, list):
            raise LabelError(f"Invalid label format. Label format must be iteratorable.")
        
        compare_format(self.label_format, self.label)
        
       
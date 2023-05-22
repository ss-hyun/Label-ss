import os
from pathlib import Path
from labelss import MyLabel

working_dir = Path(f"d:{os.sep}datasets{os.sep}cctv-AI-hub{os.sep}1_Gyeonggi{os.sep}")
file_name = Path(f"images{os.sep}valid{os.sep}meta-labels{os.sep}Suwon_CH01_20200720_1830_MON_9m_RH_highway_TW5_sunny_FHD.xml")

label = MyLabel(working_dir, file_name)
label.save()
label.save_labelme()
label.save_yolov8()

print(label.img_labels[0].label_path)
print(label.img_labels[0].data_path)
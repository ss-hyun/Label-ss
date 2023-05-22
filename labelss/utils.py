from pathlib import Path

def xyxy2xywh(x1, y1, x2, y2):
    w = x2 - x1
    h = y2 - y1
    x = x1 + (w / 2)
    y = y1 + (h / 2)
    return x, y, w, h


def pixel2ratio(x, y, w, h, img_w, img_h):
    return str(x/img_w), str(y/img_h), str(w/img_w), str(h/img_h)


def verify_path(path):
    if not path.exists():
        verify_path(path.parent)
        path.mkdir()
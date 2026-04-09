import cv2
import numpy as np

def resize_with_padding(img, size=512):
    h, w = img.shape[:2]
    
    scale = min(size / w, size / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    resized = cv2.resize(img, (new_w, new_h))
    canvas = np.zeros((size, size, 3), dtype=np.uint8)
    
    x_offset = (size - new_w) // 2
    y_offset = (size - new_h) // 2
    
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return canvas

def sharpen(img):
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    return cv2.filter2D(img, -1, kernel)

def unshape_mask(img):
    blur = cv2.GaussianBlur(img, (9, 9), 10)
    return cv2.addWeighted(img, 1.5, blur, -0.5, 0)

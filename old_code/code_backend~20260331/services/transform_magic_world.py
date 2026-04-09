import cv2
import numpy as np

from services.transform_world.preprocessing import resize_with_padding, sharpen

def transform_magic_world(img):
    # 前処理
    # TODO: aspect ratioを維持したresizeに変更する（Phase2）
    img = resize_with_padding(img, 512)
    # img = cv2.resize(img, (512, 512))
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    # カラーフィルタ
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 紫寄りにシフト
    hsv[..., 0] = (hsv[..., 0] + 30) % 180
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.2, 0, 255)
    hsv[..., 2] = np.clip(hsv[..., 2] * 1.1, 0, 255)
    
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return result

def add_edges(img):
    edges = cv2.Canny(img, 100, 200)
    
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
    return cv2.addWeighted(img, 1.0, edges_colored, 0.3, 0)

def apply_effect(base):
    particles = create_particles(base.shape)
    result = cv2.addWeighted(base, 0.9, particles, 0.3, 0)
    return result

def create_particles(shape, num_particles=200):
    h, w = shape[:2]
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    for  _ in range(num_particles):
        x = np.random.randint(0, w)
        y = np.random.randint(0, h)
        radius = np.random.randint(2, 6)
        color = (
            np.random.randint(200, 255),
            np.random.randint(150, 255),
            np.random.randint(200, 255)
        )
        
        cv2.circle(canvas, (x, y), radius, color, -1)
    canvas = cv2.GaussianBlur(canvas, (9, 9), 0)
    return canvas

def process(img):
    img = transform_magic_world(img)
    base = sharpen(img)
    base = add_edges(base)
    result = apply_effect(base)
    return result


if __name__ == '__main__':
    file_path = '/mnt/d/Itsuki/Pictures/アルバムジャケット/adamas.jpg'
    with open(file_path, mode='rb') as f:
        pic_data = f.read()
    pic_data = np.asarray(bytearray(pic_data), dtype=np.uint8)
    img = cv2.imdecode(pic_data, -1)
    img = process(img)
    file_path = '/mnt/d/Itsuki/Pictures/tmp/test.png'
    cv2.imwrite(file_path, img)
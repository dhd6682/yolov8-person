import os
import cv2
import time
import json
import pymysql
from ultralytics import YOLO
import torch

# DB 설정
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "yolouser"),
    "password": os.getenv("DB_PASSWORD", "yolopass"),
    "database": os.getenv("DB_NAME", "yolov8db"),
    "charset": "utf8mb4"
}

# DB 연결
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# file_results 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS file_results (
    file_number INT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    result VARCHAR(255)
);
""")

# bbox_results 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS bbox_results (
    file_number INT,
    person_index INT,
    class_name VARCHAR(50),
    bbox TEXT,
    PRIMARY KEY (file_number, person_index),
    FOREIGN KEY (file_number) REFERENCES file_results(file_number) ON DELETE CASCADE
);
""")
conn.commit()

# 모델 설정
MODEL_PATH = "best.pt"
CONFIDENCE_THRESHOLD = 0.6
NMS_THRESHOLD = 0.2
IMAGE_DIR = "test_images"
RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)

# GPU
if torch.cuda.is_available():
    model.to("cuda")
    print("[INFO] Using device: cuda")
else:
    print("[INFO] Using device: cpu")


image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('jpg', 'png', 'jpeg'))]

for idx, image_name in enumerate(image_files, start=1):
    image_path = os.path.join(IMAGE_DIR, image_name)
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"[WARN] Can't load image: {image_name}")
        continue

    print(f"[INFO] Processing: {image_name}")
    start = time.time()
    results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, iou=NMS_THRESHOLD, verbose=False)[0]
    end = time.time()
    print(f"[INFO] Inference time: {end - start:.2f}s")

    # 사람 클래스만 필터링 + 왼쪽부터 정렬
    person_boxes = sorted(
        [box for box in results.boxes if int(box.cls[0]) == 0],
        key=lambda b: b.xyxy[0][0]  # x 좌표 기준
    )

    # result: '1,2,3' 형태로 저장
    person_numbers = [str(i + 1) for i in range(len(person_boxes))]
    result_str = ",".join(person_numbers)

    # file_results 저장
    cursor.execute(
        "INSERT INTO file_results (file_number, file_name, result) VALUES (%s, %s, %s)",
        (idx, image_name, result_str)
    )
    conn.commit()

    # bbox_results 저장
    for i, box in enumerate(person_boxes):
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        w = x2 - x1
        h = y2 - y1
        bbox = json.dumps([int(x1), int(y1), int(w), int(h)])
        class_name = model.names[int(box.cls[0])]


        cursor.execute(
            "INSERT INTO bbox_results (file_number, person_index, class_name, bbox) VALUES (%s, %s, %s, %s)",
            (idx, i + 1, class_name, bbox)
        )
    conn.commit()

    # 결과 이미지 저장
    save_path = os.path.join(RESULT_DIR, image_name)
    annotated_frame = results.plot()
    cv2.imwrite(save_path, annotated_frame)
    print(f"[INFO] Saved result to: {save_path}")

print("[INFO] 모든 이미지 처리 및 DB 저장 완료!")
cursor.close()
conn.close()

print("[INFO] Sleeping to keep container alive for GPU check...")
time.sleep(999)

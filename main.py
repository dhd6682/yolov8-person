from ultralytics import YOLO
import os
import sys
import cv2
import time
import torch

MODEL_PATH = "best.pt"
CONFIDENCE_THRESHOLD = 0.65
NMS_THRESHOLD = 0.2
IMAGE_DIR = "test_images"  # 여기에 테스트 이미지 넣어두세요 (예: 4~5장)

# 디바이스 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {device}")

# 모델 파일 확인
if not os.path.exists(MODEL_PATH):
    print(f"[ERROR] 모델 파일 '{MODEL_PATH}'이 없습니다.")
    sys.exit(1)

# 모델 로드
model = YOLO(MODEL_PATH)

# 이미지 리스트 로드
image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
if not image_files:
    print(f"[ERROR] '{IMAGE_DIR}' 폴더에 이미지가 없습니다.")
    sys.exit(1)

# 이미지별 추론
for image_name in image_files:
    image_path = os.path.join(IMAGE_DIR, image_name)
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"[WARN] 이미지를 불러올 수 없습니다: {image_path}")
        continue

    print(f"\n[INFO] Processing: {image_name}")

    start = time.time()
    results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, iou=NMS_THRESHOLD, verbose=False, device=device)[0]
    end = time.time()
    print(f"[INFO] Inference time: {end - start:.3f} seconds")

    # 사람 클래스만 필터링
    filtered_boxes = []
    for box in results.boxes:
        if int(box.cls[0]) == 0:
            filtered_boxes.append(box)

    # 박스 그리기
    annotated_frame = frame.copy()
    for box in filtered_boxes:
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        conf = box.conf.item()
        label = f"{model.names[int(box.cls[0])]}: {conf:.2f}"

        cv2.rectangle(annotated_frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
        cv2.putText(annotated_frame, label, (xyxy[0], xyxy[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 결과 저장
    save_path = os.path.join("results", image_name)
    os.makedirs("results", exist_ok=True)
    cv2.imwrite(save_path, annotated_frame)
    print(f"[INFO] Saved result to: {save_path}")

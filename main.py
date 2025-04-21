from ultralytics import YOLO
import os
import sys
import cv2

MODEL_PATH = "best.pt"
CONFIDENCE_THRESHOLD = 0.8  # conf_thresh
NMS_THRESHOLD = 0.2         # iou_thresh = NMS threshold

# 모델 파일 확인
if not os.path.exists(MODEL_PATH):
    print(f"[ERROR] 모델 파일 '{MODEL_PATH}'이 없습니다.")
    sys.exit(1)

# 모델 로드
model = YOLO(MODEL_PATH)

# 웹캠 열기
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 추론 실행 (conf, iou 지정)
    results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, iou=NMS_THRESHOLD, verbose=False)[0]

    # 사람 클래스만 필터링
    filtered_boxes = []
    for box in results.boxes:
        if int(box.cls[0]) == 0:  # class 0 = person
            filtered_boxes.append(box)

    # 박스 그리기
    annotated_frame = frame.copy()
    for box in filtered_boxes:
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        conf = box.conf.item()
        label = f"{model.names[int(box.cls[0])]}: {conf:.2f}"

        cv2.rectangle(annotated_frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
        cv2.putText(annotated_frame, label, (xyxy[0], xyxy[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("YOLOv8 Person Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

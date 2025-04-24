import os
import json
import pymysql
import cv2

# DB 설정
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "yolouser"),
    "password": os.getenv("DB_PASSWORD", "yolopass"),
    "database": os.getenv("DB_NAME", "yolov8db"),
    "charset": "utf8mb4"
}

IMAGE_DIR = "test_images" 

def draw_boxes(file_number: int):
    # DB 연결
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. 이미지 파일가져오기
    cursor.execute("SELECT file_name FROM file_results WHERE file_number = %s", (file_number,))
    result = cursor.fetchone()
    if not result:
        print(f"[ERROR] file_number={file_number} not found in DB.")
        return

    file_name = result[0]
    image_path = os.path.join(IMAGE_DIR, file_name)

    # 2. 이미지 불러오기
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Failed to load image: {image_path}")
        return

    # 3. bbox 가져오기
    cursor.execute("""
        SELECT person_index, class_name, bbox FROM bbox_results
        WHERE file_number = %s
    """, (file_number,))
    boxes = cursor.fetchall()

    for person_index, class_name, bbox_json in boxes:
        x, y, w, h = json.loads(bbox_json)
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        label = f"{class_name} {person_index}"

        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 4. 화면에 출력
    save_dir = "drawn_results"
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, file_name)
    cv2.imwrite(save_path, image)
    print(f"[INFO] Saved: {save_path}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    # DB 연결
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 모든 file_number 가져오기
    cursor.execute("SELECT file_number FROM file_results")
    file_numbers = cursor.fetchall()

    # 하나씩 반복하며 draw_boxes 실행
    for (file_number,) in file_numbers:
        print(f"[INFO] Drawing boxes for file_number: {file_number}")
        draw_boxes(file_number)

    cursor.close()
    conn.close()


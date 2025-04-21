# yolov8-person-detector

이미지 빌드 후
docker build -t yolov8-person-detector .

실행
docker run --rm -v $(pwd)/test_images:/app/test_images -v $(pwd)/results:/app/results yolov8-person-detector


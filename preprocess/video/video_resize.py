import cv2
import os
project_folder_path = os.path.abspath('../..')
current_path = os.path.abspath('.')
video_path = os.path.join(project_folder_path,'./video/시연 영상 편집본/')
output_path = os.path.join(project_folder_path, './video/리사이즈된 영상/')
os.makedirs(output_path, exist_ok=True)

video_list = os.listdir(video_path)
for video in video_list:
    input_video_path = os.path.join(video_path, video)
    output_video_path = os.path.join(output_path, video)

    cap = cv2.VideoCapture(input_video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    target_width = width
    target_height = int(height * 16/9) # 1920*1080 or 640*360 → 1920*1920 or 640*640 / 1 : 1 비율
    # target_height = int(height * 9/16) # 1920*1920 or 640*640 → 1920*1080 or 640*360 / 16 : 9 비율/
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (target_width, target_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 영상 리사이즈
        resized_frame = cv2.resize(frame, (target_width, target_height))

        out.write(resized_frame)

    cap.release()
    out.release()
print("작업 완료")

import os
import sys
import argparse
import math
import cv2
import numpy as np
from PIL import Image

def generate_video_grid(video_path, interval_seconds, target_frame_width, grid_cols, output_image_path):
    """
    從影片中抽取指定秒數間隔的影格，在每張影格上繪製時間戳記，
    並將它們拼接成一張單一的「時間拼圖」(Grid/Storyboard Image)。
    """
    if not os.path.exists(video_path):
        print(f"錯誤: 找不到影片檔案 {video_path}")
        sys.exit(1)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if fps <= 0:
        print("錯誤: 無法讀取影片的 FPS 資訊。")
        sys.exit(1)

    duration = total_frames / fps
    print(f"影片時長: {duration:.2f} 秒, FPS: {fps:.2f}")

    frame_step = max(1, int(fps * interval_seconds))
    current_frame_idx = 0
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame_idx % frame_step == 0:
            timestamp_sec = current_frame_idx / fps
            mins = int(timestamp_sec // 60)
            secs = int(timestamp_sec % 60)
            time_str = f"{mins:02d}:{secs:02d}"

            # 等比例縮放單張影格
            h, w = frame.shape[:2]
            scale = target_frame_width / w
            new_h = int(h * scale)
            resized = cv2.resize(frame, (target_frame_width, new_h))

            # 在影格右上角繪製半透明黑色背景與白色時間戳記
            text_size = cv2.getTextSize(time_str, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            bg_x1 = resized.shape[1] - text_size[0] - 15
            bg_y1 = 5
            bg_x2 = resized.shape[1] - 5
            bg_y2 = text_size[1] + 15

            # 繪製背景矩形
            cv2.rectangle(resized, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
            # 寫入時間戳記文字
            cv2.putText(resized, time_str, (bg_x1 + 5, bg_y2 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            frames.append(resized)
            
        current_frame_idx += 1

    cap.release()
    
    total_extracted = len(frames)
    print(f"共抽取出 {total_extracted} 張帶有時間戳記的影格。")
    if total_extracted == 0:
        print("沒有抽取出任何影格，請檢查間隔設定。")
        sys.exit(1)

    # 計算拼圖網格的列數與行數
    cols = grid_cols
    rows = int(math.ceil(total_extracted / cols))
    
    single_h, single_w = frames[0].shape[:2]
    
    # 建立一個全黑的底圖用來拼貼
    grid_img = np.zeros((rows * single_h, cols * single_w, 3), dtype=np.uint8)

    for idx, img in enumerate(frames):
        r = idx // cols
        c = idx % cols
        y1 = r * single_h
        y2 = y1 + single_h
        x1 = c * single_w
        x2 = x1 + single_w
        grid_img[y1:y2, x1:x2] = img

    # 轉為 RGB 並用 Pillow 儲存
    grid_img_rgb = cv2.cvtColor(grid_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(grid_img_rgb)
    pil_img.save(output_image_path)
    
    print(f"成功產生時間拼圖！")
    print(f"拼圖規格: {cols} 列 x {rows} 行")
    print(f"輸出解析度: {grid_img.shape[1]}x{grid_img.shape[0]}")
    print(f"儲存路徑: {output_image_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="影片影格時間拼圖產生器")
    parser.add_argument("--video", type=str, default="/Users/force/Downloads/FDownloader.Net_AQPxgAvkg8kYO7vk_0A6TNjymU8NGZOO6Ck4HIXhO6ZmuSxixwhdtB_VM5WAcKYu-OkoL4FmF2UpT6s2gOIlZHjUvZ21q5Rpxls79Ov.mp4", help="影片檔案路徑")
    parser.add_argument("--interval", type=float, default=6.0, help="抽樣間隔秒數 (例如 6.0 代表每 6 秒抽一張，對 90 秒影片會抽 15 張，剛好可以排成 4x4 網格)")
    parser.add_argument("--width", type=int, default=320, help="單張影格縮小後的寬度 (預設: 320px，拼圖後總解析度適中)")
    parser.add_argument("--cols", type=int, default=4, help="拼圖網格每列放幾張圖 (預設: 4 列)")
    parser.add_argument("--output", type=str, default="/Users/force/Google_Antigravity/video-analyze/time_grid.jpg", help="輸出圖片路徑")

    args = parser.parse_args()
    generate_video_grid(args.video, args.interval, args.width, args.cols, args.output)

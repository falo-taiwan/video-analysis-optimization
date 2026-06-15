import os
import sys
import argparse
import time
import io
import cv2
from PIL import Image

def extract_and_resize_frames(video_path, interval_seconds, target_width):
    """
    從影片中抽取指定秒數間隔的影格，並將其縮小尺寸。
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
    print(f"影片總長: {duration:.2f} 秒, 原始 FPS: {fps:.2f}")
    
    frame_step = max(1, int(fps * interval_seconds))
    print(f"設定間隔: 每 {interval_seconds} 秒抽樣一次影格")
    print(f"設定尺寸: 寬度縮放至 {target_width}px")

    extracted_frames = []
    current_frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame_idx % frame_step == 0:
            timestamp_sec = current_frame_idx / fps
            
            # 進行等比例縮放
            h, w = frame.shape[:2]
            scale = target_width / w
            new_h = int(h * scale)
            resized_frame = cv2.resize(frame, (target_width, new_h))
            
            # 將圖片編碼為 JPG 二進位格式，方便直接傳給 Ollama
            _, encoded_img = cv2.imencode('.jpg', resized_frame)
            img_bytes = encoded_img.tobytes()
            
            extracted_frames.append({
                'timestamp': timestamp_sec,
                'bytes': img_bytes
            })
            
        current_frame_idx += 1

    cap.release()
    print(f"影格抽取完成，共抽取出 {len(extracted_frames)} 張影格。")
    return extracted_frames

def run_ollama_ocr(frames, model_name):
    """
    呼叫本地 Ollama 服務進行 OCR 分析。
    """
    try:
        import ollama
    except ImportError:
        print("正在為您安裝 ollama 官方 Python 套件...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
        import ollama

    # 檢查 Ollama 是否有在運行
    try:
        ollama.list()
    except Exception as e:
        print("\n錯誤: 無法連線至本地 Ollama 服務。")
        print("請確保您已經下載並啟動了 Ollama 應用程式 (https://ollama.com/)")
        print("並且在終端機中拉取了視覺模型，例如: ollama run llama3.2-vision")
        sys.exit(1)

    print(f"開始使用本地 Ollama 模型 [{model_name}] 進行逐影格 OCR 處理...")
    print("提示: 因為本地模型上下文長度與記憶體限制，我們會逐張影格發送請求，以確保穩定性。")

    results = []
    
    for idx, frame in enumerate(frames):
        t = frame['timestamp']
        mins = int(t // 60)
        secs = int(t % 60)
        time_str = f"[{mins:02d}:{secs:02d}]"
        
        print(f"正在處理影格 {idx+1}/{len(frames)} - {time_str} ... ", end="", flush=True)
        
        prompt = (
            "你是一個圖片文字辨識 (OCR) 助手。請詳細列出這張圖片中的所有文字與看板內容。"
            "請直接輸出辨識出的文字，不需要多餘的解釋或客套話。若無文字，請回答「無文字」。"
        )
        
        start_time = time.time()
        try:
            # 呼叫 Ollama API，傳入影格的 bytes
            response = ollama.chat(
                model=model_name,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [frame['bytes']]
                }]
            )
            elapsed = time.time() - start_time
            text = response['message']['content'].strip()
            print(f"完成! (耗時 {elapsed:.2f} 秒)")
            
            results.append((time_str, text))
        except Exception as e:
            print(f"失敗! 錯誤原因: {e}")
            results.append((time_str, f"錯誤: {e}"))

    # 彙整輸出結果
    print("\n" + "="*20 + " 本地 Ollama OCR 彙整結果 " + "="*20)
    for time_str, text in results:
        print(f"\n{time_str}:")
        print(text)
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="本地 Ollama 影片 OCR 工具")
    parser.add_argument("--video", type=str, default="/Users/force/Downloads/FDownloader.Net_AQPxgAvkg8kYO7vk_0A6TNjymU8NGZOO6Ck4HIXhO6ZmuSxixwhdtB_VM5WAcKYu-OkoL4FmF2UpT6s2gOIlZHjUvZ21q5Rpxls79Ov.mp4", help="影片檔案路徑")
    parser.add_argument("--interval", type=float, default=5.0, help="抽樣間隔秒數 (預設: 5.0 秒，本地跑建議設長一點)")
    parser.add_argument("--width", type=int, default=640, help="影格縮小後寬度 (預設: 640px)")
    parser.add_argument("--model", type=str, default="llama3.2-vision", help="Ollama 視覺模型名稱 (例如: llama3.2-vision, qwen2.5-vl)")
    
    args = parser.parse_args()
    
    # 1. 抽取並縮放影格
    frames = extract_and_resize_frames(args.video, args.interval, args.width)
    
    # 2. 呼叫 Ollama
    run_ollama_ocr(frames, args.model)

if __name__ == "__main__":
    main()

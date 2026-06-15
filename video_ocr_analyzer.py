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
    
    # 計算每隔多少幀抽取一次
    frame_step = max(1, int(fps * interval_seconds))
    print(f"設定間隔: 每 {interval_seconds} 秒抽樣一次影格 (每隔 {frame_step} 幀)")
    print(f"設定尺寸: 寬度縮放至 {target_width}px (等比例縮放)")

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
            
            # 將 OpenCV 的 BGR 格式轉為 PIL 的 RGB 格式以利後續處理
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            
            extracted_frames.append({
                'timestamp': timestamp_sec,
                'image': pil_img,
                'original_size': (w, h),
                'new_size': (target_width, new_h)
            })
            
        current_frame_idx += 1

    cap.release()
    print(f"影格抽取完成，共抽取出 {len(extracted_frames)} 張影格。")
    return extracted_frames

def run_gemini_ocr(frames, api_key):
    """
    使用 Gemini 1.5 Flash 進行雲端多模態 OCR 分析。
    """
    try:
        import google.generativeai as genai
    except ImportError:
        print("正在為您安裝 google-generativeai 套件...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
        import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # 建立多模態 Prompt 內容
    # 我們將所有圖片與時間戳記拼接在一個請求中，讓模型可以進行上下文關聯的 OCR 分析
    contents = [
        "你是一個專業的影片文字辨識 (Video OCR) 助手。請幫我辨識以下多張影片影格中的所有文字。"
        "請務必遵循以下規範：\n"
        "1. 請依據每個時間點（格式如 [XX:XX]）列出畫面上出現的所有文字。\n"
        "2. 如果前後影格的文字沒有變化，請合併或註明「文字無變動」。\n"
        "3. 請特別注意招牌、簡報投影、字幕、浮水印等文字的辨識。\n"
        "4. 請以繁體中文 (zh-TW) 格式輸出結果。\n"
    ]

    for frame in frames:
        t = frame['timestamp']
        mins = int(t // 60)
        secs = int(t % 60)
        time_str = f"[{mins:02d}:{secs:02d}]"
        
        contents.append(f"\n時間點: {time_str}")
        contents.append(frame['image'])

    print("正在發送多模態 OCR 請求至 Gemini API...")
    start_time = time.time()
    response = model.generate_content(contents)
    end_time = time.time()
    
    print(f"API 回應完成，耗時: {end_time - start_time:.2f} 秒\n")
    return response.text

def run_local_ocr_placeholder(frames):
    """
    本地 OCR 演示 (例如 EasyOCR / PaddleOCR)。
    因為本機目前未安裝相關套件，此處提供實作架構說明，並輸出基本統計資訊。
    """
    print("\n--- 本地 OCR 虛擬執行 (EasyOCR/Tesseract 示範) ---")
    print("若要使用本地端 OCR，通常會使用以下程式碼結構：")
    print("""
    # 安裝指令: pip install easyocr
    import easyocr
    reader = easyocr.Reader(['ch_tra', 'en']) # 支援繁中與英文
    
    for frame in frames:
        # 將 PIL Image 轉為 numpy array 供 easyocr 辨識
        img_np = np.array(frame['image'])
        result = reader.readtext(img_np)
        
        # result 格式為: [([[x, y], ...], '辨識文字', 信心度), ...]
        print(f"時間 {frame['timestamp']:.2f}s:")
        for bbox, text, prob in result:
            print(f"  - {text} (信心度: {prob:.2f})")
    """)
    print("--------------------------------------------------")
    
    # 統計資訊模擬
    print(f"本機模擬處理了 {len(frames)} 張影格。")
    for idx, frame in enumerate(frames[:3]):
        t = frame['timestamp']
        print(f"影格 {idx+1}: 時間點 {int(t//60):02d}:{int(t%60):02d}, 縮小後尺寸: {frame['new_size'][0]}x{frame['new_size'][1]}")
    if len(frames) > 3:
        print(f"... 以及其他 {len(frames)-3} 張影格。")

def main():
    parser = argparse.ArgumentParser(description="影片 OCR 分析工具 (可調整尺寸、間隔與演算法)")
    parser.add_argument("--video", type=str, default="/Users/force/Downloads/FDownloader.Net_AQPxgAvkg8kYO7vk_0A6TNjymU8NGZOO6Ck4HIXhO6ZmuSxixwhdtB_VM5WAcKYu-OkoL4FmF2UpT6s2gOIlZHjUvZ21q5Rpxls79Ov.mp4", help="影片檔案路徑")
    parser.add_argument("--interval", type=float, default=2.0, help="影格抽取間隔秒數 (預設: 2.0 秒)")
    parser.add_argument("--width", type=int, default=640, help="抽樣影格縮小後的寬度 (預設: 640px)")
    parser.add_argument("--algo", type=str, choices=["gemini", "local"], default="gemini", help="OCR 演算法方案: gemini (雲端大模型) 或 local (本地端 OCR)")
    
    args = parser.parse_args()

    # 1. 抽取影格與等比例縮放
    frames = extract_and_resize_frames(args.video, args.interval, args.width)

    # 2. 選擇 OCR 演算法執行
    if args.algo == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("\n[警告] 未設定 GEMINI_API_KEY 環境變數。")
            print("請先設定環境變數，或使用 '--algo local' 查看本地 OCR 範例。")
            print("設定方式: export GEMINI_API_KEY='你的金鑰'\n")
            sys.exit(1)
        
        result = run_gemini_ocr(frames, api_key)
        print("=== OCR 辨識結果 ===")
        print(result)
        print("====================")
    else:
        run_local_ocr_placeholder(frames)

if __name__ == "__main__":
    main()

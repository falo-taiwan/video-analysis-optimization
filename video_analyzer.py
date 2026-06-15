import os
import sys
import time

def analyze_video(video_path, prompt):
    # 檢查 API Key
    if not os.environ.get("GEMINI_API_KEY"):
        print("錯誤: 請先設定 GEMINI_API_KEY 環境變數。")
        print("例如: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    try:
        import google.generativeai as genai
    except ImportError:
        print("正在嘗試為您安裝 google-generativeai 套件...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
        import google.generativeai as genai

    print(f"正在初始化 Gemini API...")
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # 1. 上傳影片
    print(f"正在上傳影片檔案: {video_path}")
    print("這可能需要一些時間，具體取決於您的網路速度...")
    video_file = genai.upload_file(path=video_path)
    print(f"上傳完成！檔案名稱: {video_file.name}")

    # 2. 等待影片處理完成 (Gemini API 需要時間對影片進行索引與影格抽取)
    print("正在等待 Gemini API 處理影片內容...")
    while video_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(f"影片處理失敗: {video_file.error.message}")
    
    print("\n影片處理完成！開始進行 AI 分析...")

    # 3. 呼叫 Gemini 1.5 Flash 進行分析
    # Gemini 1.5 Flash 速度快且成本極低，非常適合此長度的影片
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    start_time = time.time()
    response = model.generate_content([video_file, prompt])
    end_time = time.time()

    print("\n--- 分析結果 ---")
    print(response.text)
    print("----------------")
    print(f"分析耗時: {end_time - start_time:.2f} 秒")

    # 4. 清理上傳的檔案 (建議習慣，雖然 API 幾天後也會自動刪除)
    print("\n正在清理 API 上的臨時影片檔案...")
    genai.delete_file(video_file.name)
    print("清理完成！")

if __name__ == "__main__":
    video_path = "/Users/force/Downloads/FDownloader.Net_AQPxgAvkg8kYO7vk_0A6TNjymU8NGZOO6Ck4HIXhO6ZmuSxixwhdtB_VM5WAcKYu-OkoL4FmF2UpT6s2gOIlZHjUvZ21q5Rpxls79Ov.mp4"
    default_prompt = "請幫我詳細分析這部影片的內容，包括畫面情境、音訊/口白重點、影片節奏，以及這部影片想表達的主旨。"
    
    prompt = sys.argv[1] if len(sys.argv) > 1 else default_prompt
    
    if not os.path.exists(video_path):
        print(f"找不到影片檔案: {video_path}，請確認路徑是否正確。")
        sys.exit(1)
        
    analyze_video(video_path, prompt)

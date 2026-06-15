# 影片 AI 內容分析測試 (Video AI Content Analysis Test)

本專案提供了一個使用 Google Gemini 1.5 家族進行影片多模態分析的測試腳本。

## 影片基本資訊 (偵測結果)
- **檔案路徑**: `/Users/force/Downloads/FDownloader.Net_AQPxgAvkg8kYO7vk_0A6TNjymU8NGZOO6Ck4HIXhO6ZmuSxixwhdtB_VM5WAcKYu-OkoL4FmF2UpT6s2gOIlZHjUvZ21q5Rpxls79Ov.mp4`
- **影片時長**: 89.67 秒 (約 1.5 分鐘)
- **解析度**: 640x360
- **影格率**: 23.98 FPS (共 2,150 影格)
- **檔案大小**: 3.7 MB

---

## 快速開始

### 1. 設定 API Key
請先確保您擁有 Gemini API 金鑰。在終端機中執行：
```bash
export GEMINI_API_KEY="您的_GEMINI_API_金鑰"
```

### 2. 執行分析腳本
腳本會自動為您安裝所需的 `google-generativeai` 依賴套件並執行分析：
```bash
python3 video_analyzer.py
```

### 3. 自訂分析 Prompt
您可以透過命令列參數傳入自訂的 Prompt：
```bash
python3 video_analyzer.py "請幫我摘錄影片中所有人說過的話，並標註時間點。"
```

---

## 方案、成本與效能綜合評估

對於此 90 秒 (3.7MB) 影片，我們提供以下三種 AI 分析方案的比較：

### 方案 A：原生多模態大模型 (首選推薦 🌟)
- **使用工具**: Gemini 1.5 Flash 或 Gemini 1.5 Pro。
- **運作機制**: 直接將 MP4 上傳。API 自動抽取音訊 (約 283 tokens/秒) 與影像影格 (1 fps, 約 258 tokens/秒)。整個影片轉換為約 50,000 tokens。
- **成本**:
  - **Gemini 1.5 Flash**: 每百萬 Token \$0.075 USD。**單次分析僅需約 \$0.00375 USD (約新台幣 0.12 元)**。
  - **Gemini 1.5 Pro**: 每百萬 Token \$1.25 USD。**單次分析約需 \$0.0625 USD (約新台幣 2 元)**。
- **效能/延遲**:
  - **Flash**: 推理速度極快 (約 5~15 秒)，適合絕大多數影片摘要、物件識別與快速問答。
  - **Pro**: 推理約 15~30 秒，具備更強的邏輯推理與極細微細節的辨識能力。

### 方案 B：傳統影音分離流水線 (自建 Pipeline)
- **使用工具**: OpenCV (抽取影格) + Whisper (語音轉文字) + 視覺大模型 (GPT-4o-mini)。
- **運作機制**: 本地抽幀並轉檔語音後，交由個別 API 處理，最後拼湊 Prompt。
- **成本**: Whisper API (\$0.009) + 45 張 low-res 影格輸入 GPT-4o-mini (\$0.038) = **約 \$0.047 USD (約新台幣 1.5 元)**。
- **效能/延遲**: 因多個 API 呼叫，延遲較高 (約 20~30 秒)。影像與音訊的時序連貫性較弱。

### 方案 C：專用影音 CV 服務 (企業結構化分析)
- **使用工具**: Google Cloud Video Intelligence API。
- **運作機制**: 分析影片中的物體追蹤、文字偵測 (OCR)、場景偵測等，回傳結構化 JSON。
- **成本**: 單項功能每分鐘約 \$0.15 USD，若啟用多項，費用約 **\$0.45 USD (約新台幣 14 元)**。
- **效能/延遲**: 屬於批次運算，不具備自然語言對話與大模型總結能力，需後續工程自行解析 JSON。

---

## 進階測試：客製化影片 OCR 工具 (可調秒數與尺寸)

如果您想測試 **「先縮小尺寸、自訂秒數抽樣、並選擇演算法」** 的做法，可以使用我們編寫的進階指令碼 [video_ocr_analyzer.py](file:///Users/force/Google_Antigravity/video-analyze/video_ocr_analyzer.py)。

### 參數說明：
- `--video`: 影片檔案路徑 (預設已指向您的下載影片)
- `--interval`: 抽樣間隔（秒），例如 `2.0` 代表每 2 秒抽 1 張影格進行 OCR。
- `--width`: 影格縮小後的寬度像素，預設 `640`（維持等比例縮放）。縮小尺寸能大幅降低上傳時間與 Token 成本。
- `--algo`: 選擇演算法：
  - `gemini`: (預設) 使用 Gemini 1.5 Flash 進行雲端多模態 OCR。
  - `local`: 本地 OCR（會列出 EasyOCR / Tesseract 的程式碼實作架構）。

### 範例指令：

**1. 每 3 秒抽樣一次，並縮小至寬度 480px，使用 Gemini 進行 OCR：**
```bash
python3 video_ocr_analyzer.py --interval 3.0 --width 480 --algo gemini
```

**2. 使用本地端 OCR 架構測試：**
```bash
python3 video_ocr_analyzer.py --interval 2.0 --width 640 --algo local
```

---

## 本地端 Ollama 測試工具

我們另外編寫了 [video_ocr_ollama.py](file:///Users/force/Google_Antigravity/video-analyze/video_ocr_ollama.py) 腳本，用來示範與調用您本機運行的 Ollama 視覺模型。

### 執行前準備：
1. 請先確保您的 Mac 已安裝並啟動 [Ollama](https://ollama.com/) 應用程式。
2. 在終端機中拉取您想要使用的視覺大模型。例如：
   ```bash
   ollama pull llama3.2-vision
   # 或者更適合中文 OCR 的 Qwen 模型
   ollama pull qwen2.5-vl:7b
   ```

### 執行指令：
```bash
# 預設每 5 秒抽樣一次，使用 llama3.2-vision 模型
python3 video_ocr_ollama.py --interval 5.0 --model llama3.2-vision

# 或是指定使用 qwen2.5-vl 模型
python3 video_ocr_ollama.py --interval 5.0 --model qwen2.5-vl:7b
```

---

## 時間拼圖產生器 (Grid Storyboard Generator)

我們編寫了 [video_grid_generator.py](file:///Users/force/Google_Antigravity/video-analyze/video_grid_generator.py) 用於將影片分拆後拼接成一張時間軸網格拼圖 (Storyboard Image)。這樣能將多張影格壓縮在單一圖片中，非常適合一次性發送給 Ollama 或 GPT-4o 進行低成本、高效率的視覺分析。

### 執行指令：
```bash
# 抽取間隔 6.0 秒的影格，縮小至寬度 320px，排列成 4x4 的時間網格圖片
python3 video_grid_generator.py --interval 6.0 --width 320 --cols 4 --output time_grid.jpg
```
這會在當前目錄下生成一個帶有時間戳記的 `time_grid.jpg`。




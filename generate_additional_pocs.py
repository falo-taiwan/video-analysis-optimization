import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

def get_font(font_paths, size):
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, coords, r, fill, outline=None, width=1):
    x1, y1, x2, y2 = coords
    draw.rectangle([x1+r, y1, x2-r, y2], fill=fill, outline=outline, width=width)
    draw.rectangle([x1, y1+r, x2, y2-r], fill=fill, outline=outline, width=width)
    draw.ellipse([x1, y1, x1+2*r, y1+2*r], fill=fill, outline=outline, width=width)
    draw.ellipse([x2-2*r, y1, x2, y1+2*r], fill=fill, outline=outline, width=width)
    draw.ellipse([x1, y2-2*r, x1+2*r, y2], fill=fill, outline=outline, width=width)
    draw.ellipse([x2-2*r, y2-2*r, x2, y2], fill=fill, outline=outline, width=width)

def generate_two_stage_gif(font_title, font_sub, font_mono, output_path):
    print("正在生成「雙階段按需補幀」POC 概念動畫 (GIF)...")
    frames = []
    width, height = 640, 360
    total_frames = 60

    for i in range(total_frames):
        img = Image.new("RGB", (width, height), "#0B0F19")
        draw = ImageDraw.Draw(img)
        
        # 標題
        draw.text((20, 15), "方案二：雙階段「按需補幀」回饋機制 (Two-Stage Loop)", fill="#00F2FE", font=font_title)
        draw.text((480, 15), "Falo x Force Cheng", fill="#243049", font=font_sub)

        # 繪製左方：本地伺服器/影片源
        server_x, server_y = 100, 180
        draw.rectangle([(server_x-40, server_y-30), (server_x+40, server_y+30)], fill="#1F2937", outline="#4FACFE", width=2)
        draw.text((server_x-32, server_y-10), "本地主機", fill="#F3F4F6", font=font_sub)

        # 繪製右方：雲端 AI 大模型
        ai_x, ai_y = 540, 180
        draw.ellipse([(ai_x-35, ai_y-35), (ai_x+35, ai_y+35)], fill="#0E1420", outline="#00F2FE", width=2)
        draw.text((ai_x-22, ai_y-10), "雲端 AI", fill="#00F2FE", font=font_sub)

        # 時間軸 (上方)
        timeline_y = 80
        draw.line([(80, timeline_y), (560, timeline_y)], fill="#243049", width=4)
        draw.text((75, timeline_y+10), "00:00", fill="#6B7280", font=font_mono)
        draw.text((535, timeline_y+10), "00:10", fill="#6B7280", font=font_mono)

        # 模擬狀態演進：
        # i = 0~20：第一階段 - 傳送稀疏影格
        # i = 20~40：AI 判斷有問題，回傳補幀請求
        # i = 40~60：第二階段 - 本地補幀並再次傳送，AI 確認成功
        
        if i < 20:
            # 1. 稀疏傳送：畫面上只標註兩個稀疏的採樣點 (0s 與 10s)
            draw.ellipse([(80-5, timeline_y-5), (80+5, timeline_y+5)], fill="#EF4444")
            draw.ellipse([(560-5, timeline_y-5), (560+5, timeline_y+5)], fill="#EF4444")
            
            # 飛行的信號封包 (左往右)
            pkg_x = server_x + int((ai_x - server_x) * (i / 20.0))
            draw.ellipse([(pkg_x-6, server_y-6), (pkg_x+6, server_y+6)], fill="#EF4444")
            
            draw.text((150, 240), "【第一階段】傳送稀疏影格拼圖 (節省 98% Token)", fill="#9CA3AF", font=font_sub)
            draw.text((150, 265), "→ 只擷取 00:00 與 00:10 兩個端點進行快速初掃", fill="#6B7280", font=font_sub)
            
        elif i >= 20 and i < 40:
            # 2. AI 請求補幀
            draw.ellipse([(80-5, timeline_y-5), (80+5, timeline_y+5)], fill="#EF4444")
            draw.ellipse([(560-5, timeline_y-5), (560+5, timeline_y+5)], fill="#EF4444")
            
            # 閃爍的 AI 思考標記
            draw.text((ai_x-50, ai_y-60), "⚠️ 偵測到異常！", fill="#F59E0B", font=font_sub)
            
            # 反向飛行信號封包 (右往左)
            pkg_x = ai_x - int((ai_x - server_x) * ((i - 20) / 20.0))
            draw.ellipse([(pkg_x-6, server_y-6), (pkg_x+6, server_y+6)], fill="#F59E0B")
            
            draw.text((150, 240), "【AI 反饋】偵測到 00:04 處有像素變動，發送補幀指令", fill="#F59E0B", font=font_sub)
            draw.text((150, 265), "← 請求本地主機補提 00:02、00:04、00:06、00:08 影格", fill="#6B7280", font=font_sub)
            
        else:
            # 3. 補幀傳送
            # 時間軸上補滿密集的綠色圓點
            for t_step in range(80, 561, 96):
                draw.ellipse([(t_step-5, timeline_y-5), (t_step+5, timeline_y+5)], fill="#10B981")
                
            # 飛行的信號封包 (左往右，綠色)
            pkg_x = server_x + int((ai_x - server_x) * ((i - 40) / 20.0))
            draw.ellipse([(pkg_x-6, server_y-6), (pkg_x+6, server_y+6)], fill="#10B981")
            
            draw.text((ai_x-45, ai_y-60), "✅ 識別成功！", fill="#10B981", font=font_sub)
            draw.text((150, 240), "【第二階段】本地補齊影格並傳送，AI 完成精準分析", fill="#10B981", font=font_sub)
            draw.text((150, 265), "→ 只在需要時補充中間影格，維持極低耗費與高精準度", fill="#6B7280", font=font_sub)

        # 箭頭連線
        draw.line([(server_x+50, server_y), (ai_x-50, server_y)], fill="#243049", width=2)
        
        frames.append(img)
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=150, loop=0)
    print(f"雙階段動畫生成成功：{output_path}")

def generate_restoration_gif(font_title, font_sub, font_mono, output_path):
    print("正在生成「畫面重建與邊緣修補」POC 概念動畫 (GIF)...")
    frames = []
    width, height = 640, 360
    total_frames = 60

    for i in range(total_frames):
        img = Image.new("RGB", (width, height), "#0B0F19")
        draw = ImageDraw.Draw(img)
        
        # 標題
        draw.text((20, 15), "方案三：畫面重建與邊緣修補 (Interpolation & Super-Resolution)", fill="#00F2FE", font=font_title)
        draw.text((480, 15), "Falo x Force Cheng", fill="#243049", font=font_sub)

        # 左右分割線
        draw.line([(width//2, 50), (width//2, 300)], fill="#243049", width=2)

        # 左側標題：原始動態模糊 (Original Motion Blur)
        draw.text((40, 60), "1. 原始影格 (高速行駛動態模糊)", fill="#9CA3AF", font=font_sub)
        
        # 右側標題：AI 邊緣修補 (AI Reconstructed)
        draw.text((360, 60), "2. AI 邊緣修補與超解析度", fill="#00F2FE", font=font_sub)

        # 模擬車牌區域座標
        plate_w, plate_h = 200, 80
        left_plate_x, left_plate_y = 60, 120
        right_plate_x, right_plate_y = 380, 120

        # --- 繪製左側 (模糊車牌) ---
        # 繪製車牌框 (有模糊感)
        draw.rectangle([(left_plate_x, left_plate_y), (left_plate_x+plate_w, left_plate_y+plate_h)], fill="#E5E7EB", outline="#9CA3AF", width=2)
        # 用多層偏移繪製動態模糊字體
        blur_offsets = [-4, -2, 0, 2, 4]
        for offset in blur_offsets:
            # 由於字體模糊，顏色變淡
            draw.text((left_plate_x+25+offset, left_plate_y+20), "ABC-1234", fill="#4B5563", font=font_title)
        # 紅色辨識失敗框
        draw.rectangle([(left_plate_x-5, left_plate_y-5), (left_plate_x+plate_w+5, left_plate_y+plate_h+5)], outline="#EF4444", width=2)
        draw.text((left_plate_x+45, left_plate_y+88), "❌ OCR 辨識失敗", fill="#EF4444", font=font_sub)

        # --- 繪製右側 (清晰修補車牌) ---
        draw.rectangle([(right_plate_x, right_plate_y), (right_plate_x+plate_w, right_plate_y+plate_h)], fill="#F8FAFC", outline="#1E293B", width=2)
        # 清晰銳利字體
        draw.text((right_plate_x+25, right_plate_y+20), "ABC-1234", fill="#0F172A", font=font_title)
        # 綠色辨識成功框
        draw.rectangle([(right_plate_x-5, right_plate_y-5), (right_plate_x+plate_w+5, right_plate_y+plate_h+5)], outline="#10B981", width=2)
        draw.text((right_plate_x+28, right_plate_y+88), "✅ OCR 成功: [ABC-1234]", fill="#10B981", font=font_sub)

        # 模擬動態掃描線 (橫跨右側車牌)
        scan_x = right_plate_x + int(plate_w * (abs(30 - (i % 60)) / 30.0))
        draw.line([(scan_x, right_plate_y-2), (scan_x, right_plate_y+plate_h+2)], fill="#00F2FE", width=3)

        # 說明文字 (底部)
        draw.text((40, 315), "說明：高速移動造成的邊緣模糊會使傳統 OCR 無法解析文字。", fill="#6B7280", font=font_sub)
        draw.text((360, 315), "說明：利用超解析度模型修補邊緣，大幅提升本地端辨識率。", fill="#6B7280", font=font_sub)

        frames.append(img)
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=100, loop=0)
    print(f"修補重建動畫生成成功：{output_path}")

def main():
    font_paths = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    ]
    
    font_title = get_font(font_paths, 17)
    font_sub = get_font(font_paths, 13)
    font_mono = get_font(font_paths, 11)

    # 生成第二階段動畫
    generate_two_stage_gif(font_title, font_sub, font_mono, "/Users/force/Google_Antigravity/video-analyze/two_stage_loop_poc.gif")
    
    # 生成第三階段動畫
    generate_restoration_gif(font_title, font_sub, font_mono, "/Users/force/Google_Antigravity/video-analyze/image_restoration_poc.gif")

if __name__ == "__main__":
    main()

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
    
    def draw_star_helper(draw, x, y, size, color):
        points = []
        num_points = 8
        for idx in range(num_points * 2):
            angle = idx * math.pi / num_points
            r = size if idx % 2 == 0 else size / 2.5
            points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
        draw.polygon(points, fill=color)

    frames = []
    width, height = 640, 360
    total_frames = 80

    for i in range(total_frames):
        img = Image.new("RGB", (width, height), "#0B0F19")
        draw = ImageDraw.Draw(img)
        
        # 1. 頂部標題與作者
        draw.text((20, 12), "方案二：雙階段「按需補幀」回饋機制 (Two-Stage Loop)", fill="#00F2FE", font=font_title)
        draw.text((480, 15), "Falo x Force Cheng", fill="#243049", font=font_sub)

        # 2. 繪製左側 CCTV 畫面模擬區 與 右側 雲端 AI 狀態區
        # 左側 CCTV (20 - 410px, 45 - 225px)
        cctv_x1, cctv_y1, cctv_x2, cctv_y2 = 20, 45, 410, 225
        draw.rectangle([(cctv_x1, cctv_y1), (cctv_x2, cctv_y2)], outline="#243049", width=2)
        draw.text((cctv_x1 + 10, cctv_y1 + 8), "本地 CCTV 監控畫面 (00:00 - 00:10)", fill="#9CA3AF", font=font_mono)

        # 繪製公路與車道
        road_y1, road_y2 = cctv_y1 + 35, cctv_y2 - 35
        draw.rectangle([(cctv_x1 + 2, road_y1), (cctv_x2 - 2, road_y2)], fill="#1F2937") # 柏油路
        draw.line([(cctv_x1 + 2, road_y1 + 4), (cctv_x2 - 2, road_y1 + 4)], fill="#F59E0B", width=2) # 雙黃線
        
        for x_dash in range(cctv_x1 + 10, cctv_x2 - 10, 35):
            draw.line([(x_dash, (road_y1 + road_y2) // 2), (x_dash + 15, (road_y1 + road_y2) // 2)], fill="#F3F4F6", width=1)
            
        draw.line([(cctv_x1 + 2, road_y2 - 4), (cctv_x2 - 2, road_y2 - 4)], fill="#F3F4F6", width=2) # 路肩

        # 車道上的車輛
        white_car_x = cctv_x2 - 80
        white_car_y = road_y1 + 25
        blue_car_start = cctv_x1 + 20
        blue_car_end = white_car_x - 30

        # 右側 雲端 AI 狀態區 (430 - 620px, 45 - 225px)
        ai_x1, ai_y1, ai_x2, ai_y2 = 430, 45, 620, 225
        draw.rectangle([(ai_x1, ai_y1), (ai_x2, ai_y2)], fill="#0E1420", outline="#00F2FE" if i >= 26 else "#243049", width=2)
        draw.text((ai_x1 + 12, ai_y1 + 10), "☁️ 雲端 AI 分析狀態", fill="#00F2FE", font=font_sub)

        # 根據階段繪製不同畫面與狀態
        # i = 0~25: 第一階段 - 稀疏影格傳送 (0s 與 10s)
        # i = 26~50: 雲端發現跳躍性變化，發送「補幀請求」
        # i = 51~80: 第二階段 - 本地補幀傳送 (00:04)，AI 成功識別追撞瞬間
        
        if i < 25:
            # 1. 第一階段：稀疏傳送
            # 繪製車輛：白車故障閃黃燈，藍車在左側平穩前進
            draw.rectangle([(white_car_x, white_car_y), (white_car_x + 24, white_car_y + 11)], fill="#E5E7EB", outline="#9CA3AF")
            if i % 6 < 3:
                draw.ellipse([(white_car_x - 2, white_car_y), (white_car_x, white_car_y + 2)], fill="#F59E0B")
                draw.text((white_car_x - 15, white_car_y - 12), "故障車", fill="#F59E0B", font=font_mono)
            
            blue_x = blue_car_start + int((blue_car_end - blue_car_start) * (i / 25.0) * 0.4)
            draw.rectangle([(blue_x, white_car_y), (blue_x + 24, white_car_y + 11)], fill="#3B82F6", outline="#1D4ED8")

            # 雲端 AI 狀態：等待並處理稀疏拼圖
            draw.text((ai_x1 + 15, ai_y1 + 45), "狀態: 稀疏初掃中", fill="#9CA3AF", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 75), "已收影格:", fill="#9CA3AF", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 95), "• 00:00 (正常)", fill="#10B981", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 115), "• 00:10 (事故後)", fill="#EF4444", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 145), "⚠️ 遺漏碰撞瞬間!", fill="#F59E0B", font=font_sub)

            # 網路傳輸包 (紅點從左往右飛)
            pkg_x = cctv_x2 + int((ai_x1 - cctv_x2) * (i / 25.0))
            draw.ellipse([(pkg_x-5, 135), (pkg_x+5, 145)], fill="#EF4444")
            draw.text((pkg_x - 15, 115), "0s/10s", fill="#EF4444", font=font_mono)

            sub_text = "[第一階段] 本地端僅擷取 00:00 與 00:10 進行低成本快速掃描 (節省 98% Token)"
            sub_col = "#9CA3AF"

        elif i >= 25 and i < 50:
            # 2. AI 思考並發送補幀指令
            # 畫面同第一階段，但 AI 框亮起警告，反向飛回補幀信號
            draw.rectangle([(white_car_x, white_car_y), (white_car_x + 24, white_car_y + 11)], fill="#E5E7EB", outline="#9CA3AF")
            if i % 6 < 3:
                draw.ellipse([(white_car_x - 2, white_car_y), (white_car_x, white_car_y + 2)], fill="#F59E0B")
            blue_x = blue_car_start + int((blue_car_end - blue_car_start) * 0.4)
            draw.rectangle([(blue_x, white_car_y), (blue_x + 24, white_car_y + 11)], fill="#3B82F6", outline="#1D4ED8")

            # 雲端 AI 狀態：發送補幀請求
            draw.text((ai_x1 + 15, ai_y1 + 45), "狀態: 觸發補幀回饋", fill="#F59E0B", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 75), "AI 指令發送中:", fill="#F59E0B", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 100), "← 請求 00:04", fill="#00F2FE", font=font_title)
            draw.text((ai_x1 + 15, ai_y1 + 125), "  關鍵影格", fill="#00F2FE", font=font_title)

            # 網路傳輸包 (藍點從右往左飛)
            pkg_x = ai_x1 - int((ai_x1 - cctv_x2) * ((i - 25) / 25.0))
            draw.ellipse([(pkg_x-5, 135), (pkg_x+5, 145)], fill="#00F2FE")
            draw.text((pkg_x - 20, 115), "補幀請求", fill="#00F2FE", font=font_mono)

            sub_text = "[雲端回饋] AI 偵測到跳躍性狀態變更，自動對本地 CCTV 下達「按需補幀」指令"
            sub_col = "#F59E0B"

        else:
            # 3. 第二階段：本地補幀傳送與確認
            # 畫面上顯示車禍追撞瞬間 (00:04)
            draw.rectangle([(white_car_x, white_car_y), (white_car_x + 24, white_car_y + 11)], fill="#E5E7EB", outline="#9CA3AF")
            draw.rectangle([(white_car_x - 15, white_car_y + 2), (white_car_x + 5, white_car_y + 13)], fill="#3B82F6", outline="#1D4ED8")
            draw_star_helper(draw, white_car_x - 5, white_car_y + 6, 12, "#EF4444" if i % 4 < 2 else "#FBBF24")
            draw.text((white_car_x - 30, white_car_y - 14), "🚨 碰撞瞬間(00:04)", fill="#EF4444", font=font_mono)

            # 雲端 AI 狀態：補幀成功，辨識完成
            draw.text((ai_x1 + 15, ai_y1 + 45), "狀態: 補幀識別成功", fill="#10B981", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 75), "精準定位事故:", fill="#10B981", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 100), "• 00:04 追撞點", fill="#10B981", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 125), "• 責任釐清完成", fill="#10B981", font=font_sub)
            draw.text((ai_x1 + 15, ai_y1 + 155), "✅ 成功! 累計省 95%", fill="#10B981", font=font_sub)

            # 網路傳輸包 (綠色圓點從左往右飛)
            pkg_x = cctv_x2 + int((ai_x1 - cctv_x2) * ((i - 50) / 30.0))
            draw.ellipse([(pkg_x-5, 135), (pkg_x+5, 145)], fill="#10B981")
            draw.text((pkg_x - 15, 115), "00:04", fill="#10B981", font=font_mono)

            sub_text = "[第二階段] 本地只補提 00:04 影格，雲端 AI 成功重建事故過程，兼顧省錢與精準"
            sub_col = "#10B981"

        # 3. 底部影片時間軸與採樣格 (245px 起)
        draw.text((20, 235), "教學故事板影格 (Filmstrip Storyboard Slots)", fill="#9CA3AF", font=font_sub)
        
        # 繪製三個影格格線
        box_width = 80
        box_height = 45
        box_y = 258
        
        # 影格 1: 00:00 (正常)
        box1_x = 40
        draw.rectangle([(box1_x, box_y), (box1_x + box_width, box_y + box_height)], outline="#10B981", width=2)
        # 簡易繪製格子內畫面
        draw.rectangle([(box1_x + 2, box_y + 15), (box1_x + box_width - 2, box_y + box_height - 15)], fill="#1F2937")
        draw.rectangle([(box1_x + 10, box_y + 20), (box1_x + 20, box_y + 26)], fill="#3B82F6")
        draw.rectangle([(box1_x + 50, box_y + 20), (box1_x + 60, box_y + 26)], fill="#E5E7EB")
        draw.text((box1_x + 5, box_y + box_height + 4), "00:00 正常", fill="#10B981", font=font_mono)

        # 影格 2: 00:04 (第一階段遺漏 / 第二階段補回)
        box2_x = 160
        if i < 50:
            # 遺漏狀態
            draw.rectangle([(box2_x, box_y), (box2_x + box_width, box_y + box_height)], fill="#1E2030", outline="#EF4444", width=1)
            draw.text((box2_x + 15, box_y + 15), "【 遺漏 】", fill="#EF4444", font=font_sub)
            draw.text((box2_x + 2, box_y + box_height + 4), "00:04 漏判區間", fill="#EF4444", font=font_mono)
        else:
            # 補回狀態
            draw.rectangle([(box2_x, box_y), (box2_x + box_width, box_y + box_height)], outline="#10B981", width=2)
            draw.rectangle([(box2_x + 2, box_y + 15), (box2_x + box_width - 2, box_y + box_height - 15)], fill="#1F2937")
            draw.rectangle([(box2_x + 35, box_y + 20), (box2_x + 45, box_y + 26)], fill="#E5E7EB")
            draw.rectangle([(box2_x + 25, box_y + 21), (box2_x + 35, box_y + 27)], fill="#3B82F6")
            draw_star_helper(draw, box2_x + 35, box_y + 23, 5, "#FBBF24")
            draw.text((box2_x - 5, box_y + box_height + 4), "00:04 補回 (撞擊點)", fill="#10B981", font=font_mono)

        # 影格 3: 00:10 (事故後)
        box3_x = 280
        draw.rectangle([(box3_x, box_y), (box3_x + box_width, box_y + box_height)], outline="#EF4444" if i < 50 else "#10B981", width=2)
        draw.rectangle([(box3_x + 2, box_y + 15), (box3_x + box_width - 2, box_y + box_height - 15)], fill="#1F2937")
        draw.rectangle([(box3_x + 40, box_y + 20), (box3_x + 50, box_y + 26)], fill="#E5E7EB")
        draw.rectangle([(box3_x + 30, box_y + 21), (box3_x + 40, box_y + 27)], fill="#3B82F6")
        draw.text((box3_x + 2, box_y + box_height + 4), "00:10 事故現場", fill="#10B981", font=font_mono)

        # 右側 Token 累計節省百分比
        draw.text((435, 245), "雙階段分析 Token 累計節省", fill="#9CA3AF", font=font_sub)
        savings_text = "98.1%" if i < 50 else "95.6%"
        savings_color = "#00F2FE" if i < 50 else "#10B981"
        draw.text((435, 268), savings_text, fill=savings_color, font=ImageFont.truetype("/System/Library/Fonts/Arial Unicode.ttf" if os.path.exists("/System/Library/Fonts/Arial Unicode.ttf") else "/System/Library/Fonts/STHeiti Medium.ttc", 36))
        
        # 字幕指示
        draw.rectangle([(20, height - 35), (width - 20, height - 10)], fill="#0E1420")
        draw.text((30, height - 31), sub_text, fill=sub_col, font=font_sub)

        # 封包傳輸箭頭背景線
        draw.line([(cctv_x2 + 15, 140), (ai_x1 - 15, 140)], fill="#243049", width=2)

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
